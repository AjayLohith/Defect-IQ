import React from 'react';

const STATUS_COLORS = {
  // Common states
  OPEN: 'badge-blue',
  ACTIVE: 'badge-blue',
  IN_PROCESS: 'badge-blue',
  IMPLEMENTED: 'badge-amber',
  UNDER_INVESTIGATION: 'badge-amber',
  VERIFICATION_PENDING: 'badge-amber',
  VERIFIED: 'badge-green',
  PASSED: 'badge-green',
  COMPLETED: 'badge-green',
  ACCEPTED: 'badge-green',
  CLOSED: 'badge-slate',
  RECONCILED: 'badge-green',
  RELEASED: 'badge-green',
  PARTIALLY_CONSUMED: 'badge-blue',
  CONSUMED: 'badge-slate',

  // Severity & Anomaly
  CRITICAL: 'badge-red',
  MAJOR: 'badge-amber',
  MINOR: 'badge-slate',
  FAILED: 'badge-red',
  REJECTED: 'badge-red',
  MISSING_CONSUMPTION: 'badge-red',
  VARIANCE_DETECTED: 'badge-amber',
  PREMATURE_CLOSURE_ANOMALY: 'badge-red',
  READY_FOR_CLOSURE: 'badge-green',
  VERIFICATION_REQUIRED: 'badge-amber',
  DEGRADED: 'badge-amber',
  OFFLINE: 'badge-red',
  OPERATIONAL: 'badge-green',
  CONTAINED: 'badge-purple',
  STOP_LINE: 'badge-red',
  QUARANTINE_LOT: 'badge-amber',
};

export default function Badge({ label, variant }) {
  if (!label) return null;
  const className = variant || STATUS_COLORS[label] || 'badge-slate';
  return <span className={`badge ${className}`}>{label.replace(/_/g, ' ')}</span>;
}

