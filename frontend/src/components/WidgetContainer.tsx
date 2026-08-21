import React, { useState, useCallback } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Button, Card, Typography, Space, Modal, Form, Select, Input, Row, Col } from 'antd';
import { PlusOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import DashboardWidget from './DashboardWidget';

const { Title, Text } = Typography;
const { Option } = Select;

interface WidgetConfig {
  id: string;
  title: string;
  type: string;
  size: 'small' | 'medium' | 'large';
  content: React.ReactNode;
  isLoading?: boolean;
}

interface WidgetContainerProps {
  widgets: WidgetConfig[];
  onAddWidget: (config: WidgetConfig) => void;
  onRemoveWidget: (id: string) => void;
  onRefreshWidget: (id: string) => void;
  onToggleWidgetSize: (id: string) => void;
  availableWidgetTypes: { value: string; label: string; description: string }[];
}

const WidgetContainer: React.FC<WidgetContainerProps> = ({
  widgets,
  onAddWidget,
  onRemoveWidget,
  onRefreshWidget,
  onToggleWidgetSize,
  availableWidgetTypes,
}) => {
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [selectedType, setSelectedType] = useState('');

  // Move widget in the list
  const moveWidget = useCallback((dragIndex: number, hoverIndex: number) => {
    // This will be handled by the parent component
  }, []);

  // Render widget based on type
  const renderWidgetContent = (type: string): React.ReactNode => {
    switch (type) {
      case 'metrics':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
            <div>
              <Text type="secondary" style={{ fontSize: 12 }}>Total Nodes</Text>
              <Title level={3} style={{ margin: '4px 0' }}>12,453</Title>
              <Text type="success" style={{ fontSize: 12 }}>+12%</Text>
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12 }}>Total Edges</Text>
              <Title level={3} style={{ margin: '4px 0' }}>87,342</Title>
              <Text type="success" style={{ fontSize: 12 }}>+8%</Text>
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12 }}>Active Users</Text>
              <Title level={3} style={{ margin: '4px 0' }}>42</Title>
              <Text type="warning" style={{ fontSize: 12 }}>+2</Text>
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12 }}>System Health</Text>
              <Title level={3} style={{ margin: '4px 0' }}>98%</Title>
              <Text type="success" style={{ fontSize: 12 }}>Good</Text>
            </div>
          </div>
        );
      case 'recent-activity':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <Text>Scrape Job Completed</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>5 min ago</Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <Text>New Threat Detected</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>15 min ago</Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <Text>Anomaly Detected</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>1 hour ago</Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
              <Text>User Login</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>2 hours ago</Text>
            </div>
          </Space>
        );
      case 'quick-actions':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button type="primary" block icon={<PlusOutlined />}>
              New Scrape Job
            </Button>
            <Button block icon={<AppstoreOutlined />}>
              Analyze Graph
            </Button>
            <Button block icon={<SettingOutlined />}>
              Threat Hunt
            </Button>
          </Space>
        );
      case 'graph-stats':
        return (
          <div style={{ textAlign: 'center', padding: 24 }}>
            <Title level={5}>Graph Statistics</Title>
            <Text type="secondary">Interactive chart would be displayed here</Text>
          </div>
        );
      case 'threat-feeds':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <Text>AlienVault OTX</Text>
              <Text type="success" style={{ fontSize: 12 }}>Active</Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <Text>MISP</Text>
              <Text type="success" style={{ fontSize: 12 }}>Active</Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
              <Text>Abuse.ch</Text>
              <Text type="warning" style={{ fontSize: 12 }}>Warning</Text>
            </div>
          </Space>
        );
      case 'system-health':
        return (
          <div style={{ textAlign: 'center', padding: 24 }}>
            <Title level={5}>System Health</Title>
            <div style={{ margin: '16px 0' }}>
              <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'conic-gradient(#52c41a 0deg, #52c41a 280deg, #faad14 280deg, #faad14 360deg)', display: 'inline-block' }}>
                <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--card-bg)', borderRadius: '50%' }}>
                  <Title level={3} style={{ margin: 0, color: '#52c41a' }}>98%</Title>
                </div>
              </div>
            </div>
            <Text type="secondary" style={{ fontSize: 12 }}>All systems operational</Text>
          </div>
        );
      default:
        return (
          <div style={{ textAlign: 'center', padding: 24 }}>
            <Text type="secondary">Widget content for {type}</Text>
          </div>
        );
    }
  };

  // Add widget
  const handleAddWidget = () => {
    if (!selectedType) return;

    const newWidget: WidgetConfig = {
      id: `widget-${Date.now()}`,
      title: availableWidgetTypes.find(w => w.value === selectedType)?.label || selectedType,
      type: selectedType,
      size: 'medium',
      content: renderWidgetContent(selectedType),
    };

    onAddWidget(newWidget);
    setAddModalVisible(false);
    setSelectedType('');
  };

  // Toggle widget size
  const handleToggleSize = (id: string) => {
    onToggleWidgetSize(id);
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div style={{ position: 'relative' }}>
        {/* Widget Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 16,
          }}
        >
          {widgets.map((widget, index) => (
            <DashboardWidget
              key={widget.id}
              id={widget.id}
              title={widget.title}
              type={widget.type}
              content={widget.content}
              onRemove={onRemoveWidget}
              onRefresh={onRefreshWidget}
              onSettings={() => {}}
              onToggleSize={handleToggleSize}
              isLoading={widget.isLoading}
              size={widget.size}
              draggable={true}
              index={index}
              moveWidget={moveWidget}
            />
          ))}
        </div>

        {/* Add Widget Button */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.5 }}
          style={{ marginTop: 16 }}
        >
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={() => setAddModalVisible(true)}
            block
            style={{ borderStyle: 'dashed' }}
          >
            Add Widget
          </Button>
        </motion.div>

        {/* Add Widget Modal */}
        <Modal
          title="Add Widget"
          open={addModalVisible}
          onCancel={() => setAddModalVisible(false)}
          footer={[
            <Button key="cancel" onClick={() => setAddModalVisible(false)}>
              Cancel
            </Button>,
            <Button
              key="add"
              type="primary"
              onClick={handleAddWidget}
              disabled={!selectedType}
            >
              Add Widget
            </Button>,
          ]}
        >
          <Form layout="vertical">
            <Form.Item label="Widget Type" rules={[{ required: true }]}>
              <Select
                value={selectedType}
                onChange={setSelectedType}
                options={availableWidgetTypes.map(w => ({
                  value: w.value,
                  label: (
                    <div>
                      <div>{w.label}</div>
                      <div style={{ fontSize: 12, color: '#666' }}>{w.description}</div>
                    </div>
                  ),
                }))}
                placeholder="Select widget type"
              />
            </Form.Item>
            <Form.Item label="Preview">
              <Card size="small" style={{ minHeight: 200 }}>
                {selectedType ? renderWidgetContent(selectedType) : (
                  <Text type="secondary" style={{ textAlign: 'center', display: 'block', padding: 40 }}>
                    Select a widget type to preview
                  </Text>
                )}
              </Card>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </DndProvider>
  );
};

export default WidgetContainer;
