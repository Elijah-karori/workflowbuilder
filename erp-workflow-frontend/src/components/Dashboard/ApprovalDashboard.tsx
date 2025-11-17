// =====================================================================
// FILE: src/components/Dashboard/ApprovalDashboard.tsx
// =====================================================================

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
  Eye,
} from 'lucide-react';
import { api } from '../../services/api';

interface WorkflowStats {
  pending_approvals: number;
  sla_breaches: number;
  approved_this_month: number;
  by_resource_type: { [key: string]: number };
}

interface PendingApproval {
  id: number;
  workflow: { name: string };
  related_model: string;
  related_id: number;
  current_stage: { name: string; sla_hours?: number };
  created_at: string;
  updated_at: string;
}

export function ApprovalDashboard() {
  const [stats, setStats] = useState<WorkflowStats | null>(null);
  const [pending, setPending] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, pendingRes] = await Promise.all([
        api.getWorkflowStats(),
        api.getMyApprovals(),
      ]);

      setStats(statsRes.data);
      setPending(pendingRes.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (instanceId: number) => {
    if (!window.confirm('Approve this item?')) return;

    try {
      await api.performWorkflowAction(instanceId, {
        action: 'approve',
        comment: 'Approved from dashboard',
      });
      loadDashboardData();
      alert('Approved successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to approve');
    }
  };

  const handleReject = async (instanceId: number) => {
    const comment = prompt('Reason for rejection:');
    if (!comment) return;

    try {
      await api.performWorkflowAction(instanceId, {
        action: 'reject',
        comment,
      });
      loadDashboardData();
      alert('Rejected successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to reject');
    }
  };

  const getTimeSinceUpdate = (updatedAt: string) => {
    const now = new Date();
    const updated = new Date(updatedAt);
    const hours = Math.floor((now.getTime() - updated.getTime()) / (1000 * 60 * 60));

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const isSLABreach = (approval: PendingApproval) => {
    if (!approval.current_stage.sla_hours) return false;

    const updated = new Date(approval.updated_at);
    const now = new Date();
    const hoursSince = (now.getTime() - updated.getTime()) / (1000 * 60 * 60);

    return hoursSince > approval.current_stage.sla_hours;
  };

  if (loading) {
    return <div className="flex items-center justify-center p-16 text-lg text-gray-600">Loading dashboard...</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="m-0 mb-8 text-3xl font-bold">Approval Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 flex items-center gap-5 shadow-md transition-all hover:-translate-y-1 hover:shadow-lg border-l-4 border-blue-500">
          <div className="p-4 rounded-full bg-blue-100 text-blue-500">
            <Clock size={32} />
          </div>
          <div className="flex-1">
            <div className="text-4xl font-bold leading-none mb-2">{stats?.pending_approvals || 0}</div>
            <div className="text-sm text-gray-600">Pending Approvals</div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 flex items-center gap-5 shadow-md transition-all hover:-translate-y-1 hover:shadow-lg border-l-4 border-red-500">
          <div className="p-4 rounded-full bg-red-100 text-red-500">
            <AlertTriangle size={32} />
          </div>
          <div className="flex-1">
            <div className="text-4xl font-bold leading-none mb-2">{stats?.sla_breaches || 0}</div>
            <div className="text-sm text-gray-600">SLA Breaches</div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 flex items-center gap-5 shadow-md transition-all hover:-translate-y-1 hover:shadow-lg border-l-4 border-green-500">
          <div className="p-4 rounded-full bg-green-100 text-green-500">
            <TrendingUp size={32} />
          </div>
          <div className="flex-1">
            <div className="text-4xl font-bold leading-none mb-2">{stats?.approved_this_month || 0}</div>
            <div className="text-sm text-gray-600">Approved This Month</div>
          </div>
        </div>
      </div>

      {/* By Resource Type */}
      {stats?.by_resource_type && Object.keys(stats.by_resource_type).length > 0 && (
        <div className="mb-8">
          <h3 className="m-0 mb-4 text-xl font-bold">Pending by Type</h3>
          <div className="flex gap-3 flex-wrap">
            {Object.entries(stats.by_resource_type).map(([type, count]) => (
              <div key={type} className="px-4 py-2 bg-blue-100 border border-blue-500 rounded-full text-sm text-blue-800">
                {type}: <strong>{count}</strong>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pending Approvals List */}
      <div>
        <h2 className="m-0 mb-6 text-2xl font-bold">Pending Approvals ({pending.length})</h2>

        {pending.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-16 text-center">
            <CheckCircle size={64} className="text-green-500" />
            <h3 className="mt-4 mb-2 text-2xl font-bold text-green-600">All caught up!</h3>
            <p className="m-0 text-base text-gray-600">No pending approvals at the moment</p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {pending.map((approval) => (
              <div
                key={approval.id}
                className={`bg-white border border-gray-200 rounded-lg p-5 flex items-center gap-6 transition-all hover:shadow-md ${
                  isSLABreach(approval) ? 'border-l-4 border-red-500 bg-orange-50' : 'border-l-4 border-blue-500'
                }`}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="m-0 text-lg font-bold">{approval.workflow.name}</h3>
                    {isSLABreach(approval) && (
                      <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold flex items-center gap-1">
                        <AlertTriangle size={14} />
                        SLA BREACH
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-semibold text-gray-800">{approval.related_model}</span>
                    <span className="text-sm text-gray-600">#{approval.related_id}</span>
                  </div>

                  <div className="text-sm text-gray-600">
                    Stage: {approval.current_stage.name} •
                    Updated: {getTimeSinceUpdate(approval.updated_at)}
                    {approval.current_stage.sla_hours && (
                      <> • SLA: {approval.current_stage.sla_hours}h</>
                    )}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprove(approval.id)}
                    className="bg-green-500 text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-green-600"
                  >
                    <CheckCircle size={18} />
                    Approve
                  </button>
                  <button
                    onClick={() => handleReject(approval.id)}
                    className="bg-red-500 text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-red-600"
                  >
                    <XCircle size={18} />
                    Reject
                  </button>
                  <button
                    onClick={() => navigate(`/workflows/instances/${approval.id}`)}
                    className="bg-gray-500 text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-gray-600"
                  >
                    <Eye size={18} />
                    Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}