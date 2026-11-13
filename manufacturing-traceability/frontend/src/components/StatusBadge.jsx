import React from 'react';
import Badge from './Badge';

export default function StatusBadge({ status, label, variant }) {
  return <Badge label={label || status} variant={variant} />;
}

