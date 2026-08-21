/**
 * ConnectedGraphVisualization Component
 *
 * A connected version of GraphVisualization that fetches data from the backend API.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, Button, Space, Select, Tooltip, Typography, Row, Col, Divider, Spin, Alert, Input, Tag } from 'antd';
import { SyncOutlined, SearchOutlined, FilterOutlined, NodeIndexOutlined, BranchesOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import GraphVisualization from './GraphVisualization';
import type { NodeData, EdgeData, GraphData } from './GraphVisualization';
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
import { useDebounce } from '../hooks/useApi';

const { Text, Title } = Typography;
const { Option } = Select;
const { Search } = Input;

interface ConnectedGraphVisualizationProps {
  height?: number | string;
  layout?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
  showControls?: boolean;
  showStats?: boolean;
  onNodeClick?: (node: NodeData) => void;
  onEdgeClick?: (edge: EdgeData) => void;
  style?: React.CSSProperties;
}

const ConnectedGraphVisualization: React.FC<ConnectedGraphVisualizationProps> = ({
  height = 600,
  layout = 'cose',
  autoRefresh = false,
  refreshInterval = 30000,
  showControls = true,
  showStats = true,
  onNodeClick,
  onEdgeClick,
  style = {},
}) => {
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [nodeTypeFilter, setNodeTypeFilter] = useState<string[]>([]);
  const [edgeTypeFilter, setEdgeTypeFilter] = useState<string[]>([]);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('degree');
  const [showCentrality, setShowCentrality] = useState(false);
  const [showCommunities, setShowCommunities] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [pathStartNode, setPathStartNode] = useState<string>('');
  const [pathEndNode, setPathEndNode] = useState<string>('');
  
  // Debounced search query
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  
  // API Hooks
  const { data: stats, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useGraphStats({
    enabled: showStats,
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
  const { isConnected, messages } = useWebSocket(
    '/api/ws/graph',
    (data) => {
      // Handle real-time graph updates
      if (data.type === 'graph_update') {
        refetchNodes();
        refetchEdges();
        refetchStats();
      }
    }
  );
  
  // Available node types from the data
  const availableNodeTypes = React.useMemo(() => {
    const types = new Set<string>();
    nodes.forEach(node => {
      if (node.type) types.add(node.type);
    });
    return Array.from(types);
  }, [nodes]);
  
  // Available edge types from the data
  const availableEdgeTypes = React.useMemo(() => {
    const types = new Set<string>();
    edges.forEach(edge => {
      if (edge.type) types.add(edge.type);
    });
    return Array.from(types);
  }, [edges]);
  
  // Available node IDs for path finding
  const availableNodeIds = React.useMemo(() => {
    return nodes.map(node => node.id);
  }, [nodes]);
  
  // Refresh all data
  const refreshAll = useCallback(() => {
    refetchNodes();
    refetchEdges();
    refetchStats();
  }, [refetchNodes, refetchEdges, refetchStats]);
  
  // Execute custom query
  const executeQuery = useCallback(async (query: string) => {
    try {
      const result = await queryMutation.mutateAsync({ query, params: {} });
      return result;
    } catch (error) {
      console.error('Query execution failed:', error);
      throw error;
    }
  }, [queryMutation]);
  
  // Calculate centrality
  const calculateCentrality = useCallback(async () => {
    try {
      const result = await centralityMutation.mutateAsync({
        algorithm: selectedAlgorithm,
        limit: 100,
      });
      return result;
    } catch (error) {
      console.error('Centrality calculation failed:', error);
      throw error;
    }
  }, [centralityMutation, selectedAlgorithm]);
  
  // Detect communities
  const detectCommunities = useCallback(async () => {
    try {
      const result = await communitiesMutation.mutateAsync({
        algorithm: 'louvain',
        resolution: 1.0,
      });
      return result;
    } catch (error) {
      console.error('Community detection failed:', error);
      throw error;
    }
  }, [communitiesMutation]);
  
  // Find path
  const findPath = useCallback(async (start: string, end: string) => {
    try {
      const result = await pathMutation.mutateAsync({
        start_node: start,
        end_node: end,
        algorithm: 'shortest',
      });
      return result;
    } catch (error) {
      console.error('Path finding failed:', error);
      throw error;
    }
  }, [pathMutation]);
  
  // Handle node click
  const handleNodeClick = useCallback((node: NodeData) => {
    setSelectedNodeId(node.id);
    onNodeClick?.(node);
  }, [onNodeClick]);
  
  // Handle edge click
  const handleEdgeClick = useCallback((edge: EdgeData) => {
    onEdgeClick?.(edge);
  }, [onEdgeClick]);
  
  // Transform nodes and edges for visualization
  const graphData: GraphData = React.useMemo(() => {
    const transformedNodes = nodes.map(node => ({
      ...node,
      color: getNodeColor(node.type),
      shape: getNodeShape(node.type),
      selected: node.id === selectedNodeId,
    }));
    
    const transformedEdges = edges.map(edge => ({
      ...edge,
      color: getEdgeColor(edge.type),
      width: edge.type ? 2 : 1,
    }));
    
    return { nodes: transformedNodes, edges: transformedEdges };
  }, [nodes, edges, selectedNodeId]);
  
  // Node/edge styling helpers. Declared as `function`s (hoisted) so the
  // graphData useMemo above can call them regardless of source order - as
  // consts they threw a TDZ ReferenceError on first render.
  function getNodeColor(type: string | undefined) {
    const colors: Record<string, string> = {
      person: '#1890ff',
      company: '#52c41a',
      email: '#faad14',
      ip: '#f5222d',
      domain: '#722ed1',
      url: '#fa8c16',
      default: '#666',
    };
    return colors[type || 'default'] ?? colors.default;
  }

  function getNodeShape(type: string | undefined) {
    const shapes: Record<string, string> = {
      person: 'ellipse',
      company: 'rectangle',
      email: 'ellipse',
      ip: 'ellipse',
      domain: 'ellipse',
      url: 'ellipse',
      default: 'ellipse',
    };
    return shapes[type || 'default'] ?? shapes.default;
  }

  function getEdgeColor(type: string | undefined) {
    const colors: Record<string, string> = {
      WORKS_AT: '#52c41a',
      HAS_EMAIL: '#faad14',
      KNOWS: '#1890ff',
      USES_IP: '#f5222d',
      OWNS_DOMAIN: '#722ed1',
      CONNECTED_TO: '#fa8c16',
      default: '#ccc',
    };
    return colors[type || 'default'] ?? colors.default;
  }
  
  // Loading state
  const isLoading = statsLoading || nodesLoading || edgesLoading;
  const hasError = statsError || nodesError || edgesError;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={style}
    >
      <Card>
        {/* Header */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Title level={4} style={{ margin: 0 }}>
              Graph Visualization
            </Title>
            <Text type="secondary">Real-time graph data from backend</Text>
          </Col>
          <Col>
            <Space>
              <Tooltip title="Refresh data">
                <Button
                  icon={<SyncOutlined spin={isLoading} />}
                  onClick={refreshAll}
                  loading={isLoading}
                />
              </Tooltip>
              <Tooltip title="WebSocket status">
                <Tag color={isConnected ? 'green' : 'red'}>
                  {isConnected ? 'Connected' : 'Disconnected'}
                </Tag>
              </Tooltip>
            </Space>
          </Col>
        </Row>

        {/* Stats */}
        {showStats && stats && (
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Card size="small">
                <Text type="secondary">Nodes</Text>
                <Title level={3} style={{ margin: '8px 0 0' }}>
                  {stats?.nodeCount || 0}
                </Title>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Text type="secondary">Edges</Text>
                <Title level={3} style={{ margin: '8px 0 0' }}>
                  {stats?.edgeCount || 0}
                </Title>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Text type="secondary">Types</Text>
                <Title level={3} style={{ margin: '8px 0 0' }}>
                  {availableNodeTypes.length}
                </Title>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Text type="secondary">Avg degree</Text>
                <Title level={3} style={{ margin: '8px 0 0' }}>
                  {stats?.nodeCount
                    ? ((2 * (stats.edgeCount || 0)) / stats.nodeCount).toFixed(2)
                    : '0'}
                </Title>
              </Card>
            </Col>
          </Row>
        )}

        {/* Controls */}
        {showControls && (
          <Card size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16} align="middle">
              <Col flex="auto">
                <Search
                  placeholder="Search nodes..."
                  prefix={<SearchOutlined />}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  allowClear
                />
              </Col>
              <Col>
                <Select
                  mode="multiple"
                  placeholder="Filter node types"
                  prefix={<FilterOutlined />}
                  value={nodeTypeFilter}
                  onChange={setNodeTypeFilter}
                  style={{ minWidth: 150 }}
                  allowClear
                >
                  {availableNodeTypes.map(type => (
                    <Option key={type} value={type}>
                      {type}
                    </Option>
                  ))}
                </Select>
              </Col>
              <Col>
                <Select
                  mode="multiple"
                  placeholder="Filter edge types"
                  prefix={<FilterOutlined />}
                  value={edgeTypeFilter}
                  onChange={setEdgeTypeFilter}
                  style={{ minWidth: 150 }}
                  allowClear
                >
                  {availableEdgeTypes.map(type => (
                    <Option key={type} value={type}>
                      {type}
                    </Option>
                  ))}
                </Select>
              </Col>
            </Row>
            
            <Divider style={{ margin: '16px 0' }} />
            
            <Row gutter={16} align="middle">
              <Col>
                <Space>
                  <Button
                    icon={<NodeIndexOutlined />}
                    onClick={() => setShowCentrality(!showCentrality)}
                    type={showCentrality ? 'primary' : 'default'}
                  >
                    Centrality
                  </Button>
                  {showCentrality && (
                    <Select
                      value={selectedAlgorithm}
                      onChange={setSelectedAlgorithm}
                      style={{ width: 120 }}
                    >
                      <Option value="degree">Degree</Option>
                      <Option value="betweenness">Betweenness</Option>
                      <Option value="closeness">Closeness</Option>
                      <Option value="pagerank">PageRank</Option>
                    </Select>
                  )}
                </Space>
              </Col>
              <Col>
                <Button
                  icon={<BranchesOutlined />}
                  onClick={() => setShowCommunities(!showCommunities)}
                  type={showCommunities ? 'primary' : 'default'}
                >
                  Communities
                </Button>
              </Col>
              <Col flex="auto">
                <Space>
                  <Input
                    placeholder="Start node"
                    value={pathStartNode}
                    onChange={(e) => setPathStartNode(e.target.value)}
                    style={{ width: 120 }}
                  />
                  <Input
                    placeholder="End node"
                    value={pathEndNode}
                    onChange={(e) => setPathEndNode(e.target.value)}
                    style={{ width: 120 }}
                  />
                  <Button
                    onClick={() => findPath(pathStartNode, pathEndNode)}
                    disabled={!pathStartNode || !pathEndNode}
                  >
                    Find Path
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>
        )}

        {/* Error Alert */}
        {hasError && (
          <Alert
            message="Error loading graph data"
            description={statsError?.message || nodesError?.message || edgesError?.message}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        {/* Graph Visualization */}
        <Spin spinning={isLoading} tip="Loading graph data...">
          <GraphVisualization
            data={graphData}
            height={height}
            layout={layout}
            onNodeClick={handleNodeClick}
            onEdgeClick={handleEdgeClick}
          />
        </Spin>

        {/* Selected Node Info */}
        {selectedNodeId && (
          <Card size="small" style={{ marginTop: 16 }}>
            <Title level={5}>Selected Node</Title>
            <Text code>{selectedNodeId}</Text>
          </Card>
        )}
      </Card>
    </motion.div>
  );
};

export default ConnectedGraphVisualization;
