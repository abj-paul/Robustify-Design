import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BackendService } from '../backend.service';
import { ConstantService } from '../constant.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
  sanitizedHtml?: SafeHtml;
}

interface ChatState {
  project_id: number;
  solution_name: string;
  messages: Message[];
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class ChatComponent implements OnInit {
  projectId: number = 0;
  solutions: string[] = [];
  selectedSolution: string | null = null;
  messages: Message[] = [];
  currentMessage: string = '';
  loading: boolean = false;

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute,
    private backendService: BackendService,
    private constantService: ConstantService,
    private sanitizer: DomSanitizer
  ) {
    marked.setOptions({
      gfm: true,
      breaks: true
    });
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectId = this.constantService.getProject().id;
      this.loadSolutions();
    });
  }

  loadSolutions() {
    this.http.get<{solutions: string[]}>(`${this.backendService.apiUrl}/solutions/${this.constantService.getProject().id}/`)
      .subscribe({
        next: (response) => {
          this.solutions = response.solutions.map(url => url.split('/').pop() || '');
        },
        error: (error) => {
          console.error('Error loading solutions:', error);
        }
      });
  }

  selectSolution(solution: string) {
    this.selectedSolution = solution;
    this.loadChatState(solution);
  }

  loadChatState(solution: string) {
    this.http.get<ChatState>(`${this.backendService.apiUrl}/chat-state/${this.projectId}/${solution}`)
      .subscribe({
        next: (state) => {
          this.messages = state.messages.map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
            sanitizedHtml: msg.sanitizedHtml && typeof msg.sanitizedHtml === 'object' 
              ? this.sanitizer.bypassSecurityTrustHtml(
                  (msg.sanitizedHtml as any).changingThisBreaksApplicationSecurity || msg.text
                )
              : this.parseMarkdown(msg.text)
          }));
        },
        error: (error) => {
          console.log('No existing chat state found, starting new conversation');
          this.messages = [{
            text: `Selected solution: ${solution}`,
            isUser: false,
            timestamp: new Date()
          }];
        }
      });
  }
  
  private parseMarkdown(text: string): SafeHtml {
    try {
      const rawHtml = <string>marked(text);
      return this.sanitizer.bypassSecurityTrustHtml(rawHtml);
    } catch (error) {
      console.error('Markdown parsing error:', error);
      return this.sanitizer.bypassSecurityTrustHtml(text);
    }
  }

  private saveChatState() {
    if (!this.selectedSolution) return;

    const chatState: ChatState = {
      project_id: this.projectId,
      solution_name: this.selectedSolution,
      messages: this.messages
    };

    this.http.post(`${this.backendService.apiUrl}/chat-state/`, chatState)
      .subscribe({
        error: (error) => console.error('Error saving chat state:', error)
      });
  }

  async sendMessage() {
    if (!this.currentMessage.trim() || !this.selectedSolution) return;

    this.messages.push({
      text: this.currentMessage,
      isUser: true,
      timestamp: new Date()
    });
    this.loading = true;

    try {
      const response = await this.http.get<{response: string}>(
        `${this.backendService.apiUrl}/service/gemini/${this.constantService.getProject().id}/`,
        {
          params: {
            solution_name: this.selectedSolution,
            user_query: this.currentMessage
          }
        }
      ).toPromise();

      if (response) {
        const botMessage: Message = {
          text: response.toString(),
          isUser: false,
          timestamp: new Date(),
          sanitizedHtml: this.parseMarkdown(response.toString())
        };
        
        this.messages.push(botMessage);
        this.saveChatState();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      this.messages.push({
        text: 'Sorry, there was an error processing your message.',
        isUser: false,
        timestamp: new Date()
      });
    }

    this.loading = false;
    this.currentMessage = '';
  }
}