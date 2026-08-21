import React from 'react';
import { Bar, BarConfig, Pie, PieConfig, Column, ColumnConfig } from '@ant-design/plots';
import { Card, Typography, Space, Select } from 'antd';

const { Title } = Typography;

interface DistributionChartProps {
  title?: string;
  data: any[];
  type?: 'bar' | 'pie' | 'column';
  xField: string;
  yField: string;
  seriesField?: string;
  color?: string | string[];
  height?: number;
  label?: boolean;
  onTypeChange?: (type: 'bar' | 'pie' | 'column') => void;
}

const DistributionChart: React.FC<DistributionChartProps> = ({
  title,
  data,
  type = 'bar',
  xField,
  yField,
  seriesField,
  color = '#1890ff',
  height = 300,
  label = true,
  onTypeChange,
}) => {
  const handleTypeChange = (value: string) => {
    onTypeChange && onTypeChange(value as 'bar' | 'pie' | 'column');
  };

  const renderChart = () => {
    switch (type) {
      case 'pie':
        const pieConfig: PieConfig = {
          data,
          angleField: yField,
          colorField: xField,
          radius: 0.8,
          height,
          color: Array.isArray(color) ? color : [color],
          label: label ? {
            type: 'spider',
            labelHeight: 28,
            content: '{name}\n{percentage}',
          } : false,
          interactions: [{ type: 'element-active' }, { type: 'pie-statistic-active' }],
        };
        return <Pie {...pieConfig} />;

      case 'column':
        const columnConfig: ColumnConfig = {
          data,
          xField,
          yField,
          seriesField,
          height,
          color: Array.isArray(color) ? color : [color],
          label: label ? {
            position: 'top',
            style: {
              fill: '#fff',
              fontWeight: 'bold',
            },
          } : false,
          columnStyle: {
            radius: [4, 4, 0, 0],
          },
        };
        return <Column {...columnConfig} />;

      case 'bar':
      default:
        const barConfig: BarConfig = {
          data,
          xField,
          yField,
          seriesField,
          height,
          color: Array.isArray(color) ? color : [color],
          label: label ? {
            position: 'top',
            style: {
              fill: '#fff',
              fontWeight: 'bold',
            },
          } : false,
          xAxis: {
            label: {
              autoRotate: false,
            },
          },
        };
        return <Bar {...barConfig} />;
    }
  };

  return (
    <Card
      title={title}
      extra={
        onTypeChange && (
          <Select
            defaultValue={type}
            onChange={handleTypeChange}
            options={[
              { value: 'bar', label: 'Bar' },
              { value: 'pie', label: 'Pie' },
              { value: 'column', label: 'Column' },
            ]}
            size="small"
            style={{ width: 100 }}
          />
        )
      }
      bodyStyle={{ padding: 0 }}
      style={{ borderRadius: 12 }}
    >
      {renderChart()}
    </Card>
  );
};

export default DistributionChart;
