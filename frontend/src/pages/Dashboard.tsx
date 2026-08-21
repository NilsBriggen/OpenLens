import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Progress, Space, Typography, List, Avatar, Tag, Divider, DatePicker, Select, Input } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  UserOutlined,
  ProjectOutlined,
  RobotOutlined,
  SearchOutlined,
  SafetyCertificateOutlined,
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
  FilterOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Line, Bar, Pie, Column } from '@ant-design/plots';
import dayjs from 'dayjs';
import {
  useGraphStats, useSystemHealth, useIOCs, useAlerts, useThreatFeeds,
  useScrapeJobs, useAuditLogs,
} from '../hooks/useApi';

const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;
const { Search } = Input;


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

  // Live data - no mock seeds. Missing numbers render as 0 / empty states.
  const { data: graphStats, isLoading: statsLoading } = useGraphStats();
  const { data: systemHealth, isLoading: healthLoading } = useSystemHealth();
  const { data: iocs = [] } = useIOCs({ limit: 1000 });
  const { data: alerts = [] } = useAlerts({ limit: 1000 });
  const { data: feeds = [] } = useThreatFeeds();
  const { data: jobs = [] } = useScrapeJobs();
  const { data: auditLogs = [] } = useAuditLogs(50);

  const healthPercent = React.useMemo(() => {
    const resources = (systemHealth as any)?.resources;
    if (!resources) return 0;
    // Health = headroom: 100 minus the worst of CPU/memory/disk pressure.
    const worst = Math.max(resources.cpu_usage ?? 0,
                           resources.memory_usage ?? 0,
                           resources.disk_usage ?? 0);
    return Math.max(0, Math.round((100 - worst) * 10) / 10);
  }, [systemHealth]);

  const systemStats = React.useMemo(() => ({
    totalNodes: graphStats?.nodeCount ?? 0,
    totalRelationships: graphStats?.edgeCount ?? 0,
    activeScrapeJobs: jobs.filter(j => j.status === 'running' || j.status === 'pending').length,
    threatFeeds: feeds.length,
    iocs: iocs.length,
    alerts: alerts.filter(a => a.status === 'new' || a.status === 'acknowledged').length,
    systemHealth: healthPercent,
  }), [graphStats, jobs, feeds, iocs, alerts, healthPercent]);

  // Plain values only: React elements in chart data recurse forever inside
  // the chart library's deepClone.
  const moduleUsage = React.useMemo(() => ([
    { name: 'Graph nodes', value: systemStats.totalNodes },
    { name: 'IOCs', value: systemStats.iocs },
    { name: 'Scrape jobs', value: jobs.length },
    { name: 'Alerts', value: alerts.length },
    { name: 'Feeds', value: systemStats.threatFeeds },
  ]), [systemStats, jobs.length, alerts.length]);

  const recentActivity = React.useMemo(() => auditLogs.map((event, index) => ({
    id: event.id || String(index),
    type: event.eventType || 'system',
    title: `${event.action || event.eventType || 'event'} ${event.resource || ''}`.trim(),
    description: event.username ? `by ${event.username}` : '',
    timestamp: event.timestamp || '',
    status: event.severity === 'error' ? 'error'
      : event.severity === 'warning' ? 'warning' : 'info',
    user: event.username || 'system',
  })), [auditLogs]);

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
        return <SafetyCertificateOutlined />;
      default:
        return <NodeIndexOutlined />;
    }
  };

  const lineConfig = {
    // Long format: one row per series per date. A multi-series Line needs a
    // single yField plus a seriesField - passing an array of yFields makes G2
    // build shapes the 'path-in' appear animation cannot measure, which throws
    // "element.getTotalLength is not a function" and takes the page down.
    // No trend-history endpoint exists yet; chart the current totals only.
    data: [
      { date: 'now', type: 'Nodes', value: systemStats.totalNodes },
      { date: 'now', type: 'Relationships', value: systemStats.totalRelationships },
    ],
    xField: 'date',
    yField: 'value',
    seriesField: 'type',
    color: ['#1890ff', '#52c41a'],
    legend: {
      position: 'top-right' as const,
    },
    smooth: true,
    // No 'path-in' appear animation here: it measures the element with
    // getTotalLength(), which the point markers rendered below are not, so it
    // throws during the first draw. G2's default appear animation is
    // shape-appropriate.
    style: {
      lineWidth: 3,
    },
    point: {
      size: 5,
      shape: 'diamond' as const,
    },
  };

  const barConfig = {
    data: moduleUsage,
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
    data: moduleUsage,
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

  const filteredActivity = recentActivity.filter(activity => {
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
            value={'—'}
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
                status={systemStats.systemHealth > 80 ? 'success' : systemStats.systemHealth > 50 ? 'normal' : 'exception'}
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
              <Line {...(lineConfig as any)} />
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
              <Bar {...(barConfig as any)} />
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
                  <SafetyCertificateOutlined style={{ color: '#f5222d' }} />
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

export default Dashboard;
