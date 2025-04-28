
import React from 'react';

type ActionSelectorProps = {
  selectedAction: 'explain' | 'document' | 'simplify' | 'optimize';
  setSelectedAction: (action: 'explain' | 'document' | 'simplify' | 'optimize') => void;
};

const ActionSelector = ({ selectedAction, setSelectedAction }: ActionSelectorProps) => {
  return (
    <div>
      <label className="block text-sm font-medium mb-2">Action</label>
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={() => setSelectedAction('explain')}
          className={`py-2 px-4 rounded-md ${
            selectedAction === 'explain' ? 'bg-green-600 text-white' : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Explain
        </button>
        <button
          onClick={() => setSelectedAction('document')}
          className={`py-2 px-4 rounded-md ${
            selectedAction === 'document' ? 'bg-green-600 text-white' : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Document
        </button>
        <button
          onClick={() => setSelectedAction('simplify')}
          className={`py-2 px-4 rounded-md ${
            selectedAction === 'simplify' ? 'bg-green-600 text-white' : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Simplify
        </button>
        <button
          onClick={() => setSelectedAction('optimize')}
          className={`py-2 px-4 rounded-md ${
            selectedAction === 'optimize' ? 'bg-green-600 text-white' : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Optimize
        </button>
      </div>
    </div>
  );
};

export default ActionSelector;
