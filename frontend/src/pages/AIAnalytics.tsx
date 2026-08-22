import React, { useState } from 'react';
import { Card, Tabs, Button, Space, Typography, Row, Col, Modal, Form, Input, Select, Table, Tag, Progress, Alert, Spin, DatePicker } from 'antd';
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
import { message } from 'antd';
import { apiClient, aiEndpoints, graphEndpoints } from '../lib/apiClient';
import { useLocalStorage } from '../hooks/useApi';
import PageHeader from '../components/common/PageHeader';
import StatCard from '../components/common/StatCard';
import TabEmptyState from '../components/common/TabEmptyState';

const { Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;

// API Service

// Mock data
const AIAnalytics: React.FC = () => {
  const { value: activeTab, setValue: setActiveTab } = useLocalStorage('ai-active-tab', 'anomalies');
  const [anomalyMethod, setAnomalyMethod] = useState('statistical');
  const [entityMethod, setEntityMethod] = useState('exact');
  const [predictionMethod, setPredictionMethod] = useState('common_neighbors');
  const [clusterMethod, setClusterMethod] = useState('kmeans');
  const [dateRange, setDateRange] = useState<any>(null);
  const [search, setSearch] = useState('');
  const [selectedAnomaly, setSelectedAnomaly] = useState<any>(null);
  const [selectedEntity, setSelectedEntity] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [anomalyResults, setAnomalyResults] = useState<any[]>([]);
  const [entityResults, setEntityResults] = useState<any[]>([]);
  const [predictionResults, setPredictionResults] = useState<any[]>([]);
  const [clusterResults, setClusterResults] = useState<any[]>([]);
  const [nlpResults, setNlpResults] = useState<any[]>([]);
  const [recommendationResults, setRecommendationResults] = useState<any[]>([]);

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

  // Run anomaly detection over the live graph's node properties.
  const runAnomalyDetection = async () => {
    setLoading(true);
    try {
      const nodesResponse = await apiClient.get<any[]>(graphEndpoints.nodes,
        { params: { limit: 500 } });
      const rows = (nodesResponse.data || []).map((node) => ({
        id: node.id,
        entity_type: node.type,
        ...Object.fromEntries(Object.entries(node.properties || {})
          .filter(([, v]) => typeof v === 'number')),
      }));
      const response = await apiClient.post(aiEndpoints.anomalies.detect, {
        data: rows,
        method: anomalyMethod,
        threshold: 3.0,
      });
      setAnomalyResults(response.data.anomalies || []);
    } catch (error) {
      console.error('Anomaly detection error:', error);
      message.error('Anomaly detection failed');
    } finally {
      setLoading(false);
    }
  };

  // Run entity resolution over the live graph's nodes.
  const runEntityResolution = async () => {
    setLoading(true);
    try {
      const nodesResponse = await apiClient.get<any[]>(graphEndpoints.nodes,
        { params: { limit: 500 } });
      const entities = (nodesResponse.data || []).map((node) => ({
        id: node.id,
        type: node.type,
        ...node.properties,
      }));
      const response = await apiClient.post(aiEndpoints.entities.resolve, {
        entities,
        method: entityMethod,
        threshold: 0.85,
      });
      setEntityResults(response.data.matches || []);
    } catch (error) {
      console.error('Entity resolution error:', error);
      message.error('Entity resolution failed');
    } finally {
      setLoading(false);
    }
  };

  // Run link prediction
  const runLinkPrediction = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post(aiEndpoints.predict.link, {
        node1: 'person-0',
        node2: 'person-1',
        method: predictionMethod,
      });
      setPredictionResults(response.data ? [response.data] : []);
    } catch (error) {
      console.error('Link prediction error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Run clustering via graph community detection (the nearest real endpoint).
  const runClustering = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post(graphEndpoints.communities, {
        algorithm: 'louvain',
      });
      const communities = response.data?.data?.communities || [];
      setClusterResults(communities.map((c: any, i: number) => ({
        id: c.community_id ?? String(i),
        name: `Community ${c.community_id ?? i}`,
        size: (c.nodes || []).length,
        members: c.nodes || [],
        cohesion: c.modularity ?? 0,
      })));
    } catch (error) {
      console.error('Clustering error:', error);
      message.error('Clustering failed');
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
      className: 'ol-mono',
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 150,
      render: (type: string) => (type ? <Tag color="blue">{type.replace(/_/g, ' ')}</Tag> : '-'),
    },
    {
      title: 'Entity',
      dataIndex: 'entity',
      key: 'entity',
      width: 150,
      className: 'ol-mono',
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
          status={score > 8 ? 'exception' : score > 5 ? 'normal' : 'normal'}
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
      className: 'ol-mono',
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
            <div style={{ fontSize: 12, color: 'var(--text-color-tertiary)' }}>
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
      className: 'ol-mono',
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 150,
      render: (type: string) => (type ? <Tag color="blue">{type.replace(/_/g, ' ')}</Tag> : '-'),
    },
    {
      title: 'Node 1',
      dataIndex: 'node1',
      key: 'node1',
      width: 150,
      className: 'ol-mono',
    },
    {
      title: 'Node 2',
      dataIndex: 'node2',
      key: 'node2',
      width: 150,
      className: 'ol-mono',
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
          status={score > 0.8 ? 'success' : score > 0.5 ? 'normal' : 'exception'}
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
      className: 'ol-mono',
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
          status={cohesion > 0.8 ? 'success' : cohesion > 0.5 ? 'normal' : 'exception'}
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
          status={confidence > 0.8 ? 'success' : confidence > 0.5 ? 'normal' : 'exception'}
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
    data: entityResults.flatMap(e => (e.matches || []).map((m: any) => ({
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
    <div className="ol-page-body">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <PageHeader
          icon={<RobotOutlined />}
          title="AI Analytics"
          subtitle="Advanced AI/ML-powered insights and predictions"
          actions={(
            <Space>
              <RangePicker />
              <Button icon={<SyncOutlined />} onClick={() => window.location.reload()}>
                Refresh
              </Button>
            </Space>
          )}
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
            label="Total Anomalies"
            value={anomalyResults.length}
            icon={<AlertOutlined />}
            accent="error"
          />
          <StatCard
            label="Entities Resolved"
            value={entityResults.filter(e => e.resolved).length}
            icon={<TeamOutlined />}
            accent="success"
          />
          <StatCard
            label="Predictions"
            value={predictionResults.length}
            icon={<ThunderboltOutlined />}
            accent="warning"
          />
          <StatCard
            label="Clusters Found"
            value={clusterResults.length}
            icon={<ClusterOutlined />}
            accent="purple"
          />
        </div>
      </motion.div>

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
            <div className="ol-section">
              {/* Controls */}
              <div
                style={{
                  padding: 16,
                  border: '1px solid var(--border-color-secondary)',
                  borderRadius: 8,
                  background: 'var(--bg-color-secondary)',
                }}
              >
                <Row gutter={16} align="middle">
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
              </div>

              {/* Chart */}
              <Card title="Anomaly Scores Over Time">
                <Line {...anomalyChartConfig} height={200} />
              </Card>

              {/* Results Table */}
              <Card title="Detected Anomalies">
                <Table
                  columns={anomalyColumns}
                  dataSource={anomalyResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1180 }}
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
            <div className="ol-section">
              {/* Controls */}
              <div
                style={{
                  padding: 16,
                  border: '1px solid var(--border-color-secondary)',
                  borderRadius: 8,
                  background: 'var(--bg-color-secondary)',
                }}
              >
                <Row gutter={16} align="middle">
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
              </div>

              {/* Chart */}
              <Card title="Entity Match Similarity">
                <Column {...entityChartConfig} height={200} />
              </Card>

              {/* Results Table */}
              <Card title="Entity Resolution Results">
                <Table
                  columns={entityColumns}
                  dataSource={entityResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1180 }}
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
            <div className="ol-section">
              {/* Controls */}
              <div
                style={{
                  padding: 16,
                  border: '1px solid var(--border-color-secondary)',
                  borderRadius: 8,
                  background: 'var(--bg-color-secondary)',
                }}
              >
                <Row gutter={16} align="middle">
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
              </div>

              {/* Results Table */}
              <Card title="Prediction Results">
                <Table
                  columns={predictionColumns}
                  dataSource={predictionResults}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1180 }}
                />
              </Card>
            </div>
          )}

          {activeTab === 'clustering' && (
            <div className="ol-section">
              {/* Controls */}
              <div
                style={{
                  padding: 16,
                  border: '1px solid var(--border-color-secondary)',
                  borderRadius: 8,
                  background: 'var(--bg-color-secondary)',
                }}
              >
                <Row gutter={16} align="middle">
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
              </div>

              {/* Chart */}
              <Card title="Cluster Sizes">
                <Bar {...clusterChartConfig} height={200} />
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
            <TabEmptyState
              label="NLP Analysis"
              description="Sentiment, topic, and entity extraction from free text will appear here once the NLP analysis endpoint is wired up."
            />
          )}

          {activeTab === 'recommendations' && (
            <TabEmptyState
              label="Recommendations"
              description="AI-generated recommendations based on your data will appear here once the recommendations endpoint is wired up."
            />
          )}
        </Card>
      </motion.div>
    </div>
  );
};

export default AIAnalytics;
