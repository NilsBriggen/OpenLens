import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Progress, Space, Typography, List, Avatar, Tag, Divider, DatePicker, Select, Input } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  UserOutlined,
  ProjectOutlined,
  RobotOutlined,
  SearchOutlined,
  ShieldOutlined,
  AlertOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  DatabaseOutlined,
  GlobalOutlined,
  SafetyOutlined,
  FileTextOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  ClusterOutlined,
  FilterOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Line, Bar, Pie, Column } from '@ant-design/plots';
import dayjs from 'dayjs';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';

const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;
const { Search } = Input;

// API Service
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${Cookies.get('access_token')}`,
  },
});

// Mock data for development
const mockStats = {
  totalNodes: 12453,
  totalRelationships: 87342,
  activeUsers: 42,
  activeScrapeJobs: 18,
  threatFeeds: 24,
  iocs: 1567,
  alerts: 34,
  systemHealth: 98.5,
};

const mockTrends = {
  nodes: [12000, 12100, 12200, 12300, 12400, 12453],
  relationships: [80000, 82000, 84000, 85000, 86000, 87342],
  users: [35, 38, 40, 41, 42, 42],
  dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
};

const mockModuleUsage = [
  { name: 'Graph Analytics', value: 35, icon: <ProjectOutlined /> },
  { name: 'AI/ML', value: 25, icon: <RobotOutlined /> },
  { name: 'Scraping', value: 20, icon: <SearchOutlined /> },
  { name: 'Security', value: 12, icon: <ShieldOutlined /> },
  { name: 'Threat Intel', value: 8, icon: <AlertOutlined /> },
];

const mockRecentActivity = [
  {
    id: 1,
    type: 'scrape',
    title: 'Scraped 150 URLs',
    description: 'Distributed scraping job completed',
    timestamp: '2024-01-15 14:30:00',
    status: 'success',
    user: 'admin',
  },
  {
    id: 2,
    type: 'threat',
    title: 'New IOC Detected',
    description: 'Malicious IP address identified',
    timestamp: '2024-01-15 13:45:00',
    status: 'warning',
    user: 'system',
  },
  {
    id: 3,
    type: 'ai',
    title: 'Anomaly Detected',
    description: 'Statistical anomaly found in network traffic',
    timestamp: '2024-01-15 12:15:00',
    status: 'error',
    user: 'admin',
  },
  {
    id: 4,
    type: 'graph',
    title: 'New Connections',
    description: '123 new relationships added',
    timestamp: '2024-01-15 10:00:00',
    status: 'success',
    user: 'system',
  },
  {
    id: 5,
    type: 'security',
    title: 'User Login',
    description: 'Admin logged in from new location',
    timestamp: '2024-01-15 09:30:00',
    status: 'info',
    user: 'admin',
  },
];

const mockQuickActions = [
  {
    key: 'new-scrape',
    title: 'New Scrape Job',
    description: 'Start a new distributed scraping job',
    icon: <SearchOutlined />,
    color: '#1890ff',
    path: '/scraping',
  },
  {
    key: 'analyze-graph',
    title: 'Analyze Graph',
    description: 'Run network analysis on the graph',
    icon: <ProjectOutlined />,
    color: '#52c41a',
    path: '/graph',
  },
  {
    key: 'threat-hunt',
    title: 'Threat Hunt',
    description: 'Start a new threat hunting session',
    icon: <AlertOutlined />,
    color: '#faad14',
    path: '/threat',
  },
  {
    key: 'detect-anomalies',
    title: 'Detect Anomalies',
    description: 'Run anomaly detection on the data',
    icon: <ThunderboltOutlined />,
    color: '#f5222d',
    path: '/ai',
  },
];

const Dashboard: React.FC = () => {
  const [dateRange, setDateRange] = useState<any>([dayjs().subtract(7, 'day'), dayjs()]);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  // Fetch system stats
  const { data: systemStats, isLoading: statsLoading } = useQuery({
    queryKey: ['system-stats'],
    queryFn: async () => {
      const response = await api.get('/api/system/stats');
      return response.data;
    },
    initialData: mockStats,
  });

  // Fetch system health
  const { data: systemHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: async () => {
      const response = await api.get('/api/system/health');
      return response.data;
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return '#52c41a';
      case 'warning':
        return '#faad14';
      case 'error':
        return '#f5222d';
      case 'info':
        return '#1890ff';
      default:
        return '#d9d9d9';
    }
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'success':
        return <Tag color="success">Success</Tag>;
      case 'warning':
        return <Tag color="warning">Warning</Tag>;
      case 'error':
        return <Tag color="error">Error</Tag>;
      case 'info':
        return <Tag color="info">Info</Tag>;
      default:
        return <Tag>Unknown</Tag>;
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'scrape':
        return <SearchOutlined />;
      case 'threat':
        return <AlertOutlined />;
      case 'ai':
        return <RobotOutlined />;
      case 'graph':
        return <ProjectOutlined />;
      case 'security':
        return <ShieldOutlined />;
      default:
        return <NodeIndexOutlined />;
    }
  };

  const lineConfig = {
    data: mockTrends.dates.map((date, index) => ({
      date,
      Nodes: mockTrends.nodes[index],
      Relationships: mockTrends.relationships[index],
    })),
    xField: 'date',
    yField: ['Nodes', 'Relationships'],
    seriesField: 'type',
    color: ['#1890ff', '#52c41a'],
    legend: {
      position: 'top-right' as const,
    },
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    style: {
      lineWidth: 3,
    },
    point: {
      size: 5,
      shape: 'diamond' as const,
    },
  };

  const barConfig = {
    data: mockModuleUsage,
    xField: 'name',
    yField: 'value',
    seriesField: 'name',
    color: ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'],
    legend: false,
    label: {
      position: 'top' as const,
      style: {
        fill: '#fff',
        fontWeight: 'bold',
      },
    },
    xAxis: {
      label: {
        autoRotate: false,
      },
    },
    yAxis: {
      grid: {
        line: {
          style: {
            stroke: '#f0f0f0',
          },
        },
      },
    },
    columnStyle: {
      radius: [4, 4, 0, 0],
    },
  };

  const pieConfig = {
    data: mockModuleUsage,
    angleField: 'value',
    colorField: 'name',
    radius: 0.8,
    label: {
      type: 'spider' as const,
      labelHeight: 28,
      content: '{name}\n{percentage}' as const,
      style: {
        fontSize: 12,
      },
    },
    interactions: [{ type: 'element-active' as const }, { type: 'pie-statistic-active' as const }],
    color: ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'],
  };

  const columnConfig = {
    data: [
      { type: 'Today', value: 1245 },
      { type: 'Yesterday', value: 1189 },
      { type: 'This Week', value: 8456 },
      { type: 'Last Week', value: 7834 },
      { type: 'This Month', value: 35214 },
      { type: 'Last Month', value: 31567 },
    ],
    xField: 'type',
    yField: 'value',
    color: '#1890ff',
    columnStyle: {
      radius: [4, 4, 0, 0],
    },
    label: {
      position: 'top' as const,
      style: {
        fill: '#1890ff',
        fontWeight: 'bold',
      },
    },
    xAxis: {
      label: {
        autoRotate: false,
      },
    },
  };

  const filteredActivity = mockRecentActivity.filter(activity => {
    if (filter !== 'all' && activity.type !== filter) return false;
    if (search && !activity.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="dashboard-page">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="page-header"
      >
        <div>
          <Title level={1}>
            <Space>
              <NodeIndexOutlined />
              Dashboard
            </Space>
          </Title>
          <Paragraph type="secondary">
            Welcome back! Here's an overview of your OpenLens platform.
          </Paragraph>
        </div>
        <Space>
          <RangePicker
            value={dateRange}
            onChange={setDateRange}
            disabledDate={(current) => current && current > dayjs().endOf('day')}
          />
        </Space>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="metrics-dashboard"
      >
        <Card>
          <Statistic
            title="Total Nodes"
            value={systemStats.totalNodes.toLocaleString()}
            prefix={<NodeIndexOutlined style={{ color: '#1890ff' }} />}
            suffix={<ArrowUpOutlined style={{ color: '#52c41a' }} />}
          />
        </Card>
        
        <Card>
          <Statistic
            title="Total Relationships"
            value={systemStats.totalRelationships.toLocaleString()}
            prefix={<BranchesOutlined style={{ color: '#52c41a' }} />}
            suffix={<ArrowUpOutlined style={{ color: '#52c41a' }} />}
          />
        </Card>
        
        <Card>
          <Statistic
            title="Active Users"
            value={systemStats.activeUsers}
            prefix={<UserOutlined style={{ color: '#faad14' }} />}
            suffix={<ArrowUpOutlined style={{ color: '#52c41a' }} />}
          />
        </Card>
        
        <Card>
          <Statistic
            title="Scrape Jobs"
            value={systemStats.activeScrapeJobs}
            prefix={<SearchOutlined style={{ color: '#722ed1' }} />}
            suffix={<ArrowDownOutlined style={{ color: '#f5222d' }} />}
          />
        </Card>
        
        <Card>
          <Statistic
            title="Threat Feeds"
            value={systemStats.threatFeeds}
            prefix={<GlobalOutlined style={{ color: '#1890ff' }} />}
            suffix={<ArrowUpOutlined style={{ color: '#52c41a' }} />}
          />
        </Card>
        
        <Card>
          <Statistic
            title="IOCs"
            value={systemStats.iocs.toLocaleString()}
            prefix={<DatabaseOutlined style={{ color: '#f5222d' }} />}
            suffix={<ArrowUpOutlined style={{ color: '#52c41a' }} />}
          />
        </Card>
        
        <Card>
          <Statistic
            title="Alerts"
            value={systemStats.alerts}
            prefix={<AlertOutlined style={{ color: '#faad14' }} />}
            suffix={<ArrowUpOutlined style={{ color: '#f5222d' }} />}
          />
        </Card>
        
        <Card>
          <div style={{ textAlign: 'center' }}>
            <Text type="secondary">System Health</Text>
            <div style={{ marginTop: 8 }}>
              <Progress
                type="circle"
                percent={systemHealth?.resources?.cpu_usage || systemStats.systemHealth}
                status={systemStats.systemHealth > 80 ? 'success' : systemStats.systemHealth > 50 ? 'warning' : 'exception'}
                strokeColor={systemStats.systemHealth > 80 ? '#52c41a' : systemStats.systemHealth > 50 ? '#faad14' : '#f5222d'}
              />
            </div>
          </div>
        </Card>
      </motion.div>

      <Divider />

      {/* Charts Row */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Row gutter={24}>
          <Col xs={24} lg={16}>
            <Card title="Graph Growth Trends">
              <Line {...lineConfig} />
            </Card>
          </Col>
          <Col xs={24} lg={8}>
            <Card title="Module Usage">
              <Pie {...pieConfig} />
            </Card>
          </Col>
        </Row>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        style={{ marginTop: 24 }}
      >
        <Row gutter={24}>
          <Col xs={24} lg={12}>
            <Card title="Activity by Module">
              <Bar {...barConfig} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Data Ingestion">
              <Column {...columnConfig} />
            </Card>
          </Col>
        </Row>
      </motion.div>

      <Divider />

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Title level={3} style={{ marginBottom: 24 }}>
          Quick Actions
        </Title>
        <Row gutter={24}>
          {mockQuickActions.map((action) => (
            <Col xs={24} sm={12} lg={6} key={action.key}>
              <motion.div
                whileHover={{ scale: 1.02, y: -4 }}
                whileTap={{ scale: 0.98 }}
                transition={{ duration: 0.2 }}
              >
                <Card
                  style={{ cursor: 'pointer', border: `2px solid ${action.color}20` }}
                  onClick={() => window.location.href = action.path}
                  bodyStyle={{ padding: 24, textAlign: 'center' }}
                >
                  <div
                    style={{
                      width: 48,
                      height: 48,
                      borderRadius: 12,
                      background: `${action.color}20`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto 16px',
                      fontSize: 24,
                      color: action.color,
                    }}
                  >
                    {action.icon}
                  </div>
                  <Title level={5} style={{ margin: 0, marginBottom: 8 }}>
                    {action.title}
                  </Title>
                  <Text type="secondary">{action.description}</Text>
                </Card>
              </motion.div>
            </Col>
          ))}
        </Row>
      </motion.div>

      <Divider />

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <Card
          title="Recent Activity"
          extra={
            <Space>
              <Select
                value={filter}
                onChange={setFilter}
                style={{ width: 120 }}
                size="small"
              >
                <Option value="all">All Types</Option>
                <Option value="scrape">Scraping</Option>
                <Option value="threat">Threat</Option>
                <Option value="ai">AI</Option>
                <Option value="graph">Graph</Option>
                <Option value="security">Security</Option>
              </Select>
              <Search
                placeholder="Search activity..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                size="small"
                style={{ width: 200 }}
              />
            </Space>
          }
        >
          <List
            dataSource={filteredActivity}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  avatar={
                    <Avatar
                      icon={getIcon(item.type)}
                      style={{ background: getStatusColor(item.status) }}
                    />
                  }
                  title={
                    <Space>
                      {item.title}
                      {getStatusTag(item.status)}
                    </Space>
                  }
                  description={
                    <div>
                      <Text type="secondary">{item.description}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {item.timestamp} • {item.user}
                      </Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      </motion.div>

      <Divider />

      {/* System Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Title level={3} style={{ marginBottom: 24 }}>
          System Overview
        </Title>
        <Row gutter={24}>
          <Col xs={24} lg={12}>
            <Card title="Platform Features">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <ProjectOutlined style={{ color: '#1890ff' }} />
                  <Text strong>Graph Analytics Engine</Text>
                  <Tag color="blue">6 Modules</Tag>
                </Space>
                <Space>
                  <RobotOutlined style={{ color: '#52c41a' }} />
                  <Text strong>AI/ML Insights</Text>
                  <Tag color="green">7 Modules</Tag>
                </Space>
                <Space>
                  <SearchOutlined style={{ color: '#faad14' }} />
                  <Text strong>Distributed Scraping</Text>
                  <Tag color="orange">9 Modules</Tag>
                </Space>
                <Space>
                  <ShieldOutlined style={{ color: '#f5222d' }} />
                  <Text strong>Enterprise Security</Text>
                  <Tag color="red">7 Modules</Tag>
                </Space>
                <Space>
                  <AlertOutlined style={{ color: '#722ed1' }} />
                  <Text strong>Threat Intelligence</Text>
                  <Tag color="purple">8 Modules</Tag>
                </Space>
              </Space>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Capability Highlights">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text>Real-time graph analysis</Text>
                </Space>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text>Distributed scraping at scale</Text>
                </Space>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text>AI-powered anomaly detection</Text>
                </Space>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text>Role-based access control</Text>
                </Space>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text>Real-time threat intelligence</Text>
                </Space>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text>Interactive visualizations</Text>
                </Space>
              </Space>
            </Card>
          </Col>
        </Row>
      </motion.div>
    </div>
  );
};

// Temporary icon
const CheckCircleOutlined = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);

export default Dashboard;
