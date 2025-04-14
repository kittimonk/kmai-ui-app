
import React from 'react';
import { Bot, User } from 'lucide-react';

type MessageProps = {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
};

const ChatMessage = ({ message }: { message: MessageProps }) => {
  return (
    <div 
      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div 
        className={`max-w-3xl rounded-lg p-4 ${
          message.sender === 'user' 
            ? 'bg-green-700 text-white' 
            : 'bg-white border border-gray-200'
        }`}
      >
        <div className="flex items-start mb-2">
          <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
            message.sender === 'user' 
              ? 'bg-green-600' 
              : 'bg-green-100 text-green-700'
          } mr-2`}>
            {message.sender === 'user' ? <User size={16} /> : <Bot size={16} />}
          </div>
          <div>
            <div className={`font-medium ${message.sender === 'user' ? 'text-white' : 'text-gray-900'}`}>
              {message.sender === 'user' ? 'You' : 'AI Assistant'}
            </div>
            <div className={`text-xs ${message.sender === 'user' ? 'text-green-100' : 'text-gray-500'}`}>
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
        <div className={`whitespace-pre-wrap ${message.sender === 'user' ? 'text-white' : 'text-gray-700'}`}>
          {message.content}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
