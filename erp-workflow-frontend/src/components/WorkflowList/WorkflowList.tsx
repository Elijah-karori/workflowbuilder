// =====================================================================
// FILE: src/components/WorkflowList/WorkflowList.tsx
// =====================================================================

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Copy, Trash2, Rocket, FileText, Clock } from 'lucide-react';
import { api } from '../../services/api';

interface Workflow {
  id: number;
  name: string;
  description: string;
  model_name: string;
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export default function WorkflowList() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    loadWorkflows();
  }, [filter]);

  const loadWorkflows = async () => {
    setLoading(true);
    try {
      const params = filter !== 'all' ? { status_filter: filter } : {};
      const response = await api.getWorkflows(params);
      setWorkflows(response.data);
    } catch (error) {
      console.error('Failed to load workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    navigate('/workflows/designer');
  };

  const handleEdit = (id: number) => {
    navigate(`/workflows/designer/${id}`);
  };

  const handleClone = async (workflow: Workflow) => {
    const newName = prompt(`Clone "${workflow.name}" as:`, `${workflow.name} (Copy)`);
    if (newName) {
      try {
        await api.cloneWorkflow(workflow.id, newName);
        loadWorkflows();
      } catch (error) {
        alert('Failed to clone workflow');
      }
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (window.confirm(`Delete workflow "${name}"? This action cannot be undone.`)) {
      try {
        await api.deleteWorkflow(id);
        loadWorkflows();
      } catch (error) {
        alert('Failed to delete workflow');
      }
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: { [key: string]: string } = {
      draft: 'bg-gray-500 text-white',
      active: 'bg-green-500 text-white',
      archived: 'bg-red-500 text-white',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-bold ${styles[status]}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="m-0 mb-2 text-3xl font-bold">Workflow Management</h1>
          <p className="text-gray-600 m-0 text-base">Create and manage approval workflows</p>
        </div>
        <button onClick={handleCreate} className="bg-blue-500 text-white px-5 py-2.5 rounded-md flex items-center gap-2 hover:bg-blue-600">
          <Plus size={20} />
          Create Workflow
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-8 border-b-2 border-gray-200">
        {['all', 'draft', 'active', 'archived'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-6 py-3 border-b-4 text-sm font-medium transition-colors ${
              filter === status
                ? 'border-blue-500 text-blue-500'
                : 'border-transparent text-gray-600 hover:text-blue-500'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      {/* Workflow Grid */}
      {loading ? (
        <div className="flex flex-col items-center justify-center p-16 text-gray-600">Loading workflows...</div>
      ) : workflows.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-16 text-center text-gray-600">
          <FileText size={64} className="text-gray-400" />
          <h3 className="mt-4 mb-2 text-2xl font-bold text-gray-800">No workflows found</h3>
          <p className="m-0 text-base">Create your first workflow to get started</p>
          <button onClick={handleCreate} className="bg-blue-500 text-white px-5 py-2.5 rounded-md flex items-center gap-2 hover:bg-blue-600 mt-5">
            <Plus size={20} />
            Create Workflow
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <div key={workflow.id} className="bg-white border border-gray-200 rounded-lg p-5 transition-all hover:shadow-lg hover:-translate-y-1">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="m-0 mb-1 text-lg font-bold text-gray-800">{workflow.name}</h3>
                  <p className="text-sm text-gray-600 m-0">{workflow.model_name}</p>
                </div>
                {getStatusBadge(workflow.status)}
              </div>

              <p className="text-gray-600 text-sm m-0 mb-4 leading-relaxed">{workflow.description || 'No description'}</p>

              <div className="flex flex-col gap-2 py-3 border-t border-b border-gray-100 mb-4">
                <div className="flex items-center gap-1.5 text-sm text-gray-600">
                  <Clock size={14} />
                  <span>Version {workflow.version}</span>
                </div>
                <div className="flex items-center gap-1.5 text-sm text-gray-600">
                  <span>
                    Updated {new Date(workflow.updated_at || workflow.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <button onClick={() => handleEdit(workflow.id)} className="p-2 border border-gray-300 rounded hover:bg-gray-100" title="Edit">
                  <Edit size={18} />
                </button>
                <button onClick={() => handleClone(workflow)} className="p-2 border border-gray-300 rounded hover:bg-gray-100" title="Clone">
                  <Copy size={18} />
                </button>
                <button
                  onClick={() => handleDelete(workflow.id, workflow.name)}
                  className="p-2 border border-red-500 text-red-500 rounded hover:bg-red-50"
                  title="Delete"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}