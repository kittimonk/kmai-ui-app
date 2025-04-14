
import React from 'react';
import { Textarea } from '@/components/ui/textarea';

type CodeInputProps = {
  code: string;
  setCode: (code: string) => void;
};

const CodeInput = ({ code, setCode }: CodeInputProps) => {
  return (
    <div>
      <label className="block text-sm font-medium mb-2">Code</label>
      <Textarea
        placeholder="Paste your code here..."
        className="min-h-[300px] font-mono text-sm"
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <div className="text-sm text-gray-500 mt-2">
        We support various programming languages including JavaScript, TypeScript, Python, and more.
      </div>
    </div>
  );
};

export default CodeInput;
