import { Component, OnInit, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BackendService } from '../backend.service';
import { ConstantService } from '../constant.service';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class ChatComponent implements OnInit {
  @ViewChild('messageContainer') private messageContainer!: ElementRef;

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
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.route.params.subscribe(() => {
      this.projectId = this.constantService.getProject().id;
      this.loadSolutions();
    });
  }

  loadSolutions() {
    this.http.get<{ solutions: string[] }>(`${this.backendService.apiUrl}/solutions/${this.projectId}/`)
      .subscribe({
        next: (response) => {
          this.solutions = response.solutions.map(url => url.split('/').pop() || '');
          this.cdr.detectChanges();
        },
        error: (error) => console.error('Error loading solutions:', error)
      });
  }

  selectSolution(solution: string) {
    this.selectedSolution = solution;
    this.messages = [{
      text: `Selected solution: ${solution}`,
      isUser: false,
      timestamp: new Date()
    }];
    this.cdr.detectChanges();
  }

  async sendMessage() {
    if (!this.currentMessage.trim() || !this.selectedSolution) return;

    const userMessage = this.currentMessage.trim();
    this.currentMessage = '';
    this.messages.push({
      text: userMessage,
      isUser: true,
      timestamp: new Date()
    });

    this.cdr.detectChanges();
    this.scrollToBottom();

    this.loading = true;

    try {
      const response = await this.http.get<{ response: string }>(
        `${this.backendService.apiUrl}/service/gemini/${this.projectId}/`,
        {
          params: {
            solution_name: this.selectedSolution,
            user_query: userMessage
          }
        }
      ).toPromise();
      console.log(response);
      if (response) {
        this.messages.push({
          text: response.toString(),
          isUser: false,
          timestamp: new Date()
        });
      } else {
        this.messages.push({
          text: 'No response received from the backend.',
          isUser: false,
          timestamp: new Date()
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      this.messages.push({
        text: 'Sorry, there was an error processing your message.',
        isUser: false,
        timestamp: new Date()
      });
    } finally {
      this.loading = false;
      this.cdr.detectChanges();
      this.scrollToBottom();
    }
  }

  private scrollToBottom(): void {
    try {
      setTimeout(() => {
        const element = this.messageContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      });
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }
}
