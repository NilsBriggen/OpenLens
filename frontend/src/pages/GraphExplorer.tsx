import React, { useState, useEffect, useRef } from 'react';
import { Card, Tabs, Button, Space, Input, Select, Typography, Row, Col, Divider, Modal, Form, Spin, Alert, Tag, Tooltip, Drawer } from 'antd';
import {
  ProjectOutlined,
  SearchOutlined,
  FilterOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  ClusterOutlined,
  SyncOutlined,
  ExportOutlined,
  ImportOutlined,
  SettingOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  UndoOutlined,
  RedoOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import CytoscapeComponent from 'react-cytoscapejs';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';
import * as d3 from 'd3';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
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
const mockGraphData = {
  nodes: [
    { data: { id: '1', label: 'Person A', type: 'person', properties: { name: 'John Doe', age: 35 } } },
    { data: { id: '2', label: 'Person B', type: 'person', properties: { name: 'Jane Smith', age: 28 } } },
    { data: { id: '3', label: 'Company X', type: 'company', properties: { name: 'Tech Corp', industry: 'Technology' } } },
    { data: { id: '4', label: 'Company Y', type: 'company', properties: { name: 'Data Inc', industry: 'Data' } } },
    { data: { id: '5', label: 'Email 1', type: 'email', properties: { address: 'john@tech.com' } } },
    { data: { id: '6', label: 'IP Address', type: 'ip', properties: { address: '192.168.1.1' } } },
    { data: { id: '7', label: 'Domain', type: 'domain', properties: { name: 'tech.com' } } },
  ],
  edges: [
    { data: { id: 'e1', source: '1', target: '3', label: 'WORKS_AT', type: 'employment' } },
    { data: { id: 'e2', source: '2', target: '4', label: 'WORKS_AT', type: 'employment' } },
    { data: { id: 'e3', source: '1', target: '5', label: 'HAS_EMAIL', type: 'ownership' } },
    { data: { id: 'e4', source: '3', target: '6', label: 'USES_IP', type: 'usage' } },
    { data: { id: 'e5', source: '3', target: '7', label: 'OWNS_DOMAIN', type: 'ownership' } },
    { data: { id: 'e6', source: '1', target: '2', label: 'KNOWS', type: 'relationship' } },
    { data: { id: 'e7', source: '4', target: '7', label: 'USES_DOMAIN', type: 'usage' } },
  ],
};

const mockStats = {
  totalNodes: 12453,
  totalEdges: 87342,
  nodeTypes: [
    { type: 'person', count: 4521 },
    { type: 'company', count: 2834 },
    { type: 'email', count: 1567 },
    { type: 'ip', count: 987 },
    { type: 'domain', count: 2543 },
    { type: 'url', count: 12345 },
  ],
  edgeTypes: [
    { type: 'WORKS_AT', count: 3456 },
    { type: 'HAS_EMAIL', count: 2345 },
    { type: 'KNOWS', count: 12345 },
    { type: 'USES_IP', count: 876 },
    { type: 'OWNS_DOMAIN', count: 543 },
  ],
};

const mockCentrality = [
  { node: 'Person A', degree: 45, betweenness: 0.87, closeness: 0.92, pagerank: 0.95 },
  { node: 'Company X', degree: 38, betweenness: 0.76, closeness: 0.88, pagerank: 0.89 },
  { node: 'Person B', degree: 32, betweenness: 0.65, closeness: 0.85, pagerank: 0.82 },
  { node: 'Company Y', degree: 28, betweenness: 0.54, closeness: 0.80, pagerank: 0.75 },
  { node: 'Email 1', degree: 25, betweenness: 0.43, closeness: 0.78, pagerank: 0.70 },
];

const mockCommunities = [
  {
    id: 'community-1',
    nodes: ['Person A', 'Person B', 'Company X', 'Company Y'],
    size: 4,
    cohesion: 0.85,
  },
  {
    id: 'community-2',
    nodes: ['Email 1', 'IP Address', 'Domain'],
    size: 3,
    cohesion: 0.72,
  },
];

const GraphExplorer: React.FC = () => {
  const [activeTab, setActiveTab] = useState('explore');
  const [search, setSearch] = useState('');
  const [nodeTypeFilter, setNodeTypeFilter] = useState<string[]>([]);
  const [edgeTypeFilter, setEdgeTypeFilter] = useState<string[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [selectedEdge, setSelectedEdge] = useState<any>(null);
  const [layout, setLayout] = useState('cose');
  const [zoom, setZoom] = useState(1);
  const [fullscreen, setFullscreen] = useState(false);
  const [nodeFormVisible, setNodeFormVisible] = useState(false);
  const [edgeFormVisible, setEdgeFormVisible] = useState(false);
  const [cy, setCy] = useState<any>(null);
  const cyRef = useRef<any>(null);
  const [graphData, setGraphData] = useState(mockGraphData);
  const [stats, setStats] = useState(mockStats);
  const [loading, setLoading] = useState(false);
  const [pathResult, setPathResult] = useState<any>(null);
  const [communityResult, setCommunityResult] = useState<any>(null);
  const [centralityResult, setCentralityResult] = useState<any>(null);

  const queryClient = useQueryClient();

  // Fetch graph data
  const { data: graphStats, isLoading: statsLoading } = useQuery({
    queryKey: ['graph-stats'],
    queryFn: async () => {
      const response = await api.get('/api/graph/stats');
      return response.data;
    },
    initialData: mockStats,
  });

  // Fetch nodes
  const { data: nodes, isLoading: nodesLoading } = useQuery({
    queryKey: ['graph-nodes'],
    queryFn: async () => {
      const response = await api.get('/api/graph/nodes');
      return response.data;
    },
  });

  // Node type options
  const nodeTypeOptions = [
    { label: 'Person', value: 'person' },
    { label: 'Company', value: 'company' },
    { label: 'Email', value: 'email' },
    { label: 'IP Address', value: 'ip' },
    { label: 'Domain', value: 'domain' },
    { label: 'URL', value: 'url' },
    { label: 'Phone', value: 'phone' },
    { label: 'Address', value: 'address' },
  ];

  // Edge type options
  const edgeTypeOptions = [
    { label: 'WORKS_AT', value: 'WORKS_AT' },
    { label: 'HAS_EMAIL', value: 'HAS_EMAIL' },
    { label: 'KNOWS', value: 'KNOWS' },
    { label: 'USES_IP', value: 'USES_IP' },
    { label: 'OWNS_DOMAIN', value: 'OWNS_DOMAIN' },
    { label: 'CONNECTED_TO', value: 'CONNECTED_TO' },
    { label: 'SENT_EMAIL', value: 'SENT_EMAIL' },
  ];

  // Layout options
  const layoutOptions = [
    { label: 'CoSE', value: 'cose' },
    { label: 'Circle', value: 'circle' },
    { label: 'Grid', value: 'grid' },
    { label: 'Random', value: 'random' },
    { label: 'Dagre', value: 'dagre' },
    { label: 'Breadthfirst', value: 'breadthfirst' },
    { label: 'Cose-Bilkent', value: 'cose-bilkent' },
    { label: 'Fcose', value: 'fcose' },
  ];

  // Handle node click
  const handleNodeClick = (event: any) => {
    const node = event.target;
    setSelectedNode(node.data());
    setSelectedEdge(null);
  };

  // Handle edge click
  const handleEdgeClick = (event: any) => {
    const edge = event.target;
    setSelectedEdge(edge.data());
    setSelectedNode(null);
  };

  // Handle background click
  const handleBackgroundClick = () => {
    setSelectedNode(null);
    setSelectedEdge(null);
  };

  // Apply filters
  const applyFilters = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
    }, 500);
  };

  // Run path finding
  const runPathFinding = async (source: string, target: string, algorithm: string = 'shortest') => {
    setLoading(true);
    try {
      const response = await api.post('/api/graph/path', {
        start_node: source,
        end_node: target,
        algorithm,
      });
      setPathResult(response.data);
    } catch (error) {
      console.error('Path finding error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Run community detection
  const runCommunityDetection = async (algorithm: string = 'louvain') => {
    setLoading(true);
    try {
      const response = await api.post('/api/graph/communities', {
        algorithm,
      });
      setCommunityResult(response.data);
    } catch (error) {
      console.error('Community detection error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Run centrality analysis
  const runCentralityAnalysis = async (algorithm: string = 'degree') => {
    setLoading(true);
    try {
      const response = await api.post('/api/graph/centrality', {
        algorithm,
      });
      setCentralityResult(response.data);
    } catch (error) {
      console.error('Centrality analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Add new node
  const addNode = async (values: any) => {
    setLoading(true);
    try {
      const response = await api.post('/api/graph/nodes', {
        labels: [values.type],
        properties: values.properties,
      });
      queryClient.invalidateQueries(['graph-nodes']);
      queryClient.invalidateQueries(['graph-stats']);
      setNodeFormVisible(false);
    } catch (error) {
      console.error('Add node error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Add new edge
  const addEdge = async (values: any) => {
    setLoading(true);
    try {
      const response = await api.post('/api/graph/relationships', {
        start_node_id: parseInt(values.source),
        end_node_id: parseInt(values.target),
        relationship_type: values.type,
        properties: values.properties,
      });
      queryClient.invalidateQueries(['graph-nodes']);
      queryClient.invalidateQueries(['graph-stats']);
      setEdgeFormVisible(false);
    } catch (error) {
      console.error('Add edge error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Zoom controls
  const zoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom({ level: zoom + 0.2, renderedPosition: { x: window.innerWidth / 2, y: window.innerHeight / 2 } });
      setZoom(zoom + 0.2);
    }
  };

  const zoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom({ level: Math.max(0.2, zoom - 0.2), renderedPosition: { x: window.innerWidth / 2, y: window.innerHeight / 2 } });
      setZoom(Math.max(0.2, zoom - 0.2));
    }
  };

  const resetZoom = () => {
    if (cyRef.current) {
      cyRef.current.fit();
      setZoom(1);
    }
  };

  // Cytoscape configuration
  const cyConfig = {
    style: [
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'text-valign': 'center',
          'text-halign': 'center',
          'background-color': '#666',
          'color': '#fff',
          'font-size': '12px',
          'width': 'mapData(type, person, 30, company, 40, email, 25, ip, 25, domain, 25, 30)',
          'height': 'mapData(type, person, 30, company, 40, email, 25, ip, 25, domain, 25, 30)',
          'shape': 'mapData(type, person, ellipse, company, rectangle, email, ellipse, ip, ellipse, domain, ellipse, ellipse)',
        },
      },
      {
        selector: 'node[type = "person"]',
        style: {
          'background-color': '#1890ff',
        },
      },
      {
        selector: 'node[type = "company"]',
        style: {
          'background-color': '#52c41a',
          'shape': 'rectangle',
        },
      },
      {
        selector: 'node[type = "email"]',
        style: {
          'background-color': '#faad14',
          'shape': 'ellipse',
        },
      },
      {
        selector: 'node[type = "ip"]',
        style: {
          'background-color': '#f5222d',
          'shape': 'ellipse',
        },
      },
      {
        selector: 'node[type = "domain"]',
        style: {
          'background-color': '#722ed1',
          'shape': 'ellipse',
        },
      },
      {
        selector: 'edge',
        style: {
          'width': 2,
          'line-color': '#ccc',
          'curve-style': 'bezier',
          'label': 'data(label)',
          'font-size': '10px',
          'text-background-color': '#fff',
          'text-background-opacity': 0.7,
          'text-background-padding': '2px',
        },
      },
      {
        selector: 'edge[type = "WORKS_AT"]',
        style: {
          'line-color': '#52c41a',
        },
      },
      {
        selector: 'edge[type = "HAS_EMAIL"]',
        style: {
          'line-color': '#faad14',
        },
      },
      {
        selector: 'edge[type = "KNOWS"]',
        style: {
          'line-color': '#1890ff',
        },
      },
      {
        selector: 'node:selected',
        style: {
          'border-width': 3,
          'border-color': '#1890ff',
        },
      },
      {
        selector: 'edge:selected',
        style: {
          'line-width': 3,
          'line-color': '#1890ff',
        },
      },
    ],
    layout: {
      name: layout,
      animate: true,
      animationDuration: 1000,
      randomize: false,
    },
  };

  // Get node color
  const getNodeColor = (type: string) => {
    switch (type) {
      case 'person': return '#1890ff';
      case 'company': return '#52c41a';
      case 'email': return '#faad14';
      case 'ip': return '#f5222d';
      case 'domain': return '#722ed1';
      default: return '#666';
    }
  };

  // Get edge color
  const getEdgeColor = (type: string) => {
    switch (type) {
      case 'WORKS_AT': return '#52c41a';
      case 'HAS_EMAIL': return '#faad14';
      case 'KNOWS': return '#1890ff';
      case 'USES_IP': return '#f5222d';
      case 'OWNS_DOMAIN': return '#722ed1';
      default: return '#ccc';
    }
  };

  return (
    <div className="graph-explorer-page">
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
              <ProjectOutlined />
              Graph Explorer
            </Space>
          </Title>
          <Paragraph type="secondary">
            Explore and analyze relationships in your data graph
          </Paragraph>
        </div>
        <Space>
          <Button icon={<ImportOutlined />} onClick={() => setNodeFormVisible(true)}>
            Add Node
          </Button>
          <Button icon={<ImportOutlined />} onClick={() => setEdgeFormVisible(true)}>
            Add Edge
          </Button>
          <Button icon={<ExportOutlined />}>
            Export
          </Button>
          <Button icon={<SettingOutlined />}>
            Settings
          </Button>
        </Space>
      </motion.div>

      {/* Stats Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Row gutter={24}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Nodes"
                value={stats.totalNodes.toLocaleString()}
                prefix={<NodeIndexOutlined style={{ color: '#1890ff' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Edges"
                value={stats.totalEdges.toLocaleString()}
                prefix={<BranchesOutlined style={{ color: '#52c41a' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Node Types"
                value={stats.nodeTypes.length}
                prefix={<ClusterOutlined style={{ color: '#faad14' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Edge Types"
                value={stats.edgeTypes.length}
                prefix={<SyncOutlined style={{ color: '#f5222d' }} />}
              />
            </Card>
          </Col>
        </Row>
      </motion.div>

      <Divider />

      {/* Main Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card
          title="Graph Visualization"
          extra={
            <Space>
              <Select
                value={layout}
                onChange={setLayout}
                options={layoutOptions}
                size="small"
                style={{ width: 120 }}
              />
              <Button icon={<ZoomInOutlined />} onClick={zoomIn} size="small" />
              <Button icon={<ZoomOutOutlined />} onClick={zoomOut} size="small" />
              <Button icon={<SyncOutlined />} onClick={resetZoom} size="small" />
              <Button
                icon={fullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                onClick={() => setFullscreen(!fullscreen)}
                size="small"
              />
            </Space>
          }
        >
          {loading ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <Spin size="large" />
              <Text type="secondary" style={{ marginLeft: 16 }}>Loading graph...</Text>
            </div>
          ) : (
            <div
              style={{
                height: fullscreen ? 'calc(100vh - 200px)' : 600,
                width: '100%',
                border: '1px solid #f0f0f0',
                borderRadius: 8,
                overflow: 'hidden',
              }}
            >
              <CytoscapeComponent
                elements={CytoscapeComponent.normalizeElements(graphData)}
                style={{ width: '100%', height: '100%' }}
                cy={(cy) => {
                  cyRef.current = cy;
                  setCy(cy);
                  cy.on('tap', 'node', handleNodeClick);
                  cy.on('tap', 'edge', handleEdgeClick);
                  cy.on('tap', handleBackgroundClick);
                }}
                stylesheet={cyConfig.style}
                layout={cyConfig.layout}
              />
            </div>
          )}

          {/* Node/Edge Details Panel */}
          {(selectedNode || selectedEdge) && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              style={{
                marginTop: 24,
                padding: 16,
                background: '#f0f0f0',
                borderRadius: 8,
              }}
            >
              {selectedNode && (
                <div>
                  <Title level={5} style={{ margin: 0, marginBottom: 8 }}>
                    <Space>
                      <NodeIndexOutlined />
                      Node Details
                    </Space>
                  </Title>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text strong>ID:</Text> {selectedNode.id}
                    </Col>
                    <Col span={12}>
                      <Text strong>Label:</Text> {selectedNode.label}
                    </Col>
                    <Col span={12}>
                      <Text strong>Type:</Text> {selectedNode.type}
                    </Col>
                    <Col span={12}>
                      <Text strong>Degree:</Text> {selectedNode.degree || 'N/A'}
                    </Col>
                  </Row>
                  {selectedNode.properties && (
                    <div style={{ marginTop: 16 }}>
                      <Text strong>Properties:</Text>
                      <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                        {JSON.stringify(selectedNode.properties, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
              {selectedEdge && (
                <div>
                  <Title level={5} style={{ margin: 0, marginBottom: 8 }}>
                    <Space>
                      <BranchesOutlined />
                      Edge Details
                    </Space>
                  </Title>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text strong>ID:</Text> {selectedEdge.id}
                    </Col>
                    <Col span={12}>
                      <Text strong>Label:</Text> {selectedEdge.label}
                    </Col>
                    <Col span={12}>
                      <Text strong>Type:</Text> {selectedEdge.type}
                    </Col>
                    <Col span={12}>
                      <Text strong>Source:</Text> {selectedEdge.source}
                    </Col>
                    <Col span={12}>
                      <Text strong>Target:</Text> {selectedEdge.target}
                    </Col>
                  </Row>
                  {selectedEdge.properties && (
                    <div style={{ marginTop: 16 }}>
                      <Text strong>Properties:</Text>
                      <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                        {JSON.stringify(selectedEdge.properties, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </Card>
      </motion.div>

      <Divider />

      {/* Analysis Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card
          title="Graph Analysis"
          tabList={[
            { key: 'explore', tab: 'Explore' },
            { key: 'paths', tab: 'Path Finding' },
            { key: 'communities', tab: 'Communities' },
            { key: 'centrality', tab: 'Centrality' },
            { key: 'stats', tab: 'Statistics' },
          ]}
          activeTabKey={activeTab}
          onTabChange={setActiveTab}
        >
          {activeTab === 'explore' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Search & Filter</Title>
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} lg={12}>
                  <Search
                    placeholder="Search nodes..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    enterButton
                  />
                </Col>
                <Col xs={24} lg={12}>
                  <Select
                    mode="multiple"
                    placeholder="Filter by node type"
                    value={nodeTypeFilter}
                    onChange={setNodeTypeFilter}
                    options={nodeTypeOptions}
                    style={{ width: '100%' }}
                  />
                </Col>
              </Row>
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} lg={12}>
                  <Select
                    mode="multiple"
                    placeholder="Filter by edge type"
                    value={edgeTypeFilter}
                    onChange={setEdgeTypeFilter}
                    options={edgeTypeOptions}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col xs={24} lg={12}>
                  <Button type="primary" icon={<FilterOutlined />} onClick={applyFilters}>
                    Apply Filters
                  </Button>
                </Col>
              </Row>

              <Title level={4} style={{ marginBottom: 16 }}>Node Types</Title>
              <Row gutter={16} style={{ marginBottom: 24 }}>
                {stats.nodeTypes.map((nt) => (
                  <Col key={nt.type}>
                    <Tag
                      color={getNodeColor(nt.type)}
                      style={{ padding: '8px 16px', fontSize: 14 }}
                    >
                      {nt.type} ({nt.count.toLocaleString()})
                    </Tag>
                  </Col>
                ))}
              </Row>

              <Title level={4} style={{ marginBottom: 16 }}>Edge Types</Title>
              <Row gutter={16}>
                {stats.edgeTypes.map((et) => (
                  <Col key={et.type}>
                    <Tag
                      color={getEdgeColor(et.type)}
                      style={{ padding: '8px 16px', fontSize: 14 }}
                    >
                      {et.type} ({et.count.toLocaleString()})
                    </Tag>
                  </Col>
                ))}
              </Row>
            </div>
          )}

          {activeTab === 'paths' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Find Path Between Nodes</Title>
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} lg={8}>
                  <Select
                    placeholder="Select source node"
                    options={graphData.nodes.map(n => ({ label: n.data.label, value: n.data.id }))}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col xs={24} lg={8}>
                  <Select
                    placeholder="Select target node"
                    options={graphData.nodes.map(n => ({ label: n.data.label, value: n.data.id }))}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col xs={24} lg={8}>
                  <Select
                    placeholder="Algorithm"
                    options={[
                      { label: 'Shortest Path', value: 'shortest' },
                      { label: 'All Paths', value: 'all' },
                      { label: 'Dijkstra', value: 'dijkstra' },
                      { label: 'A*', value: 'astar' },
                    ]}
                    style={{ width: '100%' }}
                  />
                </Col>
              </Row>
              <Button type="primary" icon={<SearchOutlined />} onClick={() => runPathFinding('1', '3')}>
                Find Path
              </Button>

              {pathResult && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  style={{ marginTop: 24 }}
                >
                  <Alert
                    message={`Path found: ${pathResult.path?.length || 0} nodes`}
                    type="success"
                    showIcon
                  />
                  <pre style={{ marginTop: 16, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(pathResult, null, 2)}
                  </pre>
                </motion.div>
              )}
            </div>
          )}

          {activeTab === 'communities' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Detect Communities</Title>
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} lg={12}>
                  <Select
                    placeholder="Algorithm"
                    options={[
                      { label: 'Louvain', value: 'louvain' },
                      { label: 'Label Propagation', value: 'label_propagation' },
                      { label: 'Girvan-Newman', value: 'girvan_newman' },
                    ]}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col xs={24} lg={12}>
                  <Button type="primary" icon={<ClusterOutlined />} onClick={() => runCommunityDetection()}>
                    Detect Communities
                  </Button>
                </Col>
              </Row>

              {communityResult && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  style={{ marginTop: 24 }}
                >
                  <Alert
                    message={`Found ${communityResult.communities?.length || 0} communities`}
                    type="success"
                    showIcon
                  />
                  <pre style={{ marginTop: 16, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(communityResult, null, 2)}
                  </pre>
                </motion.div>
              )}

              <Title level={4} style={{ marginTop: 24, marginBottom: 16 }}>Sample Communities</Title>
              <Row gutter={16}>
                {mockCommunities.map((community) => (
                  <Col xs={24} lg={12} key={community.id}>
                    <Card
                      title={`Community ${community.id} (${community.size} nodes)`}
                      size="small"
                    >
                      <Space direction="vertical">
                        <Text strong>Cohesion: {community.cohesion.toFixed(2)}</Text>
                        <Text type="secondary">
                          Nodes: {community.nodes.join(', ')}
                        </Text>
                      </Space>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          )}

          {activeTab === 'centrality' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Centrality Analysis</Title>
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} lg={12}>
                  <Select
                    placeholder="Algorithm"
                    options={[
                      { label: 'Degree Centrality', value: 'degree' },
                      { label: 'Betweenness Centrality', value: 'betweenness' },
                      { label: 'Closeness Centrality', value: 'closeness' },
                      { label: 'Eigenvector Centrality', value: 'eigenvector' },
                      { label: 'PageRank', value: 'pagerank' },
                    ]}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col xs={24} lg={12}>
                  <Button type="primary" icon={<BranchesOutlined />} onClick={() => runCentralityAnalysis()}>
                    Calculate Centrality
                  </Button>
                </Col>
              </Row>

              {centralityResult && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  style={{ marginTop: 24 }}
                >
                  <Alert
                    message={`Calculated centrality for ${centralityResult.result?.length || 0} nodes`}
                    type="success"
                    showIcon
                  />
                </motion.div>
              )}

              <Title level={4} style={{ marginTop: 24, marginBottom: 16 }}>Top Nodes by Centrality</Title>
              <Card>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #f0f0f0' }}>
                      <th style={{ textAlign: 'left', padding: 12 }}>Node</th>
                      <th style={{ textAlign: 'right', padding: 12 }}>Degree</th>
                      <th style={{ textAlign: 'right', padding: 12 }}>Betweenness</th>
                      <th style={{ textAlign: 'right', padding: 12 }}>Closeness</th>
                      <th style={{ textAlign: 'right', padding: 12 }}>PageRank</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockCentrality.map((item, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #f0f0f0' }}>
                        <td style={{ padding: 12 }}>
                          <Space>
                            <NodeIndexOutlined style={{ color: '#1890ff' }} />
                            {item.node}
                          </Space>
                        </td>
                        <td style={{ textAlign: 'right', padding: 12 }}>{item.degree}</td>
                        <td style={{ textAlign: 'right', padding: 12 }}>{item.betweenness.toFixed(2)}</td>
                        <td style={{ textAlign: 'right', padding: 12 }}>{item.closeness.toFixed(2)}</td>
                        <td style={{ textAlign: 'right', padding: 12 }}>{item.pagerank.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            </div>
          )}

          {activeTab === 'stats' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Graph Statistics</Title>
              <Row gutter={24}>
                <Col xs={24} lg={12}>
                  <Card title="Node Type Distribution">
                    <div style={{ height: 300 }}>
                      {/* Pie chart would go here */}
                      <div style={{ textAlign: 'center', padding: 40 }}>
                        <Text type="secondary">Node type distribution chart</Text>
                      </div>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Edge Type Distribution">
                    <div style={{ height: 300 }}>
                      {/* Pie chart would go here */}
                      <div style={{ textAlign: 'center', padding: 40 }}>
                        <Text type="secondary">Edge type distribution chart</Text>
                      </div>
                    </div>
                  </Card>
                </Col>
              </Row>

              <Row gutter={24} style={{ marginTop: 24 }}>
                <Col xs={24} lg={12}>
                  <Card title="Degree Distribution">
                    <div style={{ height: 300 }}>
                      {/* Histogram would go here */}
                      <div style={{ textAlign: 'center', padding: 40 }}>
                        <Text type="secondary">Degree distribution histogram</Text>
                      </div>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Graph Metrics">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Average Degree:</Text>
                        <Text strong>2.85</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Graph Density:</Text>
                        <Text strong>0.0023</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Average Path Length:</Text>
                        <Text strong>3.45</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Clustering Coefficient:</Text>
                        <Text strong>0.45</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0' }}>
                        <Text>Connected Components:</Text>
                        <Text strong>12</Text>
                      </div>
                    </Space>
                  </Card>
                </Col>
              </Row>
            </div>
          )}
        </Card>
      </motion.div>

      {/* Add Node Modal */}
      <Modal
        title="Add New Node"
        open={nodeFormVisible}
        onCancel={() => setNodeFormVisible(false)}
        footer={null}
        width={600}
      >
        <Form onFinish={addNode} layout="vertical">
          <Form.Item name="type" label="Node Type" rules={[{ required: true }]}>
            <Select options={nodeTypeOptions} />
          </Form.Item>
          <Form.Item name="label" label="Label" rules={[{ required: true }]}>
            <Input placeholder="Node label" />
          </Form.Item>
          <Form.Item name="properties" label="Properties">
            <Input.TextArea placeholder="JSON properties" rows={4} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Add Node
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Add Edge Modal */}
      <Modal
        title="Add New Edge"
        open={edgeFormVisible}
        onCancel={() => setEdgeFormVisible(false)}
        footer={null}
        width={600}
      >
        <Form onFinish={addEdge} layout="vertical">
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item name="source" label="Source Node" rules={[{ required: true }]}>
                <Select options={graphData.nodes.map(n => ({ label: n.data.label, value: n.data.id }))} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="target" label="Target Node" rules={[{ required: true }]}>
                <Select options={graphData.nodes.map(n => ({ label: n.data.label, value: n.data.id }))} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="type" label="Edge Type" rules={[{ required: true }]}>
            <Select options={edgeTypeOptions} />
          </Form.Item>
          <Form.Item name="properties" label="Properties">
            <Input.TextArea placeholder="JSON properties" rows={4} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Add Edge
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default GraphExplorer;
