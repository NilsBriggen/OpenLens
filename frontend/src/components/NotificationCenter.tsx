import React, { useState, useEffect } from 'react';
import { Badge, Button, Card, List, Avatar, Typography, Space, Tag, Drawer, Tooltip, Divider, Spin } from 'antd';
import {
  BellOutlined,
  CloseOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  DeleteOutlined,
  FilterOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Text, Title } = Typography;

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'warning' | 'error' | 'info';
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: 'system' | 'security' | 'threat' | 'scraping' | 'ai' | 'graph';
  timestamp: string;
  read: boolean;
  data?: any;
  actions?: { label: string; onClick: () => void }[];
}

interface NotificationCenterProps {
  visible: boolean;
  onClose: () => void;
  onNotificationClick?: (notification: Notification) => void;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  visible,
  onClose,
  onNotificationClick,
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string[]>([]);

  // Mock notifications
  const mockNotifications: Notification[] = [
    {
      id: '1',
      title: 'New Threat Detected',
      message: 'Malicious IP address 192.168.1.100 detected in network traffic',
      type: 'warning',
      priority: 'high',
      category: 'threat',
      timestamp: dayjs().subtract(5, 'minute').toISOString(),
      read: false,
      data: { ip: '192.168.1.100', severity: 'high' },
      actions: [
        { label: 'View Details', onClick: () => console.log('View threat details') },
        { label: 'Block IP', onClick: () => console.log('Block IP') },
      ],
    },
    {
      id: '2',
      title: 'Scrape Job Completed',
      message: 'Social Media Scrape job finished successfully with 150 URLs scraped',
      type: 'success',
      priority: 'medium',
      category: 'scraping',
      timestamp: dayjs().subtract(15, 'minute').toISOString(),
      read: false,
      data: { jobId: 'job-1', successCount: 150, failedCount: 5 },
      actions: [
        { label: 'View Results', onClick: () => console.log('View results') },
        { label: 'Export Data', onClick: () => console.log('Export data') },
      ],
    },
    {
      id: '3',
      title: 'Anomaly Detected',
      message: 'Statistical anomaly detected in graph data - Node 12345 has unusual connection pattern',
      type: 'warning',
      priority: 'high',
      category: 'ai',
      timestamp: dayjs().subtract(1, 'hour').toISOString(),
      read: true,
      data: { nodeId: '12345', anomalyScore: 9.5, feature: 'connection_count' },
      actions: [
        { label: 'Investigate', onClick: () => console.log('Investigate anomaly') },
        { label: 'View Node', onClick: () => console.log('View node') },
      ],
    },
    {
      id: '4',
      title: 'System Health Warning',
      message: 'CPU usage is at 85% - Consider scaling resources',
      type: 'warning',
      priority: 'medium',
      category: 'system',
      timestamp: dayjs().subtract(2, 'hour').toISOString(),
      read: true,
      data: { cpuUsage: 85, memoryUsage: 72 },
      actions: [
        { label: 'View Metrics', onClick: () => console.log('View metrics') },
        { label: 'Scale Up', onClick: () => console.log('Scale up') },
      ],
    },
    {
      id: '5',
      title: 'New User Registered',
      message: 'New user analyst3 has registered and is awaiting approval',
      type: 'info',
      priority: 'low',
      category: 'security',
      timestamp: dayjs().subtract(3, 'hour').toISOString(),
      read: false,
      data: { username: 'analyst3', email: 'analyst3@openlens.com' },
      actions: [
        { label: 'Approve', onClick: () => console.log('Approve user') },
        { label: 'Reject', onClick: () => console.log('Reject user') },
      ],
    },
    {
      id: '6',
      title: 'Threat Feed Updated',
      message: 'AlienVault OTX feed updated with 124 new IOCs',
      type: 'success',
      priority: 'low',
      category: 'threat',
      timestamp: dayjs().subtract(4, 'hour').toISOString(),
      read: true,
      data: { feedName: 'AlienVault OTX', newIOCs: 124 },
      actions: [
        { label: 'View IOCs', onClick: () => console.log('View IOCs') },
      ],
    },
  ];

  // Load notifications
  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setNotifications(mockNotifications);
      setLoading(false);
    }, 500);
  }, []);

  // Filter notifications
  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'unread' && notification.read) return false;
    if (filter === 'read' && !notification.read) return false;
    if (categoryFilter.length > 0 && !categoryFilter.includes(notification.category)) return false;
    if (priorityFilter.length > 0 && !priorityFilter.includes(notification.priority)) return false;
    return true;
  });

  // Mark as read
  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  // Mark all as read
  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(n => ({ ...n, read: true }))
    );
  };

  // Delete notification
  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Get icon for notification type
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'warning': return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'error': return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      case 'info': return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
      default: return <BellOutlined />;
    }
  };

  // Get color for notification type
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'success': return '#52c41a';
      case 'warning': return '#faad14';
      case 'error': return '#f5222d';
      case 'info': return '#1890ff';
      default: return '#d9d9d9';
    }
  };

  // Get color for priority
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#f5222d';
      case 'high': return '#fa8c16';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#d9d9d9';
    }
  };

  // Get category color
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'system': return '#1890ff';
      case 'security': return '#f5222d';
      case 'threat': return '#fa8c16';
      case 'scraping': return '#52c41a';
      case 'ai': return '#722ed1';
      case 'graph': return '#faad14';
      default: return '#d9d9d9';
    }
  };

  // Get category icon
  const getCategoryIcon = (category: string) => {
    const icons: Record<string, React.ReactNode> = {
      system: '⚙️',
      security: '🔒',
      threat: '🚨',
      scraping: '🔍',
      ai: '🤖',
      graph: '📊',
    };
    return icons[category] || '📝';
  };

  // Format time
  const formatTime = (timestamp: string) => {
    return dayjs(timestamp).fromNow();
  };

  // Category options
  const categoryOptions = [
    { label: 'System', value: 'system' },
    { label: 'Security', value: 'security' },
    { label: 'Threat', value: 'threat' },
    { label: 'Scraping', value: 'scraping' },
    { label: 'AI', value: 'ai' },
    { label: 'Graph', value: 'graph' },
  ];

  // Priority options
  const priorityOptions = [
    { label: 'Critical', value: 'critical' },
    { label: 'High', value: 'high' },
    { label: 'Medium', value: 'medium' },
    { label: 'Low', value: 'low' },
  ];

  // Unread count
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <Drawer
      title={
        <Space>
          <Badge count={unreadCount} size="small">
            <BellOutlined style={{ fontSize: 20 }} />
          </Badge>
          <Title level={4} style={{ margin: 0 }}>Notifications</Title>
        </Space>
      }
      placement="right"
      onClose={onClose}
      open={visible}
      width={450}
      maskClosable={false}
      closable={true}
      headerStyle={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}
      bodyStyle={{ padding: 0, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}
      footerStyle={{ padding: 16, borderTop: '1px solid #f0f0f0' }}
      footer={
        <Space>
          <Button icon={<SyncOutlined />} onClick={() => setLoading(true)}>
            Refresh
          </Button>
          <Button icon={<EyeOutlined />} onClick={markAllAsRead}>
            Mark All as Read
          </Button>
        </Space>
      }
    >
      {/* Filters */}
      <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
        <Space wrap>
          <Space>
            <Text type="secondary" style={{ fontSize: 12 }}>Filter:</Text>
            <Select
              value={filter}
              onChange={setFilter}
              options={[
                { label: 'All', value: 'all' },
                { label: 'Unread', value: 'unread' },
                { label: 'Read', value: 'read' },
              ]}
              size="small"
              style={{ width: 100 }}
            />
          </Space>
          
          <Space>
            <Text type="secondary" style={{ fontSize: 12 }}>Category:</Text>
            <Select
              mode="multiple"
              value={categoryFilter}
              onChange={setCategoryFilter}
              options={categoryOptions}
              size="small"
              style={{ width: 150 }}
              allowClear
            />
          </Space>
          
          <Space>
            <Text type="secondary" style={{ fontSize: 12 }}>Priority:</Text>
            <Select
              mode="multiple"
              value={priorityFilter}
              onChange={setPriorityFilter}
              options={priorityOptions}
              size="small"
              style={{ width: 120 }}
              allowClear
            />
          </Space>
        </Space>
      </div>

      {/* Notifications List */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" />
            <Text type="secondary" style={{ marginLeft: 16 }}>Loading notifications...</Text>
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <BellOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
            <Title level={5} type="secondary">No notifications found</Title>
            <Text type="secondary">Try adjusting your filters</Text>
          </div>
        ) : (
          <List
            dataSource={filteredNotifications}
            renderItem={(notification) => (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                whileHover={{ scale: 1.01 }}
              >
                <List.Item
                  style={{
                    padding: 12,
                    border: 'none',
                    borderBottom: '1px solid #f0f0f0',
                    cursor: 'pointer',
                    background: notification.read ? 'transparent' : 'rgba(24, 144, 255, 0.05)',
                    transition: 'background 0.3s',
                  }}
                  onClick={() => {
                    markAsRead(notification.id);
                    onNotificationClick && onNotificationClick(notification);
                  }}
                >
                  <div style={{ display: 'flex', gap: 12, width: '100%' }}>
                    {/* Icon */}
                    <div
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: 10,
                        background: getTypeColor(notification.type),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        fontSize: 20,
                      }}
                    >
                      {getTypeIcon(notification.type)}
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                        <Text strong style={{ fontSize: 14 }}>
                          {notification.title}
                        </Text>
                        <Text type="secondary" style={{ fontSize: 10 }}>
                          {formatTime(notification.timestamp)}
                        </Text>
                      </div>
                      
                      <Text type="secondary" style={{ fontSize: 13, display: 'block', marginBottom: 8 }}>
                        {notification.message}
                      </Text>

                      {/* Metadata */}
                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
                        <Tag
                          color={getCategoryColor(notification.category)}
                          style={{ fontSize: 10, margin: 0 }}
                        >
                          {getCategoryIcon(notification.category)} {notification.category}
                        </Tag>
                        <Tag
                          color={getPriorityColor(notification.priority)}
                          style={{ fontSize: 10, margin: 0 }}
                        >
                          {notification.priority}
                        </Tag>
                      </div>

                      {/* Actions */}
                      {notification.actions && notification.actions.length > 0 && (
                        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                          {notification.actions.map((action, index) => (
                            <Button
                              key={index}
                              type="link"
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                action.onClick();
                              }}
                              style={{ padding: 0, height: 'auto' }}
                            >
                              {action.label}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Delete Button */}
                    <Tooltip title="Delete notification">
                      <Button
                        type="text"
                        icon={<CloseOutlined />}
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNotification(notification.id);
                        }}
                        style={{ color: '#f5222d' }}
                      />
                    </Tooltip>
                  </div>
                </List.Item>
              </motion.div>
            )}
          />
        )}
      </div>
    </Drawer>
  );
};

export default NotificationCenter;
