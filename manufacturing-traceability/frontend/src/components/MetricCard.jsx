import React from 'react';

export default function MetricCard({ title, value, subtitle, icon, trend, alert }) {
  return (
    <div className={`metric-card ${alert ? 'metric-card-alert' : ''}`}>
      <div className="metric-header">
        <span className="metric-title">{title}</span>
        {icon && <span className="metric-icon">{icon}</span>}
      </div>
      <div className="metric-value">{value}</div>
      {subtitle && <div className="metric-subtitle">{subtitle}</div>}
      {trend && <div className="metric-trend">{trend}</div>}
    </div>
  );
}

