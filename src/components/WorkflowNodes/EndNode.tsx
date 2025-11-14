import React from 'react';
import { Handle, Position, NodeProps } from ' @xyflow/react';
import { CircleStop } from 'lucide-react';

export default function EndNode({ data, selected }: NodeProps) {
  return (
    <div
      style={{
        padding: '20px',
        borderRadius: '50%',
        background: selected ? '#ffebee' : '#f44336',
        border: selected ? '3px solid #f44336' : '2px solid #c62828',
        width: '100px',
        height: '100px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontWeight: 'bold',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        cursor: 'pointer',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: '#c62828',
          width: '12px',
          height: '12px',
        }}
      />

      <div style={{ textAlign: 'center' }}>
        <CircleStop size={32} />
        <div style={{ fontSize: '14px', marginTop: '4px' }}>End</div>
      </div>
    </div>
  );
}
