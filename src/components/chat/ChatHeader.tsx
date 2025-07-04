import React from 'react';
import { Plus, X, LogOut, UserPlus, LogIn } from 'lucide-react';
import { useAuthStore } from '@/services/auth';
import { useNavigate } from 'react-router-dom';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';

type ChatHeaderProps = {
  apiError: string | null;
  onNewChat: () => void;
  onClearChat: () => void;
};

const ChatHeader = ({ apiError, onNewChat, onClearChat }: ChatHeaderProps) => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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

        {isAuthenticated ? (
          <div className="flex items-center space-x-3">
            <Avatar>
              <AvatarFallback>
                {user?.name?.[0]?.toUpperCase() ?? 'U'}
              </AvatarFallback>
            </Avatar>
            <span className="text-sm">{user?.name}</span>
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-1"
              onClick={handleLogout}
            >
              <LogOut size={16} />
              Logout
            </Button>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/login')}
              className="flex items-center gap-1"
            >
              <LogIn size={16} />
              Sign in
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={() => navigate('/register')}
              className="flex items-center gap-1"
            >
              <UserPlus size={16} />
              Sign up
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatHeader;
