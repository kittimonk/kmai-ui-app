
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
  const isLovablePreview = window.location.hostname.includes('lovableproject.com') || window.location.hostname.includes('lovable.app');

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

  // Only disable input if there's an API error and we're NOT in the Lovable preview
  const isInputDisabled = apiError && !isLovablePreview;

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
          disabled={isInputDisabled}
        />
        <button
          onClick={handleSend}
          disabled={inputValue.trim() === '' || isLoading || isInputDisabled}
          className={`p-3 ${
            inputValue.trim() === '' || isLoading || isInputDisabled
              ? 'text-gray-400' 
              : 'text-green-700 hover:text-green-800'
          }`}
        >
          <Send size={20} />
        </button>
      </div>
      
      {apiError && !isLovablePreview && (
        <div className="mt-2 text-xs text-red-500">
          Chat is disabled due to API connection issues. Please check if the FastAPI server is running.
        </div>
      )}

      {isLovablePreview && apiError && (
        <div className="mt-2 text-xs text-amber-500">
          Note: Running in preview mode with mock responses. For full functionality, run locally with the FastAPI server.
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
