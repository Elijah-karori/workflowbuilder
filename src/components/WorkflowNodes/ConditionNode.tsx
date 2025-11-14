import React from 'react';
import { Handle, Position, NodeProps } from ' @xyflow/react';
import { GitBranch } from 'lucide-react';

export default function ConditionNode({ data, selected }: NodeProps) {
  return (
    <div
      style={{
        position: 'relative',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: '#FF9800',
          width: '10px',
          height: '10px',
          zIndex: 10,
        }}
      />

      <div
        style={{
          padding: '16px',
          borderRadius: '8px',
          background: selected ? '#fff3e0' : 'white',
          border: selected ? '2px solid #FF9800' : '2px solid #ddd',
          minWidth: '180px',
          transform: 'rotate(45deg)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          cursor: 'pointer',
        }}
      >
        <div style={{ transform: 'rotate(-45deg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <GitBranch size={18} color="#FF9800" />
            <span style={{ fontWeight: 'bold', color: '#FF9800', fontSize: '12px' }}>
              CONDITION
            </span>
          </div>

          <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '6px', color: '#333' }}>
            {data.label || 'If...'}
          </div>

          {data.condition_field && (
            <div style={{ fontSize: '11px', color: '#666', textAlign: 'center' }}>
              {data.condition_field} {data.condition_operator} {data.condition_value}
            </div>
          )}
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        id="true"
        style={{
          background: '#4CAF50',
          width: '10px',
          height: '10px',
          left: '25%',
          zIndex: 10,
        }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="false"
        style={{
          background: '#f44336',
          width: '10px',
          height: '10px',
          left: '75%',
          zIndex: 10,
        }}
      />
    </div>
  );
}
