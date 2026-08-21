import React, { useState } from 'react';
import { Card, Tabs, Button, Space, Typography, Row, Col, Divider, Modal, Form, Input, Select, Table, Tag, Progress, Alert, List, Tooltip } from 'antd';
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

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

// Mock data - truncated for brevity
const mockFeeds = [
  { id: 'feed-1', name: 'AlienVault OTX', feedType: 'stix', enabled: true, status: 'success', iocCount: 12453, frequency: 'Hourly', lastUpdated: '2024-01-15T14:30:00Z' },
  { id: 'feed-2', name: 'MISP', feedType: 'misp', enabled: true, status: 'success', iocCount: 8734, frequency: 'Daily', lastUpdated: '2024-01-15T14:25:00Z' },
];

const mockIOCs = [
  { id: 'ioc-1', value: '192.168.1.100', iocType: 'ip', confidence: 0.95, severity: 'high', description: 'Malicious IP', tags: ['malware'], firstSeen: '2024-01-01', lastSeen: '2024-01-15', source: 'OTX', relatedThreats: ['Emotet'] },
  { id: 'ioc-2', value: 'bad-domain.com', iocType: 'domain', confidence: 0.88, severity: 'high', description: 'Phishing domain', tags: ['phishing'], firstSeen: '2024-01-05', lastSeen: '2024-01-15', source: 'MISP', relatedThreats: ['Phishing'] },
];

const ThreatIntelligence: React.FC = () => {
  const [activeTab, setActiveTab] = useState('feeds');
  const [feedFormVisible, setFeedFormVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [feeds, setFeeds] = useState(mockFeeds);
  const [iocs, setIOCs] = useState(mockIOCs);
  const [search, setSearch] = useState('');

  const getStatusTag = (status: string) => {
    const colors = { success: 'success', warning: 'warning', error: 'error', disabled: 'default' };
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

  const feedColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Type', dataIndex: 'feedType', key: 'feedType', render: (t: string) => <Tag color="blue">{t.toUpperCase()}</Tag> },
    { title: 'Status', dataIndex: 'status', key: 'status', render: getStatusTag },
    { title: 'IOCs', dataIndex: 'iocCount', key: 'iocCount', render: (c: number) => c.toLocaleString() },
    { title: 'Actions', key: 'actions', render: () => <Button type="link" size="small">View</Button> },
  ];

  const iocColumns = [
    { title: 'Value', dataIndex: 'value', key: 'value' },
    { title: 'Type', dataIndex: 'iocType', key: 'iocType', render: (t: string) => <Tag color={getIOCTypeColor(t)}>{t.toUpperCase()}</Tag> },
    { title: 'Severity', dataIndex: 'severity', key: 'severity', render: getSeverityTag },
    { title: 'Confidence', dataIndex: 'confidence', key: 'confidence', render: (c: number) => `${(c * 100).toFixed(0)}%` },
    { title: 'Actions', key: 'actions', render: () => <Button type="link" size="small">View</Button> },
  ];

  const feedStatsConfig = {
    data: [{ type: 'STIX', count: 1 }, { type: 'MISP', count: 1 }],
    xField: 'type',
    yField: 'count',
    seriesField: 'type',
    color: ['#1890ff', '#52c41a'],
  };

  return (
    <div className="threat-intelligence-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="page-header">
        <div>
          <Title level={1}><Space><AlertOutlined />Threat Intelligence</Space></Title>
          <Paragraph type="secondary">Real-time threat intelligence and analysis</Paragraph>
        </div>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setFeedFormVisible(true)}>Add Feed</Button>
          <Button icon={<SyncOutlined />} onClick={() => window.location.reload()}>Refresh</Button>
        </Space>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}>
        <Row gutter={24}>
          <Col xs={24} sm={12} lg={6}><Card><Statistic title="Total Feeds" value={feeds.length} prefix={<GlobalOutlined style={{ color: '#1890ff' }} />} /></Card></Col>
          <Col xs={24} sm={12} lg={6}><Card><Statistic title="Total IOCs" value={iocs.length} prefix={<DatabaseOutlined style={{ color: '#52c41a' }} />} /></Card></Col>
          <Col xs={24} sm={12} lg={6}><Card><Statistic title="Threat Score" value={78} prefix={<FireOutlined style={{ color: '#f5222d' }} />} suffix="/ 100" /></Card></Col>
          <Col xs={24} sm={12} lg={6}><Card><Statistic title="System Health" value="98%" prefix={<SafetyOutlined style={{ color: '#52c41a' }} />} /></Card></Col>
        </Row>
      </motion.div>

      <Divider />

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}>
        <Card
          tabList={[
            { key: 'feeds', tab: 'Threat Feeds' },
            { key: 'iocs', tab: 'IOC Management' },
            { key: 'analysis', tab: 'Threat Analysis' },
            { key: 'alerts', tab: 'Alert Management' },
            { key: 'hunting', tab: 'Threat Hunting' },
            { key: 'sharing', tab: 'Intel Sharing' },
            { key: 'monitoring', tab: 'Monitoring' },
            { key: 'graph', tab: 'Threat Graph' },
          ]}
          activeTabKey={activeTab}
          onTabChange={setActiveTab}
        >
          {activeTab === 'feeds' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Threat Feeds</Title>
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={12}><Search placeholder="Search feeds..." value={search} onChange={(e) => setSearch(e.target.value)} /></Col>
                  <Col xs={24} lg={12}><Button type="primary" icon={<PlusOutlined />} onClick={() => setFeedFormVisible(true)} block>Add Feed</Button></Col>
                </Row>
              </Card>
              <Card title="Feeds by Type" style={{ marginBottom: 24 }}>
                <Bar {...feedStatsConfig} height={200} />
              </Card>
              <Card title="All Threat Feeds">
                <Table columns={feedColumns} dataSource={feeds} rowKey="id" size="small" />
              </Card>
            </div>
          )}

          {activeTab === 'iocs' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>IOC Management</Title>
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={12}><Search placeholder="Search IOCs..." value={search} onChange={(e) => setSearch(e.target.value)} /></Col>
                  <Col xs={24} lg={12}><Button type="primary" icon={<PlusOutlined />} block>Add IOC</Button></Col>
                </Row>
              </Card>
              <Card title="All IOCs">
                <Table columns={iocColumns} dataSource={iocs} rowKey="id" size="small" />
              </Card>
            </div>
          )}

          {activeTab === 'analysis' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Threat Analysis</Title>
              <Alert message="Analyze IOCs to determine risk levels" type="info" showIcon style={{ marginBottom: 24 }} />
              <Card title="Analysis Tools">
                <Row gutter={24}>
                  <Col span={12}>
                    <Card title="Analyze IOC" size="small">
                      <Form layout="vertical">
                        <Form.Item label="Select IOC"><Select options={iocs.map(i => ({ label: i.value, value: i.id }))} /></Form.Item>
                        <Form.Item><Button type="primary" block icon={<SearchOutlined />}>Analyze</Button></Form.Item>
                      </Form>
                    </Card>
                  </Col>
                </Row>
              </Card>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Alert Management</Title>
              <Card size="small" style={{ marginBottom: 24 }}>
                <Button type="primary" icon={<PlusOutlined />} block>Create Alert</Button>
              </Card>
              <Card title="Alerts">
                <Paragraph type="secondary">No alerts to display</Paragraph>
              </Card>
            </div>
          )}

          {activeTab === 'hunting' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Threat Hunting</Title>
              <Card size="small" style={{ marginBottom: 24 }}>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => setFeedFormVisible(true)} block>New Hunt</Button>
              </Card>
              <Card title="Threat Hunts">
                <Paragraph type="secondary">No threat hunts to display</Paragraph>
              </Card>
            </div>
          )}

          {activeTab === 'sharing' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Threat Intelligence Sharing</Title>
              <Row gutter={24}>
                <Col span={12}>
                  <Card title="Export">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Button type="primary" block icon={<ExportOutlined />}>Export as STIX</Button>
                      <Button block icon={<ExportOutlined />}>Export as MISP</Button>
                    </Space>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="Import">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Button type="primary" block icon={<ImportOutlined />}>Import STIX</Button>
                      <Button block icon={<ImportOutlined />}>Import MISP</Button>
                    </Space>
                  </Card>
                </Col>
              </Row>
            </div>
          )}

          {activeTab === 'monitoring' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Monitoring</Title>
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col span={6}><Card><Statistic title="Active Feeds" value={1} prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />} /></Card></Col>
                <Col span={6}><Card><Statistic title="Total IOCs" value={2} prefix={<DatabaseOutlined style={{ color: '#faad14' }} />} /></Card></Col>
                <Col span={6}><Card><Statistic title="System Health" value="98%" prefix={<SafetyOutlined style={{ color: '#52c41a' }} />} /></Card></Col>
                <Col span={6}><Card><Statistic title="Response Time" value="45s" prefix={<CloseCircleOutlined style={{ color: '#1890ff' }} />} /></Card></Col>
              </Row>
              <Card title="Monitoring Dashboard">
                <Paragraph type="secondary" style={{ textAlign: 'center', padding: 40 }}>Real-time monitoring dashboard</Paragraph>
              </Card>
            </div>
          )}

          {activeTab === 'graph' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Threat Graph</Title>
              <Card title="Threat Graph Visualization">
                <div style={{ height: 400, border: '1px solid #f0f0f0', borderRadius: 8, background: '#fafafa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Text type="secondary">Interactive threat graph visualization</Text>
                </div>
              </Card>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
};

export default ThreatIntelligence;
