
import { useState, useEffect } from 'react';
import { toast } from "sonner";
import { Message } from '../types/chat';
import { API_BASE_URL } from '../config';

export const useChatMessages = (apiError: string | null, isLoading: boolean, setIsLoading: (loading: boolean) => void, isLovablePreview: boolean) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [showNewChat, setShowNewChat] = useState(false);

  // Initial bot message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: '1',
          content: 'How can I help you today?\n\nAsk me anything about your knowledge base or how I can assist with document processing and code conversion.',
          sender: 'bot',
          timestamp: new Date(),
        },
      ]);
    }
  }, [messages.length]);

  const handleSendMessage = async (inputMessage: string) => {
    // For Lovable preview, use mock responses
    if (isLovablePreview) {
      handleMockResponse(inputMessage);
      return;
    }

    // Check if API is available before sending
    if (apiError) {
      toast.error("Cannot send message: API connection issue");
      return;
    }

    const newUserMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error(`API responded with status: ${response.status}`);
      }

      const data = await response.json();

      const newBotMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || "I'm processing your request. I'll have an answer shortly.",
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, newBotMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `I'm having trouble connecting to the server. Please make sure the FastAPI server is running at ${API_BASE_URL}.`,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle mock responses for Lovable preview environment
  const handleMockResponse = (inputMessage: string) => {
    const newUserMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    // Simulate API delay
    setTimeout(() => {
      let responseContent = "I'm not sure how to respond to that. Could you provide more details?";
      
      // Generate contextual responses based on input
      if (inputMessage.toLowerCase().includes('hello') || inputMessage.toLowerCase().includes('hi')) {
        responseContent = "Hello there! How can I assist you with your knowledge base or document processing needs today?";
      } else if (inputMessage.toLowerCase().includes('help')) {
        responseContent = "I can help you with several tasks:\n\n- Answering questions about your knowledge base\n- Converting code between languages\n- Explaining complex code\n- Processing and analyzing documents\n- AI remediation assistance\n\nWhat would you like help with?";
      } else if (inputMessage.toLowerCase().includes('document') || inputMessage.toLowerCase().includes('upload')) {
        responseContent = "To upload documents, navigate to the Document Ingestion page from the sidebar menu. You can upload various file formats including PDFs, Word documents, and text files. Once uploaded, the system will process them and add them to your knowledge base.";
      } else if (inputMessage.toLowerCase().includes('code')) {
        responseContent = "I can help with code conversion and explanation. Use the Code Converter tool to transform code between different languages, or the Code Explainer to get detailed explanations of complex code snippets.";
      } else if (inputMessage.toLowerCase().includes('api')) {
        responseContent = "This chat interface connects to a FastAPI backend that provides various AI capabilities. For local development, make sure the API server is running on port 3000. Check the console for any connection issues.";
      }

      const newBotMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: responseContent,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, newBotMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const startNewChat = () => {
    setMessages([
      {
        id: '1',
        content: 'How can I help you today?\n\nAsk me anything about your knowledge base or how I can assist with document processing and code conversion.',
        sender: 'bot',
        timestamp: new Date(),
      },
    ]);
    setShowNewChat(false);
  };

  const handleClearChat = () => {
    startNewChat();
  };

  const handleQuickQuestion = (question: string) => {
    handleSendMessage(question);
  };

  return {
    messages,
    showNewChat,
    setShowNewChat,
    handleSendMessage,
    startNewChat,
    handleClearChat,
    handleQuickQuestion
  };
};
