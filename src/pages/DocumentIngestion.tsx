
import React, { useState } from 'react';
import { FileText, Upload, Check, X } from 'lucide-react';

type FileStatus = 'idle' | 'uploading' | 'success' | 'error';

type FileItem = {
  id: string;
  name: string;
  size: number;
  type: string;
  status: FileStatus;
  progress: number;
};

const DocumentIngestion = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const newFiles = Array.from(e.dataTransfer.files).map(file => ({
      id: Date.now() + Math.random().toString(),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'idle' as FileStatus,
      progress: 0
    }));
    
    setFiles(prev => [...prev, ...newFiles]);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).map(file => ({
        id: Date.now() + Math.random().toString(),
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'idle' as FileStatus,
        progress: 0
      }));
      
      setFiles(prev => [...prev, ...newFiles]);
    }
  };

  const handleUpload = async () => {
    const filesToUpload = files.filter(file => file.status === 'idle');
    
    for (const file of filesToUpload) {
      // Update file status to uploading
      setFiles(prev => prev.map(f => 
        f.id === file.id ? { ...f, status: 'uploading' as FileStatus } : f
      ));
      
      // Simulate progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, progress } : f
        ));
      }
      
      try {
        // In a real app, this would be an actual API call
        await fetch('http://localhost:8000/api/ingest-document', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ filename: file.name }),
        });
        
        // Mark as successful
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'success' as FileStatus } : f
        ));
      } catch (error) {
        // Mark as error
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'error' as FileStatus } : f
        ));
      }
    }
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(file => file.id !== id));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Document Ingestion</h1>
        <p className="text-gray-600">Upload and process documents to enhance the knowledge base for RAG/LLM engines</p>
      </div>
      
      <div className="flex-1 flex flex-col">
        <div
          className={`border-2 border-dashed rounded-lg p-8 mb-6 flex flex-col items-center justify-center ${
            isDragging ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-green-400'
          }`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Upload size={32} className="text-gray-500" />
          </div>
          <p className="text-lg font-medium mb-2">Drag and drop files here</p>
          <p className="text-gray-500 mb-4">or</p>
          <label className="cursor-pointer bg-green-700 text-white px-6 py-2 rounded-lg hover:bg-green-800 transition-colors">
            Select Files
            <input
              type="file"
              multiple
              className="hidden"
              onChange={handleFileInputChange}
            />
          </label>
          <p className="text-sm text-gray-500 mt-4">
            Supported formats: .pdf, .docx, .txt, .csv, .json, .xml
          </p>
        </div>
        
        {files.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="font-semibold">Files to process</h2>
            </div>
            <ul>
              {files.map(file => (
                <li key={file.id} className="px-6 py-4 border-b border-gray-200 last:border-0 flex items-center">
                  <div className="h-10 w-10 bg-gray-100 rounded-lg flex items-center justify-center mr-4">
                    <FileText size={20} className="text-gray-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium truncate">{file.name}</p>
                      <span className="ml-2 text-xs text-gray-500">{formatFileSize(file.size)}</span>
                    </div>
                    {file.status === 'uploading' && (
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${file.progress}%` }}
                        ></div>
                      </div>
                    )}
                  </div>
                  {file.status === 'idle' && (
                    <button 
                      onClick={() => removeFile(file.id)}
                      className="ml-4 text-gray-400 hover:text-gray-600"
                    >
                      <X size={18} />
                    </button>
                  )}
                  {file.status === 'success' && (
                    <div className="ml-4 text-green-600">
                      <Check size={18} />
                    </div>
                  )}
                  {file.status === 'error' && (
                    <div className="ml-4 text-red-600">
                      <X size={18} />
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {files.some(file => file.status === 'idle') && (
          <div className="mt-auto pt-4 flex justify-center">
            <button
              onClick={handleUpload}
              className="bg-green-700 text-white px-6 py-2 rounded-lg hover:bg-green-800 transition-colors flex items-center"
            >
              <Upload size={18} className="mr-2" />
              Upload and Process Files
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentIngestion;
