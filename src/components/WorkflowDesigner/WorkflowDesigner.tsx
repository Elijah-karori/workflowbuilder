import React, { useState, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Connection,
  Edge,
  Node,
  ReactFlowProvider,
} from ' @xyflow/react';
import { nodeTypes } from '../WorkflowNodes';
import NodeConfigPanel from './NodeConfigPanel';
import Toolbar from './Toolbar';
import { api } from '../../services/api';
import { Save, Play, Copy, Download, Upload } from 'lucide-react';

interface WorkflowDesignerProps {
  workflowId?: number;
  initialNodes?: Node[];
  initialEdges?: Edge[];
  onSave?: (workflow: any) => void;
  onPublish?: (workflowId: number) => void;
  readOnly?: boolean;
}

const initialNodeTemplates = {
  start: {
    type: 'start',
    data: { label: 'Start' },
    position: { x: 250, y: 50 },
  },
  approval: {
    type: 'approval',
    data: {
      label: 'Approval Node',
      required_role: '',
      approval_type: 'sequential',
      enable_abac: false,
      abac_conditions: [],
      sla_hours: null,
    },
    position: { x: 250, y: 200 },
  },
  condition: {
    type: 'condition',
    data: {
      label: 'Condition',
      condition_field: '',
      condition_operator: '>',
      condition_value: '',
    },
    position: { x: 250, y: 200 },
  },
  end: {
    type: 'end',
    data: { label: 'End' },
    position: { x: 250, y: 400 },
  },
};

export default function WorkflowDesigner({
  workflowId,
  initialNodes = [],
  initialEdges = [],
  onSave,
  onPublish,
  readOnly = false,
}: WorkflowDesignerProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [workflowName, setWorkflowName] = useState('New Workflow');
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Add node to canvas
  const addNode = useCallback((nodeType: string) => {
    const template = initialNodeTemplates[nodeType as keyof typeof initialNodeTemplates];
    if (!template) return;

    const newNode: Node = {
      id: `${nodeType}_${Date.now()}`,
      ...template,
      position: {
        x: Math.random() * 400 + 100,
        y: Math.random() * 300 + 100,
      },
    };

    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  // Handle connections
  const onConnect = useCallback(
    (params: Connection) => {
      // For condition nodes, we need to set the sourceHandle based on condition result
      if (params.sourceHandle) {
        setEdges((eds) => addEdge({ ...params, type: 'smoothstep' }, eds));
      } else {
        setEdges((eds) => addEdge({ ...params, type: 'smoothstep' }, eds));
      }
    },
    [setEdges]
  );

  // Update node data
  const onNodeUpdate = useCallback((nodeId: string, data: any) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return { ...node, data: { ...node.data, ...data } };
        }
        return node;
      })
    );
  }, [setNodes]);

  // Node click handler
  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    if (readOnly) return;
    setSelectedNode(node);
  }, [readOnly]);

  // Pane click handler (deselect node)
  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  // Save workflow
  const saveWorkflow = useCallback(async () => {
    setIsSaving(true);
    try {
      const workflowData = {
        name: workflowName,
        description: 'Workflow created via visual designer',
        nodes: nodes.map(node => ({
          id: node.id,
          type: node.type,
          position: node.position,
          data: node.data,
        })),
        edges: edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          sourceHandle: edge.sourceHandle,
          targetHandle: edge.targetHandle,
          type: edge.type,
        })),
      };

      let result;
      if (workflowId) {
        result = await api.updateWorkflowGraph(workflowId, workflowData);
      } else {
        result = await api.createWorkflowGraph(workflowData);
      }

      setLastSaved(new Date());
      onSave?.(result.data);
      
    } catch (error) {
      console.error('Failed to save workflow:', error);
      alert('Failed to save workflow. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [workflowId, workflowName, nodes, edges, onSave]);

  // Publish workflow
  const publishWorkflow = useCallback(async () => {
    if (!workflowId) {
      alert('Please save the workflow first before publishing.');
      return;
    }

    try {
      await api.publishWorkflow(workflowId);
      onPublish?.(workflowId);
      alert('Workflow published successfully!');
    } catch (error) {
      console.error('Failed to publish workflow:', error);
      alert('Failed to publish workflow. Please try again.');
    }
  }, [workflowId, onPublish]);

  // Export workflow
  const exportWorkflow = useCallback(() => {
    const workflowData = {
      name: workflowName,
      nodes,
      edges,
      version: '1.0',
      exportedAt: new Date().toISOString(),
    };

    const dataStr = JSON.stringify(workflowData, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    
    const exportFileDefaultName = `${workflowName.replace(/\s+/g, '_')}_workflow.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }, [workflowName, nodes, edges]);

  // Import workflow
  const importWorkflow = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const workflowData = JSON.parse(e.target?.result as string);
        setNodes(workflowData.nodes || []);
        setEdges(workflowData.edges || []);
        setWorkflowName(workflowData.name || 'Imported Workflow');
      } catch (error) {
        alert('Failed to import workflow file. Please check the file format.');
      }
    }
    reader.readAsText(file);

    // Reset input
    event.target.value = '';
  }, [setNodes, setEdges]);

  // Validate workflow
  const isValidWorkflow = useMemo(() => {
    const startNodes = nodes.filter(n => n.type === 'start');
    const endNodes = nodes.filter(n => n.type === 'end');
    
    if (startNodes.length !== 1) return false;
    if (endNodes.length === 0) return false;
    
    // Check if all nodes are connected
    const connectedNodeIds = new Set();
    edges.forEach(edge => {
      connectedNodeIds.add(edge.source);
      connectedNodeIds.add(edge.target);
    });
    
    return nodes.every(node => connectedNodeIds.has(node.id) || node.type === 'start');
  }, [nodes, edges]);

  return (
    <div className="workflow-designer">
      {/* Toolbar */}
      <Toolbar
        workflowName={workflowName}
        onWorkflowNameChange={setWorkflowName}
        onAddNode={addNode}
        onSave={saveWorkflow}
        onPublish={publishWorkflow}
        onExport={exportWorkflow}
        onImport={importWorkflow}
        isSaving={isSaving}
        lastSaved={lastSaved}
        isValidWorkflow={isValidWorkflow}
        readOnly={readOnly}
        workflowId={workflowId}
      />

      {/* Main Design Area */}
      <div className="design-area">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.2}
          maxZoom={1.5}
          className="workflow-canvas"
        >
          <Background />
          <Controls />
          <MiniMap 
            nodeStrokeColor="#1976d2"
            nodeColor="#e3f2fd"
            maskColor="rgba(0, 0, 0, 0.1)"
          />
        </ReactFlow>

        {/* Node Configuration Panel */}
        {selectedNode && !readOnly && (
          <NodeConfigPanel
            node={selectedNode}
            onUpdate={onNodeUpdate}
            onClose={() => setSelectedNode(null)}
          />
        )}
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <div className="status-info">
          <span>Nodes: {nodes.length}</span>
          <span>Connections: {edges.length}</span>
          {lastSaved && (
            <span>Last saved: {lastSaved.toLocaleTimeString()}</span>
          )}
        </div>
        <div className="validation-status">
          {isValidWorkflow ? (
            <span className="status-valid">✓ Workflow is valid</span>
          ) : (
            <span className="status-invalid">⚠ Workflow needs attention</span>
          )}
        </div>
      </div>
    </div>
  );
}

// Wrapper component with ReactFlowProvider
export function WorkflowDesignerWithProvider(props: WorkflowDesignerProps) {
  return (
    <ReactFlowProvider>
      <WorkflowDesigner {...props} />
    </ReactFlowProvider>
  );
}
