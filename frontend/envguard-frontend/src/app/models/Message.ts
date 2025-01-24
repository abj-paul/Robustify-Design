import { SafeHtml } from "@angular/platform-browser";

export interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
  sanitizedHtml?: SafeHtml;
}
