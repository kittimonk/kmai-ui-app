
import React from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, Code, FileText, BrainCog, ArrowRight, CheckCircle, User, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/services/auth';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';

const Home = () => {
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogin = () => {
    window.location.href = '/login';
  };

  const handleLogout = async () => {
    await logout();
    window.location.href = '/logout';
  };

  return (
    <div className="flex flex-col h-full">
      {/* Top Navigation */}
      <div className="flex justify-between items-center p-4 bg-white border-b">
        <h1 className="text-xl font-bold text-green-600">Knowledge Management AI</h1>
        <div className="flex items-center gap-4">
          {isAuthenticated && user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  <span className="text-sm">{user.name || user.email}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem disabled>
                  <div className="flex flex-col">
                    <span className="font-medium">{user.name}</span>
                    <span className="text-sm text-gray-500">{user.email}</span>
                  </div>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button onClick={handleLogin} variant="outline">
              Sign In
            </Button>
          )}
        </div>
      </div>
      
      <div className="flex-1 p-8">
        {/* Hero Section */}
        <div className="bg-green-600 text-white rounded-xl p-10 mb-8">
          <h1 className="text-4xl font-bold mb-4">Knowledge Management AI</h1>
          <p className="text-xl mb-6">
            Access, convert, and integrate knowledge with advanced AI capabilities powered by Azure OpenAI and AI Search.
          </p>
          <div className="flex flex-wrap gap-4 mt-6">
            {isAuthenticated ? (
              <>
                <Button asChild variant="outline" className="bg-white text-green-700 hover:bg-gray-100 border-none">
                  <Link to="/chat">Start a Conversation</Link>
                </Button>
                <Button asChild variant="outline" className="bg-transparent border-white text-white hover:bg-green-500">
                  <Link to="/knowledge">Browse Knowledge Base</Link>
                </Button>
              </>
            ) : (
              <Button onClick={handleLogin} variant="outline" className="bg-white text-green-700 hover:bg-gray-100 border-none">
                Sign in to Get Started
              </Button>
            )}
          </div>
        </div>
        
        {/* Key Features Section */}
        <h2 className="text-2xl font-semibold mb-6">Key Features</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {/* AI Chat */}
          <div className="bg-white rounded-lg p-6 border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="mb-4">
              <MessageSquare className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">AI Chat</h3>
            <p className="text-gray-600 text-sm mb-4">
              Ask questions and get instant answers in a conversational interface powered by Azure OpenAI.
            </p>
            {isAuthenticated ? (
              <Link to="/chat" className="inline-flex items-center text-green-600 hover:underline text-sm">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            ) : (
              <Button onClick={handleLogin} variant="link" className="inline-flex items-center text-green-600 hover:underline text-sm p-0">
                Sign in to use <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Code Converter */}
          <div className="bg-white rounded-lg p-6 border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="mb-4">
              <Code className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Code Converter</h3>
            <p className="text-gray-600 text-sm mb-4">
              Translate code between different programming languages with precise syntax preservation.
            </p>
            {isAuthenticated ? (
              <Link to="/converter" className="inline-flex items-center text-green-600 hover:underline text-sm">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            ) : (
              <Button onClick={handleLogin} variant="link" className="inline-flex items-center text-green-600 hover:underline text-sm p-0">
                Sign in to use <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Code Explainer */}
          <div className="bg-white rounded-lg p-6 border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="mb-4">
              <Code className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Code Explainer</h3>
            <p className="text-gray-600 text-sm mb-4">
              Get detailed explanations, documentation, and optimization suggestions for your code.
            </p>
            {isAuthenticated ? (
              <Link to="/explainer" className="inline-flex items-center text-green-600 hover:underline text-sm">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            ) : (
              <Button onClick={handleLogin} variant="link" className="inline-flex items-center text-green-600 hover:underline text-sm p-0">
                Sign in to use <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Document Ingestion */}
          <div className="bg-white rounded-lg p-6 border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="mb-4">
              <FileText className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Document Ingestion</h3>
            <p className="text-gray-600 text-sm mb-4">
              Upload and process documents to enhance the knowledge base for RAG/LangChain tuning.
            </p>
            {isAuthenticated ? (
              <Link to="/ingestion" className="inline-flex items-center text-green-600 hover:underline text-sm">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            ) : (
              <Button onClick={handleLogin} variant="link" className="inline-flex items-center text-green-600 hover:underline text-sm p-0">
                Sign in to use <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Azure AI Services Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Integrated with Azure AI Services</h2>
          <p className="text-gray-600 mb-6">
            KMAI leverages Azure OpenAI and AI Search services to provide enterprise-grade intelligence and security.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-2 flex items-center">
                <CheckCircle className="text-green-600 mr-2 h-5 w-5" />
                Azure OpenAI Service
              </h3>
              <p className="text-gray-600 text-sm">
                Advanced language models with enterprise-grade security and compliance.
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-2 flex items-center">
                <CheckCircle className="text-green-600 mr-2 h-5 w-5" />
                Azure AI Search
              </h3>
              <p className="text-gray-600 text-sm">
                Cognitive search service with high-performance indexing and querying capabilities.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
