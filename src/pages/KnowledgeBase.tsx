import React, { useState } from 'react';
import { Search, FileText, Calendar, Database, Filter, ChevronDown, Code } from 'lucide-react';

type Document = {
  id: string;
  title: string;
  description: string;
  category: string;
  date: string;
  type: string;
};

const dummyDocuments: Document[] = [
  {
    id: '1',
    title: 'Python to JavaScript Code Conversion Guide',
    description: 'Best practices for converting Python code to JavaScript',
    category: 'Code',
    date: '2024-02-24',
    type: 'Technical Documentation'
  },
  {
    id: '2',
    title: 'Setting up B2C Pipelines with LangChain',
    description: 'Step-by-step instructions for implementing LangChain',
    category: 'Tutorial',
    date: '2024-03-10',
    type: 'Guide'
  },
  {
    id: '3',
    title: 'Document Processing Pipeline Architecture',
    description: 'Technical architecture for the document ingestion and processing pipeline',
    category: 'Architecture',
    date: '2024-01-15',
    type: 'Technical Documentation'
  }
];

const categories = ['All', 'Code', 'Tutorial', 'Architecture'];
const types = ['All', 'Technical Documentation', 'Guide'];

const KnowledgeBase = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedType, setSelectedType] = useState('All');
  const [documents, setDocuments] = useState(dummyDocuments);

  const handleSearch = async () => {
    try {
      // In a real app, this would call your API with the search parameters
      const response = await fetch('http://localhost:8000/api/knowledge-base/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: searchQuery }),
      });
      
      const data = await response.json();
      console.log("Search results:", data);
      
      // For the demo, we'll just filter the dummy documents
      let filtered = [...dummyDocuments];
      
      if (searchQuery) {
        filtered = filtered.filter(doc => 
          doc.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
          doc.description.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }
      
      if (selectedCategory !== 'All') {
        filtered = filtered.filter(doc => doc.category === selectedCategory);
      }
      
      if (selectedType !== 'All') {
        filtered = filtered.filter(doc => doc.type === selectedType);
      }
      
      setDocuments(filtered);
    } catch (error) {
      console.error("Error searching knowledge base:", error);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Knowledge Base</h1>
        <p className="text-gray-600">Search and browse your organization's knowledge repository</p>
      </div>
      
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center mb-4">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by title, description or category..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <button
            onClick={handleSearch}
            className="ml-4 px-6 py-2 bg-green-700 text-white rounded-md hover:bg-green-800 transition-colors"
          >
            Search Knowledge
          </button>
        </div>
        
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center">
            <span className="text-sm text-gray-600 mr-2">Category:</span>
            <div className="relative">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="pr-8 pl-3 py-2 border border-gray-300 rounded-md appearance-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                <ChevronDown size={16} className="text-gray-400" />
              </div>
            </div>
          </div>
          
          <div className="flex items-center">
            <span className="text-sm text-gray-600 mr-2">Type:</span>
            <div className="relative">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="pr-8 pl-3 py-2 border border-gray-300 rounded-md appearance-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                {types.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                <ChevronDown size={16} className="text-gray-400" />
              </div>
            </div>
          </div>
          
          <button className="ml-auto flex items-center text-gray-600 hover:text-gray-800">
            <Filter size={16} className="mr-1" />
            <span>Advanced Filters</span>
          </button>
        </div>
      </div>
      
      <div className="flex-1 bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="border-b border-gray-200 px-6 py-4 bg-gray-50">
          <h2 className="font-semibold">Browse by Category</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6">
          <div className="border border-gray-200 rounded-lg p-4 hover:border-green-500 hover:shadow-md transition-all cursor-pointer">
            <div className="flex items-center mb-3">
              <div className="h-10 w-10 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mr-3">
                <FileText size={20} />
              </div>
              <h3 className="font-medium">Documentation</h3>
            </div>
            <p className="text-sm text-gray-600">Technical architecture documentation for the document ingestion and processing pipeline.</p>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4 hover:border-green-500 hover:shadow-md transition-all cursor-pointer">
            <div className="flex items-center mb-3">
              <div className="h-10 w-10 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center mr-3">
                <Code size={20} />
              </div>
              <h3 className="font-medium">Code</h3>
            </div>
            <p className="text-sm text-gray-600">Best practices for converting Python code to JavaScript and other programming languages.</p>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4 hover:border-green-500 hover:shadow-md transition-all cursor-pointer">
            <div className="flex items-center mb-3">
              <div className="h-10 w-10 bg-green-100 text-green-600 rounded-lg flex items-center justify-center mr-3">
                <Database size={20} />
              </div>
              <h3 className="font-medium">Tutorials</h3>
            </div>
            <p className="text-sm text-gray-600">Step-by-step instructions for implementing LangChain with advanced AI features.</p>
          </div>
        </div>
        
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
          <h2 className="font-semibold">Recent Documents</h2>
        </div>
        
        <ul>
          {documents.map(doc => (
            <li key={doc.id} className="border-b border-gray-200 last:border-0">
              <div className="px-6 py-4 hover:bg-gray-50 cursor-pointer">
                <div className="flex items-start">
                  <div className="h-10 w-10 bg-gray-100 rounded-lg flex items-center justify-center mr-4 mt-1">
                    <FileText size={20} className="text-gray-500" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-green-700">{doc.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{doc.description}</p>
                    <div className="flex items-center mt-2 text-xs text-gray-500">
                      <span className="bg-gray-100 px-2 py-1 rounded-full">{doc.category}</span>
                      <span className="ml-3 flex items-center">
                        <Calendar size={12} className="mr-1" />
                        {new Date(doc.date).toLocaleDateString()}
                      </span>
                      <span className="ml-3">{doc.type}</span>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default KnowledgeBase;
