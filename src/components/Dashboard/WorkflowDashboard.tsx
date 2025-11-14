import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Play, 
  Clock, 
  CheckCircle, 
  XCircle, 
  BarChart3,
  Users,
  Shield
} from 'lucide-react';
import { api } from '../../services/api';

interface WorkflowStats {
  total_workflows: number;
  active_instances: number;
  pending_approvals: number;
  completed_today: number;
}

interface WorkflowDefinition {
  id: number;
  name: string;
  description: string;
  version: number;
  status: 'draft' | 'published' | 'archived';
  created_at: string;
  updated_at: string;
  created_by: string;
}

export default function WorkflowDashboard() {
  const [stats, setStats] = useState<WorkflowStats | null>(null);
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [recentApprovals, setRecentApprovals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, workflowsRes, approvalsRes] = await Promise.all([
        api.getWorkflowStats(),
        api.getWorkflows({ page: 1, limit: 5 }),
        api.getMyApprovals({ limit: 5 })
      ]);

      setStats(statsRes.data);
      setWorkflows(workflowsRes.data.workflows || []);
      setRecentApprovals(approvalsRes.data.approvals || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { color: 'bg-gray-100 text-gray-800', label: 'Draft' },
      published: { color: 'bg-green-100 text-green-800', label: 'Published' },
      archived: { color: 'bg-red-100 text-red-800', label: 'Archived' }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    
    return (
      <span className={`status-badge ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const getApprovalStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle size={16} className="text-green-600" />;
      case 'rejected':
        return <XCircle size={16} className="text-red-600" />;
      default:
        return <Clock size={16} className="text-orange-500" />;
    }
  };

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>Workflow Dashboard</h1>
        <Link to="/workflows/design" className="btn-primary">
          <Plus size={16} />
          Create Workflow
        </Link>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon bg-blue-100 text-blue-600">
            <BarChart3 size={24} />
          </div>
          <div className="stat-content">
            <h3>{stats?.total_workflows || 0}</h3>
            <p>Total Workflows</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon bg-green-100 text-green-600">
            <Play size={24} />
          </div>
          <div className="stat-content">
            <h3>{stats?.active_instances || 0}</h3>
            <p>Active Instances</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon bg-orange-100 text-orange-600">
            <Clock size={24} />
          </div>
          <div className="stat-content">
            <h3>{stats?.pending_approvals || 0}</h3>
            <p>Pending Approvals</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon bg-purple-100 text-purple-600">
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <h3>{stats?.completed_today || 0}</h3>
            <p>Completed Today</p>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Recent Workflows */}
        <div className="dashboard-section">
          <div className="section-header">
            <h2>Recent Workflows</h2>
            <Link to="/workflows" className="view-all-link">
              View All →
            </Link>
          </div>
          
          <div className="workflows-list">
            {workflows.length === 0 ? (
              <div className="empty-state">
                <Shield size={48} className="empty-icon" />
                <p>No workflows found</p>
                <Link to="/workflows/design" className="btn-primary">
                  Create Your First Workflow
                </Link>
              </div>
            ) : (
              workflows.map((workflow) => (
                <div key={workflow.id} className="workflow-item">
                  <div className="workflow-info">
                    <h4>{workflow.name}</h4>
                    <p>{workflow.description}</p>
                    <div className="workflow-meta">
                      <span>v{workflow.version}</span>
                      <span>Updated {new Date(workflow.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="workflow-actions">
                    {getStatusBadge(workflow.status)}
                    <div className="action-buttons">
                      <Link 
                        to={`/workflows/design/${workflow.id}`}
                        className="btn-outline"
                      >
                        Edit
                      </Link>
                      {workflow.status === 'published' && (
                        <Link 
                          to={`/workflows/start/${workflow.id}`}
                          className="btn-primary"
                        >
                          Start
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Pending Approvals */}
        <div className="dashboard-section">
          <div className="section-header">
            <h2>My Pending Approvals</h2>
            <Link to="/approvals" className="view-all-link">
              View All →
            </Link>
          </div>
          
          <div className="approvals-list">
            {recentApprovals.length === 0 ? (
              <div className="empty-state">
                <CheckCircle size={48} className="empty-icon" />
                <p>No pending approvals</p>
                <span>You're all caught up!</span>
              </div>
            ) : (
              recentApprovals.map((approval) => (
                <div key={approval.id} className="approval-item">
                  <div className="approval-icon">
                    {getApprovalStatusIcon(approval.status)}
                  </div>
                  <div className="approval-info">
                    <h4>{approval.workflow_name}</h4>
                    <p>{approval.resource_type} #{approval.resource_id}</p>
                    <div className="approval-meta">
                      <span>Initiated by: {approval.initiated_by}</span>
                      <span>Due: {new Date(approval.due_date).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="approval-actions">
                    <span className={`priority-badge ${approval.priority}`}>
                      {approval.priority}
                    </span>
                    <Link 
                      to={`/approvals/${approval.id}`}
                      className="btn-primary"
                    >
                      Review
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
