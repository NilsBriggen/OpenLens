import React, { useState, useCallback } from 'react';
import { Card, Tabs, Button, Space, Input, Select, Typography, Row, Col, Divider, Modal, Form, Spin, Alert, Tag, Tooltip, Drawer, message } from 'antd';
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
  RedoOutlined,
  DatabaseOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import ConnectedGraphVisualization from '../components/ConnectedGraphVisualization';
import {
  useGraphStats,
  useGraphNodes,
  useGraphEdges,
  useGraphQuery,
  useGraphCentrality,
  useGraphCommunities,
  useGraphPath,
  useWebSocket
} from '../hooks/useApi';
import { useDebounce, useLocalStorage } from '../hooks/useApi';
import { exportToCSV, exportToJSON, exportToSTIX } from '../utils/exportUtils';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { Search } = Input;

interface NodeData {
  id: string;
  label: string;
  type?: string;
  properties?: Record<string, any>;
  [key: string]: any;
}

interface EdgeData {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: string;
  properties?: Record<string, any>;
  [key: string]: any;
}

const GraphExplorer: React.FC = () => {
  // State
  const [activeTab, setActiveTab] = useState('visualization');
  const [searchQuery, setSearchQuery] = useState('');
  const [nodeTypeFilter, setNodeTypeFilter] = useState<string[]>([]);
  const [edgeTypeFilter, setEdgeTypeFilter] = useState<string[]>([]);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<EdgeData | null>(null);
  const [nodeDetailVisible, setNodeDetailVisible] = useState(false);
  const [edgeDetailVisible, setEdgeDetailVisible] = useState(false);
  const [settingsVisible, setSettingsVisible] = useState(false);
  const [layout, setLayout] = useState('cose');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30000);
  
  // Local storage for preferences
  const { value: savedLayout, setValue: saveLayout } = useLocalStorage('graph-layout', 'cose');
  const { value: savedAutoRefresh, setValue: saveAutoRefresh } = useLocalStorage('graph-auto-refresh', false);
  const { value: savedRefreshInterval, setValue: saveRefreshInterval } = useLocalStorage('graph-refresh-interval', 30000);
  
  // Load saved preferences
  React.useEffect(() => {
    setLayout(savedLayout);
    setAutoRefresh(savedAutoRefresh);
    setRefreshInterval(savedRefreshInterval);
  }, [savedLayout, savedAutoRefresh, savedRefreshInterval]);
  
  // Debounced search
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  
  // API Hooks
  const { data: stats, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useGraphStats({
    enabled: true,
    refetchInterval: autoRefresh ? refreshInterval : undefined,
  });
  
  const { 
    data: nodes = [], 
    isLoading: nodesLoading, 
    error: nodesError, 
    refetch: refetchNodes 
  } = useGraphNodes(
    { 
      search: debouncedSearchQuery || undefined,
      types: nodeTypeFilter.length > 0 ? nodeTypeFilter.join(',') : undefined,
    },
    { enabled: true, staleTime: 60 * 1000 }
  );
  
  const { 
    data: edges = [], 
    isLoading: edgesLoading, 
    error: edgesError, 
    refetch: refetchEdges 
  } = useGraphEdges(
    { 
      types: edgeTypeFilter.length > 0 ? edgeTypeFilter.join(',') : undefined,
    },
    { enabled: true, staleTime: 60 * 1000 }
  );
  
  const queryMutation = useGraphQuery();
  const centralityMutation = useGraphCentrality();
  const communitiesMutation = useGraphCommunities();
  const pathMutation = useGraphPath();
  
  // WebSocket for real-time updates
  const { isConnected, messages, sendMessage } = useWebSocket(
    '/api/ws/graph',
    (data) => {
      if (data.type === 'graph_update') {
        refetchNodes();
        refetchEdges();
        refetchStats();
        message.info('Graph updated in real-time');
      }
    }
  );
  
  // Available types
  const availableNodeTypes = React.useMemo(() => {
    const types = new Set<string>();
    nodes.forEach(node => {
      if (node.type) types.add(node.type);
    });
    return Array.from(types);
  }, [nodes]);
  
  const availableEdgeTypes = React.useMemo(() => {
    const types = new Set<string>();
    edges.forEach(edge => {
      if (edge.type) types.add(edge.type);
    });
    return Array.from(types);
  }, [edges]);
  
  // Refresh all
  const refreshAll = useCallback(() => {
    refetchNodes();
    refetchEdges();
    refetchStats();
  }, [refetchNodes, refetchEdges, refetchStats]);
  
  // Handle node click
  const handleNodeClick = useCallback((node: NodeData) => {
    setSelectedNode(node);
    setSelectedEdge(null);
    setNodeDetailVisible(true);
  }, []);
  
  // Handle edge click
  const handleEdgeClick = useCallback((edge: EdgeData) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
    setEdgeDetailVisible(true);
  }, []);
  
  // Export functions
  const exportGraph = useCallback((format: 'csv' | 'json' | 'stix') => {
    // The export helpers take flat arrays; combine nodes and edges into rows.
    const rows = [
      ...nodes.map((n) => ({ kind: 'node', ...n })),
      ...edges.map((e) => ({ kind: 'edge', ...e })),
    ];

    if (format === 'csv') {
      exportToCSV(rows, 'graph-data.csv');
    } else if (format === 'json') {
      exportToJSON(rows, 'graph-data.json');
    } else if (format === 'stix') {
      exportToSTIX(rows, 'graph-data-stix.json');
    }

    message.success(`Graph exported as ${format.toUpperCase()}`);
  }, [nodes, edges]);
  
  // Calculate stats
  const totalNodes = stats?.nodeCount || nodes.length;
  const totalEdges = stats?.edgeCount || edges.length;
  const nodeTypeCounts = React.useMemo(() => {
    const counts: Record<string, number> = {};
    nodes.forEach(node => {
      const type = node.type || 'unknown';
      counts[type] = (counts[type] || 0) + 1;
    });
    return counts;
  }, [nodes]);
  
  const edgeTypeCounts = React.useMemo(() => {
    const counts: Record<string, number> = {};
    edges.forEach(edge => {
      const type = edge.type || 'unknown';
      counts[type] = (counts[type] || 0) + 1;
    });
    return counts;
  }, [edges]);
  
  // Loading state
  const isLoading = statsLoading || nodesLoading || edgesLoading;
  const hasError = statsError || nodesError || edgesError;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* Header */}
        <Card>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={2} style={{ margin: 0 }}>
                <ProjectOutlined style={{ marginRight: 8 }} />
                Graph Explorer
              </Title>
              <Text type="secondary">Real-time graph analytics and visualization</Text>
            </Col>
            <Col>
              <Space>
                <Tooltip title="Refresh all data">
                  <Button
                    icon={<SyncOutlined spin={isLoading} />}
                    onClick={refreshAll}
                    loading={isLoading}
                  />
                </Tooltip>
                <Tooltip title="WebSocket status">
                  <Tag color={isConnected ? 'green' : 'red'}>
                    {isConnected ? 'Live' : 'Disconnected'}
                  </Tag>
                </Tooltip>
                <Button
                  icon={<SettingOutlined />}
                  onClick={() => setSettingsVisible(true)}
                />
              </Space>
            </Col>
          </Row>
        </Card>

        {/* Stats Overview */}
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Title level={4} style={{ margin: 0 }}>
                <DatabaseOutlined style={{ marginRight: 8 }} />
                Total Nodes
              </Title>
              <Title level={2} style={{ margin: '16px 0 0' }}>
                {totalNodes.toLocaleString()}
              </Title>
              <Text type="secondary">
                {Object.entries(nodeTypeCounts).map(([type, count]) => (
                  <Tag key={type} style={{ margin: '4px 4px 4px 0' }}>
                    {type}: {count}
                  </Tag>
                ))}
              </Text>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Title level={4} style={{ margin: 0 }}>
                <BranchesOutlined style={{ marginRight: 8 }} />
                Total Edges
              </Title>
              <Title level={2} style={{ margin: '16px 0 0' }}>
                {totalEdges.toLocaleString()}
              </Title>
              <Text type="secondary">
                {Object.entries(edgeTypeCounts).map(([type, count]) => (
                  <Tag key={type} style={{ margin: '4px 4px 4px 0' }}>
                    {type}: {count}
                  </Tag>
                ))}
              </Text>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Title level={4} style={{ margin: 0 }}>
                <NodeIndexOutlined style={{ marginRight: 8 }} />
                Node Types
              </Title>
              <Title level={2} style={{ margin: '16px 0 0' }}>
                {availableNodeTypes.length}
              </Title>
              <Text type="secondary">
                {availableNodeTypes.slice(0, 5).join(', ')}
                {availableNodeTypes.length > 5 && '...'}
              </Text>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Title level={4} style={{ margin: 0 }}>
                <ClusterOutlined style={{ marginRight: 8 }} />
                Edge Types
              </Title>
              <Title level={2} style={{ margin: '16px 0 0' }}>
                {availableEdgeTypes.length}
              </Title>
              <Text type="secondary">
                {availableEdgeTypes.slice(0, 5).join(', ')}
                {availableEdgeTypes.length > 5 && '...'}
              </Text>
            </Card>
          </Col>
        </Row>

        {/* Error Alert */}
        {hasError && (
          <Alert
            message="Error loading graph data"
            description={statsError?.message || nodesError?.message || edgesError?.message}
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
                key: 'visualization',
                label: 'Visualization',
                icon: <EyeOutlined />,
                children: (
                  <ConnectedGraphVisualization
                    height="700px"
                    layout={layout}
                    autoRefresh={autoRefresh}
                    refreshInterval={refreshInterval}
                    showControls={true}
                    showStats={false}
                    onNodeClick={handleNodeClick}
                    onEdgeClick={handleEdgeClick}
                  />
                ),
              },
              {
                key: 'data',
                label: 'Data Table',
                icon: <DatabaseOutlined />,
                children: (
                  <Card>
                    <Title level={4}>Nodes ({nodes.length})</Title>
                    <div style={{ maxHeight: 400, overflow: 'auto' }}>
                      {nodes.map(node => (
                        <Card
                          key={node.id}
                          size="small"
                          style={{ marginBottom: 8, cursor: 'pointer' }}
                          onClick={() => handleNodeClick(node)}
                        >
                          <Row>
                            <Col span={4}>
                              <Tag color={getNodeColor(node.type)}>
                                {node.type || 'unknown'}
                              </Tag>
                            </Col>
                            <Col span={16}>
                              <Text strong>{node.label || node.id}</Text>
                            </Col>
                            <Col span={4} style={{ textAlign: 'right' }}>
                              <Button size="small" icon={<EyeOutlined />} />
                            </Col>
                          </Row>
                        </Card>
                      ))}
                    </div>
                    
                    <Divider />
                    
                    <Title level={4}>Edges ({edges.length})</Title>
                    <div style={{ maxHeight: 400, overflow: 'auto' }}>
                      {edges.map(edge => (
                        <Card
                          key={edge.id}
                          size="small"
                          style={{ marginBottom: 8, cursor: 'pointer' }}
                          onClick={() => handleEdgeClick(edge)}
                        >
                          <Row>
                            <Col span={6}>
                              <Text code>{edge.source}</Text>
                            </Col>
                            <Col span={2} style={{ textAlign: 'center' }}>
                              <Tag color={getEdgeColor(edge.type)}>
                                {edge.type || 'unknown'}
                              </Tag>
                            </Col>
                            <Col span={6}>
                              <Text code>{edge.target}</Text>
                            </Col>
                            <Col span={10}>
                              <Text type="secondary">{edge.type}</Text>
                            </Col>
                          </Row>
                        </Card>
                      ))}
                    </div>
                  </Card>
                ),
              },
              {
                key: 'analysis',
                label: 'Analysis',
                icon: <NodeIndexOutlined />,
                children: (
                  <Card>
                    <Title level={4}>Graph Analysis Tools</Title>
                    <Paragraph>
                      Perform advanced graph analysis using the backend AI/ML modules.
                    </Paragraph>
                    
                    <Space direction="vertical">
                      <Card title="Centrality Analysis">
                        <Text>
                          Calculate centrality metrics to identify the most important nodes in your graph.
                        </Text>
                        <Button
                          type="primary"
                          style={{ marginTop: 16 }}
                          onClick={async () => {
                            try {
                              const result = await centralityMutation.mutateAsync({
                                algorithm: 'degree',
                                limit: 10,
                              });
                              message.success('Centrality analysis completed');
                            } catch (error) {
                              message.error('Centrality analysis failed');
                            }
                          }}
                        >
                          Run Centrality Analysis
                        </Button>
                      </Card>
                      
                      <Card title="Community Detection">
                        <Text>
                          Detect communities or clusters within your graph to identify groups of related entities.
                        </Text>
                        <Button
                          type="primary"
                          style={{ marginTop: 16 }}
                          onClick={async () => {
                            try {
                              const result = await communitiesMutation.mutateAsync({
                                algorithm: 'louvain',
                                resolution: 1.0,
                              });
                              message.success('Community detection completed');
                            } catch (error) {
                              message.error('Community detection failed');
                            }
                          }}
                        >
                          Detect Communities
                        </Button>
                      </Card>
                      
                      <Card title="Path Finding">
                        <Text>
                          Find paths between nodes to understand relationships and connections.
                        </Text>
                        <Space style={{ marginTop: 16 }}>
                          <Select
                            placeholder="Start node"
                            style={{ width: 200 }}
                          >
                            {nodes.slice(0, 50).map(node => (
                              <Option key={node.id} value={node.id}>
                                {node.label || node.id}
                              </Option>
                            ))}
                          </Select>
                          <Select
                            placeholder="End node"
                            style={{ width: 200 }}
                          >
                            {nodes.slice(0, 50).map(node => (
                              <Option key={node.id} value={node.id}>
                                {node.label || node.id}
                              </Option>
                            ))}
                          </Select>
                          <Button type="primary">Find Path</Button>
                        </Space>
                      </Card>
                    </Space>
                  </Card>
                ),
              },
            ]}
          />
        </Card>

        {/* Node Detail Modal */}
        <Modal
          title="Node Details"
          open={nodeDetailVisible}
          onCancel={() => setNodeDetailVisible(false)}
          footer={null}
          width={600}
        >
          {selectedNode && (
            <Card>
              <Title level={4}>{selectedNode.label || selectedNode.id}</Title>
              <Tag color={getNodeColor(selectedNode.type)}>
                {selectedNode.type || 'unknown'}
              </Tag>
              
              <Divider />
              
              <Title level={5}>Properties</Title>
              <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4 }}>
                {JSON.stringify(selectedNode.properties || {}, null, 2)}
              </pre>
              
              <Divider />
              
              <Space>
                <Button icon={<EyeOutlined />}>
                  View in Graph
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

        {/* Edge Detail Modal */}
        <Modal
          title="Edge Details"
          open={edgeDetailVisible}
          onCancel={() => setEdgeDetailVisible(false)}
          footer={null}
          width={600}
        >
          {selectedEdge && (
            <Card>
              <Title level={4}>
                {selectedEdge.source} → {selectedEdge.target}
              </Title>
              <Tag color={getEdgeColor(selectedEdge.type)}>
                {selectedEdge.type || 'unknown'}
              </Tag>
              
              <Divider />
              
              <Title level={5}>Properties</Title>
              <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4 }}>
                {JSON.stringify(selectedEdge.properties || {}, null, 2)}
              </pre>
              
              <Divider />
              
              <Space>
                <Button icon={<EyeOutlined />}>
                  Highlight in Graph
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

        {/* Settings Drawer */}
        <Drawer
          title="Graph Settings"
          placement="right"
          open={settingsVisible}
          onClose={() => setSettingsVisible(false)}
          width={300}
        >
          <Space direction="vertical" size="middle">
            <Card size="small">
              <Title level={5}>Layout</Title>
              <Select
                value={layout}
                onChange={(value) => {
                  setLayout(value);
                  saveLayout(value);
                }}
                style={{ width: '100%' }}
              >
                <Option value="cose">CoSE</Option>
                <Option value="circle">Circle</Option>
                <Option value="grid">Grid</Option>
                <Option value="random">Random</Option>
                <Option value="dagre">Dagre</Option>
                <Option value="breadthfirst">Breadthfirst</Option>
                <Option value="fcose">Fcose</Option>
              </Select>
            </Card>
            
            <Card size="small">
              <Title level={5}>Auto Refresh</Title>
              <Space direction="vertical">
                <Button
                  type={autoRefresh ? 'primary' : 'default'}
                  onClick={() => {
                    setAutoRefresh(!autoRefresh);
                    saveAutoRefresh(!autoRefresh);
                  }}
                >
                  {autoRefresh ? 'Enabled' : 'Disabled'}
                </Button>
                {autoRefresh && (
                  <Select
                    value={refreshInterval}
                    onChange={(value) => {
                      setRefreshInterval(value);
                      saveRefreshInterval(value);
                    }}
                    style={{ width: '100%' }}
                  >
                    <Option value={10000}>10 seconds</Option>
                    <Option value={30000}>30 seconds</Option>
                    <Option value={60000}>1 minute</Option>
                    <Option value={300000}>5 minutes</Option>
                  </Select>
                )}
              </Space>
            </Card>
            
            <Card size="small">
              <Title level={5}>Export</Title>
              <Space direction="vertical">
                <Button
                  block
                  icon={<ExportOutlined />}
                  onClick={() => exportGraph('csv')}
                >
                  Export as CSV
                </Button>
                <Button
                  block
                  icon={<ExportOutlined />}
                  onClick={() => exportGraph('json')}
                >
                  Export as JSON
                </Button>
                <Button
                  block
                  icon={<ExportOutlined />}
                  onClick={() => exportGraph('stix')}
                >
                  Export as STIX
                </Button>
              </Space>
            </Card>
          </Space>
        </Drawer>
      </Space>
    </motion.div>
  );
  
  // Helper functions
  function getNodeColor(type: string | undefined): string {
    const colors: Record<string, string> = {
      person: 'blue',
      company: 'green',
      email: 'orange',
      ip: 'red',
      domain: 'purple',
      url: 'volcano',
      default: 'default',
    };
    return colors[type || 'default'];
  }
  
  function getEdgeColor(type: string | undefined): string {
    const colors: Record<string, string> = {
      WORKS_AT: 'green',
      HAS_EMAIL: 'orange',
      KNOWS: 'blue',
      USES_IP: 'red',
      OWNS_DOMAIN: 'purple',
      CONNECTED_TO: 'volcano',
      default: 'default',
    };
    return colors[type || 'default'];
  }
};

export default GraphExplorer;
