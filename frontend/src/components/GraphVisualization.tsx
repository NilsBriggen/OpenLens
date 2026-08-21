import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface Node {
  id: string;
  name: string;
  type: 'user' | 'post' | 'hashtag' | 'location';
  group?: number;
}

interface Link {
  source: string;
  target: string;
  type: 'POSTED_BY' | 'MENTIONS' | 'TAGGED_WITH' | 'LOCATED_AT';
  value?: number;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

const GraphVisualization: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState<GraphData>({
    nodes: [],
    links: [],
  });
  const [width, setWidth] = useState<number>(800);
  const [height, setHeight] = useState<number>(600);

  // Sample data for demonstration
  const sampleData: GraphData = {
    nodes: [
      { id: 'user1', name: 'Alice', type: 'user', group: 1 },
      { id: 'user2', name: 'Bob', type: 'user', group: 1 },
      { id: 'user3', name: 'Charlie', type: 'user', group: 2 },
      { id: 'post1', name: 'Post 1', type: 'post', group: 3 },
      { id: 'post2', name: 'Post 2', type: 'post', group: 3 },
      { id: 'hashtag1', name: '#OSINT', type: 'hashtag', group: 4 },
      { id: 'loc1', name: 'San Francisco', type: 'location', group: 5 },
    ],
    links: [
      { source: 'user1', target: 'post1', type: 'POSTED_BY' },
      { source: 'user1', target: 'post2', type: 'POSTED_BY' },
      { source: 'user2', target: 'post1', type: 'MENTIONS' },
      { source: 'post1', target: 'hashtag1', type: 'TAGGED_WITH' },
      { source: 'post1', target: 'loc1', type: 'LOCATED_AT' },
      { source: 'user1', target: 'user2', type: 'FRIENDS_WITH' },
      { source: 'user3', target: 'post2', type: 'MENTIONS' },
    ],
  };

  // Load sample data
  useEffect(() => {
    setData(sampleData);
  }, []);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      const container = svgRef.current?.parentElement;
      if (container) {
        setWidth(container.clientWidth);
        setHeight(container.clientHeight || 600);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Draw the graph
  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous graph

    // Create a group for the graph
    const g = svg.append('g').attr('transform', `translate(${width / 2}, ${height / 2})`);

    // Create a force simulation
    const simulation = d3
      .forceSimulation<Node, Link>(data.nodes as Node[])
      .force(
        'link',
        d3
          .forceLink<Node, Link>(data.links as Link[])
          .id((d) => d.id)
          .distance(150)
      )
      .force('charge', d3.forceManyBody<Node>().strength(-300))
      .force('center', d3.forceCenter().x(0).y(0))
      .force('collision', d3.forceCollide<Node>().radius(30));

    // Create links
    const link = g
      .append('g')
      .selectAll('line')
      .data(data.links)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => {
        switch (d.type) {
          case 'POSTED_BY':
            return 2;
          case 'MENTIONS':
            return 1.5;
          case 'TAGGED_WITH':
            return 1;
          case 'LOCATED_AT':
            return 1.5;
          default:
            return 1;
        }
      });

    // Create nodes
    const node = g
      .append('g')
      .selectAll('g')
      .data(data.nodes)
      .enter()
      .append('g')
      .call(
        d3
          .drag<Node, any>()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended)
      );

    // Add circles for nodes
    node
      .append('circle')
      .attr('r', 15)
      .attr('fill', (d) => {
        switch (d.type) {
          case 'user':
            return '#4CAF50';
          case 'post':
            return '#2196F3';
          case 'hashtag':
            return '#FF9800';
          case 'location':
            return '#F44336';
          default:
            return '#9E9E9E';
        }
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Add labels
    node
      .append('text')
      .text((d) => d.name)
      .attr('x', 20)
      .attr('y', 5)
      .attr('font-size', '12px')
      .attr('fill', '#333');

    // Update positions on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as any).x)
        .attr('y1', (d) => (d.source as any).y)
        .attr('x2', (d) => (d.target as any).x)
        .attr('y2', (d) => (d.target as any).y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event: any, d: Node) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragged(event: any, d: Node) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: Node) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Clean up on unmount
    return () => {
      simulation.stop();
    };
  }, [data, width, height]);

  // Add zoom functionality
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        svg.select('g').attr('transform', event.transform);
      });

    svg.call(zoom);
  }, []);

  return (
    <div className="graph-visualization">
      <h2>📊 Graph Visualization</h2>
      <p>
        Visualize connections between users, posts, hashtags, and locations.
        Drag nodes to rearrange the graph, and zoom in/out to explore.
      </p>

      <div className="graph-controls">
        <button onClick={() => setData(sampleData)}>Load Sample Data</button>
        <button onClick={() => setData({ nodes: [], links: [] })}>Clear Graph</button>
      </div>

      <div className="legend">
        <h4>Legend:</h4>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#4CAF50' }}></span>
          <span>User</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#2196F3' }}></span>
          <span>Post</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#FF9800' }}></span>
          <span>Hashtag</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#F44336' }}></span>
          <span>Location</span>
        </div>
      </div>

      <div className="graph-container" style={{ width: '100%', height: '600px' }}>
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          viewBox={`0 0 ${width} ${height}`}
          preserveAspectRatio="xMidYMid meet"
        />
      </div>

      <div className="graph-info">
        <p>
          <strong>Nodes:</strong> {data.nodes.length} | <strong>Links:</strong> {data.links.length}
        </p>
      </div>
    </div>
  );
};

export default GraphVisualization;
