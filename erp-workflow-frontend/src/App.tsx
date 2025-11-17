// =====================================================================
// FILE: src/App.tsx
// =====================================================================

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import WorkflowList from './components/WorkflowList/WorkflowList';
import WorkflowDesigner from './components/WorkflowDesigner/WorkflowDesigner';
import { ApprovalDashboard } from './components/Dashboard/ApprovalDashboard';



const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<ApprovalDashboard />} />
            <Route path="/workflows" element={<WorkflowList />} />
            <Route path="/workflows/designer" element={<WorkflowDesigner />} />
            <Route path="/workflows/designer/:workflowId" element={<WorkflowDesigner />} />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;