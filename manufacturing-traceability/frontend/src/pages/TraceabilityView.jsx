import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import TraceGraph from '../components/TraceGraph';
import Badge from '../components/Badge';

export default function TraceabilityView({ initialDefectId, initialLotId }) {
  const [activeTab, setActiveTab] = useState(initialLotId ? 'downstream' : 'upstream');

  // Upstream state
  const [defectIdInput, setDefectIdInput] = useState(initialDefectId || 'DEF-2026-000001');
  const [upstreamData, setUpstreamData] = useState(null);
  const [upstreamLoading, setUpstreamLoading] = useState(false);
  const [upstreamError, setUpstreamError] = useState(null);

  // Downstream state
  const [lotIdInput, setLotIdInput] = useState(initialLotId || 'LOT-SUP-0003-2026-000063');
  const [downstreamData, setDownstreamData] = useState(null);
  const [downstreamLoading, setDownstreamLoading] = useState(false);
  const [downstreamError, setDownstreamError] = useState(null);

  useEffect(() => {
    if (initialDefectId) {
      setDefectIdInput(initialDefectId);
      loadUpstreamTrace(initialDefectId);
    } else {
      loadUpstreamTrace(defectIdInput);
    }
  }, [initialDefectId]);

  useEffect(() => {
    if (initialLotId) {
      setLotIdInput(initialLotId);
      loadDownstreamImpact(initialLotId);
    }
  }, [initialLotId]);

  async function loadUpstreamTrace(idToTrace) {
    const id = idToTrace || defectIdInput;
    if (!id) return;
    try {
      setUpstreamLoading(true);
      setUpstreamError(null);
      const data = await api.getUpstreamTrace(id);
      setUpstreamData(data);
    } catch (err) {
      setUpstreamError(err.message || `Failed to trace defect ${id}`);
    } finally {
      setUpstreamLoading(false);
    }
  }

  async function loadDownstreamImpact(idToTrace) {
    const id = idToTrace || lotIdInput;
    if (!id) return;
    try {
      setDownstreamLoading(true);
      setDownstreamError(null);
      const data = await api.getDownstreamImpact(id);
      setDownstreamData(data);
    } catch (err) {
      setDownstreamError(err.message || `Failed to trace lot impact for ${id}`);
    } finally {
      setDownstreamLoading(false);
    }
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Traceability Workbench & Blast-Radius Engine</h2>
          <p className="view-subtitle">
            Bidirectional lineage: Trace defects back to supplier lots, or isolate downstream blast radius of suspect materials.
          </p>
        </div>
      </div>

      {/* Trace Mode Tabs */}
      <div className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === 'upstream' ? 'tab-btn-active' : ''}`}
          onClick={() => setActiveTab('upstream')}
        >
          Upstream Defect-to-Supplier Root Cause Trace
        </button>
        <button
          className={`tab-btn ${activeTab === 'downstream' ? 'tab-btn-active' : ''}`}
          onClick={() => {
            setActiveTab('downstream');
            if (!downstreamData) loadDownstreamImpact(lotIdInput);
          }}
        >
          Downstream Material-Lot Blast-Radius Impact
        </button>
      </div>

      {/* Tab 1: Upstream Trace */}
      {activeTab === 'upstream' && (
        <div>
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                loadUpstreamTrace(defectIdInput);
              }}
              className="trace-search-bar"
            >
              <div className="search-field">
                <label className="search-label">Defect ID to Trace:</label>
                <input
                  type="text"
                  className="form-control font-mono"
                  value={defectIdInput}
                  onChange={(e) => setDefectIdInput(e.target.value)}
                  placeholder="e.g. DEF-2026-000001"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={upstreamLoading}>
                {upstreamLoading ? 'Tracing Lineage...' : 'Execute Upstream Trace'}
              </button>
            </form>
          </div>

          {upstreamError && <div className="error-banner">{upstreamError}</div>}

          {upstreamLoading && <div className="loading-state">Tracing defect backward through manufacturing lineage...</div>}

          {upstreamData && (
            <div className="card">
              <h3 className="card-title">Upstream Lineage Flow</h3>
              <TraceGraph type="upstream" data={upstreamData} />

              <div style={{ marginTop: '2rem' }}>
                <h4 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>
                  Consumed Raw Material Lots & Suppliers
                </h4>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Consumption ID</th>
                        <th>Material Lot ID</th>
                        <th>Raw Material</th>
                        <th>Supplier</th>
                        <th>Supplier Batch</th>
                        <th>Consumed Qty</th>
                        <th>Consumed At</th>
                        <th>Lot Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {upstreamData.consumed_lots?.map((c) => (
                        <tr key={c.consumption_id}>
                          <td className="font-mono">{c.consumption_id}</td>
                          <td className="font-mono"><strong>{c.material_lot_id}</strong></td>
                          <td>{c.material_product_name}</td>
                          <td><strong>{c.supplier_name}</strong> ({c.supplier_id})</td>
                          <td className="font-mono">{c.supplier_batch_code}</td>
                          <td>{c.consumed_quantity} {c.uom}</td>
                          <td className="font-mono">{new Date(c.consumed_at).toLocaleString()}</td>
                          <td><Badge label={c.lot_status} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Downstream Blast Radius Trace */}
      {activeTab === 'downstream' && (
        <div>
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                loadDownstreamImpact(lotIdInput);
              }}
              className="trace-search-bar"
            >
              <div className="search-field">
                <label className="search-label">Suspect Material Lot ID:</label>
                <input
                  type="text"
                  className="form-control font-mono"
                  value={lotIdInput}
                  onChange={(e) => setLotIdInput(e.target.value)}
                  placeholder="e.g. LOT-SUP-0003-2026-000063"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={downstreamLoading}>
                {downstreamLoading ? 'Analyzing Blast Radius...' : 'Analyze Downstream Impact'}
              </button>
            </form>
          </div>

          {downstreamError && <div className="error-banner">{downstreamError}</div>}

          {downstreamLoading && <div className="loading-state">Traversing consumption hierarchy & defect blast radius...</div>}

          {downstreamData && (
            <div className="card">
              <div className="card-header-flex">
                <div>
                  <h3 className="card-title">Blast-Radius Summary: {downstreamData.material_lot_id}</h3>
                  <p className="card-subtitle">
                    Supplier: <strong>{downstreamData.supplier_name}</strong> | Batch: <code>{downstreamData.supplier_batch_code}</code>
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <div className="blast-stat">
                    <span className="blast-num">{downstreamData.total_impacted_orders}</span>
                    <span className="blast-lbl">Impacted Orders</span>
                  </div>
                  <div className="blast-stat">
                    <span className={`blast-num ${downstreamData.total_defects_linked > 0 ? 'text-warn' : ''}`}>
                      {downstreamData.total_defects_linked}
                    </span>
                    <span className="blast-lbl">Linked Defects</span>
                  </div>
                </div>
              </div>

              <TraceGraph type="downstream" data={downstreamData} />

              <div style={{ marginTop: '2rem' }}>
                <h4 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>
                  Impacted Production Orders Detail
                </h4>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Production Order</th>
                        <th>Product ID</th>
                        <th>Product Name</th>
                        <th>Order Status</th>
                        <th>Lot Qty Consumed</th>
                        <th>Consumption Timestamp</th>
                        <th>Defects Count</th>
                        <th>Active Containments</th>
                      </tr>
                    </thead>
                    <tbody>
                      {downstreamData.impacted_orders?.map((po) => (
                        <tr key={po.production_order_id} className={po.defects_count > 0 ? 'row-highlight-warn' : ''}>
                          <td className="font-mono"><strong>{po.production_order_id}</strong></td>
                          <td className="font-mono">{po.product_id}</td>
                          <td>{po.product_name}</td>
                          <td><Badge label={po.order_status} /></td>
                          <td>{po.consumed_quantity} {po.consumption_uom}</td>
                          <td className="font-mono">{new Date(po.consumed_at).toLocaleString()}</td>
                          <td>
                            {po.defects_count > 0 ? (
                              <span className="badge badge-red">{po.defects_count} Defects</span>
                            ) : (
                              <span className="badge badge-green">0</span>
                            )}
                          </td>
                          <td>
                            {po.active_containments_count > 0 ? (
                              <span className="badge badge-amber">{po.active_containments_count} Active</span>
                            ) : (
                              <span className="badge badge-slate">0</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

