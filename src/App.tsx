import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from ' @tanstack/react-query';
import { ReactFlowProvider } from ' @xyflow/react';
import Layout from './components/Layout/Layout';
import WorkflowDashboard from './components/Dashboard/WorkflowDashboard';
import WorkflowDesigner from './components/WorkflowDesigner/WorkflowDesigner';
import WorkflowList from './components/Workflows/WorkflowList';
import ApprovalCenter from './components/Approvals/ApprovalCenter';
import ABACManager from './components/ABAC/ABACManager';
import './styles/WorkflowDesigner.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            {/* Dashboard */}
            <Route path="/" element={<WorkflowDashboard />} />
            
            {/* Workflows */}
            <Route path="/workflows" element={<WorkflowList />} />
            <Route 
              path="/workflows/design" 
              element={
                <ReactFlowProvider>
                  <WorkflowDesigner />
                </ReactFlowProvider>
              } 
            />
            <Route 
              path="/workflows/design/:workflowId" 
              element={
                <ReactFlowProvider>
                  <WorkflowDesigner />
                </ReactFlowProvider>
              } 
            />
            
            {/* Approvals */}
            <Route path="/approvals" element={<ApprovalCenter />} />
            <Route path="/approvals/:approvalId" element={<div>Approval Detail</div>} />
            
            {/* ABAC Management */}
            <Route path="/abac" element={<ABACManager />} />
            
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;