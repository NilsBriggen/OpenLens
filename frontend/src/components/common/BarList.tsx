import React from 'react';

export interface BarListItem {
  key?: React.Key;
  label: React.ReactNode;
  value: number;
  /** What to render at the right instead of the raw numeric value. */
  displayValue?: React.ReactNode;
  color?: string;
}

export interface BarListProps {
  items: BarListItem[];
  /** Normalizes bar width; defaults to the largest item's value. */
  max?: number;
  labelWidth?: number;
  style?: React.CSSProperties;
}

/**
 * The horizontal bar-list idiom used for "Activity by Module", "Data
 * Ingestion", "Job Status Distribution", "Users by Role", "IOC Types" and
 * "Events by Type" - a label column, a track, and a right-aligned tabular
 * value. See the UI polish handoff, Dashboard block 3.
 */
const BarList: React.FC<BarListProps> = ({ items, max, labelWidth = 96, style }) => {
  const resolvedMax = max ?? Math.max(...items.map((item) => item.value), 1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, ...style }}>
      {items.map((item, index) => {
        const pct = resolvedMax > 0 ? Math.min(100, (item.value / resolvedMax) * 100) : 0;
        return (
          <div key={item.key ?? index} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span
              style={{
                width: labelWidth,
                flexShrink: 0,
                fontSize: 13,
                color: 'var(--text-color-secondary)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              title={typeof item.label === 'string' ? item.label : undefined}
            >
              {item.label}
            </span>
            <span
              style={{
                flex: 1,
                height: 12,
                borderRadius: 6,
                background: 'var(--track-color)',
                overflow: 'hidden',
              }}
            >
              <span
                style={{
                  display: 'block',
                  height: '100%',
                  width: `${pct}%`,
                  borderRadius: 6,
                  background: item.color ?? 'var(--primary-color)',
                  transition: 'width 0.3s ease',
                }}
              />
            </span>
            <span
              style={{
                width: 56,
                flexShrink: 0,
                textAlign: 'right',
                fontSize: 13,
                fontVariantNumeric: 'tabular-nums',
                color: 'var(--text-color)',
              }}
            >
              {item.displayValue ?? item.value}
            </span>
          </div>
        );
      })}
    </div>
  );
};

export default BarList;
