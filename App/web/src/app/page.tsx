"use client";

import { useState } from "react";
import { useConversations } from "@/hooks/useConversations";
import { useChat } from "@/hooks/useChat";
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";

export default function Home() {
  const {
    conversations,
    activeConversation,
    activeId,
    hydrated,
    setActiveId,
    createConversation,
    deleteConversation,
    updateConversation,
  } = useConversations();

  const { isLoading, send } = useChat({
    activeConversation,
    updateConversation,
  });

  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (!hydrated) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={setActiveId}
        onNew={createConversation}
        onDelete={deleteConversation}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <ChatArea
        conversation={activeConversation}
        isLoading={isLoading}
        onSend={send}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onNewChat={createConversation}
      />
    </div>
  );
}
