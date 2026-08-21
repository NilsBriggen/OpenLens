import React from 'react';
import { Line, LineConfig } from '@ant-design/plots';
import { Card, Typography, Space } from 'antd';

const { Title, Text } = Typography;

interface TrendChartProps {
  title?: string;
  data: any[];
  xField: string;
  yField: string | string[];
  seriesField?: string;
  height?: number;
  color?: string | string[];
  smooth?: boolean;
  point?: boolean;
  area?: boolean;
  tooltip?: boolean;
}

const TrendChart: React.FC<TrendChartProps> = ({
  title,
  data,
  xField,
  yField,
  seriesField,
  height = 300,
  color = '#1890ff',
  smooth = true,
  point = true,
  area = false,
  tooltip = true,
}) => {
  const config: LineConfig = {
    data,
    xField,
    yField,
    seriesField,
    height,
    color: Array.isArray(color) ? color : [color],
    smooth,
    point: point ? {
      size: 5,
      shape: 'diamond',
    } : false,
    area: area ? {
      style: {
        fill: `l(270) 0:${color} 1:#ffffff`,
      },
    } : false,
    legend: seriesField ? {
      position: 'top-right',
    } : false,
    tooltip: tooltip ? {
      fields: [xField, ...(Array.isArray(yField) ? yField : [yField])],
    } : false,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    style: {
      lineWidth: 3,
    },
  };

  return (
    <Card
      title={title}
      bodyStyle={{ padding: 0 }}
      style={{ borderRadius: 12 }}
    >
      <Line {...config} />
    </Card>
  );
};

export default TrendChart;
