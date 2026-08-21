import React, { useState, useCallback } from 'react';
import { Card, Tabs, Button, Space, Typography, Row, Col, Divider, Modal, Form, Input, Select, Table, Tag, Progress, Alert, List, Tooltip, message, DatePicker, Spin } from 'antd';
import {
  AlertOutlined,
  GlobalOutlined,
  DatabaseOutlined,
  SearchOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  FilterOutlined,
  ExportOutlined,
  ImportOutlined,
  SettingOutlined,
  SyncOutlined,
  ThunderboltOutlined,
  ShareAltOutlined,
  BellOutlined,
  SafetyOutlined,
  FireOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Line, Bar, Pie } from '@ant-design/plots';
import {
  useThreatFeeds,
  useIOCs,
  useAlerts,
  useThreatRules,
  useThreatEnrichment,
  useThreatCorrelation,
  useStixImport,
  useWebSocket
} from '../hooks/useApi';
import { useDebounce, useLocalStorage } from '../hooks/useApi';
import { exportToCSV, exportToJSON, exportToSTIX } from '../utils/exportUtils';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface ThreatFeed {
  id: string;
  name: string;
  feedType: string;
  enabled: boolean;
  status: string;
  iocCount: number;
  frequency: string;
  lastUpdated: string;
  description?: string;
}

interface IOC {
  id: string;
  value: string;
  iocType: string;
  confidence: number;
  severity: string;
  description?: string;
  tags: string[];
  firstSeen: string;
  lastSeen: string;
  source: string;
  relatedThreats: string[];
}

interface Alert {
  id: string;
  title: string;
  severity: string;
  status: string;
  createdAt: string;
  iocCount: number;
  description?: string;
}

const ThreatIntelligence: React.FC = () => {
  // State
  const [activeTab, setActiveTab] = useState('feeds');
  const [feedFormVisible, setFeedFormVisible] = useState(false);
  const [iocFormVisible, setIocFormVisible] = useState(false);
  const [alertFormVisible, setAlertFormVisible] = useState(false);
  const [selectedFeed, setSelectedFeed] = useState<ThreatFeed | null>(null);
  const [selectedIOC, setSelectedIOC] = useState<IOC | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    feedType: '',
    iocType: '',
    severity: '',
    status: '',
  });
  const [dateRange, setDateRange] = useState<any>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(60000);
  
  // Local storage for preferences
  const { value: savedAutoRefresh, setValue: saveAutoRefresh } = useLocalStorage('threat-auto-refresh', false);
  const { value: savedRefreshInterval, setValue: saveRefreshInterval } = useLocalStorage('threat-refresh-interval', 60000);
  
  // Load saved preferences
  React.useEffect(() => {
    setAutoRefresh(savedAutoRefresh);
    setRefreshInterval(savedRefreshInterval);
  }, [savedAutoRefresh, savedRefreshInterval]);
  
  // Debounced search
  const debouncedSearch = useDebounce(search, 500);
  
  // API Hooks
  const { 
    data: feeds = [], 
    isLoading: feedsLoading, 
    error: feedsError, 
    refetch: refetchFeeds 
  } = useThreatFeeds({
    enabled: activeTab === 'feeds',
    refetchInterval: autoRefresh ? refreshInterval : undefined,
  });
  
  const { 
    data: iocs = [], 
    isLoading: iocsLoading, 
    error: iocsError, 
    refetch: refetchIOCs 
  } = useIOCs({
    search: debouncedSearch || undefined,
    type: filters.iocType || undefined,
    severity: filters.severity || undefined,
  }, {
    enabled: activeTab === 'iocs',
    staleTime: 30 * 1000,
  });
  
  const { 
    data: alerts = [], 
    isLoading: alertsLoading, 
    error: alertsError, 
    refetch: refetchAlerts 
  } = useAlerts({
    status: filters.status || undefined,
  }, {
    enabled: activeTab === 'alerts',
    staleTime: 30 * 1000,
  });
  
  const { 
    data: rules = [], 
    isLoading: rulesLoading, 
    error: rulesError, 
  } = useThreatRules();
  
  const enrichmentMutation = useThreatEnrichment();
  const correlationMutation = useThreatCorrelation();
  const stixImportMutation = useStixImport();
  
  // WebSocket for real-time updates
  const { isConnected, messages } = useWebSocket(
    '/ws/threat',
    (data) => {
      if (data.type === 'threat_update') {
        refetchFeeds();
        refetchIOCs();
        refetchAlerts();
        message.info('New threat data available');
      }
    }
  );
  
  // Refresh all
  const refreshAll = useCallback(() => {
    refetchFeeds();
    refetchIOCs();
    refetchAlerts();
  }, [refetchFeeds, refetchIOCs, refetchAlerts]);
  
  // Export functions
  const exportData = useCallback((format: 'csv' | 'json' | 'stix') => {
    const data = activeTab === 'feeds' ? feeds : activeTab === 'iocs' ? iocs : alerts;
    
    if (format === 'csv') {
      exportToCSV(data, `threat-${activeTab}.csv`);
    } else if (format === 'json') {
      exportToJSON(data, `threat-${activeTab}.json`);
    } else if (format === 'stix') {
      exportToSTIX(data, `threat-${activeTab}-stix.json`);
    }
    
    message.success(`Data exported as ${format.toUpperCase()}`);
  }, [feeds, iocs, alerts, activeTab]);
  
  // Enrich IOC
  const enrichIOC = useCallback(async (ioc: string, iocType: string) => {
    try {
      const result = await enrichmentMutation.mutateAsync({ ioc, ioc_type: iocType });
      message.success('IOC enriched successfully');
      return result;
    } catch (error) {
      message.error('Failed to enrich IOC');
      throw error;
    }
  }, [enrichmentMutation]);
  
  // Correlate IOCs
  const correlateIOCs = useCallback(async (iocList: string[]) => {
    try {
      const result = await correlationMutation.mutateAsync({ iocs: iocList });
      message.success('IOCs correlated successfully');
      return result;
    } catch (error) {
      message.error('Failed to correlate IOCs');
      throw error;
    }
  }, [correlationMutation]);
  
  // Import STIX
  const importSTIX = useCallback(async (bundle: any) => {
    try {
      const result = await stixImportMutation.mutateAsync({ bundle });
      message.success('STIX bundle imported successfully');
      refetchIOCs();
      return result;
    } catch (error) {
      message.error('Failed to import STIX bundle');
      throw error;
    }
  }, [stixImportMutation, refetchIOCs]);
  
  // Helper functions
  const getStatusTag = (status: string) => {
    const colors = { success: 'success', warning: 'warning', error: 'error', disabled: 'default', active: 'processing' };
    return <Tag color={colors[status as keyof typeof colors] || 'default'}>{status}</Tag>;
  };

  const getSeverityTag = (severity: string) => {
    const colors = { critical: 'error', high: 'warning', medium: 'warning', low: 'success', info: 'info' };
    return <Tag color={colors[severity as keyof typeof colors] || 'default'}>{severity}</Tag>;
  };

  const getIOCTypeColor = (type: string) => {
    const colors = { ip: '#1890ff', domain: '#52c41a', url: '#faad14', hash: '#f5222d', email: '#722ed1' };
    return colors[type as keyof typeof colors] || '#d9d9d9';
  };

  const getIOCTypeIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      ip: <GlobalOutlined />,
      domain: <DatabaseOutlined />,
      url: <ShareAltOutlined />,
      hash: <SafetyOutlined />,
      email: <AlertOutlined />,
    };
    return icons[type] || <AlertOutlined />;
  };

  // Table columns
  const feedColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: ThreatFeed) => (
        <Space>
          {getIOCTypeIcon(record.feedType)}
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    { title: 'Type', dataIndex: 'feedType', key: 'feedType', render: (t: string) => <Tag color="blue">{t.toUpperCase()}</Tag> },
    { title: 'Status', dataIndex: 'status', key: 'status', render: getStatusTag },
    { title: 'IOCs', dataIndex: 'iocCount', key: 'iocCount', render: (c: number) => c.toLocaleString() },
    { title: 'Frequency', dataIndex: 'frequency', key: 'frequency' },
    {
      title: 'Last Updated',
      dataIndex: 'lastUpdated',
      key: 'lastUpdated',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ThreatFeed) => (
        <Space>
          <Tooltip title="View feed details">
            <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => setSelectedFeed(record)} />
          </Tooltip>
          <Tooltip title="Sync now">
            <Button type="link" size="small" icon={<SyncOutlined />} />
          </Tooltip>
          <Tooltip title="Edit">
            <Button type="link" size="small" icon={<EditOutlined />} />
          </Tooltip>
          <Tooltip title="Delete">
            <Button type="link" size="small" icon={<DeleteOutlined />} danger />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const iocColumns = [
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (value: string, record: IOC) => (
        <Space>
          {getIOCTypeIcon(record.iocType)}
          <Text code>{value}</Text>
        </Space>
      ),
    },
    { title: 'Type', dataIndex: 'iocType', key: 'iocType', render: (t: string) => <Tag color={getIOCTypeColor(t)}>{t.toUpperCase()}</Tag> },
    { title: 'Severity', dataIndex: 'severity', key: 'severity', render: getSeverityTag },
    { title: 'Confidence', dataIndex: 'confidence', key: 'confidence', render: (c: number) => `${(c * 100).toFixed(0)}%` },
    {
      title: 'Tags',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) => (
        <Space wrap>
          {tags.map(tag => <Tag key={tag} color="default">{tag}</Tag>)}
        </Space>
      ),
    },
    {
      title: 'First Seen',
      dataIndex: 'firstSeen',
      key: 'firstSeen',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: IOC) => (
        <Space>
          <Tooltip title="View IOC details">
            <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => setSelectedIOC(record)} />
          </Tooltip>
          <Tooltip title="Enrich">
            <Button type="link" size="small" icon={<ThunderboltOutlined />} onClick={() => enrichIOC(record.value, record.iocType)} />
          </Tooltip>
          <Tooltip title="Delete">
            <Button type="link" size="small" icon={<DeleteOutlined />} danger />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const alertColumns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      render: (title: string) => <Text strong>{title}</Text>,
    },
    { title: 'Severity', dataIndex: 'severity', key: 'severity', render: getSeverityTag },
    { title: 'Status', dataIndex: 'status', key: 'status', render: getStatusTag },
    { title: 'IOCs', dataIndex: 'iocCount', key: 'iocCount', render: (c: number) => c.toLocaleString() },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Alert) => (
        <Space>
          <Tooltip title="View alert details">
            <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => setSelectedAlert(record)} />
          </Tooltip>
          <Tooltip title="Acknowledge">
            <Button type="link" size="small" icon={<CheckCircleOutlined />} />
          </Tooltip>
          <Tooltip title="Close">
            <Button type="link" size="small" icon={<CloseCircleOutlined />} danger />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // Stats
  const totalFeeds = feeds.length;
  const activeFeeds = feeds.filter(f => f.status === 'success').length;
  const totalIOCs = iocs.length;
  const criticalIOCs = iocs.filter(i => i.severity === 'critical').length;
  const highIOCs = iocs.filter(i => i.severity === 'high').length;
  const totalAlerts = alerts.length;
  const activeAlerts = alerts.filter(a => a.status === 'active').length;
  
  // Feed type distribution
  const feedTypeData = React.useMemo(() => {
    const counts: Record<string, number> = {};
    feeds.forEach(f => {
      counts[f.feedType] = (counts[f.feedType] || 0) + 1;
    });
    return Object.entries(counts).map(([type, count]) => ({ type, count }));
  }, [feeds]);
  
  // IOC type distribution
  const iocTypeData = React.useMemo(() => {
    const counts: Record<string, number> = {};
    iocs.forEach(i => {
      counts[i.iocType] = (counts[i.iocType] || 0) + 1;
    });
    return Object.entries(counts).map(([type, count]) => ({ type, count }));
  }, [iocs]);
  
  // Severity distribution
  const severityData = React.useMemo(() => {
    const counts: Record<string, number> = {};
    iocs.forEach(i => {
      counts[i.severity] = (counts[i.severity] || 0) + 1;
    });
    return Object.entries(counts).map(([severity, count]) => ({ severity, count }));
  }, [iocs]);
  
  // Loading state
  const isLoading = feedsLoading || iocsLoading || alertsLoading || rulesLoading;
  const hasError = feedsError || iocsError || alertsError || rulesError;
  
  return (
    <div className="threat-intelligence-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="page-header">
        <div>
          <Title level={1}><Space><AlertOutlined />Threat Intelligence</Space></Title>
          <Paragraph type="secondary">Real-time threat intelligence and analysis</Paragraph>
        </div>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setFeedFormVisible(true)}>
            Add Feed
          </Button>
          <Button icon={<SyncOutlined spin={isLoading} />} onClick={refreshAll} loading={isLoading}>
            Refresh
          </Button>
          <Tooltip title="WebSocket status">
            <Tag color={isConnected ? 'green' : 'red'}>
              {isConnected ? 'Live' : 'Disconnected'}
            </Tag>
          </Tooltip>
        </Space>
      </motion.div>

      {/* Stats Overview */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={4}>
          <Card>
            <Title level={4} style={{ margin: 0 }}>
              <DatabaseOutlined style={{ marginRight: 8 }} />
              Feeds
            </Title>
            <Title level={2} style={{ margin: '16px 0 0' }}>
              {totalFeeds}
            </Title>
            <Text type="secondary">
              {activeFeeds} active
            </Text>
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Title level={4} style={{ margin: 0 }}>
              <SafetyOutlined style={{ marginRight: 8 }} />
              IOCs
            </Title>
            <Title level={2} style={{ margin: '16px 0 0' }}>
              {totalIOCs.toLocaleString()}
            </Title>
            <Text type="secondary">
              <Tag color="red">{criticalIOCs} critical</Tag>
              <Tag color="orange" style={{ marginLeft: 4 }}>{highIOCs} high</Tag>
            </Text>
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Title level={4} style={{ margin: 0 }}>
              <BellOutlined style={{ marginRight: 8 }} />
              Alerts
            </Title>
            <Title level={2} style={{ margin: '16px 0 0' }}>
              {totalAlerts}
            </Title>
            <Text type="secondary">
              {activeAlerts} active
            </Text>
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Title level={4} style={{ margin: 0 }}>
              <FireOutlined style={{ marginRight: 8 }} />
              Threats
            </Title>
            <Title level={2} style={{ margin: '16px 0 0' }}>
              {rules.length}
            </Title>
            <Text type="secondary">
              rules loaded
            </Text>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Title level={4} style={{ margin: 0 }}>
              <GlobalOutlined style={{ marginRight: 8 }} />
              Coverage
            </Title>
            <Pie
              data={feedTypeData}
              angleField="count"
              colorField="type"
              radius={0.8}
              height={100}
            />
          </Card>
        </Col>
      </Row>

      {/* Error Alert */}
      {hasError && (
        <Alert
          message="Error loading threat intelligence data"
          description={feedsError?.message || iocsError?.message || alertsError?.message || rulesError?.message}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Main Content Tabs */}
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'feeds',
              label: 'Feeds',
              icon: <DatabaseOutlined />,
              children: (
                <Spin spinning={feedsLoading}>
                  <Space direction="vertical" size="middle">
                    <Row justify="space-between">
                      <Col>
                        <Title level={4}>Threat Feeds ({feeds.length})</Title>
                      </Col>
                      <Col>
                        <Space>
                          <Select
                            placeholder="Filter by type"
                            value={filters.feedType}
                            onChange={(value) => setFilters({ ...filters, feedType: value })}
                            style={{ width: 150 }}
                            allowClear
                          >
                            <Option value="stix">STIX</Option>
                            <Option value="misp">MISP</Option>
                            <Option value="otx">OTX</Option>
                          </Select>
                          <Button icon={<ImportOutlined />} onClick={() => setFeedFormVisible(true)}>
                            Import
                          </Button>
                        </Space>
                      </Col>
                    </Row>
                    
                    <Table
                      columns={feedColumns}
                      dataSource={feeds}
                      rowKey="id"
                      pagination={{ pageSize: 10 }}
                    />
                  </Space>
                </Spin>
              ),
            },
            {
              key: 'iocs',
              label: 'IOCs',
              icon: <SafetyOutlined />,
              children: (
                <Spin spinning={iocsLoading}>
                  <Space direction="vertical" size="middle">
                    <Row justify="space-between">
                      <Col>
                        <Title level={4}>Indicators of Compromise ({iocs.length})</Title>
                      </Col>
                      <Col>
                        <Space>
                          <Input
                            placeholder="Search IOCs..."
                            prefix={<SearchOutlined />}
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            style={{ width: 200 }}
                          />
                          <Select
                            placeholder="Filter by type"
                            value={filters.iocType}
                            onChange={(value) => setFilters({ ...filters, iocType: value })}
                            style={{ width: 120 }}
                            allowClear
                          >
                            <Option value="ip">IP</Option>
                            <Option value="domain">Domain</Option>
                            <Option value="url">URL</Option>
                            <Option value="hash">Hash</Option>
                            <Option value="email">Email</Option>
                          </Select>
                          <Select
                            placeholder="Filter by severity"
                            value={filters.severity}
                            onChange={(value) => setFilters({ ...filters, severity: value })}
                            style={{ width: 120 }}
                            allowClear
                          >
                            <Option value="critical">Critical</Option>
                            <Option value="high">High</Option>
                            <Option value="medium">Medium</Option>
                            <Option value="low">Low</Option>
                          </Select>
                          <Button icon={<PlusOutlined />} onClick={() => setIocFormVisible(true)}>
                            Add
                          </Button>
                          <Button icon={<ExportOutlined />} onClick={() => exportData('csv')}>
                            Export
                          </Button>
                        </Space>
                      </Col>
                    </Row>
                    
                    <Row gutter={16} style={{ marginBottom: 16 }}>
                      <Col span={12}>
                        <Card size="small" title="IOC Types">
                          <Bar
                            data={iocTypeData}
                            xField="type"
                            yField="count"
                            height={200}
                          />
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card size="small" title="Severity Distribution">
                          <Pie
                            data={severityData}
                            angleField="count"
                            colorField="severity"
                            radius={0.8}
                            height={200}
                          />
                        </Card>
                      </Col>
                    </Row>
                    
                    <Table
                      columns={iocColumns}
                      dataSource={iocs}
                      rowKey="id"
                      pagination={{ pageSize: 20 }}
                    />
                  </Space>
                </Spin>
              ),
            },
            {
              key: 'alerts',
              label: 'Alerts',
              icon: <BellOutlined />,
              children: (
                <Spin spinning={alertsLoading}>
                  <Space direction="vertical" size="middle">
                    <Row justify="space-between">
                      <Col>
                        <Title level={4}>Alerts ({alerts.length})</Title>
                      </Col>
                      <Col>
                        <Space>
                          <Select
                            placeholder="Filter by status"
                            value={filters.status}
                            onChange={(value) => setFilters({ ...filters, status: value })}
                            style={{ width: 150 }}
                            allowClear
                          >
                            <Option value="active">Active</Option>
                            <Option value="acknowledged">Acknowledged</Option>
                            <Option value="closed">Closed</Option>
                          </Select>
                          <Button icon={<PlusOutlined />} onClick={() => setAlertFormVisible(true)}>
                            Create
                          </Button>
                        </Space>
                      </Col>
                    </Row>
                    
                    <Table
                      columns={alertColumns}
                      dataSource={alerts}
                      rowKey="id"
                      pagination={{ pageSize: 10 }}
                    />
                  </Space>
                </Spin>
              ),
            },
            {
              key: 'analysis',
              label: 'Analysis',
              icon: <ThunderboltOutlined />,
              children: (
                <Card>
                  <Title level={4}>Threat Analysis Tools</Title>
                  <Paragraph>
                    Advanced threat analysis using AI/ML and correlation engines.
                  </Paragraph>
                  
                  <Space direction="vertical">
                    <Card title="IOC Enrichment">
                      <Text>
                        Enrich IOCs with additional context from threat intelligence feeds.
                      </Text>
                      <Button type="primary" style={{ marginTop: 16 }} icon={<ThunderboltOutlined />}>
                        Enrich Selected IOCs
                      </Button>
                    </Card>
                    
                    <Card title="IOC Correlation">
                      <Text>
                        Find relationships between IOCs to identify attack patterns.
                      </Text>
                      <Button type="primary" style={{ marginTop: 16 }} icon={<ShareAltOutlined />}>
                        Correlate IOCs
                      </Button>
                    </Card>
                    
                    <Card title="STIX Import/Export">
                      <Text>
                        Import and export threat intelligence in STIX format for interoperability.
                      </Text>
                      <Space style={{ marginTop: 16 }}>
                        <Button type="primary" icon={<ImportOutlined />} onClick={() => message.info('STIX import coming soon')}>
                          Import STIX
                        </Button>
                        <Button type="primary" icon={<ExportOutlined />} onClick={() => exportData('stix')}>
                          Export STIX
                        </Button>
                      </Space>
                    </Card>
                  </Space>
                </Card>
              ),
            },
            {
              key: 'rules',
              label: 'Rules',
              icon: <WarningOutlined />,
              children: (
                <Spin spinning={rulesLoading}>
                  <Space direction="vertical" size="middle">
                    <Row justify="space-between">
                      <Col>
                        <Title level={4}>Threat Rules ({rules.length})</Title>
                      </Col>
                      <Col>
                        <Button icon={<PlusOutlined />}>Add Rule</Button>
                      </Col>
                    </Row>
                    
                    <List
                      dataSource={rules}
                      renderItem={(rule: any) => (
                        <List.Item>
                          <Card>
                            <Row justify="space-between">
                              <Col flex="auto">
                                <Title level={5}>{rule.name || rule.id}</Title>
                                <Text type="secondary">{rule.description}</Text>
                              </Col>
                              <Col>
                                <Space>
                                  <Tag color={rule.enabled ? 'green' : 'red'}>
                                    {rule.enabled ? 'Enabled' : 'Disabled'}
                                  </Tag>
                                  <Button type="link" size="small" icon={<EditOutlined />} />
                                  <Button type="link" size="small" icon={<DeleteOutlined />} danger />
                                </Space>
                              </Col>
                            </Row>
                          </Card>
                        </List.Item>
                      )}
                    />
                  </Space>
                </Spin>
              ),
            },
          ]}
        />
      </Card>

      {/* Feed Detail Modal */}
      <Modal
        title="Feed Details"
        open={!!selectedFeed}
        onCancel={() => setSelectedFeed(null)}
        footer={null}
        width={600}
      >
        {selectedFeed && (
          <Card>
            <Title level={4}>{selectedFeed.name}</Title>
            <Tag color="blue">{selectedFeed.feedType.toUpperCase()}</Tag>
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>Status:</Text>
              </Col>
              <Col span={12}>
                {getStatusTag(selectedFeed.status)}
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Text strong>IOC Count:</Text>
              </Col>
              <Col span={12}>
                <Text>{selectedFeed.iocCount.toLocaleString()}</Text>
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Text strong>Frequency:</Text>
              </Col>
              <Col span={12}>
                <Text>{selectedFeed.frequency}</Text>
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Text strong>Last Updated:</Text>
              </Col>
              <Col span={12}>
                <Text>{new Date(selectedFeed.lastUpdated).toLocaleString()}</Text>
              </Col>
            </Row>
            
            {selectedFeed.description && (
              <>
                <Divider />
                <Text strong>Description:</Text>
                <Paragraph>{selectedFeed.description}</Paragraph>
              </>
            )}
            
            <Divider />
            
            <Space>
              <Button type="primary" icon={<SyncOutlined />}>
                Sync Now
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

      {/* IOC Detail Modal */}
      <Modal
        title="IOC Details"
        open={!!selectedIOC}
        onCancel={() => setSelectedIOC(null)}
        footer={null}
        width={600}
      >
        {selectedIOC && (
          <Card>
            <Title level={4}>
              <Space>
                {getIOCTypeIcon(selectedIOC.iocType)}
                {selectedIOC.value}
              </Space>
            </Title>
            <Tag color={getIOCTypeColor(selectedIOC.iocType)}>
              {selectedIOC.iocType.toUpperCase()}
            </Tag>
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>Severity:</Text>
              </Col>
              <Col span={12}>
                {getSeverityTag(selectedIOC.severity)}
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Text strong>Confidence:</Text>
              </Col>
              <Col span={12}>
                <Progress percent={selectedIOC.confidence * 100} showInfo={false} />
                <Text>{(selectedIOC.confidence * 100).toFixed(0)}%</Text>
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Text strong>Source:</Text>
              </Col>
              <Col span={12}>
                <Text>{selectedIOC.source}</Text>
              </Col>
            </Row>
            
            {selectedIOC.tags.length > 0 && (
              <>
                <Divider />
                <Text strong>Tags:</Text>
                <Space wrap style={{ marginTop: 8 }}>
                  {selectedIOC.tags.map(tag => (
                    <Tag key={tag} color="default">{tag}</Tag>
                  ))}
                </Space>
              </>
            )}
            
            {selectedIOC.relatedThreats.length > 0 && (
              <>
                <Divider />
                <Text strong>Related Threats:</Text>
                <Space wrap style={{ marginTop: 8 }}>
                  {selectedIOC.relatedThreats.map(threat => (
                    <Tag key={threat} color="red">{threat}</Tag>
                  ))}
                </Space>
              </>
            )}
            
            {selectedIOC.description && (
              <>
                <Divider />
                <Text strong>Description:</Text>
                <Paragraph>{selectedIOC.description}</Paragraph>
              </>
            )}
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>First Seen:</Text>
                <Text>{new Date(selectedIOC.firstSeen).toLocaleString()}</Text>
              </Col>
              <Col span={12}>
                <Text strong>Last Seen:</Text>
                <Text>{new Date(selectedIOC.lastSeen).toLocaleString()}</Text>
              </Col>
            </Row>
            
            <Divider />
            
            <Space>
              <Button type="primary" icon={<ThunderboltOutlined />} onClick={() => enrichIOC(selectedIOC.value, selectedIOC.iocType)}>
                Enrich
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

      {/* Alert Detail Modal */}
      <Modal
        title="Alert Details"
        open={!!selectedAlert}
        onCancel={() => setSelectedAlert(null)}
        footer={null}
        width={600}
      >
        {selectedAlert && (
          <Card>
            <Title level={4}>{selectedAlert.title}</Title>
            {getSeverityTag(selectedAlert.severity)}
            {getStatusTag(selectedAlert.status)}
            
            <Divider />
            
            {selectedAlert.description && (
              <>
                <Text strong>Description:</Text>
                <Paragraph>{selectedAlert.description}</Paragraph>
              </>
            )}
            
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>IOCs:</Text>
              </Col>
              <Col span={12}>
                <Text>{selectedAlert.iocCount.toLocaleString()}</Text>
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Text strong>Created:</Text>
              </Col>
              <Col span={12}>
                <Text>{new Date(selectedAlert.createdAt).toLocaleString()}</Text>
              </Col>
            </Row>
            
            <Divider />
            
            <Space>
              <Button type="primary" icon={<CheckCircleOutlined />}>
                Acknowledge
              </Button>
              <Button icon={<EditOutlined />}>
                Edit
              </Button>
              <Button icon={<CloseCircleOutlined />} danger>
                Close
              </Button>
            </Space>
          </Card>
        )}
      </Modal>

      {/* Add Feed Modal */}
      <Modal
        title="Add Threat Feed"
        open={feedFormVisible}
        onCancel={() => setFeedFormVisible(false)}
        footer={null}
        width={500}
      >
        <Form layout="vertical">
          <Form.Item label="Feed Name" name="name" rules={[{ required: true }]}>
            <Input placeholder="Enter feed name" />
          </Form.Item>
          <Form.Item label="Feed Type" name="feedType" rules={[{ required: true }]}>
            <Select placeholder="Select feed type">
              <Option value="stix">STIX</Option>
              <Option value="misp">MISP</Option>
              <Option value="otx">AlienVault OTX</Option>
              <Option value="custom">Custom</Option>
            </Select>
          </Form.Item>
          <Form.Item label="Feed URL" name="url" rules={[{ required: true }]}>
            <Input placeholder="Enter feed URL" />
          </Form.Item>
          <Form.Item label="Frequency" name="frequency">
            <Select placeholder="Select update frequency">
              <Option value="hourly">Hourly</Option>
              <Option value="daily">Daily</Option>
              <Option value="weekly">Weekly</Option>
              <Option value="manual">Manual</Option>
            </Select>
          </Form.Item>
          <Form.Item label="Description" name="description">
            <Input.TextArea placeholder="Enter feed description" rows={3} />
          </Form.Item>
          
          <Divider />
          
          <Space>
            <Button onClick={() => setFeedFormVisible(false)}>
              Cancel
            </Button>
            <Button type="primary" htmlType="submit">
              Add Feed
            </Button>
          </Space>
        </Form>
      </Modal>
    </div>
  );
};

export default ThreatIntelligence;
