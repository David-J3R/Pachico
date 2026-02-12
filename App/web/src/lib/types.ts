export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  filePaths: string[];
  timestamp: number;
}

export interface Conversation {
  threadId: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  messages: Message[];
}

export interface ChatResponse {
  text: string;
  file_paths: string[];
}
