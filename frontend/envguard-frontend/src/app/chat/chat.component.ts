// chat.component.ts
import { Component, OnInit } from '@angular/core';
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
  projectId: number = 0;
  solutions: string[] = [];
  selectedSolution: string | null = null;
  messages: Message[] = [];
  currentMessage: string = '';
  loading: boolean = false;

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute,
    private backendService : BackendService,
    private constantService : ConstantService
  ) {}

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
          console.log(response);
          this.solutions = response.solutions.map(url => {
            // Extract filename from URL
            return url.split('/').pop() || '';
          });
        },
        error: (error) => {
          console.error('Error loading solutions:', error);
        }
      });
  }

  selectSolution(solution: string) {
    this.selectedSolution = solution;
    this.messages = []; // Clear chat when new solution is selected
    // Add initial message showing selected solution
    this.messages.push({
      text: `Selected solution: ${solution}`,
      isUser: false,
      timestamp: new Date()
    });
  }

  async sendMessage() {
    if (!this.currentMessage.trim() || !this.selectedSolution) return;

    // Add user message to chat
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
        console.log(response);
        this.messages.push({
          text: response.toString(),
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
    }

    this.loading = false;
    this.currentMessage = '';
  }
}