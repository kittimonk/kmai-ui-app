
import React from 'react';
import { Plus } from 'lucide-react';

type ChatSidebarProps = {
  onNewChat: () => void;
};

const ChatSidebar = ({ onNewChat }: ChatSidebarProps) => {
  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <button 
          onClick={onNewChat} 
          className="w-full flex items-center justify-center gap-2 bg-green-700 text-white py-2 px-4 rounded-lg hover:bg-green-800 transition-colors"
        >
          <Plus size={16} />
          <span>New Conversation</span>
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        <div className="text-sm text-gray-500 mb-2">Recent conversations</div>
        <div className="space-y-2">
          {/* This would be populated with actual chat history in a real app */}
          <div className="p-2 rounded-lg bg-green-50 text-green-700 cursor-pointer">
            Current conversation
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatSidebar;
