// =====================================================================
// FILE: src/components/WorkflowNodes/ApprovalNode.tsx
// =====================================================================

import React from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { CheckCircle, Clock, Shield } from 'lucide-react';

export default function ApprovalNode({ data, selected }: NodeProps) {
  const hasABAC = data.enable_abac && data.abac_conditions?.length > 0;
  const hasSLA = data.sla_hours && data.sla_hours > 0;

  return (
    <div
      className={`p-4 rounded-lg ${
        selected ? 'bg-blue-50 border-2 border-blue-500' : 'bg-white border-2 border-gray-300'
      } min-w-[220px] shadow-md cursor-pointer relative`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-blue-500 w-2.5 h-2.5"
      />

      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <CheckCircle size={20} className="text-blue-500" />
        <span className="font-bold text-blue-500 text-xs">
          APPROVAL
        </span>
      </div>

      {/* Label */}
      <div className="text-sm font-bold mb-2 text-gray-800">
        {data.label || 'Approval Node'}
      </div>

      {/* Role Info */}
      {data.required_role && (
        <div className="text-xs text-gray-600 mb-1">
          <strong>Role:</strong> {data.required_role}
        </div>
      )}

      {data.required_roles && data.required_roles.length > 0 && (
        <div className="text-xs text-gray-600 mb-1">
          <strong>Roles:</strong> {data.required_roles.join(', ')}
        </div>
      )}

      {/* Approval Type */}
      {data.approval_type && data.approval_type !== 'sequential' && (
        <div className="text-xs text-gray-600 mb-1">
          <strong>Type:</strong> {data.approval_type.replace(/_/g, ' ')}
        </div>
      )}

      {/* Badges */}
      <div className="flex gap-1.5 mt-2 flex-wrap">
        {hasABAC && (
          <span
            className="px-2 py-1 bg-blue-100 border border-blue-500 rounded-full text-xs font-bold text-blue-700 flex items-center gap-1"
          >
            <Shield size={12} />
            ABAC
          </span>
        )}

        {hasSLA && (
          <span
            className="px-2 py-1 bg-orange-100 border border-orange-400 rounded-full text-xs font-bold text-orange-600 flex items-center gap-1"
          >
            <Clock size={12} />
            {data.sla_hours}h
          </span>
        )}
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-blue-500 w-2.5 h-2.5"
      />
    </div>
  );
}