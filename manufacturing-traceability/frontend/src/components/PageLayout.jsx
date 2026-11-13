import React from 'react';

export default function PageLayout({ title, subtitle, actions, children }) {
  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2>{title}</h2>
          {subtitle && <p className="text-secondary">{subtitle}</p>}
        </div>
        {actions && <div className="flex gap-2">{actions}</div>}
      </div>
      {children}
    </div>
  );
}

