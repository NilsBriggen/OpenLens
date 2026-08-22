import React, { useState, useCallback } from 'react';
import { Card, Tabs, Button, Space, Typography, Row, Col, Divider, Modal, Form, Input, Select, Table, Tag, Progress, Alert, Spin, DatePicker, Steps, List, Tooltip, message } from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  GlobalOutlined,
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
  TeamOutlined,
  PictureOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Line, Pie } from '@ant-design/plots';
import {
  useScrapeJobs,
  useCreateScrapeJob,
  useScrapeVkUser,
  useScrapeVkPosts,
  useScrapeVkSearch,
  useScrapeTwitterTweets,
  useScrapeTwitterUser,
  useScrapeTwitterTrends,
  useScrapeInstagramUser,
  useScrapeInstagramPosts,
  useScrapeInstagramHashtag,
  useWebSocket
} from '../hooks/useApi';
import { useDebounce, useLocalStorage } from '../hooks/useApi';
import { useWebSocket as useWebSocketContext } from '../contexts/WebSocketContext';
import type { ScrapeJob } from '../types/api';
import { exportToCSV, exportToJSON } from '../utils/exportUtils';
import StatCard from '../components/common/StatCard';
import PageHeader from '../components/common/PageHeader';
import LivePill from '../components/common/LivePill';
import BarList from '../components/common/BarList';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { Step } = Steps;

interface ProxyServer {
  id: string;
  host: string;
  port: number;
  protocol: string;
  status: string;
  location: string;
  speed: number;
  lastUsed: string;
}

interface ScrapeResult {
  id: string;
  jobId: string;
  url: string;
  status: string;
  data: any;
  timestamp: string;
}

const ScrapingHub: React.FC = () => {
  // State
  const { value: activeTab, setValue: setActiveTab } = useLocalStorage('scraping-active-tab', 'jobs');
  const [jobFormVisible, setJobFormVisible] = useState(false);
  const [jobDetailVisible, setJobDetailVisible] = useState(false);
  const [proxyFormVisible, setProxyFormVisible] = useState(false);
  const [selectedJob, setSelectedJob] = useState<ScrapeJob | null>(null);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    jobType: '',
    dateRange: null,
  });
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30000);
  
  // Local storage for preferences
  const { value: savedAutoRefresh, setValue: saveAutoRefresh } = useLocalStorage('scraping-auto-refresh', false);
  const { value: savedRefreshInterval, setValue: saveRefreshInterval } = useLocalStorage('scraping-refresh-interval', 30000);
  
  // Load saved preferences
  React.useEffect(() => {
    setAutoRefresh(savedAutoRefresh);
    setRefreshInterval(savedRefreshInterval);
  }, [savedAutoRefresh, savedRefreshInterval]);
  
  // Debounced search
  const debouncedSearch = useDebounce(search, 500);
  
  // API Hooks
  const { 
    data: jobs = [], 
    isLoading: jobsLoading, 
    error: jobsError, 
    refetch: refetchJobs 
  } = useScrapeJobs({
    search: debouncedSearch || undefined,
    status: filters.status || undefined,
    type: filters.jobType || undefined,
  });
  
  const createJobMutation = useCreateScrapeJob();
  const vkUserMutation = useScrapeVkUser();
  const vkPostsMutation = useScrapeVkPosts();
  const vkSearchMutation = useScrapeVkSearch();
  const twitterTweetsMutation = useScrapeTwitterTweets();
  const twitterUserMutation = useScrapeTwitterUser();
  const twitterTrendsMutation = useScrapeTwitterTrends();
  const instagramUserMutation = useScrapeInstagramUser();
  const instagramPostsMutation = useScrapeInstagramPosts();
  const instagramHashtagMutation = useScrapeInstagramHashtag();
  
  // WebSocket for real-time updates
  useWebSocket(
    '/api/ws/scraping',
    (data) => {
      if (data.type === 'job_update') {
        refetchJobs();
        message.info('Scrape job updated');
      }
    }
  );
  const { isConnected } = useWebSocketContext();
  
  // Refresh all
  const refreshAll = useCallback(() => {
    refetchJobs();
  }, [refetchJobs]);
  
  // Export functions
  const exportData = useCallback((format: 'csv' | 'json') => {
    if (format === 'csv') {
      exportToCSV(jobs, 'scrape-jobs.csv');
    } else if (format === 'json') {
      exportToJSON(jobs, 'scrape-jobs.json');
    }
    message.success(`Data exported as ${format.toUpperCase()}`);
  }, [jobs]);
  
  // Create scrape job
  const createScrapeJob = useCallback(async (values: any) => {
    try {
      const result = await createJobMutation.mutateAsync(values);
      message.success('Scrape job created successfully');
      refetchJobs();
      return result;
    } catch (error) {
      message.error('Failed to create scrape job');
      throw error;
    }
  }, [createJobMutation, refetchJobs]);
  
  // Run VK scrape
  const scrapeVkUser = useCallback(async (userId: string, username?: string) => {
    try {
      const result = await vkUserMutation.mutateAsync({ user_id: userId, username });
      message.success('VK user scrape started');
      return result;
    } catch (error) {
      message.error('Failed to start VK user scrape');
      throw error;
    }
  }, [vkUserMutation]);
  
  // Helper functions
  const statusColors = {
    queued: 'default',
    running: 'processing',
    paused: 'warning',
    completed: 'success',
    failed: 'error',
    cancelled: 'default',
  };

  const statusColorVars: Record<string, string> = {
    queued: 'var(--text-color-secondary)',
    running: 'var(--primary-color)',
    paused: 'var(--warning-color)',
    completed: 'var(--success-color)',
    failed: 'var(--error-color)',
    cancelled: 'var(--text-color-secondary)',
  };

  const getStatusTag = (status: string) => (
    <Tag color={statusColors[status as keyof typeof statusColors] || 'default'}>
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
        {status === 'running' && (
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: statusColorVars.running,
              animation: 'olPulse 2s infinite',
            }}
          />
        )}
        {status}
      </span>
    </Tag>
  );

  const getJobTypeColor = (type: string) => {
    const colors = {
      vk: '#1890ff',
      twitter: '#1da57a',
      instagram: '#e91e63',
      web: '#faad14',
      custom: '#722ed1',
    };
    return colors[type as keyof typeof colors] || '#d9d9d9';
  };

  const getJobTypeIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      vk: <TeamOutlined />,
      twitter: <ShareAltOutlined />,
      instagram: <PictureOutlined />,
      web: <GlobalOutlined />,
      custom: <CodeOutlined />,
    };
    return icons[type] || <GlobalOutlined />;
  };

  // Table columns
  const jobColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: ScrapeJob) => (
        <Space>
          {getJobTypeIcon(record.jobType ?? 'web')}
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    { title: 'Type', dataIndex: 'jobType', key: 'jobType', render: (t: string) => <Tag color={getJobTypeColor(t)}>{t}</Tag> },
    { title: 'Status', dataIndex: 'status', key: 'status', render: getStatusTag },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => (
        <Progress percent={progress} size="small" status={progress === 100 ? 'success' : 'active'} />
      ),
    },
    {
      title: 'Results',
      key: 'results',
      render: (_: any, record: ScrapeJob) => (
        <Space>
          <Tag color="success">{record.successCount}</Tag>
          <Tag color="error">{record.failedCount}</Tag>
        </Space>
      ),
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration: number | null) => duration ? `${Math.floor(duration / 60000)}m` : '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ScrapeJob) => (
        <Space>
          <Tooltip title="View job details">
            <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => setSelectedJob(record)} />
          </Tooltip>
          {record.status === 'running' && (
            <Tooltip title="Pause job">
              <Button type="link" size="small" icon={<PauseCircleOutlined />} />
            </Tooltip>
          )}
          {record.status === 'paused' && (
            <Tooltip title="Resume job">
              <Button type="link" size="small" icon={<PlayCircleOutlined />} />
            </Tooltip>
          )}
          <Tooltip title="Delete">
            <Button type="link" size="small" icon={<DeleteOutlined />} danger />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // Stats
  const totalJobs = jobs.length;
  const runningJobs = jobs.filter(j => j.status === 'running').length;
  const completedJobs = jobs.filter(j => j.status === 'completed').length;
  const failedJobs = jobs.filter(j => j.status === 'failed').length;
  const queuedJobs = jobs.filter(j => j.status === 'queued').length;
  
  // Job type distribution
  const jobTypeData = React.useMemo(() => {
    const counts: Record<string, number> = {};
    jobs.forEach(j => {
      const type = j.jobType ?? 'web';
      counts[type] = (counts[type] || 0) + 1;
    });
    return Object.entries(counts).map(([type, count]) => ({ type, count }));
  }, [jobs]);
  
  // Status distribution
  const statusData = React.useMemo(() => {
    const counts: Record<string, number> = {};
    jobs.forEach(j => {
      counts[j.status] = (counts[j.status] || 0) + 1;
    });
    return Object.entries(counts).map(([status, count]) => ({ status, count }));
  }, [jobs]);
  
  // Loading state
  const isLoading = jobsLoading || createJobMutation.isPending;
  const hasError = jobsError;
  
  return (
    <div className="ol-page-body">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <PageHeader
          icon={<DatabaseOutlined />}
          title="Scraping Hub"
          subtitle="Distributed web scraping and data extraction"
          actions={
            <Space>
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setJobFormVisible(true)}>
                New Job
              </Button>
              <Button icon={<SyncOutlined spin={isLoading} />} onClick={refreshAll} loading={isLoading}>
                Refresh
              </Button>
              <LivePill connected={isConnected} />
            </Space>
          }
        />
      </motion.div>

      {/* Stats Overview */}
      <div className="ol-row-split">
        <div className="ol-stats-grid-sm">
          <StatCard label="Total Jobs" value={totalJobs} icon={<CodeOutlined />} accent="neutral" dense />
          <StatCard label="Running" value={runningJobs} icon={<PlayCircleOutlined />} accent="primary" dense />
          <StatCard label="Completed" value={completedJobs} icon={<CheckCircleOutlined />} accent="success" dense />
          <StatCard label="Failed" value={failedJobs} icon={<CloseCircleOutlined />} accent="error" dense />
          <StatCard label="Queued" value={queuedJobs} icon={<ClockCircleOutlined />} accent="warning" dense />
        </div>
        <Card title="Job Types">
          <div className="ol-dial-card">
            <Pie
              data={jobTypeData}
              angleField="count"
              colorField="type"
              radius={0.8}
              innerRadius={0.6}
              height={140}
              legend={false}
              color={(datum: any) => getJobTypeColor(datum.type)}
            />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {jobTypeData.map((d) => (
                <div key={d.type} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
                  <span
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: getJobTypeColor(d.type),
                      flexShrink: 0,
                    }}
                  />
                  <span style={{ color: 'var(--text-color-secondary)', textTransform: 'capitalize' }}>{d.type}</span>
                  <span style={{ marginLeft: 'auto', fontWeight: 600, color: 'var(--text-color)' }}>{d.count}</span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Error Alert */}
      {hasError && (
        <Alert
          message="Error loading scraping data"
          description={jobsError?.message}
          type="error"
          showIcon
          closable
        />
      )}

      {/* Main Content Tabs */}
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'jobs',
              label: 'Jobs',
              icon: <DatabaseOutlined />,
              children: (
                <Spin spinning={jobsLoading}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <Row justify="space-between" align="middle">
                      <Col>
                        <Title level={4} style={{ margin: 0 }}>Scrape Jobs ({jobs.length})</Title>
                      </Col>
                      <Col>
                        <Space wrap>
                          <Input
                            placeholder="Search jobs..."
                            prefix={<SearchOutlined />}
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            style={{ width: 200 }}
                          />
                          <Select
                            placeholder="Filter by status"
                            value={filters.status}
                            onChange={(value) => setFilters({ ...filters, status: value })}
                            style={{ width: 120 }}
                            allowClear
                          >
                            <Option value="queued">Queued</Option>
                            <Option value="running">Running</Option>
                            <Option value="paused">Paused</Option>
                            <Option value="completed">Completed</Option>
                            <Option value="failed">Failed</Option>
                          </Select>
                          <Select
                            placeholder="Filter by type"
                            value={filters.jobType}
                            onChange={(value) => setFilters({ ...filters, jobType: value })}
                            style={{ width: 120 }}
                            allowClear
                          >
                            <Option value="vk">VK</Option>
                            <Option value="twitter">Twitter</Option>
                            <Option value="instagram">Instagram</Option>
                            <Option value="web">Web</Option>
                          </Select>
                          <Button icon={<ExportOutlined />} onClick={() => exportData('csv')}>
                            Export
                          </Button>
                        </Space>
                      </Col>
                    </Row>

                    <div className="ol-row-2up">
                      <Card size="small" title="Job Status Distribution">
                        <BarList
                          items={statusData.map((d) => ({
                            key: d.status,
                            label: d.status.charAt(0).toUpperCase() + d.status.slice(1),
                            value: d.count,
                            color: statusColorVars[d.status] ?? 'var(--primary-color)',
                          }))}
                        />
                      </Card>
                      <Card size="small" title="Success Rate">
                        <Progress
                          type="dashboard"
                          percent={totalJobs > 0 ? (completedJobs / totalJobs) * 100 : 0}
                          format={(percent) => `${percent?.toFixed(0)}%`}
                        />
                      </Card>
                    </div>

                    <Table
                      columns={jobColumns}
                      dataSource={jobs}
                      rowKey="id"
                      pagination={{ pageSize: 20 }}
                      scroll={{ x: 1120 }}
                    />
                  </div>
                </Spin>
              ),
            },
            {
              key: 'platforms',
              label: 'Platforms',
              icon: <GlobalOutlined />,
              children: (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <div>
                    <Title level={4} style={{ margin: 0 }}>Platform-Specific Scraping</Title>
                    <Paragraph type="secondary" style={{ margin: '4px 0 0' }}>
                      Launch targeted scraping jobs for specific platforms.
                    </Paragraph>
                  </div>

                  <Card className="ol-subcard" title="VK (VKontakte)">
                    <Text type="secondary">
                      Scrape VK user profiles, posts, and communities.
                    </Text>
                    <Space style={{ marginTop: 16 }} wrap>
                      <Input placeholder="User ID or username" style={{ width: 220 }} />
                      <Button type="primary" onClick={() => scrapeVkUser('user123')}>
                        Scrape User
                      </Button>
                      <Button onClick={() => vkPostsMutation.mutateAsync({ user_id: 'user123', limit: 10 })}>
                        Scrape Posts
                      </Button>
                      <Button onClick={() => vkSearchMutation.mutateAsync({ query: 'test', limit: 10 })}>
                        Search
                      </Button>
                    </Space>
                  </Card>

                  <Card className="ol-subcard" title="Twitter">
                    <Text type="secondary">
                      Scrape Twitter tweets, user profiles, and trends.
                    </Text>
                    <Space style={{ marginTop: 16 }} wrap>
                      <Input placeholder="Username or query" style={{ width: 220 }} />
                      <Button type="primary" onClick={() => twitterUserMutation.mutateAsync({ username: 'twitteruser' })}>
                        Scrape User
                      </Button>
                      <Button onClick={() => twitterTweetsMutation.mutateAsync({ query: 'test', limit: 10 })}>
                        Scrape Tweets
                      </Button>
                      <Button onClick={() => twitterTrendsMutation.mutateAsync()}>
                        Get Trends
                      </Button>
                    </Space>
                  </Card>

                  <Card className="ol-subcard" title="Instagram">
                    <Text type="secondary">
                      Scrape Instagram user profiles, posts, and hashtags.
                    </Text>
                    <Space style={{ marginTop: 16 }} wrap>
                      <Input placeholder="Username or hashtag" style={{ width: 220 }} />
                      <Button type="primary" onClick={() => instagramUserMutation.mutateAsync({ username: 'instauser' })}>
                        Scrape User
                      </Button>
                      <Button onClick={() => instagramPostsMutation.mutateAsync({ username: 'instauser', limit: 10 })}>
                        Scrape Posts
                      </Button>
                      <Button onClick={() => instagramHashtagMutation.mutateAsync({ hashtag: 'test', limit: 10 })}>
                        Scrape Hashtag
                      </Button>
                    </Space>
                  </Card>
                </div>
              ),
            },
            {
              key: 'proxies',
              label: 'Proxies',
              icon: <ShareAltOutlined />,
              children: (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
                    <div>
                      <Title level={4} style={{ margin: 0 }}>Proxy Servers</Title>
                      <Paragraph type="secondary" style={{ margin: '4px 0 0' }}>
                        Configure proxy servers for distributed scraping and rate limit avoidance.
                      </Paragraph>
                    </div>
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => setProxyFormVisible(true)}>
                      Add Proxy
                    </Button>
                  </div>

                  <List
                    dataSource={[
                      { id: '1', host: 'proxy1.example.com', port: 8080, protocol: 'http', status: 'active', location: 'US', speed: 150 },
                      { id: '2', host: 'proxy2.example.com', port: 8080, protocol: 'https', status: 'active', location: 'EU', speed: 200 },
                      { id: '3', host: 'proxy3.example.com', port: 8080, protocol: 'socks5', status: 'inactive', location: 'ASIA', speed: 100 },
                    ]}
                    renderItem={(proxy: any) => (
                      <List.Item
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '16px 0',
                          borderBottom: '1px solid var(--border-color-secondary)',
                        }}
                      >
                        <div>
                          <div
                            className="ol-mono"
                            style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-color)' }}
                          >
                            {proxy.protocol}://{proxy.host}:{proxy.port}
                          </div>
                          <div style={{ fontSize: 13, color: 'var(--text-color-secondary)', marginTop: 4 }}>
                            {proxy.location} · {proxy.speed}ms
                          </div>
                        </div>
                        <Space size={8}>
                          <Tag color={proxy.status === 'active' ? 'green' : 'red'}>
                            {proxy.status}
                          </Tag>
                          <button type="button" className="ol-icon-btn" aria-label="Edit proxy">
                            <EditOutlined />
                          </button>
                          <button type="button" className="ol-icon-btn" aria-label="Delete proxy">
                            <DeleteOutlined />
                          </button>
                        </Space>
                      </List.Item>
                    )}
                  />
                </div>
              ),
            },
            {
              key: 'settings',
              label: 'Settings',
              icon: <SettingOutlined />,
              children: (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <Title level={4} style={{ margin: 0 }}>Scraping Settings</Title>

                  <div className="ol-row-2up">
                    <Card title="Rate Limiting">
                      <Paragraph type="secondary" style={{ marginBottom: 16 }}>
                        Configure rate limits to avoid detection and respect website policies.
                      </Paragraph>
                      <Row gutter={16}>
                        <Col span={12}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            <Text style={{ fontSize: 14, fontWeight: 600 }}>Requests per minute</Text>
                            <Input type="number" defaultValue={60} style={{ width: '100%' }} />
                          </div>
                        </Col>
                        <Col span={12}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            <Text style={{ fontSize: 14, fontWeight: 600 }}>Delay between requests (ms)</Text>
                            <Input type="number" defaultValue={1000} style={{ width: '100%' }} />
                          </div>
                        </Col>
                      </Row>
                    </Card>

                    <Card title="Caching">
                      <Paragraph type="secondary" style={{ marginBottom: 16 }}>
                        Enable caching to avoid re-scraping the same content.
                      </Paragraph>
                      <Row gutter={16}>
                        <Col span={12}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            <Text style={{ fontSize: 14, fontWeight: 600 }}>Enable caching</Text>
                            <Select defaultValue="true" style={{ width: '100%' }}>
                              <Option value="true">Enabled</Option>
                              <Option value="false">Disabled</Option>
                            </Select>
                          </div>
                        </Col>
                        <Col span={12}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            <Text style={{ fontSize: 14, fontWeight: 600 }}>Cache expiration (hours)</Text>
                            <Input type="number" defaultValue={24} style={{ width: '100%' }} />
                          </div>
                        </Col>
                      </Row>
                    </Card>

                    <Card title="JavaScript Rendering">
                      <Paragraph type="secondary" style={{ marginBottom: 16 }}>
                        Enable JavaScript rendering for dynamic content (slower but more accurate).
                      </Paragraph>
                      <Row gutter={16}>
                        <Col span={12}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            <Text style={{ fontSize: 14, fontWeight: 600 }}>Render JavaScript</Text>
                            <Select defaultValue="false" style={{ width: '100%' }}>
                              <Option value="true">Enabled</Option>
                              <Option value="false">Disabled</Option>
                            </Select>
                          </div>
                        </Col>
                        <Col span={12}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            <Text style={{ fontSize: 14, fontWeight: 600 }}>Timeout (seconds)</Text>
                            <Input type="number" defaultValue={30} style={{ width: '100%' }} />
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </div>
                </div>
              ),
            },
          ]}
        />
      </Card>

      {/* Job Detail Modal */}
      <Modal
        title="Job Details"
        open={!!selectedJob}
        onCancel={() => setSelectedJob(null)}
        footer={null}
        width={700}
      >
        {selectedJob && (
          <Card>
            <Title level={4}>{selectedJob.name}</Title>
            <Tag color={getJobTypeColor(selectedJob.jobType ?? 'web')}>
              {selectedJob.jobType}
            </Tag>
            {getStatusTag(selectedJob.status)}
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>Progress:</Text>
                <Progress percent={selectedJob.progress} status={selectedJob.progress === 100 ? 'success' : 'active'} />
              </Col>
              <Col span={12}>
                <Text strong>Results:</Text>
                <Space>
                  <Tag color="success">{selectedJob.successCount} success</Tag>
                  <Tag color="error">{selectedJob.failedCount} failed</Tag>
                </Space>
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Text strong>Depth:</Text>
                <Text>{selectedJob.depth}</Text>
              </Col>
              <Col span={12}>
                <Text strong>URLs:</Text>
                <Text>{selectedJob.urls?.length ?? 0}</Text>
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Text strong>Proxy:</Text>
                <Tag color={selectedJob.useProxy ? 'green' : 'red'}>
                  {selectedJob.useProxy ? 'Enabled' : 'Disabled'}
                </Tag>
              </Col>
              <Col span={12}>
                <Text strong>Cache:</Text>
                <Tag color={selectedJob.useCache ? 'green' : 'red'}>
                  {selectedJob.useCache ? 'Enabled' : 'Disabled'}
                </Tag>
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Text strong>JavaScript:</Text>
                <Tag color={selectedJob.renderJs ? 'green' : 'red'}>
                  {selectedJob.renderJs ? 'Enabled' : 'Disabled'}
                </Tag>
              </Col>
              <Col span={12}>
                <Text strong>Duration:</Text>
                <Text>{selectedJob.duration ? `${Math.floor(selectedJob.duration / 60000)} minutes` : '-'}</Text>
              </Col>
            </Row>
            
            <Divider />
            
            <Text strong>URLs:</Text>
            <List
              dataSource={selectedJob.urls}
              renderItem={(url) => <List.Item><Text code>{url}</Text></List.Item>}
            />
            
            <Divider />
            
            <Space>
              {selectedJob.status === 'running' && (
                <Button type="primary" icon={<PauseCircleOutlined />}>
                  Pause
                </Button>
              )}
              {selectedJob.status === 'paused' && (
                <Button type="primary" icon={<PlayCircleOutlined />}>
                  Resume
                </Button>
              )}
              <Button icon={<EyeOutlined />}>
                View Results
              </Button>
              <Button icon={<EditOutlined />}>
                Edit
              </Button>
              <Button icon={<DeleteOutlined />} danger>
                Delete
              </Button>
            </Space>
          </Card>
        )}
      </Modal>

      {/* New Job Modal */}
      <Modal
        title="Create New Scrape Job"
        open={jobFormVisible}
        onCancel={() => setJobFormVisible(false)}
        footer={null}
        width={600}
      >
        <Form layout="vertical" onFinish={createScrapeJob}>
          <Form.Item label="Job Name" name="name" rules={[{ required: true }]}>
            <Input placeholder="Enter job name" />
          </Form.Item>
          
          <Form.Item label="Job Type" name="jobType" rules={[{ required: true }]}>
            <Select placeholder="Select job type">
              <Option value="web">Web Scraping</Option>
              <Option value="vk">VK Scraping</Option>
              <Option value="twitter">Twitter Scraping</Option>
              <Option value="instagram">Instagram Scraping</Option>
              <Option value="custom">Custom</Option>
            </Select>
          </Form.Item>
          
          <Form.Item label="URLs" name="urls" rules={[{ required: true }]}>
            <Input.TextArea
              placeholder="Enter URLs (one per line)"
              rows={4}
            />
          </Form.Item>
          
          <Form.Item label="Depth" name="depth" rules={[{ required: true }]}>
            <Input type="number" min={1} max={10} defaultValue={2} />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Use Proxy" name="useProxy" valuePropName="checked">
                <Select defaultValue="true">
                  <Option value="true">Yes</Option>
                  <Option value="false">No</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Use Cache" name="useCache" valuePropName="checked">
                <Select defaultValue="true">
                  <Option value="true">Yes</Option>
                  <Option value="false">No</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Render JavaScript" name="renderJs" valuePropName="checked">
                <Select defaultValue="false">
                  <Option value="true">Yes</Option>
                  <Option value="false">No</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Rate Limit (ms)" name="rateLimit">
                <Input type="number" defaultValue={1000} />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item label="Description" name="description">
            <Input.TextArea placeholder="Enter job description" rows={2} />
          </Form.Item>
          
          <Divider />
          
          <Space>
            <Button onClick={() => setJobFormVisible(false)}>
              Cancel
            </Button>
            <Button type="primary" htmlType="submit" loading={createJobMutation.isPending}>
              Create Job
            </Button>
          </Space>
        </Form>
      </Modal>

      {/* Add Proxy Modal */}
      <Modal
        title="Add Proxy Server"
        open={proxyFormVisible}
        onCancel={() => setProxyFormVisible(false)}
        footer={null}
        width={500}
      >
        <Form layout="vertical">
          <Form.Item label="Host" name="host" rules={[{ required: true }]}>
            <Input placeholder="Enter proxy host" />
          </Form.Item>
          <Form.Item label="Port" name="port" rules={[{ required: true }]}>
            <Input type="number" placeholder="Enter proxy port" />
          </Form.Item>
          <Form.Item label="Protocol" name="protocol" rules={[{ required: true }]}>
            <Select placeholder="Select protocol">
              <Option value="http">HTTP</Option>
              <Option value="https">HTTPS</Option>
              <Option value="socks5">SOCKS5</Option>
            </Select>
          </Form.Item>
          <Form.Item label="Username (if required)" name="username">
            <Input placeholder="Enter username" />
          </Form.Item>
          <Form.Item label="Password (if required)" name="password">
            <Input.Password placeholder="Enter password" />
          </Form.Item>
          <Form.Item label="Location" name="location">
            <Input placeholder="Enter location (e.g., US, EU)" />
          </Form.Item>
          
          <Divider />
          
          <Space>
            <Button onClick={() => setProxyFormVisible(false)}>
              Cancel
            </Button>
            <Button type="primary" htmlType="submit">
              Add Proxy
            </Button>
          </Space>
        </Form>
      </Modal>
    </div>
  );
};

export default ScrapingHub;
