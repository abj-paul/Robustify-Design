import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Message } from './models/Message';

interface ChatState {
  selectedSolution: string | null;
  messages: Message[];
}

@Injectable({
  providedIn: 'root'
})
export class ChatStateService {
  private chatStates: Record<string, ChatState> = {};

  getChatState(solution: string): ChatState {
    return this.chatStates[solution] || { 
      selectedSolution: null, 
      messages: [] 
    };
  }

  saveChatState(solution: string, state: ChatState): void {
    this.chatStates[solution] = state;
    // Optional: Add localStorage persistence
    localStorage.setItem(`chatState_${solution}`, JSON.stringify(state));
  }

  loadChatStateFromStorage(solution: string): ChatState | null {
    const storedState = localStorage.getItem(`chatState_${solution}`);
    return storedState ? JSON.parse(storedState) : null;
  }
}