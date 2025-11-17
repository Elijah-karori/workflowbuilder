// =====================================================================
// FILE: src/services/api.ts
// =====================================================================

import axios, { type AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token interceptor
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add error interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Redirect to login
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Workflow Definitions
  async getWorkflows(params?: any) {
    return this.client.get('/api/v1/workflows', { params });
  }

  async getWorkflow(id: number) {
    return this.client.get(`/api/v1/workflows/${id}`);
  }

  async createWorkflowGraph(data: any) {
    return this.client.post('/api/v1/workflows/graph', data);
  }

  async updateWorkflowGraph(id: number, data: any) {
    return this.client.put(`/api/v1/workflows/${id}/graph`, data);
  }

  async publishWorkflow(id: number) {
    return this.client.post(`/api/v1/workflows/${id}/publish`);
  }

  async cloneWorkflow(id: number, newName: string) {
    return this.client.post(`/api/v1/workflows/${id}/clone`, { name: newName });
  }

  async deleteWorkflow(id: number) {
    return this.client.delete(`/api/v1/workflows/${id}`);
  }

  async getWorkflowVersions(id: number) {
    return this.client.get(`/api/v1/workflows/${id}/versions`);
  }

  // Workflow Instances
  async startWorkflow(data: any) {
    return this.client.post('/api/v1/workflows/start', data);
  }

  async getWorkflowInstance(id: number) {
    return this.client.get(`/api/v1/workflows/instances/${id}`);
  }

  async performWorkflowAction(instanceId: number, data: any) {
    return this.client.post(`/api/v1/workflows/instances/${instanceId}/actions`, data);
  }

  async getMyApprovals() {
    return this.client.get('/api/v1/workflows/my-approvals');
  }

  async getWorkflowStats() {
    return this.client.get('/api/v1/workflows/stats');
  }

  async testAuthorization(data: any) {
    return this.client.post('/api/v1/workflows/test-authorization', data);
  }

  // ABAC Policies
  async getABACPolicies(params?: any) {
    return this.client.get('/api/v1/abac/policies', { params });
  }

  async createABACPolicy(data: any) {
    return this.client.post('/api/v1/abac/policies', data);
  }

  async updateABACPolicy(id: number, data: any) {
    return this.client.put(`/api/v1/abac/policies/${id}`, data);
  }

  async deleteABACPolicy(id: number) {
    return this.client.delete(`/api/v1/abac/policies/${id}`);
  }

  async checkABACAccess(data: any) {
    return this.client.post('/api/v1/abac/check-access', data);
  }

  async getAuditLogs(params?: any) {
    return this.client.get('/api/v1/abac/audit-logs', { params });
  }

  // Users & Attributes
  async getUserAttributes(userId: number) {
    return this.client.get(`/api/v1/abac/users/${userId}/attributes`);
  }

  async updateUserAttributes(userId: number, data: any) {
    return this.client.put(`/api/v1/abac/users/${userId}/attributes`, data);
  }

  // Resources (Examples)
  async getInvoice(id: number) {
    return this.client.get(`/api/v1/invoices/${id}`);
  }

  async getInvoices(params?: any) {
    return this.client.get('/api/v1/invoices', { params });
  }
}

export const api = new APIService();