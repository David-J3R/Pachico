"use client";

import { useState, useCallback } from "react";
import { Conversation, Message } from "@/lib/types";
import { sendMessage } from "@/lib/api";

interface UseChatOptions {
  activeConversation: Conversation | null;
  updateConversation: (
    threadId: string,
    updater: (c: Conversation) => Conversation
  ) => void;
}

export function useChat({ activeConversation, updateConversation }: UseChatOptions) {
  const [isLoading, setIsLoading] = useState(false);

  const send = useCallback(
    async (content: string) => {
      if (!activeConversation || !content.trim()) return;

      const threadId = activeConversation.threadId;

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: content.trim(),
        filePaths: [],
        timestamp: Date.now(),
      };

      // Optimistically append user message and set title from first message
      updateConversation(threadId, (c) => {
        const isFirst = c.messages.length === 0;
        return {
          ...c,
          title: isFirst
            ? content.trim().slice(0, 40) + (content.trim().length > 40 ? "..." : "")
            : c.title,
          updatedAt: Date.now(),
          messages: [...c.messages, userMessage],
        };
      });

      setIsLoading(true);

      try {
        const response = await sendMessage(content.trim(), threadId);

        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.text,
          filePaths: response.file_paths,
          timestamp: Date.now(),
        };

        updateConversation(threadId, (c) => ({
          ...c,
          updatedAt: Date.now(),
          messages: [...c.messages, assistantMessage],
        }));
      } catch (err) {
        const errorMessage: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Sorry, something went wrong. ${err instanceof Error ? err.message : "Please try again."}`,
          filePaths: [],
          timestamp: Date.now(),
        };

        updateConversation(threadId, (c) => ({
          ...c,
          updatedAt: Date.now(),
          messages: [...c.messages, errorMessage],
        }));
      } finally {
        setIsLoading(false);
      }
    },
    [activeConversation, updateConversation]
  );

  return { isLoading, send };
}
