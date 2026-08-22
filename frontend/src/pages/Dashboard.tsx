import React, { useState, useEffect } from 'react';
import { Card, Progress, Space, Typography, List, Avatar, Tag, DatePicker, Select, Input } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  UserOutlined,
  ProjectOutlined,
  RobotOutlined,
  SearchOutlined,
  SafetyCertificateOutlined,
  AlertOutlined,
  ThunderboltOutlined,
  DatabaseOutlined,
  GlobalOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Line, Pie } from '@ant-design/plots';
import dayjs from 'dayjs';
import {
  useGraphStats, useSystemHealth, useIOCs, useAlerts, useThreatFeeds,
  useScrapeJobs, useAuditLogs,
} from '../hooks/useApi';
import StatCard from '../components/common/StatCard';
import PageHeader from '../components/common/PageHeader';
import BarList from '../components/common/BarList';

const { Text } = Typography;
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
  const navigate = useNavigate();
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
        return <Tag color="blue">Info</Tag>;
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
    // Legend moves into the Card header (extra) instead of rendering in-plot.
    legend: false as const,
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

  const moduleUsageColors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'];

  const moduleUsageTotal = React.useMemo(
    () => moduleUsage.reduce((sum, item) => sum + item.value, 0),
    [moduleUsage]
  );

  const pieConfig = {
    data: moduleUsage,
    angleField: 'value',
    colorField: 'name',
    radius: 0.8,
    innerRadius: 0.64,
    // Legend and labels move to a simple list below the pie instead of
    // spider/outside labels, which were cramping this card at half width.
    label: false as const,
    legend: false as const,
    statistic: {
      title: {
        content: 'Total',
        style: { fontSize: '12px', color: 'var(--text-color-tertiary)' },
      },
      content: {
        content: moduleUsageTotal.toLocaleString(),
        style: { fontSize: '22px', fontWeight: 600, color: 'var(--text-color)' },
      },
    },
    interactions: [{ type: 'element-active' as const }, { type: 'pie-statistic-active' as const }],
    color: moduleUsageColors,
  };

  // Activity by Module and Data Ingestion render as horizontal BarLists
  // instead of a categorical column/bar chart, which clips half-width cards.
  const activityByModuleItems = React.useMemo(
    () => moduleUsage.map((item, index) => ({
      key: item.name,
      label: item.name,
      value: item.value,
      color: moduleUsageColors[index % moduleUsageColors.length],
    })),
    [moduleUsage]
  );

  // Illustrative ingestion figures - no live ingestion-rate endpoint exists
  // yet, so these are kept exactly as they were, just restyled.
  const dataIngestionItems = [
    { key: 'today', label: 'Today', value: 1245 },
    { key: 'yesterday', label: 'Yesterday', value: 1189 },
    { key: 'this-week', label: 'This Week', value: 8456 },
    { key: 'last-week', label: 'Last Week', value: 7834 },
    { key: 'this-month', label: 'This Month', value: 35214 },
    { key: 'last-month', label: 'Last Month', value: 31567 },
  ];

  const filteredActivity = recentActivity.filter(activity => {
    if (filter !== 'all' && activity.type !== filter) return false;
    if (search && !activity.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  // Presentation only - the underlying headroom calc (systemStats.systemHealth)
  // is unchanged.
  const healthLabel = systemStats.systemHealth > 80 ? 'Healthy' : systemStats.systemHealth > 50 ? 'Degraded' : 'Critical';
  const healthStrokeColor = systemStats.systemHealth > 80 ? 'var(--success-color)' : systemStats.systemHealth > 50 ? 'var(--warning-color)' : 'var(--error-color)';

  const platformFeatures = [
    { key: 'graph', icon: <ProjectOutlined style={{ color: '#1890ff' }} />, title: 'Graph Analytics Engine', tagColor: 'blue', count: 6 },
    { key: 'ai', icon: <RobotOutlined style={{ color: '#52c41a' }} />, title: 'AI/ML Insights', tagColor: 'green', count: 7 },
    { key: 'scraping', icon: <SearchOutlined style={{ color: '#faad14' }} />, title: 'Distributed Scraping', tagColor: 'orange', count: 9 },
    { key: 'security', icon: <SafetyCertificateOutlined style={{ color: '#f5222d' }} />, title: 'Enterprise Security', tagColor: 'red', count: 7 },
    { key: 'threat', icon: <AlertOutlined style={{ color: '#722ed1' }} />, title: 'Threat Intelligence', tagColor: 'purple', count: 8 },
  ];

  const capabilityHighlights = [
    'Real-time graph analysis',
    'Distributed scraping at scale',
    'AI-powered anomaly detection',
    'Role-based access control',
    'Real-time threat intelligence',
    'Interactive visualizations',
  ];

  return (
    <div className="ol-page-body">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <PageHeader
          icon={<NodeIndexOutlined />}
          title="Dashboard"
          subtitle="Welcome back! Here's an overview of your OpenLens platform."
          actions={
            <RangePicker
              value={dateRange}
              onChange={setDateRange}
              disabledDate={(current) => current && current > dayjs().endOf('day')}
            />
          }
        />
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="ol-stats-grid">
          <StatCard
            label="Total Nodes"
            value={systemStats.totalNodes.toLocaleString()}
            icon={<NodeIndexOutlined />}
            accent="primary"
          />
          <StatCard
            label="Total Relationships"
            value={systemStats.totalRelationships.toLocaleString()}
            icon={<BranchesOutlined />}
            accent="success"
          />
          <StatCard
            label="Active Users"
            value="—"
            subLabel="not reported"
            icon={<UserOutlined />}
            accent="warning"
          />
          <StatCard
            label="Scrape Jobs"
            value={systemStats.activeScrapeJobs}
            icon={<SearchOutlined />}
            accent="purple"
          />
          <StatCard
            label="Threat Feeds"
            value={systemStats.threatFeeds}
            icon={<GlobalOutlined />}
            accent="primary"
          />
          <StatCard
            label="IOCs"
            value={systemStats.iocs.toLocaleString()}
            icon={<DatabaseOutlined />}
            accent="error"
          />
          <StatCard
            label="Alerts"
            value={systemStats.alerts}
            icon={<AlertOutlined />}
            accent="warning"
          />
          <Card bodyStyle={{ padding: '20px 24px', minHeight: 120, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <span style={{ fontSize: 14, color: 'var(--text-color-tertiary)' }}>System Health</span>
            <div className="ol-dial-card" style={{ flex: 1 }}>
              <Progress
                type="circle"
                percent={systemHealth?.resources?.cpu_usage || systemStats.systemHealth}
                status={systemStats.systemHealth > 80 ? 'success' : systemStats.systemHealth > 50 ? 'normal' : 'exception'}
                strokeColor={healthStrokeColor}
                size={64}
              />
              <div>
                <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-color)' }}>{healthLabel}</div>
                <div style={{ fontSize: 12, color: 'var(--text-color-tertiary)', marginTop: 2 }}>CPU · Mem · Disk</div>
              </div>
            </div>
          </Card>
        </div>
      </motion.div>

      {/* Charts Row */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="ol-row-2-1">
          <Card
            title="Graph Growth Trends"
            extra={
              <Space size={16}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-color-secondary)' }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#1890ff', display: 'inline-block' }} />
                  Nodes
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-color-secondary)' }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#52c41a', display: 'inline-block' }} />
                  Relationships
                </span>
              </Space>
            }
          >
            <Line {...(lineConfig as any)} />
          </Card>
          <Card title="Module Usage">
            <Pie {...pieConfig} />
            <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {moduleUsage.map((item, index) => (
                <div key={item.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: moduleUsageColors[index % moduleUsageColors.length], flexShrink: 0 }} />
                  <span style={{ flex: 1, color: 'var(--text-color-secondary)' }}>{item.name}</span>
                  <span style={{ fontVariantNumeric: 'tabular-nums', color: 'var(--text-color)' }}>{item.value.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <div className="ol-row-2up">
          <Card title="Activity by Module">
            <BarList items={activityByModuleItems} labelWidth={100} />
          </Card>
          <Card title="Data Ingestion">
            <BarList items={dataIngestionItems} labelWidth={100} />
          </Card>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <div className="ol-section">
          <h2 className="ol-section-title">Quick Actions</h2>
          <div className="ol-row-quarter">
            {mockQuickActions.map((action) => (
              <Card
                key={action.key}
                className="ol-action-card"
                style={{ ['--ol-action-accent']: action.color } as React.CSSProperties}
                onClick={() => navigate(action.path)}
                bodyStyle={{ padding: 24, textAlign: 'center' }}
              >
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: `${action.color}1A`,
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
                <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8, color: 'var(--text-color)' }}>
                  {action.title}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-color-tertiary)' }}>{action.description}</div>
              </Card>
            ))}
          </div>
        </div>
      </motion.div>

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
                        {item.timestamp} · {item.user}
                      </Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      </motion.div>

      {/* System Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <div className="ol-section">
          <h2 className="ol-section-title">System Overview</h2>
          <div className="ol-row-2up">
            <Card title="Platform Features">
              {platformFeatures.map((feature, index) => (
                <div
                  key={feature.key}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    padding: '12px 0',
                    borderBottom: index < platformFeatures.length - 1 ? '1px solid var(--border-color-secondary)' : 'none',
                  }}
                >
                  {feature.icon}
                  <Text strong style={{ flex: 1 }}>{feature.title}</Text>
                  <Tag color={feature.tagColor}>{feature.count} Modules</Tag>
                </div>
              ))}
            </Card>
            <Card title="Capability Highlights">
              {capabilityHighlights.map((highlight, index) => (
                <div
                  key={highlight}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    padding: '12px 0',
                    borderBottom: index < capabilityHighlights.length - 1 ? '1px solid var(--border-color-secondary)' : 'none',
                  }}
                >
                  <CheckCircleOutlined style={{ color: 'var(--success-color)' }} />
                  <Text>{highlight}</Text>
                </div>
              ))}
            </Card>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
