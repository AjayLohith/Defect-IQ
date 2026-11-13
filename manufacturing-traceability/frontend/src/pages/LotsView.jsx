import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import Badge from '../components/Badge';

export default function LotsView({ onNavigateToBlastRadius }) {
  const [lots, setLots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    loadLots();
  }, [filterStatus]);

  async function loadLots() {
    try {
      setLoading(true);
      const params = {};
      if (filterStatus) params.status = filterStatus;
      const data = await api.getLots(params);
      setLots(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Raw Material Lots & Inventory Balances</h2>
          <p className="view-subtitle">
            Inspect supplier material lots, batch traceability codes, balance depletion, and incoming quality scores.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadLots}>Refresh Lots</button>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <label className="filter-label">Filter Lot Status:</label>
          <select
            className="filter-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="RELEASED">Released</option>
            <option value="PARTIALLY_CONSUMED">Partially Consumed</option>
            <option value="CONSUMED">Consumed</option>
            <option value="QUARANTINED">Quarantined</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>
        <div className="filter-info">
          Showing <strong>{lots.length}</strong> material lots
        </div>
      </div>

      {/* Lots Table */}
      <div className="card">
        {loading ? (
          <div className="loading-state">Loading material lots from database...</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Material Lot ID</th>
                  <th>Supplier Batch</th>
                  <th>Supplier ID</th>
                  <th>Status</th>
                  <th>Received Qty</th>
                  <th>Available Qty</th>
                  <th>Consumed Qty</th>
                  <th>Quarantined Qty</th>
                  <th>Quality Score</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {lots.map((lot) => (
                  <tr key={lot.material_lot_id}>
                    <td className="font-mono"><strong>{lot.material_lot_id}</strong></td>
                    <td className="font-mono">{lot.supplier_batch_code}</td>
                    <td className="font-mono">{lot.supplier_id}</td>
                    <td><Badge label={lot.lot_status} /></td>
                    <td>{lot.received_quantity} {lot.uom}</td>
                    <td><strong className="text-accent">{lot.available_quantity}</strong></td>
                    <td>{lot.consumed_quantity}</td>
                    <td>
                      {lot.quarantined_quantity > 0 ? (
                        <span className="badge badge-amber">{lot.quarantined_quantity}</span>
                      ) : (
                        '0.0'
                      )}
                    </td>
                    <td>
                      <span className="font-mono" style={{ color: lot.incoming_quality_score >= 95 ? 'var(--accent-green)' : 'var(--accent-amber)' }}>
                        {lot.incoming_quality_score.toFixed(1)} / 100
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-sm btn-primary"
                        onClick={() => onNavigateToBlastRadius(lot.material_lot_id)}
                      >
                        Blast Radius
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

