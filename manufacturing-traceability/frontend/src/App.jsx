import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DashboardView from './pages/DashboardView';
import DefectsView from './pages/DefectsView';
import TraceabilityView from './pages/TraceabilityView';
import OrdersView from './pages/OrdersView';
import LotsView from './pages/LotsView';
import CAPAView from './pages/CAPAView';
import AdminView from './pages/AdminView';
import { api } from './api/client';

export default function App() {
  const [currentRole, setCurrentRole] = useState('QUALITY_ENGINEER');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [health, setHealth] = useState(null);

  // Cross-view navigation state
  const [traceDefectId, setTraceDefectId] = useState(null);
  const [traceLotId, setTraceLotId] = useState(null);

  useEffect(() => {
    api.getHealth()
      .then((data) => setHealth(data))
      .catch((err) => console.error('API health check error:', err));
  }, []);

  // When role changes, switch to their primary tab if not already on an allowed tab
  const handleRoleChange = (newRole) => {
    setCurrentRole(newRole);
    if (newRole === 'PLANT_OPERATOR' && (activeTab === 'admin' || activeTab === 'capas')) {
      setActiveTab('orders');
    } else if (newRole === 'PRODUCTION_PLANNER' && (activeTab === 'admin' || activeTab === 'capas')) {
      setActiveTab('orders');
    } else if (newRole === 'IT_ADMIN' && activeTab === 'capas') {
      setActiveTab('admin');
    }
  };

  const handleNavigateToTrace = (defectId) => {
    setTraceDefectId(defectId);
    setTraceLotId(null);
    setActiveTab('traceability');
  };

  const handleNavigateToBlastRadius = (lotId) => {
    setTraceLotId(lotId);
    setTraceDefectId(null);
    setActiveTab('traceability');
  };

  return (
    <div className="app-layout">
      <Header currentRole={currentRole} onRoleChange={handleRoleChange} health={health} />

      {/* Main Navigation Bar */}
      <nav className="main-nav-bar">
        <div className="container nav-tabs-container">
          <button
            className={`nav-tab-btn ${activeTab === 'dashboard' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Executive Dashboard
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'defects' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('defects')}
          >
            Defects & Containment
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'traceability' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('traceability')}
          >
            Traceability Workbench
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'orders' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('orders')}
          >
            Production & BOM
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'lots' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('lots')}
          >
            Material Lots
          </button>

          {(currentRole === 'QUALITY_ENGINEER' || currentRole === 'IT_ADMIN') && (
            <button
              className={`nav-tab-btn ${activeTab === 'capas' ? 'nav-tab-active' : ''}`}
              onClick={() => setActiveTab('capas')}
            >
              Corrective Actions (CAPA)
            </button>
          )}

          {currentRole === 'IT_ADMIN' && (
            <button
              className={`nav-tab-btn ${activeTab === 'admin' ? 'nav-tab-active' : ''}`}
              onClick={() => setActiveTab('admin')}
            >
              OT / IT System Integrity
            </button>
          )}
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="container app-content">
        {activeTab === 'dashboard' && (
          <DashboardView
            onNavigateToDefects={() => setActiveTab('defects')}
            onNavigateToTrace={handleNavigateToTrace}
          />
        )}
        {activeTab === 'defects' && (
          <DefectsView
            currentRole={currentRole}
            onNavigateToTrace={handleNavigateToTrace}
          />
        )}
        {activeTab === 'traceability' && (
          <TraceabilityView
            initialDefectId={traceDefectId}
            initialLotId={traceLotId}
          />
        )}
        {activeTab === 'orders' && <OrdersView />}
        {activeTab === 'lots' && (
          <LotsView onNavigateToBlastRadius={handleNavigateToBlastRadius} />
        )}
        {activeTab === 'capas' && <CAPAView currentRole={currentRole} />}
        {activeTab === 'admin' && <AdminView health={health} />}
      </main>

      <footer className="app-footer">
        <div className="container footer-content">
          <span>TraceFlow // Deterministic Manufacturing Quality & Defect Traceability Engine</span>
          <span>Role-Based Demo Mode (Production Authentication Out of Scope)</span>
        </div>
      </footer>
    </div>
  );
}
