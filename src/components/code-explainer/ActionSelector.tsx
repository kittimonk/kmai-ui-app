
import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Check, FileText, Code } from 'lucide-react';

type ActionSelectorProps = {
  selectedAction: 'explain' | 'document' | 'simplify' | 'optimize';
  setSelectedAction: (action: 'explain' | 'document' | 'simplify' | 'optimize') => void;
};

const ActionSelector = ({ selectedAction, setSelectedAction }: ActionSelectorProps) => {
  return (
    <div>
      <label className="block text-sm font-medium mb-2">Action</label>
      <Tabs 
        defaultValue={selectedAction} 
        className="w-full" 
        onValueChange={(value) => setSelectedAction(value as 'explain' | 'document' | 'simplify' | 'optimize')}
      >
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="explain" className="flex items-center">
            <Check className="w-4 h-4 mr-2" />
            Explain Code
          </TabsTrigger>
          <TabsTrigger value="document" className="flex items-center">
            <FileText className="w-4 h-4 mr-2" />
            Document Code
          </TabsTrigger>
          <TabsTrigger value="simplify" className="flex items-center">
            <Code className="w-4 h-4 mr-2" />
            Simplify Code
          </TabsTrigger>
          <TabsTrigger value="optimize" className="flex items-center">
            <Code className="w-4 h-4 mr-2" />
            Optimize Code
          </TabsTrigger>
        </TabsList>
      </Tabs>
    </div>
  );
};

export default ActionSelector;
