
import React from 'react';

type ResultDisplayProps = {
  result: string;
  isGenerating: boolean;
};

const ResultDisplay = ({ result, isGenerating }: ResultDisplayProps) => {
  return (
    <div>
      <label className="block text-sm font-medium mb-2">Result</label>
      <div className="bg-gray-50 p-4 rounded-lg border min-h-[300px] whitespace-pre-wrap font-mono text-sm">
        {isGenerating ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-700"></div>
          </div>
        ) : result ? (
          result
        ) : (
          <div className="text-gray-400 h-full flex items-center justify-center">
            Results will appear here after generation.
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultDisplay;
