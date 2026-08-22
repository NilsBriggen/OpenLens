import React from 'react';
import { InboxOutlined } from '@ant-design/icons';

export interface TabEmptyStateProps {
  label: React.ReactNode;
  description: React.ReactNode;
  style?: React.CSSProperties;
}

/**
 * The empty state for a tab/screen that has no backing implementation yet -
 * a real message instead of a headerless empty `<Table>`. Used by every
 * AI Analytics tab past the first and the three unimplemented Security
 * Center tabs (Authentication, Authorization, Compliance).
 */
const TabEmptyState: React.FC<TabEmptyStateProps> = ({ label, description, style }) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      textAlign: 'center',
      padding: '64px 24px',
      maxWidth: 420,
      margin: '0 auto',
      gap: 8,
      ...style,
    }}
  >
    <InboxOutlined style={{ fontSize: 48, color: 'var(--text-color-tertiary)' }} />
    <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-color)' }}>{label}</div>
    <div style={{ fontSize: 14, color: 'var(--text-color-secondary)' }}>{description}</div>
  </div>
);

export default TabEmptyState;
