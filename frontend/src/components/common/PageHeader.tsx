import React from 'react';

export interface PageHeaderProps {
  icon: React.ReactNode;
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  actions?: React.ReactNode;
  style?: React.CSSProperties;
}

/**
 * The one page-header row for every screen - bare h1 with an accent icon and
 * a sub-line on the left, action buttons on the right, baseline-aligned via
 * `align-items: flex-end`. Replaces the Card-wrapped header Graph Explorer
 * used to have, and the ad-hoc `.page-header` div/h1 pairs elsewhere.
 */
const PageHeader: React.FC<PageHeaderProps> = ({ icon, title, subtitle, actions, style }) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'flex-end',
      justifyContent: 'space-between',
      gap: 24,
      flexWrap: 'wrap',
      ...style,
    }}
  >
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 28, color: 'var(--primary-color)', display: 'flex' }}>{icon}</span>
        <h1
          style={{
            fontSize: 30,
            fontWeight: 600,
            letterSpacing: '-0.02em',
            margin: 0,
            color: 'var(--text-color)',
          }}
        >
          {title}
        </h1>
      </div>
      {subtitle && (
        <p style={{ fontSize: 14, color: 'var(--text-color-tertiary)', margin: '4px 0 0' }}>{subtitle}</p>
      )}
    </div>
    {actions && (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, minHeight: 32 }}>{actions}</div>
    )}
  </div>
);

export default PageHeader;
