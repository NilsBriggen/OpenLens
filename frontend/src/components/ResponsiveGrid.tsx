/**
 * Responsive Grid Component for OpenLens
 * 
 * A flexible, responsive grid layout component
 */

import React from 'react';
import { Row, Col, Card, Typography, Space } from 'antd';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

interface GridItem {
  key: string;
  title?: string;
  content: React.ReactNode;
  span?: number | { xs?: number; sm?: number; md?: number; lg?: number; xl?: number; xxl?: number };
  offset?: number | { xs?: number; sm?: number; md?: number; lg?: number; xl?: number; xxl?: number };
  order?: number | { xs?: number; sm?: number; md?: number; lg?: number; xl?: number; xxl?: number };
  style?: React.CSSProperties;
  cardProps?: any;
}

interface ResponsiveGridProps {
  items: GridItem[];
  gutter?: number | [number, number];
  justify?: 'start' | 'end' | 'center' | 'space-around' | 'space-between';
  align?: 'top' | 'middle' | 'bottom';
  animated?: boolean;
  card?: boolean;
  cardProps?: any;
}

const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  items,
  gutter = 24,
  justify = 'start',
  align = 'top',
  animated = true,
  card = true,
  cardProps = {},
}) => {
  return (
    <Row gutter={gutter} justify={justify} align={align}>
      {items.map((item, index) => {
        // Normalize span
        const span = typeof item.span === 'number' 
          ? { xs: item.span, sm: item.span, md: item.span, lg: item.span, xl: item.span, xxl: item.span }
          : { xs: 24, sm: 24, md: 12, lg: 8, xl: 6, xxl: 6, ...item.span };

        // antd's Col offset/order are single numbers (the responsive spread
        // belongs on the breakpoint props). Collapse an object form to its
        // largest defined value.
        const flatten = (v?: number | Record<string, number | undefined>): number | undefined =>
          typeof v === 'number' ? v
            : v ? (v.xxl ?? v.xl ?? v.lg ?? v.md ?? v.sm ?? v.xs) : undefined;
        const offset = flatten(item.offset);
        const order = flatten(item.order);

        return (
          <Col
            key={item.key}
            xs={span.xs || 24}
            sm={span.sm || span.xs || 24}
            md={span.md || span.sm || span.xs || 24}
            lg={span.lg || span.md || span.sm || span.xs || 24}
            xl={span.xl || span.lg || span.md || span.sm || span.xs || 24}
            xxl={span.xxl || span.xl || span.lg || span.md || span.sm || span.xs || 24}
            offset={offset}
            order={order}
          >
            <motion.div
              initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              style={item.style}
            >
              {card ? (
                <Card
                  title={item.title}
                  bodyStyle={{ padding: 16 }}
                  style={{ height: '100%', borderRadius: 12, ...item.cardProps?.style }}
                  {...cardProps}
                  {...item.cardProps}
                >
                  {item.content}
                </Card>
              ) : (
                item.content
              )}
            </motion.div>
          </Col>
        );
      })}
    </Row>
  );
};

// Masonry Grid Component
interface MasonryGridProps {
  items: GridItem[];
  columns?: number;
  gap?: number;
  animated?: boolean;
  card?: boolean;
  cardProps?: any;
}

const MasonryGrid: React.FC<MasonryGridProps> = ({
  items,
  columns = 3,
  gap = 16,
  animated = true,
  card = true,
  cardProps = {},
}) => {
  // Calculate column heights
  const [columnHeights, setColumnHeights] = React.useState<number[]>(Array(columns).fill(0));
  const gridRef = React.useRef<HTMLDivElement>(null);

  // Update column heights on render
  React.useEffect(() => {
    if (gridRef.current) {
      const columnElements = gridRef.current.querySelectorAll('.masonry-column');
      const newHeights = Array.from(columnElements).map(el => el.scrollHeight);
      setColumnHeights(newHeights);
    }
  }, [items, columns]);

  // Distribute items across columns
  const getColumnItems = (columnIndex: number) => {
    return items.filter((_, index) => index % columns === columnIndex);
  };

  return (
    <div
      ref={gridRef}
      style={{
        display: 'flex',
        gap,
        width: '100%',
      }}
    >
      {Array.from({ length: columns }).map((_, columnIndex) => (
        <div
          key={columnIndex}
          className="masonry-column"
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            gap,
          }}
        >
          {getColumnItems(columnIndex).map((item, index) => (
            <motion.div
              key={item.key}
              initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: (columnIndex * items.length + index) * 0.05 }}
              style={item.style}
            >
              {card ? (
                <Card
                  title={item.title}
                  bodyStyle={{ padding: 16 }}
                  style={{ borderRadius: 12, ...item.cardProps?.style }}
                  {...cardProps}
                  {...item.cardProps}
                >
                  {item.content}
                </Card>
              ) : (
                item.content
              )}
            </motion.div>
          ))}
        </div>
      ))}
    </div>
  );
};

export { MasonryGrid };
export default ResponsiveGrid;
