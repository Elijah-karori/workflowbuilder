import React from 'react';
import { Handle, Position, NodeProps } from ' @xyflow/react';
import { Play } from 'lucide-react';

export default function StartNode({ data, selected }: NodeProps) {
  return (
    <div
      style={{
        padding: '20px',
        borderRadius: '50%',
        background: selected ? '#e8f5e9' : '#4CAF50',
        border: selected ? '3px solid #4CAF50' : '2px solid #2e7d32',
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
      <div style={{ textAlign: 'center' }}>
        <Play size={32} />
        <div style={{ fontSize: '14px', marginTop: '4px' }}>Start</div>
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: '#2e7d32',
          width: '12px',
          height: '12px',
        }}
      />
    </div>
  );
}
