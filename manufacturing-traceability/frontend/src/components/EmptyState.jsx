import React from 'react';

export default function EmptyState({ message = 'No data available', subtext, actionText, onAction }) {
  return (
    <div className="card text-center" style={{ padding: '2.5rem 1rem', color: '#64748b' }}>
      <p style={{ margin: 0, fontWeight: 500, fontSize: '0.95rem' }}>{message}</p>
      {subtext && <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.85rem' }}>{subtext}</p>}
      {actionText && onAction && (
        <button
          className="btn btn-secondary"
          onClick={onAction}
          style={{ marginTop: '1rem' }}
        >
          {actionText}
        </button>
      )}
    </div>
  );
}

