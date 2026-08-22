import React, { useState, useCallback, useRef } from 'react';
import { Card, Tabs, Button, Space, Input, Select, Typography, Divider, Modal, Form, Spin, Alert, Tag, Tooltip, Drawer, Table, message } from 'antd';
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
import StatCard from '../components/common/StatCard';
import PageHeader from '../components/common/PageHeader';
import LivePill from '../components/common/LivePill';
import { useWebSocket as useWebSocketContext } from '../contexts/WebSocketContext';
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
  const [zoomLevel, setZoomLevel] = useState(100);
  const canvasFrameRef = useRef<HTMLDivElement>(null);

  // Local storage for preferences
  const { value: savedLayout, setValue: saveLayout } = useLocalStorage('graph-layout', 'cose');
  const { value: savedAutoRefresh, setValue: saveAutoRefresh } = useLocalStorage('graph-auto-refresh', false);
  const { value: savedRefreshInterval, setValue: saveRefreshInterval } = useLocalStorage('graph-refresh-interval', 30000);
  const { value: savedActiveTab, setValue: saveActiveTab } = useLocalStorage('graph-active-tab', 'visualization');

  // Load saved preferences
  React.useEffect(() => {
    setLayout(savedLayout);
    setAutoRefresh(savedAutoRefresh);
    setRefreshInterval(savedRefreshInterval);
    setActiveTab(savedActiveTab);
  }, [savedLayout, savedAutoRefresh, savedRefreshInterval, savedActiveTab]);

  const handleTabChange = useCallback((key: string) => {
    setActiveTab(key);
    saveActiveTab(key);
  }, [saveActiveTab]);

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      canvasFrameRef.current?.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  }, []);

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
  const { messages, sendMessage } = useWebSocket(
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

  // Live/offline pill reads the shared websocket context directly - the
  // adapter above is for message subscription, not connection status.
  const { isConnected } = useWebSocketContext();

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
      <div className="ol-page-body">
        {/* Header */}
        <PageHeader
          icon={<ProjectOutlined />}
          title="Graph Explorer"
          subtitle="Real-time graph analytics and visualization"
          actions={
            <>
              <LivePill connected={isConnected} />
              <Tooltip title="Refresh all data">
                <Button
                  icon={<SyncOutlined spin={isLoading} />}
                  onClick={refreshAll}
                  loading={isLoading}
                />
              </Tooltip>
              <Tooltip title="Graph settings">
                <button
                  type="button"
                  className="ol-icon-btn"
                  onClick={() => setSettingsVisible(true)}
                >
                  <SettingOutlined />
                </button>
              </Tooltip>
            </>
          }
        />

        {/* Stats Overview */}
        <div className="ol-stats-grid">
          <StatCard
            label="Total Nodes"
            value={totalNodes.toLocaleString()}
            icon={<DatabaseOutlined />}
            accent="primary"
            minHeight={132}
            loading={statsLoading && !stats}
            footer={
              <Space wrap size={[4, 4]}>
                {Object.entries(nodeTypeCounts).map(([type, count]) => (
                  <Tag key={type} color={getNodeColor(type)} style={{ margin: 0 }}>
                    {type}: {count}
                  </Tag>
                ))}
              </Space>
            }
          />
          <StatCard
            label="Total Edges"
            value={totalEdges.toLocaleString()}
            icon={<BranchesOutlined />}
            accent="success"
            minHeight={132}
            loading={statsLoading && !stats}
            footer={
              <Space wrap size={[4, 4]}>
                {Object.entries(edgeTypeCounts).map(([type, count]) => (
                  <Tag key={type} color={getEdgeColor(type)} style={{ margin: 0 }}>
                    {type}: {count}
                  </Tag>
                ))}
              </Space>
            }
          />
          <StatCard
            label="Node Types"
            value={availableNodeTypes.length}
            icon={<NodeIndexOutlined />}
            accent="purple"
            minHeight={132}
            loading={nodesLoading && nodes.length === 0}
            footer={
              <Space wrap size={[4, 4]}>
                {availableNodeTypes.map((type) => (
                  <Tag key={type} color={getNodeColor(type)} style={{ margin: 0 }}>
                    {type}
                  </Tag>
                ))}
              </Space>
            }
          />
          <StatCard
            label="Edge Types"
            value={availableEdgeTypes.length}
            icon={<ClusterOutlined />}
            accent="warning"
            minHeight={132}
            loading={edgesLoading && edges.length === 0}
            footer={
              <Space wrap size={[4, 4]}>
                {availableEdgeTypes.map((type) => (
                  <Tag key={type} color={getEdgeColor(type)} style={{ margin: 0 }}>
                    {type}
                  </Tag>
                ))}
              </Space>
            }
          />
        </div>

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
            onChange={handleTabChange}
            items={[
              {
                key: 'visualization',
                label: 'Visualization',
                icon: <EyeOutlined />,
                children: (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    {/* Toolbar */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                      <Input
                        placeholder="Search nodes..."
                        prefix={<SearchOutlined />}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        style={{ width: 220 }}
                        allowClear
                      />
                      <Select
                        value={layout}
                        onChange={(value) => {
                          setLayout(value);
                          saveLayout(value);
                        }}
                        style={{ width: 160 }}
                      >
                        <Option value="cose">CoSE</Option>
                        <Option value="circle">Circle</Option>
                        <Option value="grid">Grid</Option>
                        <Option value="random">Random</Option>
                        <Option value="dagre">Dagre</Option>
                        <Option value="breadthfirst">Breadthfirst</Option>
                        <Option value="fcose">Fcose</Option>
                      </Select>
                      <div style={{ flex: 1 }} />
                      <Space size={8}>
                        <Tooltip title="Zoom in">
                          <button
                            type="button"
                            className="ol-icon-btn"
                            onClick={() => setZoomLevel((z) => Math.min(200, z + 10))}
                          >
                            <ZoomInOutlined />
                          </button>
                        </Tooltip>
                        <Tooltip title="Zoom out">
                          <button
                            type="button"
                            className="ol-icon-btn"
                            onClick={() => setZoomLevel((z) => Math.max(25, z - 10))}
                          >
                            <ZoomOutOutlined />
                          </button>
                        </Tooltip>
                        <Tooltip title="Fullscreen">
                          <button type="button" className="ol-icon-btn" onClick={toggleFullscreen}>
                            <FullscreenOutlined />
                          </button>
                        </Tooltip>
                        <Tooltip title="Export as JSON">
                          <button
                            type="button"
                            className="ol-icon-btn"
                            onClick={() => exportGraph('json')}
                          >
                            <ExportOutlined />
                          </button>
                        </Tooltip>
                      </Space>
                    </div>

                    {/* Canvas */}
                    <div
                      ref={canvasFrameRef}
                      style={{
                        position: 'relative',
                        height: 560,
                        border: '1px solid var(--border-color)',
                        borderRadius: 12,
                        background: 'var(--bg-color-secondary)',
                      }}
                    >
                      <div style={{ position: 'absolute', inset: 0, overflow: 'auto', borderRadius: 12 }}>
                        <ConnectedGraphVisualization
                          height={420}
                          layout={layout}
                          autoRefresh={autoRefresh}
                          refreshInterval={refreshInterval}
                          showControls={false}
                          showStats={false}
                          showHeader={false}
                          showLegend={false}
                          onNodeClick={handleNodeClick}
                          onEdgeClick={handleEdgeClick}
                        />
                      </div>

                      {/* Stats strip */}
                      <div
                        style={{
                          position: 'absolute',
                          top: 12,
                          right: 16,
                          padding: '6px 12px',
                          borderRadius: 6,
                          background: 'var(--card-bg)',
                          border: '1px solid var(--border-color-secondary)',
                          fontSize: 12,
                          color: 'var(--text-color-secondary)',
                          boxShadow: '0 2px 8px var(--shadow-color)',
                        }}
                      >
                        {nodes.length.toLocaleString()} nodes shown · {edges.length.toLocaleString()} edges · {zoomLevel}% zoom
                      </div>

                      {/* Legend */}
                      <div
                        style={{
                          position: 'absolute',
                          bottom: 12,
                          left: 14,
                          padding: '12px 14px',
                          borderRadius: 8,
                          background: 'var(--card-bg)',
                          boxShadow: '0 2px 8px var(--shadow-color)',
                        }}
                      >
                        <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 8, color: 'var(--text-color)' }}>
                          Legend
                        </div>
                        <Space direction="vertical" size={4}>
                          {['person', 'company', 'email', 'ip', 'domain'].map((type) => (
                            <Space key={type} size={6}>
                              <span
                                style={{
                                  width: 10,
                                  height: 10,
                                  borderRadius: '50%',
                                  background: getNodeColor(type),
                                  display: 'inline-block',
                                }}
                              />
                              <span
                                style={{
                                  fontSize: 12,
                                  color: 'var(--text-color-secondary)',
                                  textTransform: 'capitalize',
                                }}
                              >
                                {type}
                              </span>
                            </Space>
                          ))}
                        </Space>
                      </div>
                    </div>
                  </div>
                ),
              },
              {
                key: 'data',
                label: 'Data Table',
                icon: <DatabaseOutlined />,
                children: (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                    <div className="ol-section">
                      <Title level={5} className="ol-section-title">
                        Nodes ({totalNodes.toLocaleString()} · showing {nodes.length.toLocaleString()})
                      </Title>
                      <Table
                        rowKey="id"
                        dataSource={nodes}
                        loading={nodesLoading}
                        scroll={{ x: 640 }}
                        columns={[
                          {
                            title: 'Type',
                            dataIndex: 'type',
                            key: 'type',
                            width: 120,
                            render: (type?: string) => (
                              <Tag color={getNodeColor(type)}>{type || 'unknown'}</Tag>
                            ),
                          },
                          {
                            title: 'Label',
                            dataIndex: 'label',
                            key: 'label',
                            render: (label: string, record: NodeData) => (
                              <Text strong>{label || record.id}</Text>
                            ),
                          },
                          {
                            title: 'ID',
                            dataIndex: 'id',
                            key: 'id',
                            render: (id: string) => <span className="ol-mono">{id}</span>,
                          },
                          {
                            title: '',
                            key: 'actions',
                            width: 60,
                            render: (_: unknown, record: NodeData) => (
                              <Button size="small" icon={<EyeOutlined />} onClick={() => handleNodeClick(record)} />
                            ),
                          },
                        ]}
                      />
                    </div>

                    <div className="ol-section">
                      <Title level={5} className="ol-section-title">
                        Edges ({totalEdges.toLocaleString()} · showing {edges.length.toLocaleString()})
                      </Title>
                      <Table
                        rowKey="id"
                        dataSource={edges}
                        loading={edgesLoading}
                        scroll={{ x: 520 }}
                        columns={[
                          {
                            title: 'Source',
                            dataIndex: 'source',
                            key: 'source',
                            render: (source: string) => <span className="ol-mono">{source}</span>,
                          },
                          {
                            title: 'Type',
                            dataIndex: 'type',
                            key: 'type',
                            width: 120,
                            render: (type?: string) => (
                              <Tag color={getEdgeColor(type)}>{type || 'unknown'}</Tag>
                            ),
                          },
                          {
                            title: 'Target',
                            dataIndex: 'target',
                            key: 'target',
                            render: (target: string) => <span className="ol-mono">{target}</span>,
                          },
                          {
                            title: '',
                            key: 'actions',
                            width: 60,
                            render: (_: unknown, record: EdgeData) => (
                              <Button size="small" icon={<EyeOutlined />} onClick={() => handleEdgeClick(record)} />
                            ),
                          },
                        ]}
                      />
                    </div>
                  </div>
                ),
              },
              {
                key: 'analysis',
                label: 'Analysis',
                icon: <NodeIndexOutlined />,
                children: (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                    <Paragraph type="secondary" style={{ margin: 0 }}>
                      Perform advanced graph analysis using the backend AI/ML modules.
                    </Paragraph>

                    <div className="ol-row-2up">
                      <Card title="Centrality Analysis" className="ol-subcard">
                        <Text>
                          Calculate centrality metrics to identify the most important nodes in your graph.
                        </Text>
                        <div>
                          <Button
                            type="primary"
                            style={{ marginTop: 16 }}
                            loading={centralityMutation.isLoading}
                            onClick={async () => {
                              try {
                                await centralityMutation.mutateAsync({
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
                        </div>
                      </Card>

                      <Card title="Community Detection" className="ol-subcard">
                        <Text>
                          Detect communities or clusters within your graph to identify groups of related entities.
                        </Text>
                        <div>
                          <Button
                            type="primary"
                            style={{ marginTop: 16 }}
                            loading={communitiesMutation.isLoading}
                            onClick={async () => {
                              try {
                                await communitiesMutation.mutateAsync({
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
                        </div>
                      </Card>
                    </div>

                    <Card title="Path Finding" className="ol-subcard">
                      <Text>
                        Find paths between nodes to understand relationships and connections.
                      </Text>
                      <Space style={{ marginTop: 16 }} wrap>
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
                  </div>
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
      </div>
    </motion.div>
  );

  // Helper functions
  function getNodeColor(type: string | undefined): string {
    const colors: Record<string, string> = {
      person: '#1890ff',
      company: '#52c41a',
      email: '#faad14',
      ip: '#f5222d',
      domain: '#722ed1',
      default: '#8c8c8c',
    };
    return colors[type || 'default'] ?? colors.default;
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
