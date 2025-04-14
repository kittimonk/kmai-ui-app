
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FileText, Code, Database, MessageSquare, Home, Settings, LogOut, User, BrainCog } from 'lucide-react';
import { useAuth } from './AuthProvider';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';

const Layout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const year = new Date().getFullYear();
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo & Brand */}
        <div className="h-16 border-b border-gray-200 flex items-center px-6">
          <Link to="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-green-700 flex items-center justify-center text-white font-bold">
              K
            </div>
            <span className="text-gray-700 font-medium">KMAI</span>
          </Link>
        </div>
        
        {/* Nav Links */}
        <div className="flex-1 overflow-y-auto py-4 px-3">
          <nav className="space-y-1">
            <Link 
              to="/" 
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${location.pathname === '/' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              <Home className="mr-3 h-5 w-5" />
              Home
            </Link>
            <Link 
              to="/chat" 
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${location.pathname === '/chat' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              <MessageSquare className="mr-3 h-5 w-5" />
              Chat
            </Link>
            <Link 
              to="/code-converter" 
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${location.pathname === '/code-converter' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              <Code className="mr-3 h-5 w-5" />
              Code Converter
            </Link>
            <Link 
              to="/code-explainer" 
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${location.pathname === '/code-explainer' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              <Code className="mr-3 h-5 w-5" />
              Code Explainer
            </Link>
            <Link 
              to="/ai-remediation-assistant" 
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${location.pathname === '/ai-remediation-assistant' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              <BrainCog className="mr-3 h-5 w-5" />
              AI Remediation Assistant
            </Link>
            <Link 
              to="/document-ingestion" 
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${location.pathname === '/document-ingestion' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              <FileText className="mr-3 h-5 w-5" />
              Document Ingestion
            </Link>
            <Link 
              to="/knowledge-base" 
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${location.pathname === '/knowledge-base' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              <Database className="mr-3 h-5 w-5" />
              Knowledge Base
            </Link>
          </nav>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center px-6 justify-between">
          <div className="flex items-center">
            <div className="hidden md:block">
              <div className="flex space-x-2">
                {location.pathname !== '/' && (
                  <Button variant="ghost" size="sm" asChild>
                    <Link to="/">Home</Link>
                  </Button>
                )}
                <span className="flex items-center text-gray-500">/</span>
                <span className="text-gray-700 font-medium">
                  {location.pathname === '/' ? 'Home' : 
                   location.pathname === '/chat' ? 'AI Chat' :
                   location.pathname === '/code-converter' ? 'Code Converter' :
                   location.pathname === '/code-explainer' ? 'Code Explainer' :
                   location.pathname === '/ai-remediation-assistant' ? 'AI Remediation Assistant' :
                   location.pathname === '/document-ingestion' ? 'Document Ingestion' :
                   location.pathname === '/knowledge-base' ? 'Knowledge Base' : 'Page'}
                </span>
              </div>
            </div>
          </div>
          
          <div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center space-x-2 focus:outline-none">
                  <Avatar className="h-9 w-9">
                    <AvatarImage src="" />
                    <AvatarFallback className="bg-green-100 text-green-800">
                      {user?.name?.charAt(0) || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div className="text-sm text-left hidden md:block">
                    <div className="font-medium">Demo User</div>
                    <div className="text-xs text-gray-500">demo@example.com</div>
                  </div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-4 py-2">
                  <p className="text-sm font-medium">Demo User</p>
                  <p className="text-xs text-gray-500">demo@example.com</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="w-4 h-4 mr-2" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="w-4 h-4 mr-2" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
        
        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {children}
        </main>
        
        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 h-6 flex items-center px-6 text-xs text-gray-500">
          <span>{year} KMAI</span>
          <span className="ml-auto">v1.0.0</span>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
