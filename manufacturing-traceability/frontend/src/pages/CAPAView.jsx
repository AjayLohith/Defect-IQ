import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

export default function CAPAView({ currentRole }) {
  const [capas, setCapas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCapa, setSelectedCapa] = useState(null);

  // Modals
  const [isVerifModalOpen, setIsVerifModalOpen] = useState(false);
  const [isCloseModalOpen, setIsCloseModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Form states
  const [verifData, setVerifData] = useState({
    verification_date: '2026-11-20',
    verification_method: 'STATISTICAL_SAMPLING',
    verification_result: 'PASSED',
    evidence_reference: 'DOC-QA-SPC-2026-001',
    notes: 'Sampled 125 consecutive parts after tooling insert replacement; 0 defects found.',
  });

  const [closeData, setCloseData] = useState({
    closure_notes: 'Formal closure after statistical verification confirmed zero recurrence.',
  });

  const [newCapaData, setNewCapaData] = useState({
    defect_id: 'DEF-2026-000001',
    root_cause_category: 'TOOLING_WEAR',
    root_cause_description: 'End mill carbide insert micro-fracture during high-feed finishing.',
    due_date: '2026-12-15',
    effectiveness_target: 'Zero surface finish defects over next 30 days',
  });

  const [actionError, setActionError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadCAPAs();
  }, []);

  async function loadCAPAs() {
    try {
      setLoading(true);
      const data = await api.getCAPAs();
      setCapas(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function openVerifications(capaId) {
    try {
      const detail = await api.getCAPA(capaId);
      setSelectedCapa(detail);
    } catch (err) {
      alert(`Error loading CAPA details: ${err.message}`);
    }
  }

  async function handleAddVerification(e) {
    e.preventDefault();
    if (!selectedCapa) return;
    try {
      setSubmitting(true);
      setActionError(null);
      await api.addVerification(selectedCapa.corrective_action_id, {
        ...verifData,
        verified_by_role: currentRole,
      });
      setIsVerifModalOpen(false);
      // Reload detail
      const updated = await api.getCAPA(selectedCapa.corrective_action_id);
      setSelectedCapa(updated);
      loadCAPAs();
    } catch (err) {
      setActionError(err.message || 'Failed to record verification');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCloseCAPA(e) {
    e.preventDefault();
    if (!selectedCapa) return;
    try {
      setSubmitting(true);
      setActionError(null);
      await api.closeCAPA(selectedCapa.corrective_action_id, {
        actor_role: currentRole,
        closure_notes: closeData.closure_notes,
      });
      setIsCloseModalOpen(false);
      const updated = await api.getCAPA(selectedCapa.corrective_action_id);
      setSelectedCapa(updated);
      loadCAPAs();
    } catch (err) {
      // Capture 422 ERR_CAPA_VERIFICATION_REQUIRED and display formatted message
      setActionError(err.message || 'Failed to close CAPA');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateCAPA(e) {
    e.preventDefault();
    try {
      setSubmitting(true);
      setActionError(null);
      await api.createCAPA({
        ...newCapaData,
        owner_role: currentRole,
        actor_role: currentRole,
      });
      setIsCreateModalOpen(false);
      loadCAPAs();
    } catch (err) {
      setActionError(err.message || 'Failed to create CAPA');
    } finally {
      setSubmitting(false);
    }
  }

  const isQE = currentRole === 'QUALITY_ENGINEER';

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Corrective & Preventive Action (CAPA) Workflow</h2>
          <p className="view-subtitle">
            Enforce compliance: CAPA closure strictly requires at least one passing effectiveness verification.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          {isQE && (
            <button className="btn btn-primary" onClick={() => setIsCreateModalOpen(true)}>
              + Initiate New CAPA
            </button>
          )}
          <button className="btn btn-secondary" onClick={loadCAPAs}>Refresh CAPAs</button>
        </div>
      </div>

      {/* CAPA Table */}
      <div className="card">
        {loading ? (
          <div className="loading-state">Loading corrective action registry...</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>CAPA ID</th>
                  <th>Defect ID</th>
                  <th>Root Cause Category</th>
                  <th>Status</th>
                  <th>Due Date</th>
                  <th>Verifications</th>
                  <th>Passed Verification</th>
                  <th>Readiness</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {capas.map((c) => (
                  <tr key={c.corrective_action_id}>
                    <td className="font-mono"><strong>{c.corrective_action_id}</strong></td>
                    <td className="font-mono">{c.defect_id}</td>
                    <td><span className="badge badge-slate">{c.root_cause_category}</span></td>
                    <td><Badge label={c.corrective_action_status} /></td>
                    <td className="font-mono">{c.due_date}</td>
                    <td>
                      <span className="badge badge-slate">{c.verifications?.length || 0} Records</span>
                    </td>
                    <td>
                      {c.has_passed_verification ? (
                        <span className="badge badge-green">YES (Passed)</span>
                      ) : (
                        <span className="badge badge-amber">PENDING</span>
                      )}
                    </td>
                    <td>
                      {c.corrective_action_status === 'CLOSED' ? (
                        <span className="badge badge-slate">CLOSED</span>
                      ) : c.ready_for_closure ? (
                        <span className="badge badge-green">READY FOR CLOSURE</span>
                      ) : (
                        <span className="badge badge-amber">VERIFICATION REQUIRED</span>
                      )}
                    </td>
                    <td>
                      <div className="action-buttons-cell">
                        <button
                          className="btn-sm btn-secondary"
                          onClick={() => openVerifications(c.corrective_action_id)}
                        >
                          Verifications & Audit
                        </button>
                        {isQE && c.corrective_action_status !== 'CLOSED' && (
                          <button
                            className={`btn-sm ${c.has_passed_verification ? 'btn-primary' : 'btn-warning'}`}
                            onClick={() => {
                              setSelectedCapa(c);
                              setActionError(null);
                              setIsCloseModalOpen(true);
                            }}
                          >
                            Close CAPA
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* CAPA Detail / Verifications Modal */}
      {selectedCapa && (
        <Modal
          isOpen={!!selectedCapa && !isVerifModalOpen && !isCloseModalOpen}
          onClose={() => setSelectedCapa(null)}
          title={`CAPA Audit & Verifications: ${selectedCapa.corrective_action_id}`}
        >
          <div className="modal-detail-grid">
            <div className="detail-item">
              <span className="detail-label">Status</span>
              <span className="detail-value"><Badge label={selectedCapa.corrective_action_status} /></span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Linked Defect</span>
              <span className="detail-value font-mono">{selectedCapa.defect_id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Root Cause Category</span>
              <span className="detail-value">{selectedCapa.root_cause_category}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Effectiveness Target</span>
              <span className="detail-value">{selectedCapa.effectiveness_target}</span>
            </div>
          </div>

          <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--bg-tertiary)', borderRadius: '6px' }}>
            <span className="detail-label">Root Cause Investigation Description</span>
            <p style={{ marginTop: '0.25rem', fontSize: '0.9rem' }}>{selectedCapa.root_cause_description}</p>
          </div>

          <div style={{ marginTop: '1.5rem' }}>
            <div className="card-header-flex">
              <h4 style={{ fontSize: '1rem', color: 'var(--text-primary)' }}>
                Effectiveness Verifications ({selectedCapa.verifications?.length || 0})
              </h4>
              {isQE && selectedCapa.corrective_action_status !== 'CLOSED' && (
                <button
                  className="btn-sm btn-primary"
                  onClick={() => {
                    setActionError(null);
                    setIsVerifModalOpen(true);
                  }}
                >
                  + Record Verification
                </button>
              )}
            </div>

            {selectedCapa.verifications?.length === 0 ? (
              <div className="node-empty" style={{ margin: '1rem 0' }}>
                No effectiveness verifications recorded yet. Closure is blocked until a PASSED verification exists.
              </div>
            ) : (
              <div className="table-responsive" style={{ marginTop: '0.5rem' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Verification ID</th>
                      <th>Date</th>
                      <th>Method</th>
                      <th>Result</th>
                      <th>Evidence Document</th>
                      <th>Verified By</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedCapa.verifications.map((v) => (
                      <tr key={v.verification_id}>
                        <td className="font-mono"><strong>{v.verification_id}</strong></td>
                        <td className="font-mono">{v.verification_date}</td>
                        <td><span className="badge badge-slate">{v.verification_method}</span></td>
                        <td><Badge label={v.verification_result} /></td>
                        <td className="font-mono">{v.evidence_reference}</td>
                        <td>{v.verified_by_role}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Add Verification Modal */}
      <Modal
        isOpen={isVerifModalOpen}
        onClose={() => setIsVerifModalOpen(false)}
        title={`Add Verification: ${selectedCapa?.corrective_action_id}`}
      >
        <form onSubmit={handleAddVerification}>
          {actionError && <div className="error-banner">{actionError}</div>}
          <div className="form-group">
            <label className="form-label">Verification Method</label>
            <select
              className="form-control"
              value={verifData.verification_method}
              onChange={(e) => setVerifData({ ...verifData, verification_method: e.target.value })}
            >
              <option value="AUDIT_CHECK">AUDIT CHECK (Physical inspection of countermeasure)</option>
              <option value="STATISTICAL_SAMPLING">STATISTICAL SAMPLING (Sample lot testing)</option>
              <option value="CAPABILITY_STUDY">CAPABILITY STUDY (Cpk study across production)</option>
              <option value="SPC_MONITORING">SPC MONITORING (Statistical Process Control chart audit)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Verification Outcome</label>
            <select
              className="form-control"
              value={verifData.verification_result}
              onChange={(e) => setVerifData({ ...verifData, verification_result: e.target.value })}
            >
              <option value="PASSED">PASSED (Countermeasure effective; enables closure)</option>
              <option value="FAILED">FAILED (Defect recurred; closure remains blocked)</option>
              <option value="INCONCLUSIVE">INCONCLUSIVE (Further run data required)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Evidence Document Reference</label>
            <input
              type="text"
              className="form-control font-mono"
              value={verifData.evidence_reference}
              onChange={(e) => setVerifData({ ...verifData, evidence_reference: e.target.value })}
              placeholder="e.g. DOC-SPC-2026-0042"
              required
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setIsVerifModalOpen(false)}
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Recording...' : 'Commit Verification Record'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Close CAPA Modal */}
      <Modal
        isOpen={isCloseModalOpen}
        onClose={() => setIsCloseModalOpen(false)}
        title={`Close CAPA: ${selectedCapa?.corrective_action_id}`}
      >
        <form onSubmit={handleCloseCAPA}>
          {actionError && <div className="error-banner">{actionError}</div>}

          {!selectedCapa?.has_passed_verification ? (
            <div className="warning-banner" style={{ marginBottom: '1rem' }}>
              <strong>Mandatory Compliance Warning:</strong>
              <p style={{ marginTop: '0.25rem', fontSize: '0.875rem' }}>
                This CAPA does NOT have a PASSED verification record. The backend validation rule will strictly reject closure
                with HTTP 422 (<code>ERR_CAPA_VERIFICATION_REQUIRED</code>). You must record a passing verification first.
              </p>
            </div>
          ) : (
            <div className="success-banner" style={{ marginBottom: '1rem' }}>
              <strong>Ready for Formal Closure:</strong>
              <p style={{ marginTop: '0.25rem', fontSize: '0.875rem' }}>
                A passing verification record is present. Proceeding will formally transition status to CLOSED and append a StateEvent.
              </p>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Formal Closure Sign-Off Notes</label>
            <textarea
              className="form-control"
              rows="3"
              value={closeData.closure_notes}
              onChange={(e) => setCloseData({ ...closeData, closure_notes: e.target.value })}
              placeholder="Sign-off comments, residual risk assessment, archiving reference..."
              required
            ></textarea>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setIsCloseModalOpen(false)}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`btn ${selectedCapa?.has_passed_verification ? 'btn-primary' : 'btn-danger'}`}
              disabled={submitting}
            >
              {submitting ? 'Validating & Closing...' : 'Submit Closure Request'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Create New CAPA Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Initiate New Corrective Action (CAPA)"
      >
        <form onSubmit={handleCreateCAPA}>
          {actionError && <div className="error-banner">{actionError}</div>}
          <div className="form-group">
            <label className="form-label">Defect ID</label>
            <input
              type="text"
              className="form-control font-mono"
              value={newCapaData.defect_id}
              onChange={(e) => setNewCapaData({ ...newCapaData, defect_id: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Root Cause Category</label>
            <select
              className="form-control"
              value={newCapaData.root_cause_category}
              onChange={(e) => setNewCapaData({ ...newCapaData, root_cause_category: e.target.value })}
            >
              <option value="TOOLING_WEAR">TOOLING WEAR</option>
              <option value="CALIBRATION_DRIFT">CALIBRATION DRIFT</option>
              <option value="SETUP_ERROR">SETUP ERROR</option>
              <option value="SUPPLIER_QUALITY">SUPPLIER QUALITY</option>
              <option value="PROCEDURAL_OMISSION">PROCEDURAL OMISSION</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Target Completion Due Date</label>
            <input
              type="date"
              className="form-control font-mono"
              value={newCapaData.due_date}
              onChange={(e) => setNewCapaData({ ...newCapaData, due_date: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Root Cause Investigation Description</label>
            <textarea
              className="form-control"
              rows="3"
              value={newCapaData.root_cause_description}
              onChange={(e) => setNewCapaData({ ...newCapaData, root_cause_description: e.target.value })}
              placeholder="5-Why analysis outcome, technical root cause details..."
              required
            ></textarea>
          </div>

          <div className="form-group">
            <label className="form-label">Effectiveness Target Criteria</label>
            <input
              type="text"
              className="form-control"
              value={newCapaData.effectiveness_target}
              onChange={(e) => setNewCapaData({ ...newCapaData, effectiveness_target: e.target.value })}
              placeholder="e.g. Zero recurrence over next 50 production units"
              required
            />
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
              {submitting ? 'Initiating...' : 'Initiate CAPA & Append StateEvent'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

