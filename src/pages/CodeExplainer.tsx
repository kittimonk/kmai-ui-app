
import React from 'react';
import { useCodeExplainer } from '@/hooks/useCodeExplainer';
import CodeInput from '@/components/code-explainer/CodeInput';
import ActionSelector from '@/components/code-explainer/ActionSelector';
import ModelSelector from '@/components/code-explainer/ModelSelector';
import ResultDisplay from '@/components/code-explainer/ResultDisplay';
import ApiStatusAlert from '@/components/code-explainer/ApiStatusAlert';
import { Button } from '@/components/ui/button';

const CodeExplainer = () => {
  const {
    code,
    setCode,
    selectedAction,
    setSelectedAction,
    selectedModel,
    setSelectedModel,
    isGenerating,
    result,
    apiStatus,
    handleGenerate,
    checkApiAvailability
  } = useCodeExplainer();

  return (
    <div className="container mx-auto max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Code Explainer</h1>
        <p className="text-gray-600">
          Get AI-powered explanations, documentation, simplification, or optimization suggestions for your code.
        </p>
      </div>

      {apiStatus !== 'available' && (
        <ApiStatusAlert status={apiStatus} onRetry={checkApiAvailability} />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <CodeInput code={code} setCode={setCode} />
        <div className="space-y-6">
          <ActionSelector selectedAction={selectedAction} setSelectedAction={setSelectedAction} />
          <ModelSelector selectedModel={selectedModel} setSelectedModel={setSelectedModel} />
          <Button 
            onClick={handleGenerate} 
            disabled={isGenerating || !code} 
            className="w-full"
          >
            {isGenerating ? 'Generating...' : 'Generate'}
          </Button>
        </div>
      </div>

      <ResultDisplay result={result} isGenerating={isGenerating} />
    </div>
  );
};

export default CodeExplainer;
