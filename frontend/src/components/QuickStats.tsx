import React from 'react';
import { Row, Col, Card, Statistic, Space, Typography, Tooltip } from 'antd';
import { motion } from 'framer-motion';
import MetricCard from './charts/MetricCard';

const { Text } = Typography;

interface StatItem {
  key: string;
  title: string;
  value: string | number;
  icon: React.ReactNode;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  trend?: string;
  trendValue?: string | number;
  tooltip?: string;
  color?: string;
}

interface QuickStatsProps {
  stats: StatItem[];
  columns?: number;
  animated?: boolean;
  onStatClick?: (key: string) => void;
}

const QuickStats: React.FC<QuickStatsProps> = ({
  stats,
  columns = 4,
  animated = true,
  onStatClick,
}) => {
  // Determine grid columns
  const gridColumns = {
    1: '1fr',
    2: 'repeat(2, 1fr)',
    3: 'repeat(3, 1fr)',
    4: 'repeat(4, 1fr)',
    5: 'repeat(5, 1fr)',
    6: 'repeat(6, 1fr)',
  };

  return (
    <Row gutter={16}>
      {stats.map((stat, index) => (
        <Col key={stat.key} xs={24} sm={12} lg={Math.max(24 / columns, 6)}>
          <motion.div
            initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.02, y: -4 }}
            onClick={() => onStatClick && onStatClick(stat.key)}
            style={{ cursor: onStatClick ? 'pointer' : 'default' }}
          >
            <MetricCard
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              prefix={stat.prefix}
              suffix={stat.suffix}
              trend={stat.trend}
              trendValue={stat.trendValue}
              tooltip={stat.tooltip}
              color={stat.color || '#1890ff'}
            />
          </motion.div>
        </Col>
      ))}
    </Row>
  );
};

export default QuickStats;
