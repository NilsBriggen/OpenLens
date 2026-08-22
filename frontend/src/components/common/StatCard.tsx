import React from 'react';
import { Card } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

export type StatAccent = 'primary' | 'success' | 'warning' | 'error' | 'purple' | 'neutral';

const ACCENT_TOKENS: Record<StatAccent, { color: string; soft: string }> = {
  primary: { color: 'var(--primary-color)', soft: 'var(--primary-soft)' },
  success: { color: 'var(--success-color)', soft: 'var(--success-soft)' },
  warning: { color: 'var(--warning-color)', soft: 'var(--warning-soft)' },
  error: { color: 'var(--error-color)', soft: 'var(--error-soft)' },
  purple: { color: 'var(--purple-color)', soft: 'var(--purple-soft)' },
  neutral: { color: 'var(--text-color-secondary)', soft: 'var(--hover-color)' },
};

export interface StatCardDelta {
  value: React.ReactNode;
  direction: 'up' | 'down';
}

export interface StatCardProps {
  label: React.ReactNode;
  value: React.ReactNode;
  /** Shown under the value, e.g. "not reported" for a stat with no backing endpoint. */
  subLabel?: React.ReactNode;
  icon?: React.ReactNode;
  accent?: StatAccent;
  delta?: StatCardDelta;
  /** 108px min-height / 28px value, for dense 5-6up rows. */
  dense?: boolean;
  /** Overrides the dense/default min-height (e.g. 132px for cards with a tag footer). */
  minHeight?: number;
  /** Breakdown tags or similar, pinned to the card's bottom edge. */
  footer?: React.ReactNode;
  loading?: boolean;
  style?: React.CSSProperties;
  className?: string;
  onClick?: () => void;
}

/**
 * The one stat-card treatment for the whole app.
 *
 * Consolidates the two competing patterns that used to exist side by side -
 * `<Statistic>` inside a `<Card>` on some screens, hand-built `<Title>` pairs
 * on others - which produced different label/value sizes and uneven card
 * heights within the same row. See the UI polish handoff, decision 1.
 */
const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subLabel,
  icon,
  accent = 'primary',
  delta,
  dense = false,
  minHeight,
  footer,
  loading,
  style,
  className,
  onClick,
}) => {
  const tokens = ACCENT_TOKENS[accent];
  const hasSubRow = Boolean(subLabel || delta);

  return (
    <Card
      loading={loading}
      onClick={onClick}
      className={className}
      style={style}
      bodyStyle={{
        padding: '20px 24px',
        minHeight: minHeight ?? (dense ? 108 : 120),
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        cursor: onClick ? 'pointer' : undefined,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
        <span style={{ fontSize: 14, color: 'var(--text-color-tertiary)' }}>{label}</span>
        {icon && (
          <span
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: tokens.soft,
              color: tokens.color,
              fontSize: 16,
              flexShrink: 0,
            }}
          >
            {icon}
          </span>
        )}
      </div>

      <div style={{ marginTop: footer ? 0 : 'auto' }}>
        <div
          style={{
            fontSize: dense ? 28 : 30,
            fontWeight: 600,
            lineHeight: 1.1,
            letterSpacing: '-0.02em',
            fontVariantNumeric: 'tabular-nums',
            color: 'var(--text-color)',
          }}
        >
          {value}
        </div>
        {hasSubRow && (
          <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 6, fontSize: 13 }}>
            {delta && (
              <span
                style={{
                  color: delta.direction === 'up' ? 'var(--success-color)' : 'var(--error-color)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 4,
                }}
              >
                {delta.direction === 'up' ? (
                  <ArrowUpOutlined style={{ fontSize: 11 }} />
                ) : (
                  <ArrowDownOutlined style={{ fontSize: 11 }} />
                )}
                {delta.value}
              </span>
            )}
            {subLabel && <span style={{ color: 'var(--text-color-tertiary)' }}>{subLabel}</span>}
          </div>
        )}
      </div>

      {footer && <div style={{ marginTop: 'auto' }}>{footer}</div>}
    </Card>
  );
};

export default StatCard;
