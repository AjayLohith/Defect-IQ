import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

export default function OrdersView() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');

  // BOM Reconciliation state
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [bomReport, setBomReport] = useState(null);
  const [bomLoading, setBomLoading] = useState(false);
  const [bomError, setBomError] = useState(null);

  useEffect(() => {
    loadOrders();
  }, [filterStatus]);

  async function loadOrders() {
    try {
      setLoading(true);
      const params = {};
      if (filterStatus) params.status = filterStatus;
      const data = await api.getOrders(params);
      setOrders(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function openBOMReconciliation(orderId) {
    try {
      setSelectedOrder(orderId);
      setBomLoading(true);
      setBomError(null);
      const report = await api.getOrderBOMReconciliation(orderId);
      setBomReport(report);
    } catch (err) {
      setBomError(err.message || 'Failed to fetch BOM reconciliation report');
    } finally {
      setBomLoading(false);
    }
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Production Orders & BOM Reconciliation Console</h2>
          <p className="view-subtitle">
            Inspect order execution status, quantity reconciliation partitions, and BOM material consumption compliance.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadOrders}>Refresh Orders</button>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <label className="filter-label">Filter Status:</label>
          <select
            className="filter-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="COMPLETED">Completed</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="PLANNED">Planned</option>
            <option value="HELD">Held</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
        <div className="filter-info">
          Showing <strong>{orders.length}</strong> production orders
        </div>
      </div>

      {/* Orders Table */}
      <div className="card">
        {loading ? (
          <div className="loading-state">Loading production orders...</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Product ID</th>
                  <th>Production Lot</th>
                  <th>Status</th>
                  <th>Planned Qty</th>
                  <th>Completed Qty</th>
                  <th>Scrap</th>
                  <th>Rework</th>
                  <th>Quarantine</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((po) => (
                  <tr key={po.production_order_id}>
                    <td className="font-mono"><strong>{po.production_order_id}</strong></td>
                    <td className="font-mono">{po.product_id}</td>
                    <td className="font-mono">{po.production_lot_code}</td>
                    <td><Badge label={po.order_status} /></td>
                    <td>{po.planned_quantity} {po.uom}</td>
                    <td><strong>{po.completed_quantity}</strong></td>
                    <td>{po.scrap_quantity > 0 ? <span className="text-warn">{po.scrap_quantity}</span> : '0'}</td>
                    <td>{po.rework_quantity > 0 ? <span className="text-warn">{po.rework_quantity}</span> : '0'}</td>
                    <td>{po.quarantined_quantity > 0 ? <span className="badge badge-amber">{po.quarantined_quantity}</span> : '0'}</td>
                    <td>
                      <button
                        className="btn-sm btn-primary"
                        onClick={() => openBOMReconciliation(po.production_order_id)}
                      >
                        BOM Reconciliation
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* BOM Reconciliation Modal */}
      {selectedOrder && (
        <Modal
          isOpen={!!selectedOrder}
          onClose={() => {
            setSelectedOrder(null);
            setBomReport(null);
          }}
          title={`BOM Consumption Reconciliation: ${selectedOrder}`}
        >
          {bomLoading && <div className="loading-state">Reconciling BOM lines against committed consumptions...</div>}
          {bomError && <div className="error-banner">{bomError}</div>}

          {bomReport && (
            <div>
              <div className="reconciliation-summary-banner">
                <div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Product</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
                    {bomReport.product_name} ({bomReport.product_id})
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Reconciliation Outcome</div>
                  <div>
                    {bomReport.is_fully_reconciled ? (
                      <span className="badge badge-green">FULLY RECONCILED</span>
                    ) : (
                      <span className="badge badge-red">VARIANCE / ANOMALY DETECTED</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="table-responsive" style={{ marginTop: '1.5rem' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>BOM Line ID</th>
                      <th>Material Product</th>
                      <th>Required (Planned)</th>
                      <th>Actual Consumed</th>
                      <th>Variance</th>
                      <th>Consumptions Count</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bomReport.items?.map((item) => (
                      <tr
                        key={item.bom_line_id}
                        className={
                          item.reconciliation_status === 'MISSING_CONSUMPTION'
                            ? 'row-highlight-critical'
                            : item.reconciliation_status === 'VARIANCE_DETECTED'
                            ? 'row-highlight-warn'
                            : ''
                        }
                      >
                        <td className="font-mono"><strong>{item.bom_line_id}</strong></td>
                        <td>
                          <div>{item.material_name}</div>
                          <div className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            {item.material_product_id}
                          </div>
                        </td>
                        <td>{item.expected_required_quantity} {item.uom}</td>
                        <td><strong>{item.actual_consumed_quantity} {item.uom}</strong></td>
                        <td className="font-mono">
                          {item.quantity_variance !== 0 ? (
                            <span className={item.quantity_variance < 0 ? 'text-warn' : ''}>
                              {item.quantity_variance > 0 ? `+${item.quantity_variance}` : item.quantity_variance}
                            </span>
                          ) : (
                            '0.0000'
                          )}
                        </td>
                        <td>{item.consumption_records_count}</td>
                        <td><Badge label={item.reconciliation_status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Modal>
      )}
    </div>
  );
}

