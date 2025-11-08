"use client";

import { useEffect, useRef, useState, useCallback } from "react";

export interface Message {
  id: string;
  type: "user" | "assistant" | "thinking" | "error";
  content: string;
  timestamp: string;
}

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log("WebSocket connected");
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "thinking") {
          setIsThinking(true);
        } else if (data.type === "message") {
          setIsThinking(false);
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              type: "assistant",
              content: data.content,
              timestamp: data.timestamp || new Date().toISOString(),
            },
          ]);
        } else if (data.type === "error") {
          setIsThinking(false);
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              type: "error",
              content: data.error,
              timestamp: new Date().toISOString(),
            },
          ]);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setIsConnected(false);
        setIsThinking(false);

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log("Attempting to reconnect...");
          connect();
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error("Failed to connect:", error);
    }
  }, [url]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback(
    (content: string) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not connected");
        return;
      }

      // Add user message to UI
      const userMessage: Message = {
        id: Date.now().toString(),
        type: "user",
        content,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Send to server
      wsRef.current.send(
        JSON.stringify({
          message: content,
          model: "gpt-4o",
        })
      );
    },
    []
  );

  return {
    messages,
    isConnected,
    isThinking,
    sendMessage,
  };
}
