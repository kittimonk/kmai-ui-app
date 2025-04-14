
import React, { useState, useEffect } from 'react';
import { Copy, ArrowRight, Code as CodeIcon, Terminal, BookOpen } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from 'sonner';

const languages = [
  { id: 'typescript', name: 'TypeScript' },
  { id: 'javascript', name: 'JavaScript' },
  { id: 'python', name: 'Python' },
  { id: 'java', name: 'Java' },
  { id: 'csharp', name: 'C#' },
  { id: 'go', name: 'Go' },
  { id: 'rust', name: 'Rust' },
  { id: 'swift', name: 'Swift' },
  { id: 'php', name: 'PHP' },
  { id: 'ruby', name: 'Ruby' },
  { id: 'kotlin', name: 'Kotlin' },
];

const aiModels = [
  { id: 'GPT-4 Turbo', name: 'GPT-4 Turbo' },
  { id: 'AI Model', name: 'AI Model' },
];

const CodeConverter = () => {
  const [sourceCode, setSourceCode] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('javascript');
  const [targetLanguage, setTargetLanguage] = useState('python');
  const [convertedCode, setConvertedCode] = useState('');
  const [isConverting, setIsConverting] = useState(false);
  const [showCopiedMessage, setShowCopiedMessage] = useState(false);
  const [activeTab, setActiveTab] = useState('converter');
  
  // Code explanation state
  const [explainedCode, setExplainedCode] = useState('');
  const [simplifiedCode, setSimplifiedCode] = useState('');
  const [typescriptCode, setTypescriptCode] = useState('');
  const [isExplaining, setIsExplaining] = useState(false);
  const [selectedModel, setSelectedModel] = useState('GPT-4 Turbo');
  const [activeExplainTab, setActiveExplainTab] = useState('explanation');

  const handleConvert = async () => {
    if (!sourceCode.trim()) return;
    
    setIsConverting(true);
    
    try {
      // Make API call to convert code
      const response = await fetch('http://localhost:8000/api/convert-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: sourceCode,
          sourceLanguage,
          targetLanguage,
        }),
      });
      
      const data = await response.json();
      setConvertedCode(data.convertedCode || 'Error converting code');
      toast.success('Code successfully converted!');
    } catch (error) {
      console.error('Error converting code:', error);
      setConvertedCode('Error: Failed to convert code. Please try again later.');
      toast.error('Failed to convert code');
    } finally {
      setIsConverting(false);
    }
  };

  const handleExplain = async () => {
    if (!sourceCode.trim()) return;
    
    setIsExplaining(true);
    
    try {
      // Make API call to explain code
      const response = await fetch('http://localhost:8000/api/explain-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: sourceCode,
          language: sourceLanguage,
          model: selectedModel,
        }),
      });
      
      const data = await response.json();
      setExplainedCode(data.explanation || 'Error explaining code');
      setSimplifiedCode(data.simplified || '');
      setTypescriptCode(data.typescript || '');
      toast.success('Code explanation generated!');
    } catch (error) {
      console.error('Error explaining code:', error);
      setExplainedCode('Error: Failed to explain code. Please try again later.');
      toast.error('Failed to explain code');
    } finally {
      setIsExplaining(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setShowCopiedMessage(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setShowCopiedMessage(false), 2000);
  };

  const swapLanguages = () => {
    const temp = sourceLanguage;
    setSourceLanguage(targetLanguage);
    setTargetLanguage(temp);
    
    // Also swap the code if conversion has been done
    if (convertedCode) {
      setSourceCode(convertedCode);
      setConvertedCode('');
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Code Converter</h1>
        <p className="text-gray-600">Convert code between different programming languages</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="mb-4 grid grid-cols-2 w-80">
          <TabsTrigger value="converter" className="flex items-center gap-2">
            <CodeIcon size={16} />
            <span>Code Converter</span>
          </TabsTrigger>
          <TabsTrigger value="explainer" className="flex items-center gap-2">
            <BookOpen size={16} />
            <span>Code Explainer</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="converter" className="mt-0">
          <div className="flex items-center mb-4 space-x-4">
            <div className="flex-1">
              <label htmlFor="sourceLanguage" className="block text-sm font-medium text-gray-700 mb-1">Source Language</label>
              <select
                id="sourceLanguage"
                value={sourceLanguage}
                onChange={(e) => setSourceLanguage(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                {languages.map((lang) => (
                  <option key={lang.id} value={lang.id}>{lang.name}</option>
                ))}
              </select>
            </div>
            
            <button 
              onClick={swapLanguages}
              className="mt-6 p-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <ArrowRight className="transform rotate-90" size={20} />
            </button>
            
            <div className="flex-1">
              <label htmlFor="targetLanguage" className="block text-sm font-medium text-gray-700 mb-1">Target Language</label>
              <select
                id="targetLanguage"
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                {languages.map((lang) => (
                  <option key={lang.id} value={lang.id}>{lang.name}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 flex-1">
            <div className="flex flex-col">
              <label htmlFor="sourceCode" className="block text-sm font-medium text-gray-700 mb-1">Source Code</label>
              <textarea
                id="sourceCode"
                value={sourceCode}
                onChange={(e) => setSourceCode(e.target.value)}
                placeholder="Paste your code here..."
                className="flex-1 p-3 border border-gray-300 rounded-md resize-none font-mono text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
            
            <div className="flex flex-col">
              <div className="flex justify-between items-center mb-1">
                <label htmlFor="convertedCode" className="block text-sm font-medium text-gray-700">Converted Code</label>
                {convertedCode && (
                  <div className="relative">
                    <button
                      onClick={() => copyToClipboard(convertedCode)}
                      className="text-gray-500 hover:text-gray-700 flex items-center text-xs"
                    >
                      <Copy size={14} className="mr-1" />
                      Copy
                    </button>
                    {showCopiedMessage && (
                      <div className="absolute -top-8 right-0 bg-gray-800 text-white px-2 py-1 rounded text-xs">
                        Copied!
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="flex-1 relative">
                <textarea
                  id="convertedCode"
                  value={convertedCode}
                  readOnly
                  placeholder="Converted code will appear here..."
                  className="w-full h-full p-3 border border-gray-300 rounded-md resize-none font-mono text-sm bg-gray-50"
                />
                {isConverting && (
                  <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
                    <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-green-500 border-r-transparent"></div>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="mt-4 flex justify-center">
            <Button
              onClick={handleConvert}
              disabled={!sourceCode.trim() || isConverting}
              className={`px-6 py-2 rounded-lg flex items-center ${
                !sourceCode.trim() || isConverting
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-700 text-white hover:bg-green-800'
              }`}
            >
              {isConverting ? (
                <>
                  <span className="inline-block h-4 w-4 mr-2 animate-spin rounded-full border-2 border-solid border-white border-r-transparent"></span>
                  Converting...
                </>
              ) : (
                'Convert Code'
              )}
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="explainer" className="mt-0">
          <div className="flex flex-col">
            <div className="flex items-center mb-4 space-x-4">
              <div className="flex-1">
                <label htmlFor="sourceLanguageExplain" className="block text-sm font-medium text-gray-700 mb-1">Language</label>
                <select
                  id="sourceLanguageExplain"
                  value={sourceLanguage}
                  onChange={(e) => setSourceLanguage(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
                >
                  {languages.map((lang) => (
                    <option key={lang.id} value={lang.id}>{lang.name}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex-1">
                <label htmlFor="aiModel" className="block text-sm font-medium text-gray-700 mb-1">AI Model</label>
                <select
                  id="aiModel"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
                >
                  {aiModels.map((model) => (
                    <option key={model.id} value={model.id}>{model.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 flex-1">
              <div className="flex flex-col">
                <label htmlFor="sourceCodeExplain" className="block text-sm font-medium text-gray-700 mb-1">Paste your Code</label>
                <textarea
                  id="sourceCodeExplain"
                  value={sourceCode}
                  onChange={(e) => setSourceCode(e.target.value)}
                  placeholder="Paste your code here to analyze and select the appropriate action."
                  className="flex-1 p-3 border border-gray-300 rounded-md resize-none font-mono text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  rows={12}
                />
              </div>
              
              <div className="flex flex-col">
                <div className="flex justify-between items-center mb-1">
                  <label className="block text-sm font-medium text-gray-700">Result</label>
                  {explainedCode && (
                    <div className="relative">
                      <button
                        onClick={() => copyToClipboard(
                          activeExplainTab === 'explanation' ? explainedCode : 
                          activeExplainTab === 'simplified' ? simplifiedCode : 
                          typescriptCode
                        )}
                        className="text-gray-500 hover:text-gray-700 flex items-center text-xs"
                      >
                        <Copy size={14} className="mr-1" />
                        Copy
                      </button>
                    </div>
                  )}
                </div>
                
                {explainedCode ? (
                  <div className="flex-1 flex flex-col">
                    <Tabs value={activeExplainTab} onValueChange={setActiveExplainTab} className="w-full">
                      <TabsList className="mb-2">
                        <TabsTrigger value="explanation">Explanation</TabsTrigger>
                        <TabsTrigger value="simplified">Simplified Code</TabsTrigger>
                        <TabsTrigger value="typescript">TypeScript</TabsTrigger>
                      </TabsList>
                      
                      <TabsContent value="explanation" className="flex-1">
                        <div className="h-full overflow-auto p-3 border border-gray-300 rounded-md bg-gray-50 font-mono text-sm whitespace-pre-wrap">
                          {explainedCode}
                        </div>
                      </TabsContent>
                      
                      <TabsContent value="simplified" className="flex-1">
                        <div className="h-full overflow-auto p-3 border border-gray-300 rounded-md bg-gray-50 font-mono text-sm">
                          {simplifiedCode}
                        </div>
                      </TabsContent>
                      
                      <TabsContent value="typescript" className="flex-1">
                        <div className="h-full overflow-auto p-3 border border-gray-300 rounded-md bg-gray-50 font-mono text-sm">
                          {typescriptCode}
                        </div>
                      </TabsContent>
                    </Tabs>
                  </div>
                ) : (
                  <div className="flex-1 relative">
                    <div className="w-full h-full p-3 border border-gray-300 rounded-md resize-none font-mono text-sm bg-gray-50 flex items-center justify-center text-gray-400">
                      {isExplaining ? (
                        <div className="flex flex-col items-center">
                          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-green-500 border-r-transparent mb-2"></div>
                          <span>Analyzing your code...</span>
                        </div>
                      ) : (
                        "Here's the explanation code of your code."
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            <div className="mt-4 flex justify-center">
              <Button
                onClick={handleExplain}
                disabled={!sourceCode.trim() || isExplaining}
                variant="default"
                className={`px-8 py-2 rounded-md ${
                  !sourceCode.trim() || isExplaining
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-green-700 text-white hover:bg-green-800'
                }`}
              >
                {isExplaining ? (
                  <>
                    <span className="inline-block h-4 w-4 mr-2 animate-spin rounded-full border-2 border-solid border-white border-r-transparent"></span>
                    Generating Explanation...
                  </>
                ) : (
                  'Generate Explanation'
                )}
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CodeConverter;
