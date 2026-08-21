import React, { useState, useEffect } from 'react';
import { Card, Tabs, Button, Space, Typography, Row, Col, Divider, Modal, Form, Input, Select, Table, Tag, Progress, Alert, Spin, DatePicker, Steps, List, Avatar, Tooltip } from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  GlobalOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
  ExportOutlined,
  ImportOutlined,
  SettingOutlined,
  SyncOutlined,
  FilterOutlined,
  DatabaseOutlined,
  CodeOutlined,
  ShareAltOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Line, Bar, Pie } from '@ant-design/plots';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { Step } = Steps;

// API Service
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${Cookies.get('access_token')}`,
  },
});

// Mock data
const mockJobs = [
  {
    id: 'job-1',
    name: 'Social Media Scrape',
    status: 'completed',
    urls: ['https://twitter.com/user1', 'https://facebook.com/page1'],
    depth: 2,
    progress: 100,
    successCount: 150,
    failedCount: 5,
    startTime: '2024-01-15T14:30:00Z',
    endTime: '2024-01-15T15:45:00Z',
    duration: 45 * 60 * 1000,
    useProxy: true,
    useCache: true,
    renderJs: false,
  },
  {
    id: 'job-2',
    name: 'E-commerce Product Scrape',
    status: 'running',
    urls: ['https://amazon.com/products'],
    depth: 3,
    progress: 65,
    successCount: 89,
    failedCount: 2,
    startTime: '2024-01-15T13:00:00Z',
    endTime: null,
    duration: null,
    useProxy: true,
    useCache: true,
    renderJs: true,
  },
  {
    id: 'job-3',
    name: 'News Aggregation',
    status: 'queued',
    urls: ['https://news.com', 'https://bbc.com'],
    depth: 1,
    progress: 0,
    successCount: 0,
    failedCount: 0,
    startTime: null,
    endTime: null,
    duration: null,
    useProxy: false,
    useCache: true,
    renderJs: false,
  },
  {
    id: 'job-4',
    name: 'Competitor Analysis',
    status: 'failed',
    urls: ['https://competitor.com'],
    depth: 2,
    progress: 30,
    successCount: 12,
    failedCount: 8,
    startTime: '2024-01-15T10:00:00Z',
    endTime: '2024-01-15T10:30:00Z',
    duration: 30 * 60 * 1000,
    useProxy: true,
    useCache: false,
    renderJs: true,
  },
  {
    id: 'job-5',
    name: 'Blog Content Scrape',
    status: 'paused',
    urls: ['https://blog.com'],
    depth: 2,
    progress: 45,
    successCount: 42,
    failedCount: 3,
    startTime: '2024-01-15T09:00:00Z',
    endTime: null,
    duration: null,
    useProxy: true,
    useCache: true,
    renderJs: false,
  },
];

const mockProxies = [
  {
    id: 'proxy-1',
    address: '192.168.1.100:8080',
    country: 'US',
    type: 'HTTP',
    anonymous: true,
    healthy: true,
    latency: 45,
    lastChecked: '2024-01-15T14:30:00Z',
    successRate: 0.98,
  },
  {
    id: 'proxy-2',
    address: '192.168.1.101:8080',
    country: 'UK',
    type: 'HTTPS',
    anonymous: true,
    healthy: true,
    latency: 67,
    lastChecked: '2024-01-15T14:25:00Z',
    successRate: 0.95,
  },
  {
    id: 'proxy-3',
    address: '192.168.1.102:8080',
    country: 'DE',
    type: 'SOCKS5',
    anonymous: false,
    healthy: false,
    latency: 0,
    lastChecked: '2024-01-15T14:20:00Z',
    successRate: 0.65,
  },
  {
    id: 'proxy-4',
    address: '192.168.1.103:8080',
    country: 'FR',
    type: 'HTTP',
    anonymous: true,
    healthy: true,
    latency: 52,
    lastChecked: '2024-01-15T14:15:00Z',
    successRate: 0.92,
  },
];

const mockUserAgents = [
  {
    id: 'ua-1',
    name: 'Chrome Windows',
    value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    usage: 45,
    lastUsed: '2024-01-15T14:30:00Z',
  },
  {
    id: 'ua-2',
    name: 'Firefox Mac',
    value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Gecko/20100101 Firefox/121.0',
    usage: 30,
    lastUsed: '2024-01-15T14:25:00Z',
  },
  {
    id: 'ua-3',
    name: 'Safari iOS',
    value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    usage: 15,
    lastUsed: '2024-01-15T14:20:00Z',
  },
  {
    id: 'ua-4',
    name: 'Edge Windows',
    value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    usage: 10,
    lastUsed: '2024-01-15T14:15:00Z',
  },
];

const mockRateLimits = [
  {
    id: 'limit-1',
    domain: 'example.com',
    limit: 100,
    window: 60,
    current: 45,
    resetIn: 30,
  },
  {
    id: 'limit-2',
    domain: 'api.example.com',
    limit: 50,
    window: 60,
    current: 23,
    resetIn: 45,
  },
  {
    id: 'limit-3',
    domain: 'test.com',
    limit: 200,
    window: 120,
    current: 189,
    resetIn: 15,
  },
];

const mockCacheStats = {
  totalRequests: 12453,
  cacheHits: 8734,
  cacheMisses: 3719,
  hitRate: 0.70,
  storageUsed: 2.4,
  storageLimit: 10,
  averageResponseTime: 45,
  savedBandwidth: 15.2,
};

const mockDistributedStats = {
  totalWorkers: 8,
  activeWorkers: 6,
  idleWorkers: 2,
  queueSize: 12,
  jobsCompleted: 156,
  jobsFailed: 12,
  averageJobTime: 120,
};

const mockSchedulerStats = {
  scheduledJobs: 24,
  runningJobs: 8,
  completedJobs: 156,
  failedJobs: 12,
  nextJob: '2024-01-15T16:00:00Z',
};

const ScrapingHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState('jobs');
  const [jobFormVisible, setJobFormVisible] = useState(false);
  const [proxyFormVisible, setProxyFormVisible] = useState(false);
  const [rateLimitFormVisible, setRateLimitFormVisible] = useState(false);
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [selectedProxy, setSelectedProxy] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState(mockJobs);
  const [proxies, setProxies] = useState(mockProxies);
  const [userAgents, setUserAgents] = useState(mockUserAgents);
  const [rateLimits, setRateLimits] = useState(mockRateLimits);
  const [cacheStats, setCacheStats] = useState(mockCacheStats);
  const [distributedStats, setDistributedStats] = useState(mockDistributedStats);
  const [schedulerStats, setSchedulerStats] = useState(mockSchedulerStats);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string[]>([]);

  const queryClient = useQueryClient();

  // Status options
  const statusOptions = [
    { label: 'All', value: '' },
    { label: 'Queued', value: 'queued' },
    { label: 'Running', value: 'running' },
    { label: 'Completed', value: 'completed' },
    { label: 'Failed', value: 'failed' },
    { label: 'Paused', value: 'paused' },
  ];

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#52c41a';
      case 'running': return '#1890ff';
      case 'queued': return '#faad14';
      case 'failed': return '#f5222d';
      case 'paused': return '#722ed1';
      default: return '#d9d9d9';
    }
  };

  // Get status tag
  const getStatusTag = (status: string) => {
    switch (status) {
      case 'completed': return <Tag color="success">Completed</Tag>;
      case 'running': return <Tag color="processing">Running</Tag>;
      case 'queued': return <Tag color="warning">Queued</Tag>;
      case 'failed': return <Tag color="error">Failed</Tag>;
      case 'paused': return <Tag color="purple">Paused</Tag>;
      default: return <Tag>Unknown</Tag>;
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'running': return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      case 'queued': return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      case 'failed': return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      case 'paused': return <PauseCircleOutlined style={{ color: '#722ed1' }} />;
      default: return <NodeIndexOutlined />;
    }
  };

  // Job columns
  const jobColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress: number) => (
        <Progress
          percent={progress}
          size="small"
          status={progress === 100 ? 'success' : 'active'}
        />
      ),
    },
    {
      title: 'URLs',
      dataIndex: 'urls',
      key: 'urls',
      width: 200,
      render: (urls: string[]) => (
        <Tooltip title={urls.join(', ')'>
          <Text style={{ maxWidth: 150, display: 'inline-block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {urls.length} URL{urls.length !== 1 ? 's' : ''}
          </Text>
        </Tooltip>
      ),
    },
    {
      title: 'Success/Fail',
      key: 'results',
      width: 120,
      render: (_: any, record: any) => (
        <Space>
          <Tag color="success">{record.successCount}</Tag>
          <Tag color="error">{record.failedCount}</Tag>
        </Space>
      ),
    },
    {
      title: 'Duration',
      key: 'duration',
      width: 120,
      render: (_: any, record: any) => {
        if (!record.duration) return '-';
        const minutes = Math.floor(record.duration / 60000);
        const seconds = Math.floor((record.duration % 60000) / 1000);
        return `${minutes}m ${seconds}s`;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small" onClick={() => setSelectedJob(record)}>
            View
          </Button>
          {record.status === 'paused' && (
            <Button type="link" size="small" icon={<PlayCircleOutlined />}>
              Resume
            </Button>
          )}
          {record.status === 'running' && (
            <Button type="link" size="small" icon={<PauseCircleOutlined />}>
              Pause
            </Button>
          )}
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  // Proxy columns
  const proxyColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Address',
      dataIndex: 'address',
      key: 'address',
      width: 200,
    },
    {
      title: 'Country',
      dataIndex: 'country',
      key: 'country',
      width: 100,
      render: (country: string) => (
        <Tag color="blue">{country}</Tag>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => (
        <Tag color="green">{type}</Tag>
      ),
    },
    {
      title: 'Anonymous',
      dataIndex: 'anonymous',
      key: 'anonymous',
      width: 100,
      render: (anonymous: boolean) => (
        <Tag color={anonymous ? '#52c41a' : '#faad14'}>
          {anonymous ? 'Yes' : 'No'}
        </Tag>
      ),
    },
    {
      title: 'Healthy',
      dataIndex: 'healthy',
      key: 'healthy',
      width: 100,
      render: (healthy: boolean) => (
        <Tag color={healthy ? '#52c41a' : '#f5222d'}>
          {healthy ? 'Yes' : 'No'}
        </Tag>
      ),
    },
    {
      title: 'Latency',
      dataIndex: 'latency',
      key: 'latency',
      width: 100,
      render: (latency: number) => latency ? `${latency}ms` : '-',
    },
    {
      title: 'Success Rate',
      dataIndex: 'successRate',
      key: 'successRate',
      width: 120,
      render: (rate: number) => (
        <Progress
          percent={rate * 100}
          size="small"
          status={rate > 0.8 ? 'success' : rate > 0.5 ? 'warning' : 'exception'}
        />
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small" onClick={() => setSelectedProxy(record)}>
            Test
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            Remove
          </Button>
        </Space>
      ),
    },
  ];

  // User Agent columns
  const userAgentColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: 'Usage',
      dataIndex: 'usage',
      key: 'usage',
      width: 100,
      render: (usage: number) => (
        <Progress
          percent={usage}
          size="small"
          status={usage > 70 ? 'success' : usage > 30 ? 'warning' : 'exception'}
        />
      ),
    },
    {
      title: 'Last Used',
      dataIndex: 'lastUsed',
      key: 'lastUsed',
      width: 200,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small">
            Copy
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            Remove
          </Button>
        </Space>
      ),
    },
  ];

  // Rate Limit columns
  const rateLimitColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Domain',
      dataIndex: 'domain',
      key: 'domain',
      width: 200,
    },
    {
      title: 'Limit',
      dataIndex: 'limit',
      key: 'limit',
      width: 100,
    },
    {
      title: 'Window (s)',
      dataIndex: 'window',
      key: 'window',
      width: 120,
    },
    {
      title: 'Current',
      dataIndex: 'current',
      key: 'current',
      width: 100,
    },
    {
      title: 'Reset In',
      dataIndex: 'resetIn',
      key: 'resetIn',
      width: 100,
      render: (seconds: number) => `${seconds}s`,
    },
    {
      title: 'Progress',
      key: 'progress',
      width: 150,
      render: (_: any, record: any) => (
        <Progress
          percent={(record.current / record.limit) * 100}
          size="small"
          status={record.current >= record.limit ? 'exception' : 'active'}
        />
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small" onClick={() => setRateLimitFormVisible(true)}>
            Edit
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            Remove
          </Button>
        </Space>
      ),
    },
  ];

  // Create new job
  const createJob = async (values: any) => {
    setLoading(true);
    try {
      const newJob = {
        id: `job-${Date.now()}`,
        name: values.name,
        status: 'queued',
        urls: values.urls.split('\n').filter((url: string) => url.trim()),
        depth: values.depth || 1,
        progress: 0,
        successCount: 0,
        failedCount: 0,
        startTime: null,
        endTime: null,
        duration: null,
        useProxy: values.useProxy,
        useCache: values.useCache,
        renderJs: values.renderJs,
      };
      setJobs([...jobs, newJob]);
      setJobFormVisible(false);
    } catch (error) {
      console.error('Create job error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Add proxy
  const addProxy = async (values: any) => {
    setLoading(true);
    try {
      const newProxy = {
        id: `proxy-${Date.now()}`,
        address: values.address,
        country: values.country,
        type: values.type,
        anonymous: values.anonymous,
        healthy: true,
        latency: 0,
        lastChecked: new Date().toISOString(),
        successRate: 1.0,
      };
      setProxies([...proxies, newProxy]);
      setProxyFormVisible(false);
    } catch (error) {
      console.error('Add proxy error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Add rate limit
  const addRateLimit = async (values: any) => {
    setLoading(true);
    try {
      const newLimit = {
        id: `limit-${Date.now()}`,
        domain: values.domain,
        limit: values.limit,
        window: values.window,
        current: 0,
        resetIn: values.window,
      };
      setRateLimits([...rateLimits, newLimit]);
      setRateLimitFormVisible(false);
    } catch (error) {
      console.error('Add rate limit error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter jobs
  const filteredJobs = jobs.filter(job => {
    if (search && !job.name.toLowerCase().includes(search.toLowerCase())) return false;
    if (statusFilter.length > 0 && !statusFilter.includes(job.status)) return false;
    return true;
  });

  // Job stats chart
  const jobStatsConfig = {
    data: [
      { status: 'Completed', count: jobs.filter(j => j.status === 'completed').length },
      { status: 'Running', count: jobs.filter(j => j.status === 'running').length },
      { status: 'Queued', count: jobs.filter(j => j.status === 'queued').length },
      { status: 'Failed', count: jobs.filter(j => j.status === 'failed').length },
      { status: 'Paused', count: jobs.filter(j => j.status === 'paused').length },
    ],
    xField: 'status',
    yField: 'count',
    colorField: 'status',
    color: ['#52c41a', '#1890ff', '#faad14', '#f5222d', '#722ed1'],
    label: {
      position: 'top' as const,
      style: {
        fill: '#fff',
        fontWeight: 'bold',
      },
    },
  };

  // Proxy stats chart
  const proxyStatsConfig = {
    data: [
      { country: 'US', count: proxies.filter(p => p.country === 'US').length },
      { country: 'UK', count: proxies.filter(p => p.country === 'UK').length },
      { country: 'DE', count: proxies.filter(p => p.country === 'DE').length },
      { country: 'FR', count: proxies.filter(p => p.country === 'FR').length },
    ],
    xField: 'country',
    yField: 'count',
    seriesField: 'country',
    color: ['#1890ff', '#52c41a', '#faad14', '#f5222d'],
    label: {
      position: 'top' as const,
    },
  };

  // Cache chart
  const cacheChartConfig = {
    data: [
      { type: 'Hits', value: cacheStats.cacheHits },
      { type: 'Misses', value: cacheStats.cacheMisses },
    ],
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'spider' as const,
      labelHeight: 28,
      content: '{name}\n{percentage}' as const,
    },
    color: ['#52c41a', '#faad14'],
  };

  return (
    <div className="scraping-hub-page">
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
              <SearchOutlined />
              Scraping Hub
            </Space>
          </Title>
          <Paragraph type="secondary">
            Distributed web scraping at scale
          </Paragraph>
        </div>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setJobFormVisible(true)}>
            New Scrape Job
          </Button>
          <Button icon={<SyncOutlined />} onClick={() => window.location.reload()}>
            Refresh
          </Button>
        </Space>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Row gutter={24}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Jobs"
                value={jobs.length}
                prefix={<DatabaseOutlined style={{ color: '#1890ff' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Active Proxies"
                value={proxies.filter(p => p.healthy).length}
                prefix={<GlobalOutlined style={{ color: '#52c41a' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="User Agents"
                value={userAgents.length}
                prefix={<UserOutlined style={{ color: '#faad14' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Cache Hit Rate"
                value={`${(cacheStats.hitRate * 100).toFixed(1)}%`}
                prefix={<CodeOutlined style={{ color: '#722ed1' }} />}
              />
            </Card>
          </Col>
        </Row>
      </motion.div>

      <Divider />

      {/* Main Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card
          tabList={[
            { key: 'jobs', tab: 'Scrape Jobs' },
            { key: 'proxies', tab: 'Proxy Manager' },
            { key: 'agents', tab: 'User Agents' },
            { key: 'rate-limits', tab: 'Rate Limiting' },
            { key: 'cache', tab: 'Result Cache' },
            { key: 'distributed', tab: 'Distributed' },
            { key: 'scheduler', tab: 'Scheduler' },
            { key: 'export', tab: 'Data Export' },
            { key: 'monitoring', tab: 'Monitoring' },
          ]}
          activeTabKey={activeTab}
          onTabChange={setActiveTab}
        >
          {activeTab === 'jobs' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Scrape Jobs</Title>
              
              {/* Filters */}
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={8}>
                    <Search
                      placeholder="Search jobs..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </Col>
                  <Col xs={24} lg={8}>
                    <Select
                      mode="multiple"
                      placeholder="Filter by status"
                      value={statusFilter}
                      onChange={setStatusFilter}
                      options={statusOptions}
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={8}>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => setJobFormVisible(true)}
                      block
                    >
                      New Job
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Stats Chart */}
              <Card title="Job Status Distribution" style={{ marginBottom: 24 }}>
                <Bar {...jobStatsConfig} height={200} />
              </Card>

              {/* Jobs Table */}
              <Card title="All Scrape Jobs">
                <Table
                  columns={jobColumns}
                  dataSource={filteredJobs}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1400 }}
                />
              </Card>

              {/* Job Details Modal */}
              <Modal
                title="Job Details"
                open={!!selectedJob}
                onCancel={() => setSelectedJob(null)}
                footer={null}
                width={800}
              >
                {selectedJob && (
                  <div>
                    <Row gutter={24}>
                      <Col span={24}>
                        <Card title="Job Information" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>ID:</Text> {selectedJob.id}
                            </div>
                            <div>
                              <Text strong>Name:</Text> {selectedJob.name}
                            </div>
                            <div>
                              <Text strong>Status:</Text> {getStatusTag(selectedJob.status)}
                            </div>
                            <div>
                              <Text strong>Depth:</Text> {selectedJob.depth}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                    
                    <Row style={{ marginTop: 24 }} gutter={24}>
                      <Col span={12}>
                        <Card title="Configuration" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>Use Proxy:</Text> {selectedJob.useProxy ? 'Yes' : 'No'}
                            </div>
                            <div>
                              <Text strong>Use Cache:</Text> {selectedJob.useCache ? 'Yes' : 'No'}
                            </div>
                            <div>
                              <Text strong>Render JS:</Text> {selectedJob.renderJs ? 'Yes' : 'No'}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card title="Progress" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>Progress:</Text> {selectedJob.progress}%
                            </div>
                            <Progress
                              percent={selectedJob.progress}
                              status={selectedJob.progress === 100 ? 'success' : 'active'}
                            />
                            <div style={{ marginTop: 16 }}>
                              <Text strong>Success:</Text> {selectedJob.successCount}
                            </div>
                            <div>
                              <Text strong>Failed:</Text> {selectedJob.failedCount}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                    
                    <Row style={{ marginTop: 24 }}>
                      <Col span={24}>
                        <Card title="URLs" size="small">
                          <List
                            dataSource={selectedJob.urls}
                            renderItem={(url: string) => (
                              <List.Item>
                                <Typography.Link href={url} target="_blank">
                                  {url}
                                </Typography.Link>
                              </List.Item>
                            )}
                          />
                        </Card>
                      </Col>
                    </Row>
                    
                    <Row style={{ marginTop: 24 }}>
                      <Col span={24}>
                        <Card title="Timing" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>Start Time:</Text> {selectedJob.startTime || 'Not started'}
                            </div>
                            <div>
                              <Text strong>End Time:</Text> {selectedJob.endTime || 'Not completed'}
                            </div>
                            <div>
                              <Text strong>Duration:</Text> {selectedJob.duration ? `${Math.floor(selectedJob.duration / 60000)}m ${Math.floor((selectedJob.duration % 60000) / 1000)}s` : '-'}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                  </div>
                )}
              </Modal>

              {/* New Job Modal */}
              <Modal
                title="New Scrape Job"
                open={jobFormVisible}
                onCancel={() => setJobFormVisible(false)}
                footer={null}
                width={600}
              >
                <Form onFinish={createJob} layout="vertical">
                  <Form.Item name="name" label="Job Name" rules={[{ required: true }]}>
                    <Input placeholder="Enter job name" />
                  </Form.Item>
                  <Form.Item name="urls" label="URLs (one per line)" rules={[{ required: true }]}>
                    <Input.TextArea placeholder="https://example.com&#10;https://example.org" rows={4} />
                  </Form.Item>
                  <Row gutter={24}>
                    <Col span={12}>
                      <Form.Item name="depth" label="Depth" initialValue={1}>
                        <Input type="number" min={1} max={10} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="useProxy" label="Use Proxy" initialValue={true} valuePropName="checked">
                        <Select options={[
                          { label: 'Yes', value: true },
                          { label: 'No', value: false },
                        ]} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Row gutter={24}>
                    <Col span={12}>
                      <Form.Item name="useCache" label="Use Cache" initialValue={true} valuePropName="checked">
                        <Select options={[
                          { label: 'Yes', value: true },
                          { label: 'No', value: false },
                        ]} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="renderJs" label="Render JavaScript" initialValue={false} valuePropName="checked">
                        <Select options={[
                          { label: 'Yes', value: true },
                          { label: 'No', value: false },
                        ]} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                      Create Job
                    </Button>
                  </Form.Item>
                </Form>
              </Modal>
            </div>
          )}

          {activeTab === 'proxies' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Proxy Manager</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={12}>
                    <Search
                      placeholder="Search proxies..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Select
                      placeholder="Filter by country"
                      style={{ width: '100%' }}
                      options={[
                        { label: 'All', value: '' },
                        { label: 'US', value: 'US' },
                        { label: 'UK', value: 'UK' },
                        { label: 'DE', value: 'DE' },
                        { label: 'FR', value: 'FR' },
                      ]}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => setProxyFormVisible(true)}
                      block
                    >
                      Add Proxy
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Proxy Stats Chart */}
              <Card title="Proxies by Country" style={{ marginBottom: 24 }}>
                <Bar {...proxyStatsConfig} height={200} />
              </Card>

              {/* Proxies Table */}
              <Card title="All Proxies">
                <Table
                  columns={proxyColumns}
                  dataSource={proxies}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1200 }}
                />
              </Card>

              {/* Proxy Details Modal */}
              <Modal
                title="Proxy Details"
                open={!!selectedProxy}
                onCancel={() => setSelectedProxy(null)}
                footer={null}
                width={600}
              >
                {selectedProxy && (
                  <div>
                    <Card title="Proxy Information" size="small">
                      <Space direction="vertical">
                        <div>
                          <Text strong>ID:</Text> {selectedProxy.id}
                        </div>
                        <div>
                          <Text strong>Address:</Text> {selectedProxy.address}
                        </div>
                        <div>
                          <Text strong>Country:</Text> {selectedProxy.country}
                        </div>
                        <div>
                          <Text strong>Type:</Text> {selectedProxy.type}
                        </div>
                        <div>
                          <Text strong>Anonymous:</Text> {selectedProxy.anonymous ? 'Yes' : 'No'}
                        </div>
                        <div>
                          <Text strong>Healthy:</Text> {selectedProxy.healthy ? 'Yes' : 'No'}
                        </div>
                        <div>
                          <Text strong>Latency:</Text> {selectedProxy.latency}ms
                        </div>
                        <div>
                          <Text strong>Success Rate:</Text> {(selectedProxy.successRate * 100).toFixed(1)}%
                        </div>
                        <div>
                          <Text strong>Last Checked:</Text> {selectedProxy.lastChecked}
                        </div>
                      </Space>
                    </Card>
                  </div>
                )}
              </Modal>

              {/* Add Proxy Modal */}
              <Modal
                title="Add Proxy"
                open={proxyFormVisible}
                onCancel={() => setProxyFormVisible(false)}
                footer={null}
                width={600}
              >
                <Form onFinish={addProxy} layout="vertical">
                  <Form.Item name="address" label="Proxy Address" rules={[{ required: true }]}>
                    <Input placeholder="e.g., 192.168.1.100:8080" />
                  </Form.Item>
                  <Row gutter={24}>
                    <Col span={12}>
                      <Form.Item name="country" label="Country" rules={[{ required: true }]}>
                        <Select options={[
                          { label: 'US', value: 'US' },
                          { label: 'UK', value: 'UK' },
                          { label: 'DE', value: 'DE' },
                          { label: 'FR', value: 'FR' },
                          { label: 'CA', value: 'CA' },
                          { label: 'AU', value: 'AU' },
                        ]} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="type" label="Type" rules={[{ required: true }]}>
                        <Select options={[
                          { label: 'HTTP', value: 'HTTP' },
                          { label: 'HTTPS', value: 'HTTPS' },
                          { label: 'SOCKS4', value: 'SOCKS4' },
                          { label: 'SOCKS5', value: 'SOCKS5' },
                        ]} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Form.Item name="anonymous" label="Anonymous" initialValue={true} valuePropName="checked">
                    <Select options={[
                      { label: 'Yes', value: true },
                      { label: 'No', value: false },
                    ]} />
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                      Add Proxy
                    </Button>
                  </Form.Item>
                </Form>
              </Modal>
            </div>
          )}

          {activeTab === 'agents' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>User Agents</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={18}>
                    <Search
                      placeholder="Search user agents..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      block
                    >
                      Add User Agent
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* User Agents Table */}
              <Card title="All User Agents">
                <Table
                  columns={userAgentColumns}
                  dataSource={userAgents}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1000 }}
                />
              </Card>
            </div>
          )}

          {activeTab === 'rate-limits' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Rate Limiting</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={18}>
                    <Search
                      placeholder="Search rate limits..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => setRateLimitFormVisible(true)}
                      block
                    >
                      Add Rate Limit
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Rate Limits Table */}
              <Card title="All Rate Limits">
                <Table
                  columns={rateLimitColumns}
                  dataSource={rateLimits}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1000 }}
                />
              </Card>

              {/* Add Rate Limit Modal */}
              <Modal
                title="Add Rate Limit"
                open={rateLimitFormVisible}
                onCancel={() => setRateLimitFormVisible(false)}
                footer={null}
                width={600}
              >
                <Form onFinish={addRateLimit} layout="vertical">
                  <Form.Item name="domain" label="Domain" rules={[{ required: true }]}>
                    <Input placeholder="e.g., example.com" />
                  </Form.Item>
                  <Row gutter={24}>
                    <Col span={12}>
                      <Form.Item name="limit" label="Limit" rules={[{ required: true }]} initialValue={100}>
                        <Input type="number" min={1} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="window" label="Window (seconds)" rules={[{ required: true }]} initialValue={60}>
                        <Input type="number" min={1} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                      Add Rate Limit
                    </Button>
                  </Form.Item>
                </Form>
              </Modal>
            </div>
          )}

          {activeTab === 'cache' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Result Cache</Title>
              
              {/* Stats */}
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Total Requests"
                      value={cacheStats.totalRequests.toLocaleString()}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Cache Hits"
                      value={cacheStats.cacheHits.toLocaleString()}
                      suffix={<Tag color="success">{(cacheStats.hitRate * 100).toFixed(1)}%</Tag>}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Cache Misses"
                      value={cacheStats.cacheMisses.toLocaleString()}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Storage Used"
                      value={`${cacheStats.storageUsed} GB`}
                      suffix={`/ ${cacheStats.storageLimit} GB`}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Cache Chart */}
              <Card title="Cache Performance" style={{ marginBottom: 24 }}>
                <Pie {...cacheChartConfig} height={300} />
              </Card>

              {/* Stats */}
              <Row gutter={24}>
                <Col xs={24} lg={12}>
                  <Card title="Cache Statistics" size="small">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text>Average Response Time:</Text>
                        <Text strong>{cacheStats.averageResponseTime}ms</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text>Bandwidth Saved:</Text>
                        <Text strong>{cacheStats.savedBandwidth} GB</Text>
                      </div>
                    </Space>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Actions" size="small">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Button type="primary" block icon={<SyncOutlined />}>
                        Clear Cache
                      </Button>
                      <Button block icon={<SettingOutlined />}>
                        Configure Cache
                      </Button>
                    </Space>
                  </Card>
                </Col>
              </Row>
            </div>
          )}

          {activeTab === 'distributed' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Distributed Scraping</Title>
              
              {/* Stats */}
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Total Workers"
                      value={distributedStats.totalWorkers}
                      prefix={<TeamOutlined style={{ color: '#1890ff' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Active Workers"
                      value={distributedStats.activeWorkers}
                      prefix={<ThunderboltOutlined style={{ color: '#52c41a' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Idle Workers"
                      value={distributedStats.idleWorkers}
                      prefix={<PauseCircleOutlined style={{ color: '#faad14' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Queue Size"
                      value={distributedStats.queueSize}
                      prefix={<DatabaseOutlined style={{ color: '#722ed1' }} />}
                    />
                  </Card>
                </Col>
              </Row>

              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Jobs Completed"
                      value={distributedStats.jobsCompleted}
                      prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Jobs Failed"
                      value={distributedStats.jobsFailed}
                      prefix={<CloseCircleOutlined style={{ color: '#f5222d' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Avg Job Time"
                      value={`${distributedStats.averageJobTime}s`}
                      prefix={<ClockCircleOutlined style={{ color: '#1890ff' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Efficiency"
                      value={`${((distributedStats.jobsCompleted / (distributedStats.jobsCompleted + distributedStats.jobsFailed)) * 100).toFixed(1)}%`}
                      prefix={<BarChartOutlined style={{ color: '#faad14' }} />}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Worker List */}
              <Card title="Worker Status">
                <List
                  dataSource={Array(distributedStats.totalWorkers).fill(0).map((_, i) => ({
                    id: `worker-${i + 1}`,
                    status: i < distributedStats.activeWorkers ? 'active' : 'idle',
                    jobs: Math.floor(Math.random() * 10),
                    uptime: `${Math.floor(Math.random() * 24) + 1}h`,
                  }))}
                  renderItem={(worker: any) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={
                          <Avatar
                            icon={worker.status === 'active' ? <ThunderboltOutlined /> : <PauseCircleOutlined />}
                            style={{ background: worker.status === 'active' ? '#52c41a' : '#faad14' }}
                          />
                        }
                        title={worker.id}
                        description={
                          <Space>
                            <Tag color={worker.status === 'active' ? 'success' : 'warning'}>
                              {worker.status}
                            </Tag>
                            <Text type="secondary">Jobs: {worker.jobs}</Text>
                            <Text type="secondary">Uptime: {worker.uptime}</Text>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>

              {/* Actions */}
              <Card title="Actions" style={{ marginTop: 24 }}>
                <Space>
                  <Button type="primary" icon={<PlusOutlined />}>
                    Add Worker
                  </Button>
                  <Button icon={<SyncOutlined />}>
                    Scale Up
                  </Button>
                  <Button icon={<SyncOutlined />}>
                    Scale Down
                  </Button>
                  <Button icon={<SettingOutlined />}>
                    Configure
                  </Button>
                </Space>
              </Card>
            </div>
          )}

          {activeTab === 'scheduler' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Scheduler</Title>
              
              {/* Stats */}
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Scheduled Jobs"
                      value={schedulerStats.scheduledJobs}
                      prefix={<ClockCircleOutlined style={{ color: '#1890ff' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Running Jobs"
                      value={schedulerStats.runningJobs}
                      prefix={<SyncOutlined spin style={{ color: '#52c41a' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Completed Jobs"
                      value={schedulerStats.completedJobs}
                      prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Failed Jobs"
                      value={schedulerStats.failedJobs}
                      prefix={<CloseCircleOutlined style={{ color: '#f5222d' }} />}
                    />
                  </Card>
                </Col>
              </Row>

              <Alert
                message={`Next scheduled job: ${schedulerStats.nextJob}`}
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              {/* Calendar would go here */}
              <Card title="Schedule Calendar" style={{ marginBottom: 24 }}>
                <div style={{ textAlign: 'center', padding: 40 }}>
                  <Text type="secondary">Calendar view would be displayed here</Text>
                </div>
              </Card>

              {/* Actions */}
              <Card title="Actions">
                <Space>
                  <Button type="primary" icon={<PlusOutlined />}>
                    New Scheduled Job
                  </Button>
                  <Button icon={<SyncOutlined />}>
                    Run Now
                  </Button>
                  <Button icon={<EditOutlined />}>
                    Edit Schedule
                  </Button>
                  <Button icon={<DeleteOutlined />} danger>
                    Clear Schedule
                  </Button>
                </Space>
              </Card>
            </div>
          )}

          {activeTab === 'export' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Data Export</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Paragraph type="secondary">
                  Export your scraped data in various formats
                </Paragraph>
              </Card>

              {/* Export Options */}
              <Row gutter={24}>
                <Col xs={24} lg={12}>
                  <Card title="Quick Export">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Button type="primary" block icon={<ExportOutlined />}>
                        Export All as CSV
                      </Button>
                      <Button block icon={<ExportOutlined />}>
                        Export All as JSON
                      </Button>
                      <Button block icon={<ExportOutlined />}>
                        Export All as Excel
                      </Button>
                    </Space>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Custom Export">
                    <Form layout="vertical">
                      <Form.Item label="Format">
                        <Select options={[
                          { label: 'CSV', value: 'csv' },
                          { label: 'JSON', value: 'json' },
                          { label: 'Excel', value: 'excel' },
                          { label: 'SQL', value: 'sql' },
                        ]} />
                      </Form.Item>
                      <Form.Item label="Date Range">
                        <RangePicker style={{ width: '100%' }} />
                      </Form.Item>
                      <Form.Item label="Job Filter">
                        <Select mode="multiple" options={jobs.map(j => ({ label: j.name, value: j.id }))} />
                      </Form.Item>
                      <Form.Item>
                        <Button type="primary" block icon={<ExportOutlined />}>
                          Export
                        </Button>
                      </Form.Item>
                    </Form>
                  </Card>
                </Col>
              </Row>

              {/* Export History */}
              <Card title="Export History" style={{ marginTop: 24 }}>
                <Table
                  columns={[
                    { title: 'ID', dataIndex: 'id', key: 'id' },
                    { title: 'Format', dataIndex: 'format', key: 'format' },
                    { title: 'Date', dataIndex: 'date', key: 'date' },
                    { title: 'Size', dataIndex: 'size', key: 'size' },
                    { title: 'Status', dataIndex: 'status', key: 'status', render: (s: string) => getStatusTag(s) },
                    { title: 'Actions', key: 'actions', render: () => <Button type="link" size="small">Download</Button> },
                  ]}
                  dataSource={[]}
                  rowKey="id"
                  size="small"
                />
              </Card>
            </div>
          )}

          {activeTab === 'monitoring' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Monitoring</Title>
              
              {/* Monitoring Dashboard */}
              <Row gutter={24}>
                <Col xs={24} lg={12}>
                  <Card title="System Health">
                    <div style={{ textAlign: 'center', padding: 40 }}>
                      <Text type="secondary">System health monitoring dashboard</Text>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Performance Metrics">
                    <div style={{ textAlign: 'center', padding: 40 }}>
                      <Text type="secondary">Performance metrics would be displayed here</Text>
                    </div>
                  </Card>
                </Col>
              </Row>

              <Row gutter={24} style={{ marginTop: 24 }}>
                <Col xs={24} lg={12}>
                  <Card title="Alerts">
                    <List
                      dataSource={[]}
                      renderItem={(alert: any) => (
                        <List.Item>
                          <List.Item.Meta
                            avatar={<AlertOutlined style={{ color: '#f5222d' }} />}
                            title={alert.title}
                            description={alert.message}
                          />
                        </List.Item>
                      )}
                    />
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Logs">
                    <div style={{ height: 300, overflowY: 'auto', background: '#f0f0f0', padding: 16, borderRadius: 4 }}>
                      <Text type="secondary">Logs would be displayed here</Text>
                    </div>
                  </Card>
                </Col>
              </Row>

              {/* Actions */}
              <Card title="Actions" style={{ marginTop: 24 }}>
                <Space>
                  <Button type="primary" icon={<SyncOutlined />}>
                    Refresh
                  </Button>
                  <Button icon={<SettingOutlined />}>
                    Configure Alerts
                  </Button>
                  <Button icon={<FilterOutlined />}>
                    Filter Logs
                  </Button>
                </Space>
              </Card>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
};

export default ScrapingHub;
