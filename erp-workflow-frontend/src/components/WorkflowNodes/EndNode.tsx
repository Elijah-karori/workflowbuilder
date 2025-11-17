// =====================================================================
// FILE: src/components/WorkflowNodes/EndNode.tsx
// =====================================================================

import React from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { CircleStop } from 'lucide-react';

export default function EndNode({ selected }: NodeProps) {
  return (
    <div
      className={`p-5 rounded-full ${
        selected ? 'bg-red-100 border-4 border-red-500' : 'bg-red-500 border-2 border-red-700'
      } w-28 h-28 flex items-center justify-center text-white font-bold shadow-lg cursor-pointer`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-red-700 w-3 h-3"
      />

      <div className="text-center">
        <CircleStop size={32} />
        <div className="text-sm mt-1">End</div>
      </div>
    </div>
  );
}