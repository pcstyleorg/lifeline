"use client";

import { Message } from "../hooks/useWebSocket";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.type === "user";
  const isError = message.type === "error";
  const isThinking = message.type === "thinking";

  if (isThinking) {
    return null; // Thinking indicator is handled separately
  }

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4 px-4`}
    >
      <div
        className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : isError
            ? "bg-red-100 text-red-900 border border-red-300"
            : "bg-gray-100 text-gray-900"
        }`}
      >
        <div className="prose prose-sm max-w-none">
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>
        </div>
        <div
          className={`text-xs mt-1 ${
            isUser ? "text-blue-100" : "text-gray-500"
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
