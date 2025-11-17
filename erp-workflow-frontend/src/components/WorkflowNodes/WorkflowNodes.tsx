import React from 'react';
import { Handle, Position } from 'reactflow';

const nodeStyles = {
  padding: '10px 15px',
  border: '1px solid #ddd',
  borderRadius: '5px',
  background: '#fff',
};

export const StartNode = ({ data }: { data: { label: string } }) => (
  <div style={{ ...nodeStyles, backgroundColor: '#b0f2c2' }}>
    <Handle type="source" position={Position.Right} />
    {data.label}
  </div>
);

export const EndNode = ({ data }: { data: { label: string } }) => (
  <div style={{ ...nodeStyles, backgroundColor: '#f2b0b0' }}>
    <Handle type="target" position={Position.Left} />
    {data.label}
  </div>
);

export const ApprovalNode = ({ data }: { data: { label: string } }) => (
  <div style={nodeStyles}>
    <Handle type="target" position={Position.Left} />
    {data.label}
    <Handle type="source" position={Position.Right} />
  </div>
);

export const ConditionNode = ({ data }: { data: { label: string } }) => (
  <div style={{ ...nodeStyles, backgroundColor: '#f2e5b0' }}>
    <Handle type="target" position={Position.Left} />
    {data.label}
    <Handle type="source" position={Position.Right} id="a" style={{ top: '33%' }} />
    <Handle type="source" position={Position.Right} id="b" style={{ top: '66%' }} />
  </div>
);
