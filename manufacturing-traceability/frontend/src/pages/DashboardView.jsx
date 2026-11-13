import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import MetricCard from '../components/MetricCard';
import Badge from '../components/Badge';

export default function DashboardView({ onNavigateToDefects, onNavigateToTrace }) {
  const [metrics, setMetrics] = useState(null);
  const [drift, setDrift] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);
      const [metricsData, driftData] = await Promise.all([
        api.getDashboardMetrics(),
        api.getMachineDrift(),
      ]);
      setMetrics(metricsData);
      setDrift(driftData);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="loading-state">Loading manufacturing telemetry & quality metrics...</div>;
  if (error) return <div className="error-banner">Error loading metrics: {error}</div>;
  if (!metrics) return null;

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Quality & Traceability Executive Dashboard</h2>
          <p className="view-subtitle">High-level quality KPIs, defect trends, and machine drift indicators.</p>
        </div>
        <button className="btn btn-secondary" onClick={loadData}>Refresh Telemetry</button>
      </div>

      {/* KPI Cards Row */}
      <div className="metric-cards-grid">
        <MetricCard
          title="Total Production Orders"
          value={metrics.total_production_orders}
          subtitle={`${metrics.completed_production_orders} Completed Orders`}
        />
        <MetricCard
          title="Total Defects Discovered"
          value={metrics.total_defects}
          subtitle={`${metrics.open_defects} Currently Open`}
          alert={metrics.open_defects > 0}
        />
        <MetricCard
          title="Critical Severity Defects"
          value={metrics.critical_defects}
          subtitle="Immediate quarantine priority"
          alert={metrics.critical_defects > 0}
        />
        <MetricCard
          title="Overall Defect Rate"
          value={`${(metrics.overall_defect_rate * 100).toFixed(2)}%`}
          subtitle={`Across ${metrics.total_inspections} Quality Inspections`}
        />
        <MetricCard
          title="Active Containment Actions"
          value={metrics.active_containments}
          subtitle="Quarantined lots & line stops"
        />
        <MetricCard
          title="Open CAPAs"
          value={metrics.open_capas}
          subtitle={`${metrics.pending_verifications} Pending Verification`}
        />
      </div>

      {/* Breakdowns Row */}
      <div className="dashboard-grid-2col">
        {/* Severity Distribution */}
        <div className="card">
          <h3 className="card-title">Defect Distribution by Severity</h3>
          <div className="distribution-bars">
            {Object.entries(metrics.defects_by_severity || {}).map(([sev, count]) => {
              const pct = metrics.total_defects ? ((count / metrics.total_defects) * 100).toFixed(1) : 0;
              return (
                <div key={sev} className="distribution-row">
                  <div className="dist-label">
                    <Badge label={sev} />
                    <span>{count} occurrences ({pct}%)</span>
                  </div>
                  <div className="dist-bar-bg">
                    <div
                      className={`dist-bar-fill fill-${sev.toLowerCase()}`}
                      style={{ width: `${pct}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Category Distribution */}
        <div className="card">
          <h3 className="card-title">Defect Distribution by Root Category</h3>
          <div className="distribution-bars">
            {Object.entries(metrics.defects_by_category || {}).map(([cat, count]) => {
              const pct = metrics.total_defects ? ((count / metrics.total_defects) * 100).toFixed(1) : 0;
              return (
                <div key={cat} className="distribution-row">
                  <div className="dist-label">
                    <span className="cat-name">{cat.replace(/_/g, ' ')}</span>
                    <span>{count} ({pct}%)</span>
                  </div>
                  <div className="dist-bar-bg">
                    <div
                      className="dist-bar-fill fill-blue"
                      style={{ width: `${pct}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Machine Drift & Quality Table */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header-flex">
          <div>
            <h3 className="card-title">Machine Defect Rate & Calibration Drift Analysis</h3>
            <p className="card-subtitle">
              Calculates defect rate per execution. High rates indicate mechanical wear or calibration drift.
            </p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Machine ID</th>
                <th>Machine Name</th>
                <th>Machine Type</th>
                <th>Operational Status</th>
                <th>Maintenance Risk</th>
                <th>Total Executions</th>
                <th>Linked Defects</th>
                <th>Defect Rate</th>
              </tr>
            </thead>
            <tbody>
              {drift.map((m) => (
                <tr key={m.machine_id} className={m.defect_rate > 0.05 ? 'row-highlight-warn' : ''}>
                  <td className="font-mono"><strong>{m.machine_id}</strong></td>
                  <td>{m.machine_name}</td>
                  <td><span className="badge badge-slate">{m.machine_type}</span></td>
                  <td><Badge label={m.machine_status} /></td>
                  <td>
                    <div className="risk-indicator">
                      <span>{m.maintenance_risk_score.toFixed(1)}</span>
                      <div className="risk-pill-bar">
                        <div
                          className={`risk-fill ${m.maintenance_risk_score > 50 ? 'risk-high' : 'risk-normal'}`}
                          style={{ width: `${Math.min(100, m.maintenance_risk_score)}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td>{m.total_process_executions}</td>
                  <td><strong>{m.total_defects}</strong></td>
                  <td>
                    <span className={`font-mono ${m.defect_rate > 0 ? 'text-warn' : ''}`}>
                      {(m.defect_rate * 100).toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

