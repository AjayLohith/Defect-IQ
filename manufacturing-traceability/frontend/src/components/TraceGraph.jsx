import React from 'react';
import Badge from './Badge';

export default function TraceGraph({ type = 'upstream', data }) {
  if (!data) return null;

  if (type === 'upstream') {
    return (
      <div className="trace-graph-container">
        <div className="trace-stage">
          <div className="trace-node-card trace-node-defect">
            <div className="node-tag">Discovered Defect</div>
            <div className="node-id">{data.defect_id}</div>
            <div className="node-title">{data.defect_code} ({data.defect_category})</div>
            <div className="node-badges">
              <Badge label={data.severity} />
              <Badge label={data.defect_status} />
            </div>
            <div className="node-meta">
              <span>Qty: {data.defect_quantity}</span>
              <span>Source: {data.suspected_source}</span>
            </div>
          </div>
        </div>

        <div className="trace-arrow">&rarr;</div>

        <div className="trace-stage">
          <div className="trace-node-card">
            <div className="node-tag">Quality Gate</div>
            <div className="node-id">{data.inspection_result_id}</div>
            <div className="node-title">Inspection Outcome</div>
            <div className="node-badges">
              <Badge label={data.disposition} />
            </div>
            <div className="node-meta">
              <span>Order: {data.production_order_id}</span>
            </div>
          </div>
        </div>

        <div className="trace-arrow">&rarr;</div>

        <div className="trace-stage">
          <div className="trace-node-card">
            <div className="node-tag">Process & Machine</div>
            <div className="node-id">{data.process_execution_id}</div>
            <div className="node-title">{data.step_name}</div>
            <div className="node-subtitle">Machine: {data.machine_name} ({data.machine_id})</div>
            <div className="node-meta">
              <span>Product: {data.product_name}</span>
            </div>
          </div>
        </div>

        <div className="trace-arrow">&rarr;</div>

        <div className="trace-stage">
          <div className="trace-node-card trace-node-supplier">
            <div className="node-tag">Raw Material Lots ({data.consumed_lots?.length || 0})</div>
            {data.consumed_lots?.length === 0 ? (
              <div className="node-empty">No direct material consumptions recorded.</div>
            ) : (
              <div className="consumed-lots-list">
                {data.consumed_lots.map((lot, idx) => (
                  <div key={idx} className="consumed-lot-item">
                    <div className="lot-header">
                      <span className="lot-id">{lot.material_lot_id}</span>
                      <Badge label={lot.lot_status} />
                    </div>
                    <div className="lot-material">{lot.material_product_name}</div>
                    <div className="lot-supplier">
                      <span>Supplier: <strong>{lot.supplier_name}</strong></span>
                      <span>Batch: {lot.supplier_batch_code}</span>
                    </div>
                    <div className="lot-qty">
                      Consumed: {lot.consumed_quantity} {lot.uom}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Downstream Blast Radius Trace
  return (
    <div className="trace-graph-container">
      <div className="trace-stage">
        <div className="trace-node-card trace-node-supplier">
          <div className="node-tag">Suspect Material Lot</div>
          <div className="node-id">{data.material_lot_id}</div>
          <div className="node-title">{data.material_product_name}</div>
          <div className="node-subtitle">Supplier: {data.supplier_name} ({data.supplier_id})</div>
          <div className="node-badges">
            <Badge label={data.lot_status} />
          </div>
          <div className="node-meta">
            <span>Available: {data.available_quantity} {data.uom}</span>
            <span>Consumed: {data.consumed_quantity} {data.uom}</span>
          </div>
        </div>
      </div>

      <div className="trace-arrow">&rarr;</div>

      <div className="trace-stage" style={{ flex: 2 }}>
        <div className="trace-node-card">
          <div className="node-tag">
            Impacted Production Orders ({data.total_impacted_orders})
          </div>
          {data.impacted_orders?.length === 0 ? (
            <div className="node-empty">No downstream orders have consumed this lot.</div>
          ) : (
            <div className="impacted-orders-grid">
              {data.impacted_orders.map((po, idx) => (
                <div key={idx} className={`impacted-order-item ${po.defects_count > 0 ? 'order-has-defects' : ''}`}>
                  <div className="po-header">
                    <span className="po-id">{po.production_order_id}</span>
                    <Badge label={po.order_status} />
                  </div>
                  <div className="po-product">{po.product_name}</div>
                  <div className="po-qty">Consumed: {po.consumed_quantity} {po.consumption_uom}</div>
                  <div className="po-outcomes">
                    {po.defects_count > 0 ? (
                      <span className="badge badge-red">{po.defects_count} Defects</span>
                    ) : (
                      <span className="badge badge-green">0 Defects</span>
                    )}
                    {po.active_containments_count > 0 && (
                      <span className="badge badge-amber">{po.active_containments_count} Active Containments</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

