"use client";

import { useState, useRef, useCallback, KeyboardEvent } from "react";

interface InputBarProps {
  onSend: (content: string) => void;
  disabled: boolean;
  onFocus?: () => void;
}

export default function InputBar({ onSend, disabled, onFocus }: InputBarProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
    }
  };

  return (
    <div className="p-4">
      <div className="mx-auto max-w-3xl">
        <div className="flex items-end gap-2 rounded-2xl bg-bg-secondary border border-border-input p-2">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => {
              setValue(e.target.value);
              handleInput();
            }}
            onKeyDown={handleKeyDown}
            placeholder="Message Pachico..."
            rows={1}
            className="flex-1 resize-none bg-transparent px-2 py-1.5 text-text-primary placeholder:text-text-placeholder outline-none text-sm leading-relaxed"
            disabled={disabled}
            onFocus={onFocus}
          />
          <button
            onClick={handleSend}
            disabled={!value.trim() || disabled}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-primary text-white transition-colors hover:bg-accent-hover disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 10l7-7m0 0l7 7m-7-7v18"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
