"use client";

export function ThinkingIndicator() {
  return (
    <div className="flex justify-start mb-4 px-4">
      <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 bg-gray-100">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          </div>
          <span className="text-sm text-gray-600">LifeLine is thinking...</span>
        </div>
      </div>
    </div>
  );
}
