import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

export default function DefectsView({ currentRole, onNavigateToTrace }) {
  const [defects, setDefects] = useState([]);
  const [selectedDefect, setSelectedDefect] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isContainmentModalOpen, setIsContainmentModalOpen] = useState(false);

  // Forms
  const [newDefect, setNewDefect] = useState({
    production_order_id: 'WO-2026-000012',
    process_execution_id: 'PEX-000058',
    inspection_result_id: 'INSP-WO-2026-000012-001',
    machine_id: 'MCH-0009',
    reported_material_lot_id: 'LOT-SUP-0003-2026-000063',
    defect_code: 'ERR-MANUAL-001',
    defect_category: 'DIMENSIONAL',
    severity: 'MAJOR',
    defect_quantity: 1.0,
    suspected_source: 'MACHINE',
    reason_code: 'RC_DEFECT_DISCOVERED',
    event_notes: '',
  });

  const [containmentData, setContainmentData] = useState({
    action_type: 'QUARANTINE_LOT',
    affected_quantity: 1.0,
    notes: '',
  });

  const [actionError, setActionError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadDefects();
  }, [filterSeverity, filterStatus]);

  async function loadDefects() {
    try {
      setLoading(true);
      const params = {};
      if (filterSeverity) params.severity = filterSeverity;
      if (filterStatus) params.status = filterStatus;
      const data = await api.getDefects(params);
      setDefects(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function openDefectDetail(defectId) {
    try {
      const detail = await api.getDefect(defectId);
      setSelectedDefect(detail);
    } catch (err) {
      alert(`Error loading defect detail: ${err.message}`);
    }
  }

  async function handleCreateDefect(e) {
    e.preventDefault();
    try {
      setSubmitting(true);
      setActionError(null);
      await api.createDefect({
        ...newDefect,
        defect_quantity: parseFloat(newDefect.defect_quantity),
        actor_role: currentRole,
      });
      setIsCreateModalOpen(false);
      loadDefects();
    } catch (err) {
      setActionError(err.message || 'Failed to create defect');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeployContainment(e) {
    e.preventDefault();
    if (!selectedDefect) return;
    try {
      setSubmitting(true);
      setActionError(null);
      await api.createContainmentAction({
        defect_id: selectedDefect.defect_id,
        action_type: containmentData.action_type,
        owner_role: currentRole,
        affected_quantity: parseFloat(containmentData.affected_quantity),
        notes: containmentData.notes,
        reason_code: 'RC_IMMEDIATE_QUARANTINE',
      });
      setIsContainmentModalOpen(false);
      // Reload defect details
      await openDefectDetail(selectedDefect.defect_id);
      loadDefects();
    } catch (err) {
      setActionError(err.message || 'Failed to deploy containment action');
    } finally {
      setSubmitting(false);
    }
  }

  const canCreate = currentRole === 'PLANT_OPERATOR' || currentRole === 'QUALITY_ENGINEER';
  const canContain = currentRole === 'QUALITY_ENGINEER' || currentRole === 'PLANT_OPERATOR';

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Manufacturing Defect Log & Containment Console</h2>
          <p className="view-subtitle">
            Inspect defects from inspection gates, deploy immediate containment, and launch root-cause traces.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          {canCreate && (
            <button className="btn btn-primary" onClick={() => setIsCreateModalOpen(true)}>
              + Log New Defect
            </button>
          )}
          <button className="btn btn-secondary" onClick={loadDefects}>Refresh</button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <label className="filter-label">Filter Severity:</label>
          <select
            className="filter-select"
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="MAJOR">Major</option>
            <option value="MINOR">Minor</option>
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Filter Status:</label>
          <select
            className="filter-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="CONTAINED">Contained</option>
            <option value="UNDER_INVESTIGATION">Under Investigation</option>
            <option value="CAPA_IN_PROGRESS">CAPA In Progress</option>
            <option value="VERIFIED">Verified</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>

        <div className="filter-info">
          Showing <strong>{defects.length}</strong> recorded defects
        </div>
      </div>

      {/* Defects Table */}
      <div className="card">
        {loading ? (
          <div className="loading-state">Loading defects from database...</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Defect ID</th>
                  <th>Defect Code</th>
                  <th>Category</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Qty</th>
                  <th>Order ID</th>
                  <th>Machine</th>
                  <th>Reported Lot</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {defects.map((d) => (
                  <tr key={d.defect_id} className={d.severity === 'CRITICAL' ? 'row-highlight-critical' : ''}>
                    <td className="font-mono"><strong>{d.defect_id}</strong></td>
                    <td>{d.defect_code}</td>
                    <td><span className="badge badge-slate">{d.defect_category}</span></td>
                    <td><Badge label={d.severity} /></td>
                    <td><Badge label={d.defect_status} /></td>
                    <td>{d.defect_quantity}</td>
                    <td className="font-mono">{d.production_order_id}</td>
                    <td className="font-mono">{d.machine_id}</td>
                    <td className="font-mono">{d.reported_material_lot_id}</td>
                    <td>
                      <div className="action-buttons-cell">
                        <button
                          className="btn-sm btn-secondary"
                          onClick={() => openDefectDetail(d.defect_id)}
                        >
                          Details
                        </button>
                        <button
                          className="btn-sm btn-primary"
                          onClick={() => onNavigateToTrace(d.defect_id)}
                        >
                          Trace Upstream
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Defect Detail Modal */}
      {selectedDefect && (
        <Modal
          isOpen={!!selectedDefect}
          onClose={() => setSelectedDefect(null)}
          title={`Defect Investigation: ${selectedDefect.defect_id}`}
        >
          <div className="modal-detail-grid">
            <div className="detail-item">
              <span className="detail-label">Defect Code</span>
              <span className="detail-value">{selectedDefect.defect_code}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Category</span>
              <span className="detail-value">{selectedDefect.defect_category}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Severity</span>
              <span className="detail-value"><Badge label={selectedDefect.severity} /></span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Status</span>
              <span className="detail-value"><Badge label={selectedDefect.defect_status} /></span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Product Name</span>
              <span className="detail-value">{selectedDefect.product_name || selectedDefect.product_id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Machine Station</span>
              <span className="detail-value">{selectedDefect.machine_name} ({selectedDefect.machine_id})</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Production Order</span>
              <span className="detail-value font-mono">{selectedDefect.production_order_id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Inspection Gate</span>
              <span className="detail-value font-mono">{selectedDefect.inspection_result_id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Reported Material Lot</span>
              <span className="detail-value font-mono">{selectedDefect.reported_material_lot_id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Suspected Source</span>
              <span className="detail-value">{selectedDefect.suspected_source}</span>
            </div>
          </div>

          <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                Linked Containment Actions: <strong>{selectedDefect.containment_actions_count}</strong> |
                Active CAPAs: <strong>{selectedDefect.corrective_actions_count}</strong>
              </span>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {canContain && selectedDefect.defect_status === 'OPEN' && (
                <button
                  className="btn btn-warning"
                  onClick={() => setIsContainmentModalOpen(true)}
                >
                  Deploy Containment Action
                </button>
              )}
              <button
                className="btn btn-primary"
                onClick={() => {
                  const id = selectedDefect.defect_id;
                  setSelectedDefect(null);
                  onNavigateToTrace(id);
                }}
              >
                Launch Upstream Root-Cause Trace
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Deploy Containment Modal */}
      <Modal
        isOpen={isContainmentModalOpen}
        onClose={() => setIsContainmentModalOpen(false)}
        title={`Deploy Containment: ${selectedDefect?.defect_id}`}
      >
        <form onSubmit={handleDeployContainment}>
          {actionError && <div className="error-banner">{actionError}</div>}
          <div className="form-group">
            <label className="form-label">Containment Action Type</label>
            <select
              className="form-control"
              value={containmentData.action_type}
              onChange={(e) => setContainmentData({ ...containmentData, action_type: e.target.value })}
            >
              <option value="QUARANTINE_LOT">QUARANTINE LOT (Hold raw material & WIP)</option>
              <option value="STOP_LINE">STOP LINE (Halt execution station)</option>
              <option value="SORT_INVENTORY">SORT INVENTORY (100% sort warehouse stock)</option>
              <option value="REWORK_WIP">REWORK WIP (Route rejected parts to rework)</option>
              <option value="NOTIFY_SUPPLIER">NOTIFY SUPPLIER (Issue supplier quarantine notice)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Affected Quantity</label>
            <input
              type="number"
              step="0.01"
              min="0"
              className="form-control"
              value={containmentData.affected_quantity}
              onChange={(e) => setContainmentData({ ...containmentData, affected_quantity: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Containment Rationale & Execution Notes</label>
            <textarea
              className="form-control"
              rows="3"
              value={containmentData.notes}
              onChange={(e) => setContainmentData({ ...containmentData, notes: e.target.value })}
              placeholder="Enter quarantine batch IDs, holding pallet numbers, or line shutdown details..."
              required
            ></textarea>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setIsContainmentModalOpen(false)}
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Applying...' : 'Enforce Containment & Append StateEvent'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Log Defect Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Log New Defect (Inspection Gate)"
      >
        <form onSubmit={handleCreateDefect}>
          {actionError && <div className="error-banner">{actionError}</div>}
          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label">Production Order ID</label>
              <input
                type="text"
                className="form-control"
                value={newDefect.production_order_id}
                onChange={(e) => setNewDefect({ ...newDefect, production_order_id: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Inspection Gate ID</label>
              <input
                type="text"
                className="form-control"
                value={newDefect.inspection_result_id}
                onChange={(e) => setNewDefect({ ...newDefect, inspection_result_id: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Process Execution ID</label>
              <input
                type="text"
                className="form-control"
                value={newDefect.process_execution_id}
                onChange={(e) => setNewDefect({ ...newDefect, process_execution_id: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Machine Station ID</label>
              <input
                type="text"
                className="form-control"
                value={newDefect.machine_id}
                onChange={(e) => setNewDefect({ ...newDefect, machine_id: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Reported Material Lot ID</label>
              <input
                type="text"
                className="form-control"
                value={newDefect.reported_material_lot_id}
                onChange={(e) => setNewDefect({ ...newDefect, reported_material_lot_id: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Defect Code</label>
              <input
                type="text"
                className="form-control"
                value={newDefect.defect_code}
                onChange={(e) => setNewDefect({ ...newDefect, defect_code: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Category</label>
              <select
                className="form-control"
                value={newDefect.defect_category}
                onChange={(e) => setNewDefect({ ...newDefect, defect_category: e.target.value })}
              >
                <option value="DIMENSIONAL">DIMENSIONAL</option>
                <option value="SURFACE_FINISH">SURFACE_FINISH</option>
                <option value="ELECTRICAL">ELECTRICAL</option>
                <option value="CONTAMINATION">CONTAMINATION</option>
                <option value="ASSEMBLY_ALIGNMENT">ASSEMBLY_ALIGNMENT</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Severity</label>
              <select
                className="form-control"
                value={newDefect.severity}
                onChange={(e) => setNewDefect({ ...newDefect, severity: e.target.value })}
              >
                <option value="CRITICAL">CRITICAL</option>
                <option value="MAJOR">MAJOR</option>
                <option value="MINOR">MINOR</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Defect Quantity</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                className="form-control"
                value={newDefect.defect_quantity}
                onChange={(e) => setNewDefect({ ...newDefect, defect_quantity: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Suspected Source</label>
              <select
                className="form-control"
                value={newDefect.suspected_source}
                onChange={(e) => setNewDefect({ ...newDefect, suspected_source: e.target.value })}
              >
                <option value="MACHINE">MACHINE</option>
                <option value="MATERIAL">MATERIAL</option>
                <option value="OPERATOR">OPERATOR</option>
                <option value="METHOD">METHOD</option>
                <option value="ENVIRONMENT">ENVIRONMENT</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Inspection Notes</label>
            <textarea
              className="form-control"
              rows="2"
              value={newDefect.event_notes}
              onChange={(e) => setNewDefect({ ...newDefect, event_notes: e.target.value })}
              placeholder="Optical micrometer out-of-tolerance readings, visual crack description..."
            ></textarea>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setIsCreateModalOpen(false)}
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Registering...' : 'Register Defect & Append StateEvent'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

