"use client";

interface HeaderProps {
  isConnected: boolean;
}

export function Header({ isConnected }: HeaderProps) {
  return (
    <header className="border-b border-gray-200 bg-white px-4 py-4 sm:px-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="text-2xl">🧬</div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">LifeLine</h1>
            <p className="text-sm text-gray-500">Your Personal Timeline</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? "bg-green-500" : "bg-red-500"
            }`}
          />
          <span className="text-sm text-gray-600 hidden sm:inline">
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>
    </header>
  );
}
