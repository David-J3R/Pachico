"use client";

import { useState, useEffect, useCallback } from "react";
import { Conversation } from "@/lib/types";
import {
  loadConversations,
  saveConversations,
  generateThreadId,
} from "@/lib/storage";

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const stored = loadConversations();
    setConversations(stored);
    setHydrated(true);
  }, []);

  // Persist to localStorage on every change (after hydration)
  useEffect(() => {
    if (hydrated) {
      saveConversations(conversations);
    }
  }, [conversations, hydrated]);

  const activeConversation =
    conversations.find((c) => c.threadId === activeId) ?? null;

  const createConversation = useCallback(() => {
    const threadId = generateThreadId();
    const now = Date.now();
    const convo: Conversation = {
      threadId,
      title: "New Chat",
      createdAt: now,
      updatedAt: now,
      messages: [],
    };
    setConversations((prev) => [convo, ...prev]);
    setActiveId(threadId);
    return threadId;
  }, []);

  const deleteConversation = useCallback(
    (threadId: string) => {
      setConversations((prev) => prev.filter((c) => c.threadId !== threadId));
      if (activeId === threadId) {
        setActiveId(null);
      }
    },
    [activeId]
  );

  const updateConversation = useCallback(
    (threadId: string, updater: (c: Conversation) => Conversation) => {
      setConversations((prev) =>
        prev.map((c) => (c.threadId === threadId ? updater(c) : c))
      );
    },
    []
  );

  return {
    conversations,
    activeConversation,
    activeId,
    hydrated,
    setActiveId,
    createConversation,
    deleteConversation,
    updateConversation,
  };
}
