"""
Graph Visualizer Module for OpenLens

Provides graph visualization capabilities:
- Graph layout algorithms
- Node/edge styling
- Export to various formats
- Interactive visualization
- 3D visualization
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict

# Try to import networkx
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("NetworkX not available. Install with: pip install networkx")

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available. Install with: pip install matplotlib")

# Try to import pyvis
try:
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False
    print("PyVis not available. Install with: pip install pyvis")

# Try to import plotly
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly not available. Install with: pip install plotly")

# Try to import folium
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Folium not available. Install with: pip install folium")


@dataclass
class NodeStyle:
    """Style for a node in visualization."""
    color: str = '#3498db'
    size: int = 25
    shape: str = 'circle'
    label: str = ''
    title: str = ''
    font_size: int = 12
    font_color: str = '#ffffff'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'color': self.color,
            'size': self.size,
            'shape': self.shape,
            'label': self.label,
            'title': self.title,
            'font_size': self.font_size,
            'font_color': self.font_color,
        }


@dataclass
class EdgeStyle:
    """Style for an edge in visualization."""
    color: str = '#95a5a6'
    width: int = 1
    label: str = ''
    title: str = ''
    font_size: int = 10
    font_color: str = '#000000'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'color': self.color,
            'width': self.width,
            'label': self.label,
            'title': self.title,
            'font_size': self.font_size,
            'font_color': self.font_color,
        }


@dataclass
class VisualizationOptions:
    """Options for graph visualization."""
    width: int = 800
    height: int = 600
    layout: str = 'spring'  # spring, circular, random, kamada_kawai, fruchterman_reingold
    node_size_scaling: float = 1.0
    edge_width_scaling: float = 1.0
    show_labels: bool = True
    show_legend: bool = False
    background_color: str = '#ffffff'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'width': self.width,
            'height': self.height,
            'layout': self.layout,
            'node_size_scaling': self.node_size_scaling,
            'edge_width_scaling': self.edge_width_scaling,
            'show_labels': self.show_labels,
            'show_legend': self.show_legend,
            'background_color': self.background_color,
        }


@dataclass
class VisualizationResult:
    """Result of graph visualization."""
    format: str  # svg, png, html, json
    data: Any  # The visualization data
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'format': self.format,
            'nodes': self.nodes,
            'edges': self.edges,
        }


class GraphVisualizer:
    """
    Graph visualizer for OpenLens.
    
    Provides advanced visualization capabilities for graph data.
    """
    
    def __init__(self, graph_engine=None):
        """
        Initialize the graph visualizer.
        
        Args:
            graph_engine: GraphEngine instance.
        """
        self.graph_engine = graph_engine
        self._graph = None
        self._last_updated = 0
        self._cache_ttl = 300  # 5 minutes
    
    def _get_networkx_graph(self, force_refresh: bool = False) -> Optional[nx.Graph]:
        """
        Materialise the graph via the engine, which is the single
        correct implementation (business ids, hydrated edge endpoints).
        """
        if not self.graph_engine:
            return None
        graph = self.graph_engine.to_networkx(force_refresh=force_refresh)
        self._graph = graph
        self._last_updated = time.time()
        return graph
    def visualize_matplotlib(self, options: VisualizationOptions = None,
                            output_path: str = None) -> Optional[VisualizationResult]:
        """
        Visualize graph using Matplotlib.
        
        Args:
            options: VisualizationOptions.
            output_path: Path to save the visualization.
            
        Returns:
            VisualizationResult or None.
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        options = options or VisualizationOptions()
        
        try:
            plt.figure(figsize=(options.width / 100, options.height / 100))
            plt.gca().set_facecolor(options.background_color)
            
            # Get positions based on layout
            pos = self._get_layout(graph, options.layout)
            
            # Draw nodes
            node_colors = []
            node_sizes = []
            node_labels = {}
            
            for node in graph.nodes():
                labels = graph.nodes[node].get('labels', [])
                
                # Determine color based on labels
                color = self._get_color_for_labels(labels)
                node_colors.append(color)
                
                # Determine size
                size = 25 * options.node_size_scaling
                node_sizes.append(size)
                
                # Set label
                label = graph.nodes[node].get('name', node)
                node_labels[node] = label if options.show_labels else ''
            
            nx.draw_networkx_nodes(
                graph, pos,
                node_color=node_colors,
                node_size=node_sizes,
                alpha=0.9
            )
            
            # Draw edges
            edge_colors = []
            edge_widths = []
            
            for u, v in graph.edges():
                edge_type = graph.edges[u, v].get('type', '')
                color = self._get_color_for_edge_type(edge_type)
                edge_colors.append(color)
                edge_widths.append(1 * options.edge_width_scaling)
            
            nx.draw_networkx_edges(
                graph, pos,
                edge_color=edge_colors,
                width=edge_widths,
                alpha=0.5
            )
            
            # Draw labels
            if options.show_labels:
                nx.draw_networkx_labels(
                    graph, pos,
                    labels=node_labels,
                    font_size=options.font_size if hasattr(options, 'font_size') else 10,
                    font_color=options.font_color if hasattr(options, 'font_color') else '#000000'
                )
            
            # Draw edge labels
            edge_labels = {}
            for u, v in graph.edges():
                edge_type = graph.edges[u, v].get('type', '')
                if edge_type:
                    edge_labels[(u, v)] = edge_type
            
            nx.draw_networkx_edge_labels(
                graph, pos,
                edge_labels=edge_labels,
                font_size=8,
                alpha=0.7
            )
            
            plt.axis('off')
            plt.tight_layout()
            
            if output_path:
                plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
            
            # Return as base64 encoded image
            import io
            import base64
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_data = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return VisualizationResult(
                format='png',
                data=f'data:image/png;base64,{image_data}',
                nodes=list(graph.nodes()),
                edges=list(graph.edges()),
            )
        
        except Exception as e:
            print(f"Matplotlib visualization error: {e}")
            return None
    
    def visualize_pyvis(self, options: VisualizationOptions = None,
                       output_path: str = None) -> Optional[VisualizationResult]:
        """
        Visualize graph using PyVis (interactive HTML).
        
        Args:
            options: VisualizationOptions.
            output_path: Path to save the HTML file.
            
        Returns:
            VisualizationResult or None.
        """
        if not PYVIS_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        options = options or VisualizationOptions()
        
        try:
            net = Network(
                width=f"{options.width}px",
                height=f"{options.height}px",
                bgcolor=options.background_color,
                font_color='#333333',
                directed=False,
                notebook=False
            )
            
            # Configure physics
            net.set_options("""
            {
                "physics": {
                    "enabled": true,
                    "barnesHut": {
                        "gravitationalConstant": -80000,
                        "centralGravity": 0.3,
                        "springLength": 200,
                        "springConstant": 0.04,
                        "damping": 0.09,
                        "avoidOverlap": 0.1
                    },
                    "minVelocity": 0.75
                }
            }
            """)
            
            # Add nodes
            for node in graph.nodes():
                node_data = graph.nodes[node]
                labels = node_data.get('labels', [])
                
                color = self._get_color_for_labels(labels)
                size = 25 * options.node_size_scaling
                
                title = f"<b>{node}</b><br>"
                for key, value in node_data.items():
                    if key != 'labels':
                        title += f"{key}: {value}<br>"
                
                net.add_node(
                    node,
                    label=str(node),
                    color=color,
                    size=size,
                    title=title,
                    shape='circle'
                )
            
            # Add edges
            for u, v in graph.edges():
                edge_data = graph.edges[u, v]
                edge_type = edge_data.get('type', '')
                
                color = self._get_color_for_edge_type(edge_type)
                width = 1 * options.edge_width_scaling
                
                title = f"Type: {edge_type}<br>"
                for key, value in edge_data.items():
                    if key != 'type':
                        title += f"{key}: {value}<br>"
                
                net.add_edge(
                    u, v,
                    color=color,
                    width=width,
                    title=title,
                    label=edge_type if edge_type else ''
                )
            
            # Save to file or return HTML
            if output_path:
                net.save_graph(output_path)
            
            html = net.generate_html()
            
            return VisualizationResult(
                format='html',
                data=html,
                nodes=list(graph.nodes()),
                edges=list(graph.edges()),
            )
        
        except Exception as e:
            print(f"PyVis visualization error: {e}")
            return None
    
    def visualize_plotly(self, options: VisualizationOptions = None) -> Optional[VisualizationResult]:
        """
        Visualize graph using Plotly (3D).
        
        Args:
            options: VisualizationOptions.
            
        Returns:
            VisualizationResult or None.
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        options = options or VisualizationOptions()
        
        try:
            # Get 3D positions
            pos = nx.spring_layout(graph, dim=3, seed=42)
            
            # Prepare data for Plotly
            node_x = []
            node_y = []
            node_z = []
            node_text = []
            node_colors = []
            node_sizes = []
            
            for node in graph.nodes():
                x, y, z = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_z.append(z)
                
                labels = graph.nodes[node].get('labels', [])
                color = self._get_color_for_labels(labels)
                node_colors.append(color)
                node_sizes.append(25 * options.node_size_scaling)
                
                label = graph.nodes[node].get('name', node)
                node_text.append(label)
            
            # Edge data
            edge_x = []
            edge_y = []
            edge_z = []
            
            for u, v in graph.edges():
                x0, y0, z0 = pos[u]
                x1, y1, z1 = pos[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_z.extend([z0, z1, None])
            
            # Create figure
            fig = go.Figure()
            
            # Add edges
            fig.add_trace(go.Scatter3d(
                x=edge_x,
                y=edge_y,
                z=edge_z,
                mode='lines',
                line=dict(
                    color='#95a5a6',
                    width=1 * options.edge_width_scaling
                ),
                hoverinfo='none',
                showlegend=False
            ))
            
            # Add nodes
            fig.add_trace(go.Scatter3d(
                x=node_x,
                y=node_y,
                z=node_z,
                mode='markers+text' if options.show_labels else 'markers',
                marker=dict(
                    color=node_colors,
                    size=node_sizes,
                    line=dict(width=0.5, color='DarkSlateGrey')
                ),
                text=node_text if options.show_labels else [],
                textposition="top center",
                textfont=dict(size=10),
                hovertext=node_text,
                hoverinfo='text',
                showlegend=False
            ))
            
            fig.update_layout(
                width=options.width,
                height=options.height,
                margin=dict(l=0, r=0, b=0, t=0),
                paper_bgcolor=options.background_color,
                scene=dict(
                    xaxis=dict(showbackground=False, showticklabels=False, title=''),
                    yaxis=dict(showbackground=False, showticklabels=False, title=''),
                    zaxis=dict(showbackground=False, showticklabels=False, title=''),
                    bgcolor=options.background_color
                )
            )
            
            # Return as JSON
            graph_json = json.loads(fig.to_json())
            
            return VisualizationResult(
                format='plotly_json',
                data=graph_json,
                nodes=list(graph.nodes()),
                edges=list(graph.edges()),
            )
        
        except Exception as e:
            print(f"Plotly visualization error: {e}")
            return None
    
    def visualize_geospatial(self, latitude_property: str = 'latitude',
                            longitude_property: str = 'longitude',
                            output_path: str = None) -> Optional[VisualizationResult]:
        """
        Visualize geospatial graph using Folium.
        
        Args:
            latitude_property: Property name for latitude.
            longitude_property: Property name for longitude.
            output_path: Path to save the HTML file.
            
        Returns:
            VisualizationResult or None.
        """
        if not FOLIUM_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        try:
            # Create map centered on average position
            lats = []
            lons = []
            
            for node in graph.nodes():
                node_data = graph.nodes[node]
                lat = node_data.get(latitude_property)
                lon = node_data.get(longitude_property)
                
                if lat is not None and lon is not None:
                    lats.append(float(lat))
                    lons.append(float(lon))
            
            if not lats or not lons:
                return None
            
            avg_lat = sum(lats) / len(lats)
            avg_lon = sum(lons) / len(lons)
            
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
            
            # Add nodes as markers
            for node in graph.nodes():
                node_data = graph.nodes[node]
                lat = node_data.get(latitude_property)
                lon = node_data.get(longitude_property)
                
                if lat is not None and lon is not None:
                    labels = node_data.get('labels', [])
                    color = self._get_color_for_labels(labels)
                    
                    # Convert hex color to RGB
                    if color.startswith('#'):
                        color = color[1:]
                        if len(color) == 6:
                            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
                            color = f'rgb({r}, {g}, {b})'
                    
                    label = node_data.get('name', node)
                    
                    folium.CircleMarker(
                        location=[float(lat), float(lon)],
                        radius=10,
                        color=color,
                        fill=True,
                        fill_color=color,
                        popup=label
                    ).add_to(m)
            
            # Add edges as lines
            for u, v in graph.edges():
                u_data = graph.nodes[u]
                v_data = graph.nodes[v]
                
                u_lat = u_data.get(latitude_property)
                u_lon = u_data.get(longitude_property)
                v_lat = v_data.get(latitude_property)
                v_lon = v_data.get(longitude_property)
                
                if u_lat is not None and u_lon is not None and v_lat is not None and v_lon is not None:
                    folium.PolyLine(
                        locations=[[float(u_lat), float(u_lon)], [float(v_lat), float(v_lon)]],
                        color='#95a5a6',
                        weight=1,
                        opacity=0.5
                    ).add_to(m)
            
            if output_path:
                m.save(output_path)
            
            html = m._repr_html_()
            
            return VisualizationResult(
                format='folium_html',
                data=html,
                nodes=list(graph.nodes()),
                edges=list(graph.edges()),
            )
        
        except Exception as e:
            print(f"Geospatial visualization error: {e}")
            return None
    
    def _get_layout(self, graph: nx.Graph, layout: str) -> Dict:
        """Get node positions based on layout algorithm."""
        if layout == 'spring':
            return nx.spring_layout(graph, k=0.15, iterations=50)
        elif layout == 'circular':
            return nx.circular_layout(graph)
        elif layout == 'random':
            return nx.random_layout(graph)
        elif layout == 'kamada_kawai':
            return nx.kamada_kawai_layout(graph)
        elif layout == 'fruchterman_reingold':
            return nx.fruchterman_reingold_layout(graph)
        elif layout == 'spectral':
            return nx.spectral_layout(graph)
        elif layout == 'shell':
            return nx.shell_layout(graph)
        else:
            return nx.spring_layout(graph)
    
    def _get_color_for_labels(self, labels: List[str]) -> str:
        """Get color based on node labels."""
        label_colors = {
            'Person': '#e74c3c',
            'Organization': '#3498db',
            'Location': '#2ecc71',
            'Event': '#f39c12',
            'Document': '#9b59b6',
            'Vehicle': '#1abc9c',
            'Device': '#e67e22',
            'Account': '#34495e',
            'IPAddress': '#16a085',
            'Domain': '#27ae60',
        }
        
        for label in labels:
            if label in label_colors:
                return label_colors[label]
        
        return '#95a5a6'  # Default gray
    
    def _get_color_for_edge_type(self, edge_type: str) -> str:
        """Get color based on edge type."""
        edge_colors = {
            'KNOWS': '#3498db',
            'WORKS_FOR': '#e74c3c',
            'OWNED_BY': '#2ecc71',
            'LOCATED_AT': '#f39c12',
            'PARTICIPATED_IN': '#9b59b6',
            'COMMUNICATED_WITH': '#1abc9c',
            'TRANSACTION': '#e67e22',
            'MEMBER_OF': '#34495e',
            'CONNECTED_TO': '#16a085',
        }
        
        if edge_type in edge_colors:
            return edge_colors[edge_type]
        
        return '#95a5a6'  # Default gray
    
    def get_graph_json(self) -> Dict[str, Any]:
        """
        Get graph data as JSON for frontend visualization.
        
        Returns:
            Dictionary with nodes and edges.
        """
        graph = self._get_networkx_graph()
        if not graph:
            return {'nodes': [], 'edges': []}
        
        nodes = []
        for node in graph.nodes():
            node_data = graph.nodes[node]
            labels = node_data.get('labels', [])
            
            nodes.append({
                'id': str(node),
                'labels': labels,
                'properties': {k: v for k, v in node_data.items() if k != 'labels'},
                'color': self._get_color_for_labels(labels),
                'size': 25,
            })
        
        edges = []
        for u, v in graph.edges():
            edge_data = graph.edges[u, v]
            edge_type = edge_data.get('type', '')
            
            edges.append({
                'source': str(u),
                'target': str(v),
                'type': edge_type,
                'properties': {k: v for k, v in edge_data.items() if k != 'type'},
                'color': self._get_color_for_edge_type(edge_type),
                'width': 1,
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
        }


# Global graph visualizer instance
graph_visualizer = GraphVisualizer()
