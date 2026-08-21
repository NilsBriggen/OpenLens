import React, { useState, useEffect } from 'react';
import { Card, Typography, Space, Button, Dropdown, Menu, Tooltip, Spin } from 'antd';
import {
  MoreOutlined,
  CloseOutlined,
  SettingOutlined,
  ExpandOutlined,
  ShrinkOutlined,
  RefreshOutlined
} from '@ant-design/icons';
import { motion, PanInfo } from 'framer-motion';
import { useDrag, useDrop } from 'react-dnd';

const { Text, Title } = Typography;

interface WidgetProps {
  id: string;
  title: string;
  type: string;
  content: React.ReactNode;
  onRemove: (id: string) => void;
  onRefresh: (id: string) => void;
  onSettings: (id: string) => void;
  onToggleSize: (id: string) => void;
  isLoading?: boolean;
  size?: 'small' | 'medium' | 'large';
  draggable?: boolean;
  index: number;
  moveWidget: (dragIndex: number, hoverIndex: number) => void;
}

interface DragItem {
  index: number;
  id: string;
  type: string;
}

const DashboardWidget: React.FC<WidgetProps> = ({
  id,
  title,
  type,
  content,
  onRemove,
  onRefresh,
  onSettings,
  onToggleSize,
  isLoading = false,
  size = 'medium',
  draggable = true,
  index,
  moveWidget,
}) => {
  const ref = React.useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Drag and Drop
  const [{ isDragging }, drag] = useDrag({
    type: 'widget',
    item: { id, index, type },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const [, drop] = useDrop({
    accept: 'widget',
    hover(item: DragItem, monitor) {
      if (!ref.current) return;
      const dragIndex = item.index;
      const hoverIndex = index;

      if (dragIndex === hoverIndex) return;

      const hoverBoundingRect = ref.current?.getBoundingClientRect();
      const hoverMiddleY = (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2;
      const clientOffset = monitor.getClientOffset();
      const hoverClientY = clientOffset?.y || 0 - hoverBoundingRect.top;

      if (dragIndex < hoverIndex && hoverClientY < hoverMiddleY) return;
      if (dragIndex > hoverIndex && hoverClientY > hoverMiddleY) return;

      moveWidget(dragIndex, hoverIndex);
      item.index = hoverIndex;
    },
  });

  drag(drop(ref));

  // Widget menu
  const widgetMenu = (
    <Menu
      onClick={({ key }) => {
        switch (key) {
          case 'refresh':
            onRefresh(id);
            break;
          case 'settings':
            onSettings(id);
            break;
          case 'toggle-size':
            onToggleSize(id);
            break;
          case 'fullscreen':
            setIsFullscreen(true);
            break;
          case 'remove':
            onRemove(id);
            break;
        }
      }}
      items={[
        {
          key: 'refresh',
          label: 'Refresh',
          icon: <RefreshOutlined />,
        },
        {
          key: 'settings',
          label: 'Settings',
          icon: <SettingOutlined />,
        },
        {
          key: 'toggle-size',
          label: size === 'large' ? 'Shrink' : 'Expand',
          icon: size === 'large' ? <ShrinkOutlined /> : <ExpandOutlined />,
        },
        {
          key: 'fullscreen',
          label: 'Fullscreen',
          icon: <ExpandOutlined />,
        },
        {
          type: 'divider',
        },
        {
          key: 'remove',
          label: 'Remove Widget',
          icon: <CloseOutlined />,
          danger: true,
        },
      ]}
    />
  );

  // Get widget size styles
  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return { gridColumn: 'span 1', minHeight: 200 };
      case 'large':
        return { gridColumn: 'span 2', minHeight: 400 };
      case 'medium':
      default:
        return { gridColumn: 'span 1', minHeight: 300 };
    }
  };

  // Fullscreen modal
  if (isFullscreen) {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        onClick={() => setIsFullscreen(false)}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.2 }}
          onClick={(e) => e.stopPropagation()}
          style={{
            background: 'var(--card-bg)',
            borderRadius: 12,
            padding: 24,
            width: '90%',
            maxWidth: 1200,
            maxHeight: '90vh',
            overflow: 'auto',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <Title level={4} style={{ margin: 0 }}>{title}</Title>
            <Space>
              <Button icon={<RefreshOutlined />} onClick={() => onRefresh(id)} size="small" />
              <Button icon={<CloseOutlined />} onClick={() => setIsFullscreen(false)} size="small" />
            </Space>
          </div>
          <div style={{ height: 'calc(90vh - 150px)' }}>
            {content}
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        ...getSizeStyles(),
        opacity: isDragging ? 0.5 : 1,
        cursor: draggable ? 'move' : 'default',
      }}
      className="dashboard-widget"
    >
      <Card
        title={
          <Space>
            <Text strong>{title}</Text>
          </Space>
        }
        extra={
          <Space>
            {isLoading ? (
              <Spin size="small" />
            ) : (
              <Tooltip title="Refresh">
                <Button type="text" icon={<RefreshOutlined />} onClick={() => onRefresh(id)} size="small" />
              </Tooltip>
            )}
            <Dropdown overlay={widgetMenu} trigger={['click']}>
              <Button type="text" icon={<MoreOutlined />} size="small" />
            </Dropdown>
          </Space>
        }
        bodyStyle={{ padding: 16, height: '100%', overflow: 'hidden' }}
        style={{ height: '100%', borderRadius: 12 }}
      >
        {content}
      </Card>
    </motion.div>
  );
};

export default DashboardWidget;
