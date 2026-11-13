import React from 'react';

const ROLE_CONFIGS = {
  PLANT_OPERATOR: {
    label: 'Plant Operator',
    badge: 'badge-blue',
    description: 'Inspect production orders, active inspections, log defects, review rework & scrap.',
  },
  QUALITY_ENGINEER: {
    label: 'Maintenance / Quality Engineer',
    badge: 'badge-purple',
    description: 'Investigate defects, inspect machine context, deploy containment, verify & close CAPAs.',
  },
  PRODUCTION_PLANNER: {
    label: 'Production Planner',
    badge: 'badge-amber',
    description: 'Audit BOM reconciliation, trace material lots, and quantify downstream blast-radius impact.',
  },
  IT_ADMIN: {
    label: 'OT / IT Administrator',
    badge: 'badge-green',
    description: 'Run data integrity validation, inspect reproducibility manifests, review append-only audit trail.',
  },
};

export default function Header({ currentRole, onRoleChange, health }) {
  const currentConfig = ROLE_CONFIGS[currentRole] || ROLE_CONFIGS.QUALITY_ENGINEER;

  return (
    <header className="app-header">
      <div className="brand-group">
        <div className="logo-title">
          <span className="logo-icon font-mono">[TF]</span>
          <div>
            <h1 className="brand-title">TraceFlow &mdash; Manufacturing Defect Traceability</h1>
            <p className="brand-subtitle">
              Root-cause isolation, downstream blast radius, and audit trail
            </p>
          </div>
        </div>
        <div className="engine-meta">
          <span className="engine-badge">
            <span className="status-dot"></span> Online
          </span>
          <span className="seed-badge">Seed: {health?.seed || '20261022'}</span>
          <span className="profile-badge">Profile: {health?.profile || 'starter'}</span>
        </div>
      </div>

      <div className="role-selector-card">
        <div className="role-selector-row">
          <label htmlFor="role-select" className="role-label">Demo Role (Evaluation Only):</label>
          <select
            id="role-select"
            className="role-select"
            value={currentRole}
            onChange={(e) => onRoleChange(e.target.value)}
          >
            <option value="PLANT_OPERATOR">Plant Operator</option>
            <option value="QUALITY_ENGINEER">Maintenance / Quality Engineer</option>
            <option value="PRODUCTION_PLANNER">Production Planner</option>
            <option value="IT_ADMIN">OT / IT Administrator</option>
          </select>
        </div>
        <div className="role-description">
          <span className={`badge ${currentConfig.badge}`}>{currentConfig.label}</span>
          <span className="role-scope-text">{currentConfig.description}</span>
        </div>
      </div>
    </header>
  );
}

