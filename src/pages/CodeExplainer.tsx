
import React from 'react';
import { Button } from '@/components/ui/button';
import { Code } from 'lucide-react';
import { useCodeExplainer } from '@/hooks/useCodeExplainer';

// Components
import ApiStatusAlert from '@/components/code-explainer/ApiStatusAlert';
import CodeInput from '@/components/code-explainer/CodeInput';
import ActionSelector from '@/components/code-explainer/ActionSelector';
import ModelSelector from '@/components/code-explainer/ModelSelector';
import ResultDisplay from '@/components/code-explainer/ResultDisplay';

const CodeExplainer = () => {
  const {
    code,
    selectedAction,
    selectedModel,
    isGenerating,
    result,
    apiStatus,
    setCode,
    setSelectedAction,
    setSelectedModel,
    handleGenerate
  } = useCodeExplainer();

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center">
          <Code className="mr-2" /> Code Explainer
        </h1>
        <p className="text-gray-600 mt-1">
          Paste the code you want to analyze and select the appropriate action.
        </p>
      </div>

      <ApiStatusAlert apiStatus={apiStatus} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <CodeInput code={code} setCode={setCode} />
          
          <ActionSelector 
            selectedAction={selectedAction} 
            setSelectedAction={setSelectedAction} 
          />

          <ModelSelector 
            selectedModel={selectedModel} 
            setSelectedModel={setSelectedModel} 
          />

          <Button 
            onClick={handleGenerate} 
            className="w-full bg-green-700 hover:bg-green-800"
            disabled={!code || isGenerating}
          >
            Generate Explanation
          </Button>
        </div>

        <ResultDisplay result={result} isGenerating={isGenerating} />
      </div>
    </div>
  );
};

export default CodeExplainer;
