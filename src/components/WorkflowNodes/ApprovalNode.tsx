import React from 'react';
import { Handle, Position, NodeProps } from ' @xyflow/react';
import { CheckCircle, Clock, Shield } from 'lucide-react';

export default function ApprovalNode({ data, selected }: NodeProps) {
  const hasABAC = data.enable_abac && data.abac_conditions?.length > 0;
  const hasSLA = data.sla_hours && data.sla_hours > 0;

  return (
    <div
      style={{
        padding: '16px',
        borderRadius: '8px',
        background: selected ? '#e3f2fd' : 'white',
        border: selected ? '2px solid #2196F3' : '2px solid #ddd',
        minWidth: '220px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        cursor: 'pointer',
        position: 'relative',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: '#2196F3',
          width: '10px',
          height: '10px',
        }}
      />

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <CheckCircle size={20} color="#2196F3" />
        <span style={{ fontWeight: 'bold', color: '#2196F3', fontSize: '12px' }}>
          APPROVAL
        </span>
      </div>

      {/* Label */}
      <div style={{ fontSize: '15px', fontWeight: 'bold', marginBottom: '8px', color: '#333' }}>
        {data.label || 'Approval Node'}
      </div>

      {/* Role Info */}
      {data.required_role && (
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
          <strong>Role:</strong> {data.required_role}
        </div>
      )}

      {data.required_roles && data.required_roles.length > 0 && (
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
          <strong>Roles:</strong> {data.required_roles.join(', ')}
        </div>
      )}

      {/* Approval Type */}
      {data.approval_type && data.approval_type !== 'sequential' && (
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
          <strong>Type:</strong> {data.approval_type.replace(/_/g, ' ')}
        </div>
      )}

      {/* Badges */}
      <div style={{ display: 'flex', gap: '6px', marginTop: '8px', flexWrap: 'wrap' }}>
        {hasABAC && (
          <span
            style={{
              padding: '3px 8px',
              background: '#e3f2fd',
              border: '1px solid #2196F3',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 'bold',
              color: '#1976d2',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Shield size={12} />
            ABAC
          </span>
        )}

        {hasSLA && (
          <span
            style={{
              padding: '3px 8px',
              background: '#fff3e0',
              border: '1px solid #ff9800',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 'bold',
              color: '#f57c00',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Clock size={12} />
            {data.sla_hours}h
          </span>
        )}
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: '#2196F3',
          width: '10px',
          height: '10px',
        }}
      />
    </div>
  );
}
