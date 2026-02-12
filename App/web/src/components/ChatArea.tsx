"use client";

import { useRef, useEffect } from "react";
import { Conversation } from "@/lib/types";
import MessageBubble from "./MessageBubble";
import LoadingDots from "./LoadingDots";
import InputBar from "./InputBar";

interface ChatAreaProps {
  conversation: Conversation | null;
  isLoading: boolean;
  onSend: (content: string) => void;
  onToggleSidebar: () => void;
  onNewChat: () => void;
}

export default function ChatArea({
  conversation,
  isLoading,
  onSend,
  onToggleSidebar,
  onNewChat,
}: ChatAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation?.messages.length, isLoading]);

  return (
    <div className="flex flex-1 flex-col h-screen min-w-0">
      {/* Header */}
      <header className="flex items-center gap-3 border-b border-border-primary px-4 py-3">
        <button
          onClick={onToggleSidebar}
          className="rounded p-1.5 text-text-secondary hover:bg-bg-tertiary hover:text-text-primary transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
        <h1 className="text-sm font-medium text-text-primary truncate">
          {conversation?.title || "Pachico"}
        </h1>
      </header>

      {/* Messages or empty state */}
      {!conversation || conversation.messages.length === 0 ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-6 px-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/photos/Pachico.png"
            alt="Pachico"
            className="w-32 h-32 rounded-full object-cover border-2 border-accent-primary shadow-lg"
          />
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-semibold text-text-primary">
              What are we eating today?
            </h2>
            <p className="text-sm text-text-secondary max-w-sm">
              I&apos;m Pachico — part nutritionist, part gym bro, full-time pear enthusiast. Let&apos;s get your diet in check.
            </p>
          </div>
          {!conversation && (
            <button
              onClick={onNewChat}
              className="mt-2 rounded-lg bg-accent-primary px-4 py-2 text-sm text-white hover:bg-accent-hover transition-colors"
            >
              Start a conversation
            </button>
          )}
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto px-4 py-4">
          <div className="mx-auto max-w-3xl">
            {conversation.messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && <LoadingDots />}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* Input bar — only show when conversation is active */}
      {conversation && <InputBar onSend={onSend} disabled={isLoading} />}
    </div>
  );
}
