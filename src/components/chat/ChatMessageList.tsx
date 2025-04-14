
import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';

type Message = {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
};

type ChatMessageListProps = {
  messages: Message[];
  isLoading: boolean;
  showNewChatModal: boolean;
  setShowNewChatModal: (show: boolean) => void;
  startNewChat: () => void;
};

const ChatMessageList = ({ 
  messages, 
  isLoading, 
  showNewChatModal,
  setShowNewChatModal,
  startNewChat
}: ChatMessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {showNewChatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h2 className="text-xl font-semibold mb-4">New Conversation</h2>
            <button 
              onClick={startNewChat}
              className="w-full py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 transition-colors"
            >
              Start New Conversation
            </button>
            <button 
              onClick={() => setShowNewChatModal(false)}
              className="w-full mt-2 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
      
      {isLoading && <TypingIndicator />}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatMessageList;
