// =====================================================================
// FILE: src/components/WorkflowNodes/ConditionNode.tsx
// =====================================================================

import React from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { GitBranch } from 'lucide-react';

export default function ConditionNode({ data, selected }: NodeProps) {
  return (
    <div className="relative">
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-orange-400 w-2.5 h-2.5 z-10"
      />

      <div
        className={`p-4 rounded-lg ${
          selected ? 'bg-orange-100 border-2 border-orange-400' : 'bg-white border-2 border-gray-300'
        } min-w-[180px] transform rotate-45 shadow-md cursor-pointer`}
      >
        <div className="transform -rotate-45">
          <div className="flex items-center gap-2 mb-2">
            <GitBranch size={18} className="text-orange-400" />
            <span className="font-bold text-orange-400 text-xs">
              CONDITION
            </span>
          </div>

          <div className="text-sm font-bold mb-1.5 text-gray-800">
            {data.label || 'If...'}
          </div>

          {data.condition_field && (
            <div className="text-xs text-gray-600 text-center">
              {data.condition_field} {data.condition_operator} {data.condition_value}
            </div>
          )}
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        id="true"
        className="!bg-green-500 w-2.5 h-2.5 !left-1/4 z-10"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="false"
        className="!bg-red-500 w-2.5 h-2.5 !left-3/4 z-10"
      />
    </div>
  );
}