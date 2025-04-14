
import React, { useState } from 'react';
import { Send } from 'lucide-react';

type ChatInputProps = {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  apiError: string | null;
  handleQuickQuestion?: (question: string) => void;
  isInitialState: boolean;
};

const ChatInput = ({ onSendMessage, isLoading, apiError, handleQuickQuestion, isInitialState }: ChatInputProps) => {
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    if (inputValue.trim() === '') return;
    onSendMessage(inputValue);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-4 border-t border-gray-200 bg-white">
      <div className="flex items-center bg-gray-50 border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-green-500 focus-within:border-green-500">
        <textarea
          id="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 outline-none p-3 bg-transparent resize-none"
          placeholder="Ask a question..."
          rows={1}
          style={{ maxHeight: '120px' }}
          disabled={!!apiError}
        />
        <button
          onClick={handleSend}
          disabled={inputValue.trim() === '' || isLoading || !!apiError}
          className={`p-3 ${
            inputValue.trim() === '' || isLoading || !!apiError
              ? 'text-gray-400' 
              : 'text-green-700 hover:text-green-800'
          }`}
        >
          <Send size={20} />
        </button>
      </div>
      
      {apiError && (
        <div className="mt-2 text-xs text-red-500">
          Chat is disabled due to API connection issues. Please check if the FastAPI server is running.
        </div>
      )}

      {/* Quick question suggestions */}
      {isInitialState && (
        <div className="mt-4 flex justify-center space-x-4">
          <button 
            onClick={() => handleQuickQuestion && handleQuickQuestion("What can you help me with?")}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
          >
            What can you help me with?
          </button>
          <button 
            onClick={() => handleQuickQuestion && handleQuickQuestion("How do I upload documents?")}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
          >
            How do I upload documents?
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatInput;
