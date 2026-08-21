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
  // @ant-design/plots v1 config typing is stricter than its runtime: a
  // multi-series line takes a single yField + seriesField, point/area/legend
  // accept the object forms below, and lineWidth is a valid line style at
  // runtime. Built as a plain object and asserted to LineConfig.
  const config = {
    data,
    xField,
    yField: Array.isArray(yField) ? yField[0] : yField,
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
    // See Dashboard.tsx: a 'path-in' appear animation calls getTotalLength() on
    // every element, including non-path point markers, and throws on first draw.
    lineStyle: {
      lineWidth: 3,
    },
  } as unknown as LineConfig;

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
