import React, { useRef } from 'react';
import {
  Save,
  Play,
  Copy,
  Download,
  Upload,
  Plus,
  Shield,
  GitBranch,
  CircleStop,
} from 'lucide-react';

interface ToolbarProps {
  workflowName: string;
  onWorkflowNameChange: (name: string) => void;
  onAddNode: (nodeType: string) => void;
  onSave: () => void;
  onPublish: () => void;
  onExport: () => void;
  onImport: (event: React.ChangeEvent<HTMLInputElement>) => void;
  isSaving: boolean;
  lastSaved: Date | null;
  isValidWorkflow: boolean;
  readOnly: boolean;
  workflowId?: number;
}

export default function Toolbar({
  workflowName,
  onWorkflowNameChange,
  onAddNode,
  onSave,
  onPublish,
  onExport,
  onImport,
  isSaving,
  lastSaved,
  isValidWorkflow,
  readOnly,
  workflowId,
}: ToolbarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const nodeTypes = [
    { type: 'start', label: 'Start', icon: Play, color: '#4CAF50' },
    { type: 'approval', label: 'Approval', icon: Shield, color: '#2196F3' },
    { type: 'condition', label: 'Condition', icon: GitBranch, color: '#FF9800' },
    { type: 'end', label: 'End', icon: CircleStop, color: '#f44336' },
  ];

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="toolbar">
      {/* Workflow Name & Basic Info */}
      <div className="toolbar-section">
        <input
          type="text"
          value={workflowName}
          onChange={(e) => onWorkflowNameChange(e.target.value)}
          className="workflow-name-input"
          placeholder="Enter workflow name..."
          disabled={readOnly}
        />
        {workflowId && (
          <span className="workflow-id">ID: {workflowId}</span>
        )}
      </div>

      {/* Node Palette */}
      {!readOnly && (
        <div className="toolbar-section">
          <div className="node-palette">
            <span className="palette-label">Add Node:</span>
            {nodeTypes.map((nodeType) => (
              <button
                key={nodeType.type}
                onClick={() => onAddNode(nodeType.type)}
                className="node-type-btn"
                style={{ '--node-color': nodeType.color } as any}
                title={`Add ${nodeType.label} Node`}
              >
                <nodeType.icon size={16} />
                <span>{nodeType.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="toolbar-section actions">
        {!readOnly && (
          <>
            <button
              onClick={onSave}
              disabled={isSaving || !isValidWorkflow}
              className="btn-primary"
              title="Save Workflow"
            >
              <Save size={16} />
              {isSaving ? 'Saving...' : 'Save'}
            </button>

            <button
              onClick={onPublish}
              disabled={!workflowId || !isValidWorkflow}
              className="btn-success"
              title="Publish Workflow"
            >
              <Play size={16} />
              Publish
            </button>
          </>
        )}

        <button
          onClick={onExport}
          className="btn-secondary"
          title="Export Workflow"
        >
          <Download size={16} />
          Export
        </button>

        {!readOnly && (
          <>
            <input
              type="file"
              ref={fileInputRef}
              onChange={onImport}
              accept=".json"
              style={{ display: 'none' }}
            />
            <button
              onClick={handleImportClick}
              className="btn-secondary"
              title="Import Workflow"
            >
              <Upload size={16} />
              Import
            </button>
          </>
        )}

        {workflowId && (
          <button
            onClick={() => {/* Clone functionality */}}
            className="btn-secondary"
            title="Clone Workflow"
          >
            <Copy size={16} />
            Clone
          </button>
        )}
      </div>

      {/* Status Indicators */}
      <div className="toolbar-section status">
        {lastSaved && (
          <div className="last-saved">
            Saved: {lastSaved.toLocaleTimeString()}
          </div>
        )}
        <div className={`validation-status ${isValidWorkflow ? 'valid' : 'invalid'}`}>
          {isValidWorkflow ? '✓ Valid' : '⚠ Invalid'}
        </div>
      </div>
    </div>
  );
}
