import React from 'react';
import { Card, Statistic, Space, Typography, Tooltip } from 'antd';
import { ReactNode } from 'react';

const { Text } = Typography;

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  prefix?: ReactNode;
  suffix?: ReactNode;
  trend?: string;
  trendValue?: string | number;
  tooltip?: string;
  color?: string;
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  prefix,
  suffix,
  trend,
  trendValue,
  tooltip,
  color = '#1890ff',
  onClick,
}) => {
  const content = (
    <Card
      bodyStyle={{ padding: 24 }}
      style={{
        border: 'none',
        borderRadius: 12,
        background: 'var(--card-bg)',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
      }}
      onClick={onClick}
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space>
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: 12,
              background: `${color}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              color: color,
            }}
          >
            {icon}
          </div>
          {trend && (
            <Tooltip title={trend}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: trend.includes('+') ? '#52c41a20' : '#f5222d20',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 12,
                  color: trend.includes('+') ? '#52c41a' : '#f5222d',
                }}
              >
                {trend}
              </div>
            </Tooltip>
          )}
        </Space>
        
        <Statistic
          title={
            <Text type="secondary" style={{ fontSize: 14 }}>
              {title}
            </Text>
          }
          value={value}
          prefix={prefix}
          suffix={suffix}
          style={{ marginTop: 8 }}
        />
        
        {trendValue && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {trendValue}
          </Text>
        )}
      </Space>
    </Card>
  );

  if (tooltip) {
    return <Tooltip title={tooltip}>{content}</Tooltip>;
  }

  return content;
};

export default MetricCard;
