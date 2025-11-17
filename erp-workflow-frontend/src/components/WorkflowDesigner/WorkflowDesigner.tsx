// =====================================================================
// FILE: src/components/WorkflowDesigner/WorkflowDesigner.tsx
// =====================================================================

import React, { useState, useCallback, useEffect } from 'react';
import {
  ReactFlow,
  type Node,
  type Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  Panel,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Save,
  Rocket,
  Play,
  CheckCircle,
  GitBranch,
  CircleStop,
  Loader2,
  ArrowLeft,
} from 'lucide-react';

import { nodeTypes } from '../WorkflowNodes/nodeTypes';
import NodeConfigPanel from './NodeConfigPanel';
import { api } from '../../services/api';

export default function WorkflowDesigner() {
  const { workflowId } = useParams();
  const navigate = useNavigate();

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [workflowName, setWorkflowName] = useState('New Workflow');
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [modelName, setModelName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);

  // Load existing workflow
  useEffect(() => {
    if (workflowId) {
      loadWorkflow(parseInt(workflowId));
    } else {
      // Initialize with start node
      setNodes([
        {
          id: 'start-1',
          type: 'start',
          position: { x: 400, y: 50 },
          data: { label: 'Start' },
        },
      ]);
    }
  }, [workflowId]);

  const loadWorkflow = async (id: number) => {
    try {
      const response = await api.getWorkflow(id);
      const workflow = response.data;

      setWorkflowName(workflow.name);
      setWorkflowDescription(workflow.description || '');
      setModelName(workflow.model_name);

      if (workflow.workflow_graph) {
        setNodes(workflow.workflow_graph.nodes || []);
        setEdges(workflow.workflow_graph.edges || []);
      }
    } catch (error) {
      console.error('Failed to load workflow:', error);
      alert('Failed to load workflow');
    }
  };

  // Handle connections between nodes
  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: 'smoothstep',
            animated: true,
            style: { stroke: '#2196F3', strokeWidth: 2 },
          },
          eds
        )
      );
    },
    [setEdges]
  );

  // Add new node
  const addNode = (type: string) => {
    const newNode: Node = {
      id: `${type}-${Date.now()}`,
      type,
      position: {
        x: Math.random() * 400 + 200,
        y: Math.random() * 300 + 150,
      },
      data: {
        label: `${type.charAt(0).toUpperCase() + type.slice(1)} Node`,
        required_role: '',
        approval_type: 'sequential',
        enable_abac: false,
        abac_conditions: [],
      },
    };

    setNodes((nds) => [...nds, newNode]);
  };

  // Handle node click
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  // Update node data
  const updateNodeData = useCallback(
    (nodeId: string, newData: any) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                ...newData,
              },
            };
          }
          return node;
        })
      );
    },
    [setNodes]
  );

  // Delete selected node
  const deleteNode = () => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id));
      setEdges((eds) =>
        eds.filter((e) => e.source !== selectedNode.id && e.target !== selectedNode.id)
      );
      setSelectedNode(null);
    }
  };

  // Save workflow
  const saveWorkflow = async () => {
    if (!workflowName || !modelName) {
      alert('Please provide workflow name and model name');
      return;
    }

    setIsSaving(true);
    try {
      const graphData = {
        name: workflowName,
        description: workflowDescription,
        model_name: modelName,
        nodes,
        edges,
      };

      let response;
      if (workflowId) {
        response = await api.updateWorkflowGraph(parseInt(workflowId), graphData);
      } else {
        response = await api.createWorkflowGraph(graphData);
      }

      alert('Workflow saved successfully!');

      // Navigate to the workflow editor if newly created
      if (!workflowId && response.data.id) {
        navigate(`/workflows/designer/${response.data.id}`);
      }
    } catch (error: any) {
      console.error('Failed to save workflow:', error);
      alert(error.response?.data?.detail || 'Failed to save workflow');
    } finally {
      setIsSaving(false);
    }
  };

  // Publish workflow
  const publishWorkflow = async () => {
    if (!workflowId) {
      alert('Please save the workflow first');
      return;
    }

    if (!window.confirm('Are you sure you want to publish this workflow? It will become active.')) {
      return;
    }

    setIsPublishing(true);
    try {
      await api.publishWorkflow(parseInt(workflowId));
      alert('Workflow published successfully!');
      navigate('/workflows');
    } catch (error: any) {
      console.error('Failed to publish workflow:', error);
      alert(error.response?.data?.detail || 'Failed to publish workflow');
    } finally {
      setIsPublishing(false);
    }
  };

  // Test workflow
  const testWorkflow = () => {
    // Simple validation
    const hasStart = nodes.some((n) => n.type === 'start');
    const hasEnd = nodes.some((n) => n.type === 'end');

    if (!hasStart) {
      alert('❌ Workflow must have a START node');
      return;
    }

    if (!hasEnd) {
      alert('❌ Workflow must have an END node');
      return;
    }

    // Check all approval nodes have required role
    const approvalNodes = nodes.filter((n) => n.type === 'approval');
    const invalidNodes = approvalNodes.filter(
      (n) => !n.data.required_role && (!n.data.required_roles || n.data.required_roles.length === 0)
    );

    if (invalidNodes.length > 0) {
      alert(`❌ The following nodes are missing required roles:\n${invalidNodes.map((n) => n.data.label).join('\n')}`);
      return;
    }

    alert('✅ Workflow validation passed!');
  };

  return (
    <div className="w-screen h-screen flex">
      {/* Main Canvas */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.2}
          maxZoom={2}
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              switch (node.type) {
                case 'start':
                  return '#4CAF50';
                case 'approval':
                  return '#2196F3';
                case 'condition':
                  return '#FF9800';
                case 'end':
                  return '#f44336';
                default:
                  return '#ccc';
              }
            }}
            nodeStrokeWidth={3}
            zoomable
            pannable
          />

          {/* Top Toolbar */}
          <Panel position="top-left" className="bg-white rounded-lg p-3 shadow-md flex justify-between items-center gap-4 m-4">
            <div className="flex items-center gap-3">
              <button onClick={() => navigate('/workflows')} className="p-2 border border-gray-300 rounded hover:bg-gray-100" title="Back">
                <ArrowLeft size={20} />
              </button>

              <div className="w-px h-8 bg-gray-300" />

              <div className="flex flex-col gap-1">
                <input
                  type="text"
                  value={workflowName}
                  onChange={(e) => setWorkflowName(e.target.value)}
                  placeholder="Workflow Name"
                  className="p-1.5 border border-gray-300 rounded text-base font-semibold min-w-[250px]"
                />
                <input
                  type="text"
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  placeholder="Model Name (e.g., Invoice)"
                  className="p-1.5 border border-gray-300 rounded text-sm text-gray-600 min-w-[250px]"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button onClick={testWorkflow} className="bg-gray-500 text-white px-5 py-2.5 rounded-md flex items-center gap-2 hover:bg-gray-600" title="Test Workflow">
                <Play size={18} />
                Test
              </button>

              <button
                onClick={saveWorkflow}
                disabled={isSaving}
                className="bg-blue-500 text-white px-5 py-2.5 rounded-md flex items-center gap-2 hover:bg-blue-600 disabled:opacity-50"
                title="Save Workflow"
              >
                {isSaving ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={18} />
                    Save
                  </>
                )}
              </button>

              {workflowId && (
                <button
                  onClick={publishWorkflow}
                  disabled={isPublishing}
                  className="bg-green-500 text-white px-5 py-2.5 rounded-md flex items-center gap-2 hover:bg-green-600 disabled:opacity-50"
                  title="Publish Workflow"
                >
                  {isPublishing ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      Publishing...
                    </>
                  ) : (
                    <>
                      <Rocket size={18} />
                      Publish
                    </>
                  )}
                </button>
              )}
            </div>
          </Panel>

          {/* Node Palette */}
          <Panel position="top-right" className="bg-white rounded-lg p-4 shadow-md m-4 min-w-[200px]">
            <div className="font-bold mb-3 text-gray-800">Add Nodes</div>
            <div className="flex flex-col gap-2">
              <button onClick={() => addNode('approval')} className="flex items-center gap-2 p-2.5 border-2 border-blue-500 rounded-md bg-white text-blue-500 hover:bg-blue-50 text-sm font-medium transition-all hover:-translate-y-0.5 hover:shadow-md">
                <CheckCircle size={20} />
                <span>Approval</span>
              </button>
              <button onClick={() => addNode('condition')} className="flex items-center gap-2 p-2.5 border-2 border-orange-400 rounded-md bg-white text-orange-400 hover:bg-orange-50 text-sm font-medium transition-all hover:-translate-y-0.5 hover:shadow-md">
                <GitBranch size={20} />
                <span>Condition</span>
              </button>
              <button onClick={() => addNode('end')} className="flex items-center gap-2 p-2.5 border-2 border-red-500 rounded-md bg-white text-red-500 hover:bg-red-50 text-sm font-medium transition-all hover:-translate-y-0.5 hover:shadow-md">
                <CircleStop size={20} />
                <span>End</span>
              </button>
            </div>

            {selectedNode && (
              <>
                <div className="h-px bg-gray-300 my-3" />
                <button onClick={deleteNode} className="bg-red-500 text-white px-5 py-2.5 rounded-md w-full hover:bg-red-600">
                  Delete Selected
                </button>
              </>
            )}
          </Panel>
        </ReactFlow>
      </div>

      {/* Configuration Panel */}
      {selectedNode && (
        <NodeConfigPanel
          node={selectedNode}
          onUpdate={updateNodeData}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}