import React from 'react';
import { PanelLeft, MessageSquare, Settings } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

const SidebarItem = ({ icon: Icon, label, to, active }) => (
    <Link
        to={to}
        className={`btn btn-ghost ${active ? 'bg-surface-hover text-primary' : ''}`}
        style={{ justifyContent: 'flex-start', width: '100%', marginBottom: '0.25rem', color: active ? 'var(--color-primary)' : 'inherit' }}
    >
        <Icon size={18} />
        {label}
    </Link>
);

export const Layout = ({ children }) => {
    const location = useLocation();

    return (
        <div className="layout">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <PanelLeft size={24} style={{ marginRight: '0.5rem' }} />
                    Datasmith AI
                </div>
                <div className="sidebar-content">
                    <SidebarItem
                        icon={MessageSquare}
                        label="New Chat"
                        to="/"
                        active={location.pathname === '/' || location.pathname === ''}
                    />
                </div>
            </aside>
            <main className="main-content">
                <header className="header">
                    <h2 style={{ margin: 0, fontSize: '1.25rem' }}>
                        Datasmith AI
                    </h2>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>v1.0.0</span>
                    </div>
                </header>
                <div className="page-content">
                    {children}
                </div>
            </main>
        </div>
    );
};
