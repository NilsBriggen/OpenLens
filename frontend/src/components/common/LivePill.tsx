import React from 'react';

export interface LivePillProps {
  connected: boolean;
  style?: React.CSSProperties;
}

/**
 * The one "Live" websocket indicator used across the shell, Dashboard, Graph
 * Explorer, Scraping Hub and Threat Intelligence. Renders honestly: when the
 * socket is not connected it says so rather than claiming "Live" regardless.
 */
const LivePill: React.FC<LivePillProps> = ({ connected, style }) => {
  const color = connected ? 'var(--success-color)' : 'var(--text-color-secondary)';

  return (
    <span
      style={{
        height: 32,
        borderRadius: 6,
        padding: '0 12px',
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        fontSize: 13,
        fontWeight: 500,
        color,
        background: connected ? 'var(--success-soft)' : 'var(--hover-color)',
        border: `1px solid ${connected ? 'rgba(82, 196, 26, 0.4)' : 'var(--border-color)'}`,
        whiteSpace: 'nowrap',
        ...style,
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: color,
          animation: connected ? 'olPulse 2s infinite' : undefined,
        }}
      />
      {connected ? 'Live' : 'Offline'}
    </span>
  );
};

export default LivePill;
