
import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Code, Database, MessageSquare, BrainCog, ArrowRight, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Home = () => {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1">
        {/* Hero Section */}
        <div className="bg-green-700 text-white rounded-xl p-10 mb-8">
          <h1 className="text-4xl font-bold mb-4">Knowledge Management AI</h1>
          <p className="text-xl mb-6">
            Access, convert, and integrate knowledge with advanced AI capabilities powered by Azure OpenAI and AI Search.
          </p>
          <div className="flex flex-wrap gap-4 mt-6">
            <Button asChild className="bg-white text-green-700 hover:bg-gray-100">
              <Link to="/chat">Start a Conversation</Link>
            </Button>
            <Button asChild variant="outline" className="bg-transparent border-white text-white hover:bg-green-600">
              <Link to="/knowledge-base">Browse Knowledge Base</Link>
            </Button>
          </div>
        </div>
        
        {/* Key Features Section */}
        <h2 className="text-2xl font-bold mb-6">Key Features</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="h-12 w-12 bg-green-700 rounded-lg flex items-center justify-center text-white mb-4">
              <MessageSquare size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Chat</h3>
            <p className="text-gray-600 mb-4">
              Ask questions and get instant answers in a conversational interface powered by Azure OpenAI.
            </p>
            <Link to="/chat" className="inline-flex items-center text-green-700 hover:underline">
              Get Started <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="h-12 w-12 bg-green-700 rounded-lg flex items-center justify-center text-white mb-4">
              <Code size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Code Converter</h3>
            <p className="text-gray-600 mb-4">
              Translate code between different programming languages with precise syntax preservation.
            </p>
            <Link to="/code-converter" className="inline-flex items-center text-green-700 hover:underline">
              Get Started <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="h-12 w-12 bg-green-700 rounded-lg flex items-center justify-center text-white mb-4">
              <Code size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Code Explainer</h3>
            <p className="text-gray-600 mb-4">
              Get detailed explanations, documentation, and optimization suggestions for your code.
            </p>
            <Link to="/code-explainer" className="inline-flex items-center text-green-700 hover:underline">
              Get Started <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="h-12 w-12 bg-green-700 rounded-lg flex items-center justify-center text-white mb-4">
              <FileText size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Document Ingestion</h3>
            <p className="text-gray-600 mb-4">
              Upload and process documents to enhance the knowledge base for RAG/LangChain tuning.
            </p>
            <Link to="/document-ingestion" className="inline-flex items-center text-green-700 hover:underline">
              Get Started <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        </div>
        
        {/* Azure AI Services Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Integrated with Azure AI Services</h2>
          <p className="text-gray-600 mb-6">
            KMAI leverages Azure OpenAI and AI Search services to provide enterprise-grade intelligence and security.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-2 flex items-center">
                <CheckCircle className="text-green-600 mr-2 h-5 w-5" />
                Azure OpenAI Service
              </h3>
              <p className="text-gray-600">
                Advanced language models with enterprise-grade security and compliance.
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-2 flex items-center">
                <CheckCircle className="text-green-600 mr-2 h-5 w-5" />
                Azure AI Search
              </h3>
              <p className="text-gray-600">
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
