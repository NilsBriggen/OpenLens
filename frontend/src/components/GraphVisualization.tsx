import React, { useState, useRef, useEffect } from 'react';
import { Card, Button, Space, Select, Tooltip, Typography, Row, Col, Divider, Spin, Alert } from 'antd';
import {
  ProjectOutlined,
  EyeOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  SyncOutlined,
  SettingOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  ClusterOutlined,
  PicCenterOutlined,
  PicLeftOutlined,
  PicRightOutlined
} from '@ant-design/icons';
import CytoscapeComponent from 'react-cytoscapejs';
import { motion } from 'framer-motion';

const { Text, Title } = Typography;
const { Option } = Select;

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

interface GraphData {
  nodes: NodeData[];
  edges: EdgeData[];
}

interface GraphVisualizationProps {
  data: GraphData;
  height?: number | string;
  layout?: string;
  onNodeClick?: (node: NodeData) => void;
  onEdgeClick?: (edge: EdgeData) => void;
  onReady?: (cy: any) => void;
  style?: React.CSSProperties;
}

const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  data,
  height = 600,
  layout = 'cose',
  onNodeClick,
  onEdgeClick,
  onReady,
  style = {},
}) => {
  const [cy, setCy] = useState<any>(null);
  const [zoom, setZoom] = useState(1);
  const [fullscreen, setFullscreen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<EdgeData | null>(null);
  const [loading, setLoading] = useState(false);
  const cyRef = useRef<any>(null);

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
    { label: 'KK', value: 'kk' },
    { label: 'ForceAtlas2', value: 'forceAtlas2' },
  ];

  // Handle node click
  const handleNodeClick = (event: any) => {
    const node = event.target;
    const nodeData = node.data();
    setSelectedNode(nodeData);
    setSelectedEdge(null);
    onNodeClick && onNodeClick(nodeData);
  };

  // Handle edge click
  const handleEdgeClick = (event: any) => {
    const edge = event.target;
    const edgeData = edge.data();
    setSelectedEdge(edgeData);
    setSelectedNode(null);
    onEdgeClick && onEdgeClick(edgeData);
  };

  // Handle background click
  const handleBackgroundClick = () => {
    setSelectedNode(null);
    setSelectedEdge(null);
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

  // Layout change
  const handleLayoutChange = (newLayout: string) => {
    if (cyRef.current) {
      cyRef.current.layout({ name: newLayout, animate: true }).run();
    }
  };

  // Get node color based on type
  const getNodeColor = (type: string | undefined) => {
    const colors: Record<string, string> = {
      person: '#1890ff',
      company: '#52c41a',
      email: '#faad14',
      ip: '#f5222d',
      domain: '#722ed1',
      url: '#fa8c16',
      default: '#666',
    };
    return colors[type || 'default'];
  };

  // Get edge color based on type
  const getEdgeColor = (type: string | undefined) => {
    const colors: Record<string, string> = {
      WORKS_AT: '#52c41a',
      HAS_EMAIL: '#faad14',
      KNOWS: '#1890ff',
      USES_IP: '#f5222d',
      OWNS_DOMAIN: '#722ed1',
      CONNECTED_TO: '#fa8c16',
      default: '#ccc',
    };
    return colors[type || 'default'];
  };

  // Get node shape based on type
  const getNodeShape = (type: string | undefined) => {
    const shapes: Record<string, string> = {
      person: 'ellipse',
      company: 'rectangle',
      email: 'ellipse',
      ip: 'ellipse',
      domain: 'ellipse',
      url: 'ellipse',
      default: 'ellipse',
    };
    return shapes[type || 'default'];
  };

  // Cytoscape configuration
  const cyConfig = {
    style: [
      // Node styles
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'text-valign': 'center',
          'text-halign': 'center',
          'background-color': 'data(color)',
          'color': '#fff',
          'font-size': '12px',
          'width': 'mapData(type, person, 30, company, 40, email, 25, ip, 25, domain, 25, 30)',
          'height': 'mapData(type, person, 30, company, 40, email, 25, ip, 25, domain, 25, 30)',
          'shape': 'data(shape)',
          'border-width': 'mapData(selected, true, 3, false, 1)',
          'border-color': 'mapData(selected, true, #1890ff, false, #666)',
        },
      },
      // Edge styles
      {
        selector: 'edge',
        style: {
          'width': 'mapData(selected, true, 3, false, 2)',
          'line-color': 'data(color)',
          'curve-style': 'bezier',
          'label': 'data(label)',
          'font-size': '10px',
          'text-background-color': '#fff',
          'text-background-opacity': 0.7,
          'text-background-padding': '2px',
        },
      },
      // Selected styles
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

  // Prepare data with colors and shapes
  const preparedData = {
    nodes: data.nodes.map(node => ({
      ...node,
      color: getNodeColor(node.type),
      shape: getNodeShape(node.type),
      selected: selectedNode?.id === node.id,
    })),
    edges: data.edges.map(edge => ({
      ...edge,
      color: getEdgeColor(edge.type),
      selected: selectedEdge?.id === edge.id,
    })),
  };

  // Stats
  const nodeCount = data.nodes.length;
  const edgeCount = data.edges.length;
  const nodeTypes = [...new Set(data.nodes.map(n => n.type))].filter(Boolean);
  const edgeTypes = [...new Set(data.edges.map(e => e.type))].filter(Boolean);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
    >
      {/* Stats Bar */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={24}>
          <Col span={6}>
            <Space>
              <NodeIndexOutlined style={{ color: '#1890ff' }} />
              <Text strong>{nodeCount}</Text>
              <Text type="secondary">Nodes</Text>
            </Space>
          </Col>
          <Col span={6}>
            <Space>
              <BranchesOutlined style={{ color: '#52c41a' }} />
              <Text strong>{edgeCount}</Text>
              <Text type="secondary">Edges</Text>
            </Space>
          </Col>
          <Col span={12}>
            <Space wrap>
              {nodeTypes.map(type => (
                <Tooltip key={type} title={`Node type: ${type}`}>
                  <Tag color={getNodeColor(type)} style={{ margin: 0 }}>
                    {type} ({data.nodes.filter(n => n.type === type).length})
                  </Tag>
                </Tooltip>
              ))}
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Graph Container */}
      <Card
        title={
          <Space>
            <ProjectOutlined />
            Graph Visualization
          </Space>
        }
        extra={
          <Space>
            <Select
              value={layout}
              onChange={handleLayoutChange}
              options={layoutOptions}
              size="small"
              style={{ width: 120 }}
            />
            <Tooltip title="Zoom In">
              <Button icon={<ZoomInOutlined />} onClick={zoomIn} size="small" />
            </Tooltip>
            <Tooltip title="Zoom Out">
              <Button icon={<ZoomOutOutlined />} onClick={zoomOut} size="small" />
            </Tooltip>
            <Tooltip title="Reset Zoom">
              <Button icon={<SyncOutlined />} onClick={resetZoom} size="small" />
            </Tooltip>
            <Tooltip title={fullscreen ? 'Exit Fullscreen' : 'Fullscreen'}>
              <Button
                icon={fullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                onClick={() => setFullscreen(!fullscreen)}
                size="small"
              />
            </Tooltip>
            <Tooltip title="Settings">
              <Button icon={<SettingOutlined />} size="small" />
            </Tooltip>
          </Space>
        }
        style={{ marginBottom: 16 }}
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" />
            <Text type="secondary" style={{ marginLeft: 16 }}>Loading graph...</Text>
          </div>
        ) : (
          <div
            style={{
              height: fullscreen ? 'calc(100vh - 200px)' : height,
              width: '100%',
              border: '1px solid #f0f0f0',
              borderRadius: 8,
              overflow: 'hidden',
              background: 'var(--bg-color-secondary)',
            }}
          >
            <CytoscapeComponent
              elements={CytoscapeComponent.normalizeElements(preparedData)}
              style={{ width: '100%', height: '100%' }}
              cy={(cy) => {
                cyRef.current = cy;
                setCy(cy);
                onReady && onReady(cy);
                cy.on('tap', 'node', handleNodeClick);
                cy.on('tap', 'edge', handleEdgeClick);
                cy.on('tap', handleBackgroundClick);
              }}
              stylesheet={cyConfig.style}
              layout={cyConfig.layout}
            />
          </div>
        )}
      </Card>

      {/* Selection Details */}
      {(selectedNode || selectedEdge) && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card
            title={
              <Space>
                {selectedNode ? <NodeIndexOutlined /> : <BranchesOutlined />}
                {selectedNode ? 'Node Details' : 'Edge Details'}
              </Space>
            }
            size="small"
          >
            {selectedNode && (
              <Row gutter={24}>
                <Col span={24}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text strong>ID:</Text>
                      <Text code>{selectedNode.id}</Text>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text strong>Label:</Text>
                      <Text>{selectedNode.label}</Text>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text strong>Type:</Text>
                      <Tag color={getNodeColor(selectedNode.type)}>{selectedNode.type || 'unknown'}</Tag>
                    </div>
                    {selectedNode.properties && (
                      <div>
                        <Text strong>Properties:</Text>
                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 12 }}>
                          {JSON.stringify(selectedNode.properties, null, 2)}
                        </pre>
                      </div>
                    )}
                  </Space>
                </Col>
              </Row>
            )}
            
            {selectedEdge && (
              <Row gutter={24}>
                <Col span={24}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text strong>ID:</Text>
                      <Text code>{selectedEdge.id}</Text>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text strong>Source:</Text>
                      <Text>{selectedEdge.source}</Text>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text strong>Target:</Text>
                      <Text>{selectedEdge.target}</Text>
                    </div>
                    {selectedEdge.label && (
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text strong>Label:</Text>
                        <Text>{selectedEdge.label}</Text>
                      </div>
                    )}
                    {selectedEdge.type && (
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text strong>Type:</Text>
                        <Tag color={getEdgeColor(selectedEdge.type)}>{selectedEdge.type}</Tag>
                      </div>
                    )}
                    {selectedEdge.properties && (
                      <div>
                        <Text strong>Properties:</Text>
                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 12 }}>
                          {JSON.stringify(selectedEdge.properties, null, 2)}
                        </pre>
                      </div>
                    )}
                  </Space>
                </Col>
              </Row>
            )}
          </Card>
        </motion.div>
      )}

      {/* Legend */}
      <Card size="small" style={{ marginTop: 16 }}>
        <Title level={5} style={{ margin: 0, marginBottom: 12 }}>
          Legend
        </Title>
        <Row gutter={24}>
          <Col span={12}>
            <Text strong style={{ marginBottom: 8, display: 'block' }}>Node Types:</Text>
            <Space wrap>
              {nodeTypes.map(type => (
                <Space key={type}>
                  <div
                    style={{
                      width: 16,
                      height: 16,
                      borderRadius: getNodeShape(type) === 'rectangle' ? 4 : '50%',
                      background: getNodeColor(type),
                    }}
                  />
                  <Text style={{ fontSize: 12 }}>{type}</Text>
                </Space>
              ))}
            </Space>
          </Col>
          <Col span={12}>
            <Text strong style={{ marginBottom: 8, display: 'block' }}>Edge Types:</Text>
            <Space wrap>
              {edgeTypes.map(type => (
                <Space key={type}>
                  <div
                    style={{
                      width: 30,
                      height: 2,
                      background: getEdgeColor(type),
                    }}
                  />
                  <Text style={{ fontSize: 12 }}>{type}</Text>
                </Space>
              ))}
            </Space>
          </Col>
        </Row>
      </Card>
    </motion.div>
  );
};

export default GraphVisualization;
