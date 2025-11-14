import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  BarChart3, 
  Workflow, 
  CheckSquare, 
  Shield, 
  Settings,
  User,
  LogOut
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Workflows', href: '/workflows', icon: Workflow },
    { name: 'Approvals', href: '/approvals', icon: CheckSquare },
    { name: 'ABAC Policies', href: '/abac', icon: Shield },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <Shield size={32} className="logo-icon" />
            <span className="logo-text">ERP Workflows</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`nav-item ${active ? 'nav-item-active' : ''}`}
              >
                <Icon size={20} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="user-menu">
            <div className="user-avatar">
              <User size={20} />
            </div>
            <div className="user-info">
              <div className="user-name">John Doe</div>
              <div className="user-role">Administrator</div>
            </div>
          </div>
          
          <div className="footer-actions">
            <button className="icon-btn" title="Settings">
              <Settings size={18} />
            </button>
            <button className="icon-btn" title="Logout">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
