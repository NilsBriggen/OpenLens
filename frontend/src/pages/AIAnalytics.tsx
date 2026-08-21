import React, { useState } from 'react';
import { Card, Tabs, Button, Space, Typography, Row, Col, Divider, Modal, Form, Input, Select, Table, Tag, Progress, Alert, Spin, DatePicker } from 'antd';
import {
  RobotOutlined,
  SearchOutlined,
  FilterOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  AlertOutlined,
  ThunderboltOutlined,
  TeamOutlined,
  FileTextOutlined,
  BarChartOutlined,
  ClusterOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  ExportOutlined,
  SettingOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Line, Bar, Pie, Column, Scatter } from '@ant-design/plots';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;

// API Service
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${Cookies.get('access_token')}`,
  },
});

// Mock data
const mockAnomalies = [
  {
    id: 'anomaly-1',
    type: 'statistical',
    score: 9.5,
    entity: 'Node 12345',
    feature: 'connection_count',
    value: 156,
    expected: 45,
    timestamp: '2024-01-15T14:30:00Z',
    status: 'high',
  },
  {
    id: 'anomaly-2',
    type: 'isolation_forest',
    score: 8.2,
    entity: 'Node 67890',
    feature: 'activity_pattern',
    value: 'suspicious',
    expected: 'normal',
    timestamp: '2024-01-15T13:45:00Z',
    status: 'medium',
  },
  {
    id: 'anomaly-3',
    type: 'graph',
    score: 7.8,
    entity: 'Subgraph A',
    feature: 'density',
    value: 0.95,
    expected: 0.45,
    timestamp: '2024-01-15T12:15:00Z',
    status: 'medium',
  },
  {
    id: 'anomaly-4',
    type: 'temporal',
    score: 6.5,
    entity: 'Node 54321',
    feature: 'activity_spike',
    value: 45,
    expected: 15,
    timestamp: '2024-01-15T10:00:00Z',
    status: 'low',
  },
];

const mockEntities = [
  {
    id: 'entity-1',
    name: 'John Doe',
    type: 'person',
    matches: [
      { id: 'match-1', name: 'John Doe', similarity: 0.98, source: 'database_a' },
      { id: 'match-2', name: 'John H. Doe', similarity: 0.85, source: 'database_b' },
      { id: 'match-3', name: 'Jon Doe', similarity: 0.72, source: 'database_c' },
    ],
    resolved: true,
  },
  {
    id: 'entity-2',
    name: 'Tech Corp',
    type: 'company',
    matches: [
      { id: 'match-4', name: 'Tech Corp Inc', similarity: 0.95, source: 'database_a' },
      { id: 'match-5', name: 'Tech Corporation', similarity: 0.88, source: 'database_b' },
    ],
    resolved: false,
  },
];

const mockPredictions = [
  {
    id: 'prediction-1',
    type: 'link',
    node1: 'Person A',
    node2: 'Person B',
    score: 0.92,
    method: 'common_neighbors',
    confidence: 'high',
    timestamp: '2024-01-15T14:30:00Z',
  },
  {
    id: 'prediction-2',
    type: 'link',
    node1: 'Company X',
    node2: 'Company Y',
    score: 0.78,
    method: 'jaccard',
    confidence: 'medium',
    timestamp: '2024-01-15T13:45:00Z',
  },
  {
    id: 'prediction-3',
    type: 'node_classification',
    node: 'Person C',
    class: 'suspicious',
    score: 0.85,
    method: 'logistic_regression',
    confidence: 'high',
    timestamp: '2024-01-15T12:15:00Z',
  },
];

const mockClusters = [
  {
    id: 'cluster-1',
    size: 45,
    cohesion: 0.85,
    labels: ['person', 'company'],
    topFeatures: ['high_activity', 'multiple_connections'],
  },
  {
    id: 'cluster-2',
    size: 32,
    cohesion: 0.78,
    labels: ['ip', 'domain'],
    topFeatures: ['suspicious_patterns', 'unusual_traffic'],
  },
  {
    id: 'cluster-3',
    size: 28,
    cohesion: 0.92,
    labels: ['email', 'person'],
    topFeatures: ['communication_network', 'frequent_messages'],
  },
];

const mockNLPResults = [
  {
    id: 'nlp-1',
    text: 'The company is planning to expand into new markets next quarter.',
    sentiment: 'positive',
    entities: [
      { text: 'company', type: 'ORG', score: 0.95 },
      { text: 'new markets', type: 'MISC', score: 0.88 },
      { text: 'next quarter', type: 'DATE', score: 0.92 },
    ],
    topics: ['business', 'expansion', 'growth'],
  },
  {
    id: 'nlp-2',
    text: 'Security breach detected in the main server.',
    sentiment: 'negative',
    entities: [
      { text: 'security breach', type: 'EVENT', score: 0.98 },
      { text: 'main server', type: 'MISC', score: 0.95 },
    ],
    topics: ['security', 'incident', 'threat'],
  },
];

const mockRecommendations = [
  {
    id: 'rec-1',
    type: 'investigation',
    title: 'Investigate Anomaly Cluster',
    description: 'A cluster of 12 nodes shows unusual activity patterns.',
    priority: 'high',
    confidence: 0.92,
    actions: ['Review connections', 'Check timestamps', 'Verify identities'],
  },
  {
    id: 'rec-2',
    type: 'monitoring',
    title: 'Monitor IP Range',
    description: 'IP addresses in the 192.168.1.x range show suspicious behavior.',
    priority: 'medium',
    confidence: 0.85,
    actions: ['Set up alerts', 'Increase logging', 'Review firewall rules'],
  },
];

const AIAnalytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState('anomalies');
  const [anomalyMethod, setAnomalyMethod] = useState('statistical');
  const [entityMethod, setEntityMethod] = useState('exact');
  const [predictionMethod, setPredictionMethod] = useState('common_neighbors');
  const [clusterMethod, setClusterMethod] = useState('kmeans');
  const [dateRange, setDateRange] = useState<any>(null);
  const [search, setSearch] = useState('');
  const [selectedAnomaly, setSelectedAnomaly] = useState<any>(null);
  const [selectedEntity, setSelectedEntity] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [anomalyResults, setAnomalyResults] = useState(mockAnomalies);
  const [entityResults, setEntityResults] = useState(mockEntities);
  const [predictionResults, setPredictionResults] = useState(mockPredictions);
  const [clusterResults, setClusterResults] = useState(mockClusters);
  const [nlpResults, setNlpResults] = useState(mockNLPResults);
  const [recommendationResults, setRecommendationResults] = useState(mockRecommendations);

  const queryClient = useQueryClient();

  // Anomaly detection methods
  const anomalyMethods = [
    { label: 'Statistical', value: 'statistical' },
    { label: 'Z-Score', value: 'zscore' },
    { label: 'IQR', value: 'iqr' },
    { label: 'Isolation Forest', value: 'isolation_forest' },
    { label: 'Local Outlier Factor', value: 'lof' },
    { label: 'DBSCAN', value: 'dbscan' },
    { label: 'Graph Anomalies', value: 'graph' },
    { label: 'Temporal Anomalies', value: 'temporal' },
  ];

  // Entity resolution methods
  const entityMethods = [
    { label: 'Exact Match', value: 'exact' },
    { label: 'Fuzzy Match', value: 'fuzzy' },
    { label: 'Record Linkage', value: 'record_linkage' },
    { label: 'Graph-Based', value: 'graph' },
  ];

  // Link prediction methods
  const predictionMethods = [
    { label: 'Common Neighbors', value: 'common_neighbors' },
    { label: 'Jaccard Coefficient', value: 'jaccard' },
    { label: 'Adamic-Adar', value: 'adamic_adar' },
    { label: 'Preferential Attachment', value: 'preferential_attachment' },
  ];

  // Clustering methods
  const clusterMethods = [
    { label: 'K-Means', value: 'kmeans' },
    { label: 'DBSCAN', value: 'dbscan' },
    { label: 'Hierarchical', value: 'hierarchical' },
    { label: 'Spectral', value: 'spectral' },
    { label: 'Gaussian Mixture', value: 'gmm' },
  ];

  // Run anomaly detection
  const runAnomalyDetection = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/ai/anomalies/detect', {
        method: anomalyMethod,
        threshold: 3.0,
      });
      setAnomalyResults(response.data.anomalies || mockAnomalies);
    } catch (error) {
      console.error('Anomaly detection error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Run entity resolution
  const runEntityResolution = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/ai/entities/resolve', {
        method: entityMethod,
        threshold: 0.85,
      });
      setEntityResults(response.data.matches || mockEntities);
    } catch (error) {
      console.error('Entity resolution error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Run link prediction
  const runLinkPrediction = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/ai/predict/link', {
        node1: 'Person A',
        node2: 'Person B',
        method: predictionMethod,
      });
      setPredictionResults([response.data] || mockPredictions);
    } catch (error) {
      console.error('Link prediction error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Run clustering
  const runClustering = async () => {
    setLoading(true);
    try {
      // This would call the clustering endpoint
      setClusterResults(mockClusters);
    } catch (error) {
      console.error('Clustering error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'high': return '#f5222d';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#d9d9d9';
    }
  };

  // Get confidence color
  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return '#52c41a';
      case 'medium': return '#faad14';
      case 'low': return '#f5222d';
      default: return '#d9d9d9';
    }
  };

  // Get sentiment color
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '#52c41a';
      case 'negative': return '#f5222d';
      case 'neutral': return '#d9d9d9';
      default: return '#d9d9d9';
    }
  };

  // Anomaly columns
  const anomalyColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 150,
      render: (type: string) => <Tag color="blue">{type.replace('_', ' ')}</Tag>,
    },
    {
      title: 'Entity',
      dataIndex: 'entity',
      key: 'entity',
      width: 150,
    },
    {
      title: 'Feature',
      dataIndex: 'feature',
      key: 'feature',
      width: 150,
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      width: 100,
      sorter: (a: any, b: any) => a.score - b.score,
      render: (score: number) => (
        <Progress
          percent={Math.min(score * 10, 100)}
          size="small"
          status={score > 8 ? 'exception' : score > 5 ? 'warning' : 'normal'}
        />
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)} style={{ textTransform: 'capitalize' }}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 200,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small" onClick={() => setSelectedAnomaly(record)}>
            View
          </Button>
        </Space>
      ),
    },
  ];

  // Entity columns
  const entityColumns = [
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
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type: string) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: 'Matches',
      dataIndex: 'matches',
      key: 'matches',
      width: 100,
      render: (matches: any[]) => matches.length,
    },
    {
      title: 'Best Match',
      key: 'bestMatch',
      width: 200,
      render: (_: any, record: any) => {
        const bestMatch = record.matches[0];
        return bestMatch ? (
          <div>
            <div>{bestMatch.name}</div>
            <div style={{ fontSize: 12, color: '#666' }}>
              Similarity: {(bestMatch.similarity * 100).toFixed(1)}%
            </div>
          </div>
        ) : null;
      },
    },
    {
      title: 'Resolved',
      dataIndex: 'resolved',
      key: 'resolved',
      width: 100,
      render: (resolved: boolean) => (
        <Tag color={resolved ? '#52c41a' : '#faad14'}>
          {resolved ? 'Yes' : 'No'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small" onClick={() => setSelectedEntity(record)}>
            View
          </Button>
        </Space>
      ),
    },
  ];

  // Prediction columns
  const predictionColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 150,
      render: (type: string) => <Tag color="blue">{type.replace('_', ' ')}</Tag>,
    },
    {
      title: 'Node 1',
      dataIndex: 'node1',
      key: 'node1',
      width: 150,
    },
    {
      title: 'Node 2',
      dataIndex: 'node2',
      key: 'node2',
      width: 150,
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      width: 100,
      render: (score: number) => (
        <Progress
          percent={score * 100}
          size="small"
          status={score > 0.8 ? 'success' : score > 0.5 ? 'warning' : 'exception'}
        />
      ),
    },
    {
      title: 'Method',
      dataIndex: 'method',
      key: 'method',
      width: 150,
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 100,
      render: (confidence: string) => (
        <Tag color={getConfidenceColor(confidence)} style={{ textTransform: 'capitalize' }}>
          {confidence}
        </Tag>
      ),
    },
  ];

  // Cluster columns
  const clusterColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
    },
    {
      title: 'Size',
      dataIndex: 'size',
      key: 'size',
      width: 100,
      sorter: (a: any, b: any) => a.size - b.size,
    },
    {
      title: 'Cohesion',
      dataIndex: 'cohesion',
      key: 'cohesion',
      width: 100,
      render: (cohesion: number) => (
        <Progress
          percent={cohesion * 100}
          size="small"
          status={cohesion > 0.8 ? 'success' : cohesion > 0.5 ? 'warning' : 'exception'}
        />
      ),
    },
    {
      title: 'Labels',
      dataIndex: 'labels',
      key: 'labels',
      width: 200,
      render: (labels: string[]) => (
        <Space>
          {labels.map(label => <Tag key={label} color="blue">{label}</Tag>)}
        </Space>
      ),
    },
    {
      title: 'Top Features',
      dataIndex: 'topFeatures',
      key: 'topFeatures',
      width: 250,
      render: (features: string[]) => (
        <Space>
          {features.map(feature => <Tag key={feature} color="green">{feature}</Tag>)}
        </Space>
      ),
    },
  ];

  // NLP columns
  const nlpColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Text',
      dataIndex: 'text',
      key: 'text',
      width: 300,
      render: (text: string) => (
        <div style={{ maxWidth: 300, whiteSpace: 'normal' }}>
          {text}
        </div>
      ),
    },
    {
      title: 'Sentiment',
      dataIndex: 'sentiment',
      key: 'sentiment',
      width: 120,
      render: (sentiment: string) => (
        <Tag color={getSentimentColor(sentiment)} style={{ textTransform: 'capitalize' }}>
          {sentiment}
        </Tag>
      ),
    },
    {
      title: 'Topics',
      dataIndex: 'topics',
      key: 'topics',
      width: 200,
      render: (topics: string[]) => (
        <Space>
          {topics.map(topic => <Tag key={topic} color="purple">{topic}</Tag>)}
        </Space>
      ),
    },
    {
      title: 'Entities',
      dataIndex: 'entities',
      key: 'entities',
      width: 200,
      render: (entities: any[]) => (
        <Space direction="vertical">
          {entities.map(entity => (
            <Tag key={entity.id} color="geekblue">
              {entity.text} ({entity.type})
            </Tag>
          ))}
        </Space>
      ),
    },
  ];

  // Recommendation columns
  const recommendationColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type: string) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: 200,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: string) => (
        <Tag color={getStatusColor(priority)} style={{ textTransform: 'capitalize' }}>
          {priority}
        </Tag>
      ),
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 100,
      render: (confidence: number) => (
        <Progress
          percent={confidence * 100}
          size="small"
          status={confidence > 0.8 ? 'success' : confidence > 0.5 ? 'warning' : 'exception'}
        />
      ),
    },
    {
      title: 'Actions',
      dataIndex: 'actions',
      key: 'actions',
      width: 200,
      render: (actions: string[]) => (
        <Space direction="vertical">
          {actions.map(action => (
            <Tag key={action} color="green">{action}</Tag>
          ))}
        </Space>
      ),
    },
  ];

  // Anomaly chart config
  const anomalyChartConfig = {
    data: anomalyResults.map(a => ({
      date: a.timestamp,
      score: a.score,
      type: a.type,
    })),
    xField: 'date',
    yField: 'score',
    seriesField: 'type',
    color: ['#1890ff', '#52c41a', '#faad14', '#f5222d'],
    legend: {
      position: 'top-right' as const,
    },
    smooth: true,
    point: {
      size: 5,
      shape: 'diamond' as const,
    },
  };

  // Entity match chart config
  const entityChartConfig = {
    data: entityResults.flatMap(e => e.matches.map(m => ({
      entity: e.name,
      match: m.name,
      similarity: m.similarity,
    }))),
    xField: 'entity',
    yField: 'similarity',
    seriesField: 'match',
    color: ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'],
    legend: {
      position: 'top-right' as const,
    },
    columnStyle: {
      radius: [4, 4, 0, 0],
    },
  };

  // Cluster chart config
  const clusterChartConfig = {
    data: clusterResults.map(c => ({
      cluster: c.id,
      size: c.size,
      cohesion: c.cohesion,
    })),
    xField: 'cluster',
    yField: 'size',
    seriesField: 'cluster',
    color: ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'],
    label: {
      position: 'top' as const,
      style: {
        fill: '#fff',
        fontWeight: 'bold',
      },
    },
  };

  return (
    <div className="ai-analytics-page">
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
              <RobotOutlined />
              AI Analytics
            </Space>
          </Title>
          <Paragraph type="secondary">
            Advanced AI/ML-powered insights and predictions
          </Paragraph>
        </div>
        <Space>
          <RangePicker />
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
                title="Total Anomalies"
                value={anomalyResults.length}
                prefix={<AlertOutlined style={{ color: '#f5222d' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Entities Resolved"
                value={entityResults.filter(e => e.resolved).length}
                prefix={<TeamOutlined style={{ color: '#52c41a' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Predictions"
                value={predictionResults.length}
                prefix={<ThunderboltOutlined style={{ color: '#faad14' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Clusters Found"
                value={clusterResults.length}
                prefix={<ClusterOutlined style={{ color: '#722ed1' }} />}
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
            { key: 'anomalies', tab: 'Anomaly Detection' },
            { key: 'entities', tab: 'Entity Resolution' },
            { key: 'predictions', tab: 'Predictive Analytics' },
            { key: 'clustering', tab: 'Clustering' },
            { key: 'nlp', tab: 'NLP Analysis' },
            { key: 'recommendations', tab: 'Recommendations' },
          ]}
          activeTabKey={activeTab}
          onTabChange={setActiveTab}
        >
          {activeTab === 'anomalies' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Anomaly Detection</Title>
              
              {/* Controls */}
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={8}>
                    <Select
                      placeholder="Select detection method"
                      value={anomalyMethod}
                      onChange={setAnomalyMethod}
                      options={anomalyMethods}
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={8}>
                    <Input
                      placeholder="Threshold (for statistical methods)"
                      defaultValue="3.0"
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={8}>
                    <Button
                      type="primary"
                      icon={<SearchOutlined />}
                      onClick={runAnomalyDetection}
                      loading={loading}
                      block
                    >
                      Detect Anomalies
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Chart */}
              <Card title="Anomaly Scores Over Time" style={{ marginBottom: 24 }}>
                <Line {...anomalyChartConfig} height={300} />
              </Card>

              {/* Results Table */}
              <Card title="Detected Anomalies">
                <Table
                  columns={anomalyColumns}
                  dataSource={anomalyResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1200 }}
                />
              </Card>

              {/* Details Modal */}
              <Modal
                title="Anomaly Details"
                open={!!selectedAnomaly}
                onCancel={() => setSelectedAnomaly(null)}
                footer={null}
                width={800}
              >
                {selectedAnomaly && (
                  <div>
                    <Row gutter={24}>
                      <Col span={12}>
                        <Card title="Basic Information" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>ID:</Text> {selectedAnomaly.id}
                            </div>
                            <div>
                              <Text strong>Type:</Text> {selectedAnomaly.type}
                            </div>
                            <div>
                              <Text strong>Entity:</Text> {selectedAnomaly.entity}
                            </div>
                            <div>
                              <Text strong>Feature:</Text> {selectedAnomaly.feature}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card title="Values" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>Actual Value:</Text> {selectedAnomaly.value}
                            </div>
                            <div>
                              <Text strong>Expected Value:</Text> {selectedAnomaly.expected}
                            </div>
                            <div>
                              <Text strong>Anomaly Score:</Text> {selectedAnomaly.score}
                            </div>
                            <div>
                              <Text strong>Status:</Text> {selectedAnomaly.status}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                    <Row style={{ marginTop: 24 }}>
                      <Col span={24}>
                        <Card title="Context" size="small">
                          <Text strong>Timestamp:</Text> {selectedAnomaly.timestamp}
                          <br />
                          <Text type="secondary">
                            Additional context and related data would be displayed here.
                          </Text>
                        </Card>
                      </Col>
                    </Row>
                  </div>
                )}
              </Modal>
            </div>
          )}

          {activeTab === 'entities' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Entity Resolution</Title>
              
              {/* Controls */}
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={12}>
                    <Select
                      placeholder="Select resolution method"
                      value={entityMethod}
                      onChange={setEntityMethod}
                      options={entityMethods}
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Input
                      placeholder="Similarity threshold"
                      defaultValue="0.85"
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<TeamOutlined />}
                      onClick={runEntityResolution}
                      loading={loading}
                      block
                    >
                      Resolve Entities
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Chart */}
              <Card title="Entity Match Similarity" style={{ marginBottom: 24 }}>
                <Column {...entityChartConfig} height={300} />
              </Card>

              {/* Results Table */}
              <Card title="Entity Resolution Results">
                <Table
                  columns={entityColumns}
                  dataSource={entityResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1200 }}
                />
              </Card>

              {/* Details Modal */}
              <Modal
                title="Entity Details"
                open={!!selectedEntity}
                onCancel={() => setSelectedEntity(null)}
                footer={null}
                width={800}
              >
                {selectedEntity && (
                  <div>
                    <Row gutter={24}>
                      <Col span={24}>
                        <Card title="Entity Information" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>ID:</Text> {selectedEntity.id}
                            </div>
                            <div>
                              <Text strong>Name:</Text> {selectedEntity.name}
                            </div>
                            <div>
                              <Text strong>Type:</Text> {selectedEntity.type}
                            </div>
                            <div>
                              <Text strong>Resolved:</Text> {selectedEntity.resolved ? 'Yes' : 'No'}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                    
                    <Row style={{ marginTop: 24 }}>
                      <Col span={24}>
                        <Card title="Matches" size="small">
                          <Table
                            columns={[
                              { title: 'Name', dataIndex: 'name', key: 'name' },
                              { title: 'Similarity', dataIndex: 'similarity', key: 'similarity', render: (s: number) => `${(s * 100).toFixed(1)}%` },
                              { title: 'Source', dataIndex: 'source', key: 'source' },
                            ]}
                            dataSource={selectedEntity.matches}
                            rowKey="id"
                            size="small"
                          />
                        </Card>
                      </Col>
                    </Row>
                  </div>
                )}
              </Modal>
            </div>
          )}

          {activeTab === 'predictions' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Predictive Analytics</Title>
              
              {/* Controls */}
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={12}>
                    <Select
                      placeholder="Select prediction method"
                      value={predictionMethod}
                      onChange={setPredictionMethod}
                      options={predictionMethods}
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Select
                      placeholder="Node 1"
                      options={[
                        { label: 'Person A', value: 'Person A' },
                        { label: 'Person B', value: 'Person B' },
                        { label: 'Company X', value: 'Company X' },
                      ]}
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<ThunderboltOutlined />}
                      onClick={runLinkPrediction}
                      loading={loading}
                      block
                    >
                      Predict Link
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Results Table */}
              <Card title="Prediction Results">
                <Table
                  columns={predictionColumns}
                  dataSource={predictionResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1200 }}
                />
              </Card>
            </div>
          )}

          {activeTab === 'clustering' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Clustering</Title>
              
              {/* Controls */}
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={12}>
                    <Select
                      placeholder="Select clustering method"
                      value={clusterMethod}
                      onChange={setClusterMethod}
                      options={clusterMethods}
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Input
                      placeholder="Number of clusters (for K-Means)"
                      defaultValue="5"
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<ClusterOutlined />}
                      onClick={runClustering}
                      loading={loading}
                      block
                    >
                      Run Clustering
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Chart */}
              <Card title="Cluster Sizes" style={{ marginBottom: 24 }}>
                <Bar {...clusterChartConfig} height={300} />
              </Card>

              {/* Results Table */}
              <Card title="Clustering Results">
                <Table
                  columns={clusterColumns}
                  dataSource={clusterResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1000 }}
                />
              </Card>
            </div>
          )}

          {activeTab === 'nlp' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>NLP Analysis</Title>
              
              {/* Controls */}
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={18}>
                    <Input.TextArea
                      placeholder="Enter text to analyze..."
                      rows={2}
                      style={{ width: '100%' }}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<FileTextOutlined />}
                      loading={loading}
                      block
                    >
                      Analyze Text
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Results Table */}
              <Card title="NLP Analysis Results">
                <Table
                  columns={nlpColumns}
                  dataSource={nlpResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1200 }}
                />
              </Card>
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>AI Recommendations</Title>
              
              <Alert
                message="These recommendations are generated based on AI analysis of your data"
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              {/* Results Table */}
              <Card title="Recommendations">
                <Table
                  columns={recommendationColumns}
                  dataSource={recommendationResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1200 }}
                />
              </Card>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
};

export default AIAnalytics;
