
import React from 'react';
import { Bot } from 'lucide-react';

export const TypingIndicator = () => {
  return (
    <div className="flex justify-start">
      <div className="max-w-3xl rounded-lg p-4 bg-white border border-gray-200">
        <div className="flex items-start mb-2">
          <div className="h-8 w-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center mr-2">
            <Bot size={16} />
          </div>
          <div>
            <div className="font-medium text-gray-900">AI Assistant</div>
            <div className="text-xs text-gray-500">Just now</div>
          </div>
        </div>
        <div className="flex items-center text-gray-500">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '600ms' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};
