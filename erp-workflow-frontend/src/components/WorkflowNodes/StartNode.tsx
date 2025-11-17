// =====================================================================
// FILE: src/components/WorkflowNodes/StartNode.tsx
// =====================================================================

import React from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Play } from 'lucide-react';

export default function StartNode({ selected }: NodeProps) {
  return (
    <div
      className={`p-5 rounded-full ${
        selected ? 'bg-green-100 border-4 border-green-500' : 'bg-green-500 border-2 border-green-700'
      } w-28 h-28 flex items-center justify-center text-white font-bold shadow-lg cursor-pointer`}
    >
      <div className="text-center">
        <Play size={32} />
        <div className="text-sm mt-1">Start</div>
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-green-700 w-3 h-3"
      />
    </div>
  );
}