
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Upload, FileText, Check, Settings } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const AIRemediationAssistant = () => {
  const [files, setFiles] = useState<{ name: string; status: string; }[]>([]);
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [customPrompt, setCustomPrompt] = useState('');
  const [activeTab, setActiveTab] = useState('upload');

  const handleFileUpload = (type: string) => {
    // In a real application, this would open a file picker
    // For demo, we'll simulate adding a file
    const newFile = { 
      name: `Sample-${type}-${Math.floor(Math.random() * 1000)}.pdf`, 
      status: 'uploaded' 
    };
    setFiles([...files, newFile]);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, type: string) => {
    e.preventDefault();
    // In a real application, we would process the dropped files
    const newFile = { 
      name: `Dropped-${type}-${Math.floor(Math.random() * 1000)}.pdf`, 
      status: 'uploaded' 
    };
    setFiles([...files, newFile]);
  };

  const handleAnalyze = () => {
    // In a real application, this would start the analysis process
    console.log("Starting analysis with model:", selectedModel);
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">AI Remediation Assistant</h1>
        <p className="text-gray-600 mt-1">
          Get AI-assisted guidance on your remediation plans against governance and compliance requirements.
        </p>
        <p className="text-gray-500 text-sm mt-2">
          This assistant uses a specialized system prompt designed to validate remediation plans against compliance standards.
          <br />
          The built-in system prompt will take precedence over any user provided instructions by design.
        </p>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">AI Analysis Input</h2>
        <p className="text-gray-600 mb-4">
          Upload your remediation plans and compliance requirements for analysis.
        </p>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2">Remediation Plan</h3>
            <div 
              className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, 'remediation')}
              onClick={() => handleFileUpload('remediation')}
            >
              <div className="flex flex-col items-center">
                <Upload className="h-12 w-12 text-gray-400 mb-3" />
                <p className="text-sm text-gray-500 mb-1">Click to upload or drag and drop</p>
                <p className="text-xs text-gray-400">PDF, DOCX, TXT, JSON, RTF (MAX. 10MB)</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Compliance Requirements</h3>
            <div 
              className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, 'compliance')}
              onClick={() => handleFileUpload('compliance')}
            >
              <div className="flex flex-col items-center">
                <Upload className="h-12 w-12 text-gray-400 mb-3" />
                <p className="text-sm text-gray-500 mb-1">Click to upload or drag and drop</p>
                <p className="text-xs text-gray-400">PDF, DOCX, TXT, JSON, RTF (MAX. 10MB)</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Findings Details</h3>
            <div 
              className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, 'findings')}
              onClick={() => handleFileUpload('findings')}
            >
              <div className="flex flex-col items-center">
                <Upload className="h-12 w-12 text-gray-400 mb-3" />
                <p className="text-sm text-gray-500 mb-1">Click to upload or drag and drop</p>
                <p className="text-xs text-gray-400">PDF, DOCX, TXT, JSON, RTF (MAX. 10MB)</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <h3 className="text-lg font-medium mb-2">Custom Prompt</h3>
          <p className="text-sm text-gray-500 mb-3">
            Use your own custom prompt for analysis instead of the default one.
          </p>
          <textarea 
            className="w-full p-3 border rounded-lg min-h-[100px]"
            placeholder="Enter your custom prompt here..."
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
          ></textarea>
        </div>

        <div className="mt-8">
          <h3 className="text-lg font-medium mb-2">AI Model</h3>
          <select 
            className="w-full md:w-1/3 p-2 border rounded"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          </select>
          <p className="text-sm text-gray-500 mt-1">
            Select the model that best suits your compliance analysis needs.
          </p>
        </div>

        <div className="mt-6 text-right">
          <Button 
            onClick={handleAnalyze} 
            className="bg-green-700 hover:bg-green-800"
            disabled={files.length === 0}
          >
            <Check className="w-4 h-4 mr-2" />
            Analyze Plan
          </Button>
        </div>
        
        <div className="mt-8">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Findings Details</h2>
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              System & User Prompts
            </Button>
          </div>
          
          {files.length > 0 ? (
            <div className="mt-4 border rounded-lg p-4">
              <ul className="divide-y">
                {files.map((file, index) => (
                  <li key={index} className="py-3 flex justify-between items-center">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 mr-3 text-gray-400" />
                      <span>{file.name}</span>
                    </div>
                    <span className="text-sm text-green-600">{file.status}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <Card className="mt-4">
              <CardContent className="pt-6 text-center">
                <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                <h3 className="text-lg font-medium">No analysis results yet</h3>
                <p className="text-sm text-gray-500">
                  Upload documents and submit to see AI recommendations here.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIRemediationAssistant;
