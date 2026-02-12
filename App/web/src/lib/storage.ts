import { Conversation } from "./types";

const STORAGE_KEY = "pachico-conversations";

export function loadConversations(): Conversation[] {
  if (typeof window === "undefined") return [];
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

export function saveConversations(conversations: Conversation[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
}

export function generateThreadId(): string {
  return crypto.randomUUID();
}
