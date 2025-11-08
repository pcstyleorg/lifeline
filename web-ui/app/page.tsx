"use client";

import { useEffect, useRef } from "react";
import { useWebSocket } from "./hooks/useWebSocket";
import { ChatMessage } from "./components/ChatMessage";
import { ChatInput } from "./components/ChatInput";
import { Header } from "./components/Header";
import { ThinkingIndicator } from "./components/ThinkingIndicator";

const WS_URL = "ws://localhost:8000/ws/chat";

export default function Home() {
  const { messages, isConnected, isThinking, sendMessage } = useWebSocket(WS_URL);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <Header isConnected={isConnected} />

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto py-6">
          {messages.length === 0 && !isThinking && (
            <div className="text-center py-12 px-4">
              <div className="text-6xl mb-4">🧬</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Welcome to LifeLine
              </h2>
              <p className="text-gray-600 max-w-md mx-auto">
                I'm here to help you capture, organize, and reflect on the meaningful
                moments of your life. What would you like to log or ask about today?
              </p>
              <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto px-4">
                <button
                  onClick={() => sendMessage("What can you help me with?")}
                  className="p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
                >
                  <div className="font-medium text-gray-900">
                    What can you do?
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    Learn about LifeLine features
                  </div>
                </button>
                <button
                  onClick={() =>
                    sendMessage("Log: Today I started working on a new project")
                  }
                  className="p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
                >
                  <div className="font-medium text-gray-900">
                    Log an event
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    Start capturing your timeline
                  </div>
                </button>
                <button
                  onClick={() => sendMessage("Show my recent events")}
                  className="p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
                >
                  <div className="font-medium text-gray-900">
                    Recent events
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    View your latest memories
                  </div>
                </button>
                <button
                  onClick={() => sendMessage("Show me my timeline statistics")}
                  className="p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
                >
                  <div className="font-medium text-gray-900">
                    Statistics
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    See your timeline stats
                  </div>
                </button>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {isThinking && <ThinkingIndicator />}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <ChatInput
        onSend={sendMessage}
        disabled={!isConnected || isThinking}
        placeholder={
          isConnected
            ? "Tell me what happened today..."
            : "Connecting to LifeLine..."
        }
      />
    </div>
  );
}
