
import React from 'react';

type ModelSelectorProps = {
  selectedModel: string;
  setSelectedModel: (model: string) => void;
};

const ModelSelector = ({ selectedModel, setSelectedModel }: ModelSelectorProps) => {
  return (
    <div>
      <label className="block text-sm font-medium mb-2">AI Model</label>
      <select 
        className="w-full p-2 border rounded"
        value={selectedModel}
        onChange={(e) => setSelectedModel(e.target.value)}
      >
        <option value="gpt-4-turbo">GPT-4 Turbo</option>
        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
      </select>
      <p className="text-xs text-gray-500 mt-1">
        Select the model that best suits your needs.
      </p>
    </div>
  );
};

export default ModelSelector;
