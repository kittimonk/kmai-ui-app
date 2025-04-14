
import React from 'react';
import { Plus, X } from 'lucide-react';

type ChatHeaderProps = {
  apiError: string | null;
  onNewChat: () => void;
  onClearChat: () => void;
};

const ChatHeader = ({ apiError, onNewChat, onClearChat }: ChatHeaderProps) => {
  return (
    <div className="p-4 border-b border-gray-200 bg-white flex justify-between items-center">
      <h1 className="text-xl font-semibold">AI Chat</h1>
      <div className="flex items-center space-x-4">
        <div className="flex items-center">
          <div className={`mr-2 h-3 w-3 rounded-full ${apiError ? 'bg-red-500' : 'bg-green-500'}`}></div>
          <span className="text-sm">{apiError ? 'API Connection Error' : 'Azure OpenAI (MSI)'}</span>
        </div>
        <button 
          onClick={onNewChat}
          className="px-3 py-1 border border-gray-300 rounded-lg text-sm flex items-center gap-1 hover:bg-gray-50"
        >
          <Plus size={16} />
          <span>New Chat</span>
        </button>
        <button 
          onClick={onClearChat}
          className="px-3 py-1 border border-gray-300 rounded-lg text-sm flex items-center gap-1 hover:bg-gray-50"
        >
          <X size={16} />
          <span>Clear Chat</span>
        </button>
      </div>
    </div>
  );
};

export default ChatHeader;
