import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Typography, Space, Button, Statistic, Tag, List, Avatar, Spin, Alert, Divider } from 'antd';
import {
  DashboardOutlined,
  SyncOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { useWebSocket } from '../contexts';
import MetricCard from '../components/charts/MetricCard';
import QuickStats from '../components/QuickStats';

const { Title, Text } = Typography;

interface RealTimeEvent {
  id: string;
  type: 'threat' | 'scraping' | 'ai' | 'system' | 'security';
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  data?: any;
}

const RealTimeDashboard: React.FC = () => {
  const { isConnected, messages, subscribe, unsubscribe } = useWebSocket();
  const [events, setEvents] = useState<RealTimeEvent[]>([]);
  const [stats, setStats] = useState({
    threats: 0,
    scrapes: 0,
    anomalies: 0,
    users: 0,
  });
  const [loading, setLoading] = useState(true);

  // Mock initial data
  const mockEvents: RealTimeEvent[] = [
    {
      id: '1',
      type: 'threat',
      title: 'New IOC Detected',
      message: 'Malicious IP 192.168.1.100 detected in network traffic',
      severity: 'high',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      data: { ip: '192.168.1.100', source: 'AlienVault' },
    },
    {
      id: '2',
      type: 'scraping',
      title: 'Scrape Job Completed',
      message: 'Successfully scraped 150 URLs from social media',
      severity: 'low',
      timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      data: { jobId: 'job-123', success: 150, failed: 5 },
    },
    {
      id: '3',
      type: 'ai',
      title: 'Anomaly Detected',
      message: 'Statistical anomaly detected in graph data',
      severity: 'medium',
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      data: { nodeId: 'node-456', score: 9.5 },
    },
    {
      id: '4',
      type: 'system',
      title: 'High CPU Usage',
      message: 'CPU usage is at 85% - Consider scaling resources',
      severity: 'medium',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      data: { cpu: 85, memory: 72 },
    },
    {
      id: '5',
      type: 'security',
      title: 'New User Login',
      message: 'User admin logged in from new location',
      severity: 'low',
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      data: { username: 'admin', location: 'New York' },
    },
  ];

  // Initialize
  useEffect(() => {
    setLoading(true);
    setEvents(mockEvents);
    setStats({
      threats: 12,
      scrapes: 45,
      anomalies: 8,
      users: 42,
    });
    setLoading(false);

    // Subscribe to real-time channels
    subscribe('threat-events');
    subscribe('scraping-events');
    subscribe('ai-events');
    subscribe('system-events');
    subscribe('security-events');

    return () => {
      unsubscribe('threat-events');
      unsubscribe('scraping-events');
      unsubscribe('ai-events');
      unsubscribe('system-events');
      unsubscribe('security-events');
    };
  }, [subscribe, unsubscribe]);

  // Process WebSocket messages
  useEffect(() => {
    if (messages.length > 0) {
      const newEvents = messages.map(msg => ({
        id: msg.timestamp || Date.now().toString(),
        type: msg.type || 'system',
        title: msg.data?.title || msg.type || 'Event',
        message: msg.data?.message || JSON.stringify(msg.data),
        severity: msg.data?.severity || 'low',
        timestamp: msg.timestamp || new Date().toISOString(),
        data: msg.data,
      }));
      
      setEvents(prev => [...(newEvents as RealTimeEvent[]), ...prev].slice(0, 50));
    }
  }, [messages]);

  // Get icon for event type
  const getEventIcon = (type: string) => {
    switch (type) {
      case 'threat': return <ThunderboltOutlined style={{ color: '#f5222d' }} />;
      case 'scraping': return <DashboardOutlined style={{ color: '#52c41a' }} />;
      case 'ai': return <WarningOutlined style={{ color: '#fa8c16' }} />;
      case 'system': return <SyncOutlined style={{ color: '#1890ff' }} />;
      case 'security': return <CloseCircleOutlined style={{ color: '#722ed1' }} />;
      default: return <InfoCircleOutlined />;
    }
  };

  // Get color for severity
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#f5222d';
      case 'high': return '#fa8c16';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#d9d9d9';
    }
  };

  // Format time
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  // Format relative time
  const formatRelativeTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  // Refresh data
  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <Row gutter={24} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Space>
            <Title level={2} style={{ margin: 0 }}>
              <ClockCircleOutlined style={{ marginRight: 8 }} />
              Real-Time Dashboard
            </Title>
            <Tag color={isConnected ? '#52c41a' : '#f5222d'}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Tag>
          </Space>
          <Text type="secondary">Live updates from all OpenLens modules</Text>
        </Col>
      </Row>

      {/* Quick Stats */}
      <QuickStats
        stats={[
          {
            key: 'threats',
            title: 'Active Threats',
            value: stats.threats,
            icon: <ThunderboltOutlined />,
            trend: 'up',
            trendValue: '+12%',
            color: '#f5222d',
            tooltip: 'Number of active threat indicators',
          },
          {
            key: 'scrapes',
            title: 'Active Scrapes',
            value: stats.scrapes,
            icon: <DashboardOutlined />,
            trend: 'up',
            trendValue: '+8%',
            color: '#52c41a',
            tooltip: 'Number of active scraping jobs',
          },
          {
            key: 'anomalies',
            title: 'Anomalies',
            value: stats.anomalies,
            icon: <WarningOutlined />,
            trend: 'down',
            trendValue: '-5%',
            color: '#fa8c16',
            tooltip: 'Number of detected anomalies',
          },
          {
            key: 'users',
            title: 'Active Users',
            value: stats.users,
            icon: <CheckCircleOutlined />,
            trend: 'up',
            trendValue: '+2',
            color: '#1890ff',
            tooltip: 'Number of active users',
          },
        ]}
      />

      <Divider style={{ margin: '24px 0' }} />

      {/* Real-Time Events */}
      <Row gutter={24}>
        <Col span={24}>
          <Card
            title={
              <Space>
                <ClockCircleOutlined />
                Real-Time Events
              </Space>
            }
            extra={
              <Button icon={<SyncOutlined />} onClick={handleRefresh} loading={loading}>
                Refresh
              </Button>
            }
            bodyStyle={{ padding: 0 }}
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Spin size="large" />
                <Text type="secondary" style={{ marginLeft: 16 }}>Loading events...</Text>
              </div>
            ) : events.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Alert message="No events yet" type="info" showIcon />
              </div>
            ) : (
              <List
                dataSource={events}
                renderItem={(event) => (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <List.Item
                      style={{
                        padding: 16,
                        border: 'none',
                        borderBottom: '1px solid #f0f0f0',
                      }}
                    >
                      <div style={{ display: 'flex', gap: 16, width: '100%' }}>
                        {/* Icon */}
                        <div
                          style={{
                            width: 40,
                            height: 40,
                            borderRadius: 8,
                            background: getSeverityColor(event.severity),
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0,
                            fontSize: 20,
                          }}
                        >
                          {getEventIcon(event.type)}
                        </div>

                        {/* Content */}
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                            <Text strong style={{ fontSize: 14 }}>
                              {event.title}
                            </Text>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              {formatTime(event.timestamp)}
                            </Text>
                          </div>
                          
                          <Text type="secondary" style={{ fontSize: 13, display: 'block', marginBottom: 8 }}>
                            {event.message}
                          </Text>

                          {/* Metadata */}
                          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                            <Tag
                              color={getSeverityColor(event.severity)}
                              style={{ fontSize: 10, margin: 0 }}
                            >
                              {event.severity.toUpperCase()}
                            </Tag>
                            <Tag
                              color="blue"
                              style={{ fontSize: 10, margin: 0 }}
                            >
                              {event.type}
                            </Tag>
                            <Text type="secondary" style={{ fontSize: 10 }}>
                              {formatRelativeTime(event.timestamp)}
                            </Text>
                          </div>
                        </div>
                      </div>
                    </List.Item>
                  </motion.div>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>

      <Divider style={{ margin: '24px 0' }} />

      {/* Module Status */}
      <Row gutter={24}>
        <Col span={24}>
          <Title level={4} style={{ margin: 0, marginBottom: 16 }}>
            Module Status
          </Title>
        </Col>
        
        {[
          { name: 'Graph Engine', status: 'active', lastUpdate: '5s ago', color: '#52c41a' },
          { name: 'AI Analytics', status: 'active', lastUpdate: '15s ago', color: '#52c41a' },
          { name: 'Scraping Hub', status: 'active', lastUpdate: '30s ago', color: '#52c41a' },
          { name: 'Threat Intelligence', status: 'active', lastUpdate: '1m ago', color: '#52c41a' },
          { name: 'Security Center', status: 'active', lastUpdate: '2m ago', color: '#52c41a' },
        ].map((module, index) => (
          <Col key={module.name} xs={24} sm={12} lg={8}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card size="small">
                <Space>
                  <div
                    style={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      background: module.color,
                    }}
                  />
                  <Text strong>{module.name}</Text>
                </Space>
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Status: {module.status}
                  </Text>
                </div>
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Last update: {module.lastUpdate}
                  </Text>
                </div>
              </Card>
            </motion.div>
          </Col>
        ))}
      </Row>
    </motion.div>
  );
};

export default RealTimeDashboard;
