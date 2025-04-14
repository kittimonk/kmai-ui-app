
import React from 'react';
import { useChatApi } from '../hooks/useChatApi';
import { useChatMessages } from '../hooks/useChatMessages';
import { API_BASE_URL } from '../config';

// Import components
import ChatSidebar from '../components/chat/ChatSidebar';
import ChatHeader from '../components/chat/ChatHeader';
import ApiErrorBanner from '../components/chat/ApiErrorBanner';
import ChatMessageList from '../components/chat/ChatMessageList';
import ChatInput from '../components/chat/ChatInput';

const Chat = () => {
  const { 
    isLoading, 
    setIsLoading, 
    apiError, 
    setApiError, 
    isLovablePreview, 
    retryApiConnection 
  } = useChatApi();

  const {
    messages,
    showNewChat,
    setShowNewChat,
    handleSendMessage,
    startNewChat,
    handleClearChat,
    handleQuickQuestion
  } = useChatMessages(apiError, isLoading, setIsLoading, isLovablePreview);

  return (
    <div className="flex h-full">
      {/* Left sidebar for chat history */}
      <ChatSidebar onNewChat={() => setShowNewChat(true)} />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col bg-gray-50">
        <ChatHeader 
          apiError={apiError} 
          onNewChat={() => setShowNewChat(true)} 
          onClearChat={handleClearChat}
        />

        {!isLovablePreview && apiError && (
          <ApiErrorBanner 
            error={apiError || ''} 
            apiBaseUrl={API_BASE_URL} 
            onRetry={retryApiConnection} 
          />
        )}

        <ChatMessageList 
          messages={messages} 
          isLoading={isLoading} 
          showNewChatModal={showNewChat}
          setShowNewChatModal={setShowNewChat}
          startNewChat={startNewChat}
        />

        <ChatInput 
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          apiError={isLovablePreview ? null : apiError}
          handleQuickQuestion={handleQuickQuestion}
          isInitialState={messages.length === 1}
        />
      </div>
    </div>
  );
};

export default Chat;
