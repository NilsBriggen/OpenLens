"""
Visualization Generator for OpenLens

Generates various visualizations:
- Charts (line, bar, pie, doughnut)
- Maps (heatmaps, marker maps)
- Graphs (network graphs)
- Tables
- Export to various formats
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import base64
import io
import hashlib

# Try to import visualization libraries
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available. Install with: pip install matplotlib")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly not available. Install with: pip install plotly")

try:
    import folium
    from folium.plugins import HeatMap, MarkerCluster
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Folium not available. Install with: pip install folium")

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("NetworkX not available. Install with: pip install networkx")


@dataclass
class ChartConfig:
    """Configuration for a chart."""
    chart_type: str  # 'line', 'bar', 'pie', 'doughnut', 'scatter', 'heatmap'
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    width: int = 800
    height: int = 600
    colors: List[str] = field(default_factory=list)
    show_legend: bool = True
    legend_position: str = "best"
    grid: bool = True
    x_axis_type: str = "linear"  # 'linear', 'log', 'date'
    y_axis_type: str = "linear"
    stack: bool = False  # For bar charts
    horizontal: bool = False  # For bar charts


@dataclass
class MapConfig:
    """Configuration for a map."""
    map_type: str  # 'heatmap', 'markers', 'choropleth'
    title: str = ""
    latitude_field: str = "latitude"
    longitude_field: str = "longitude"
    value_field: str = "value"
    zoom: int = 12
    center: Tuple[float, float] = (0, 0)
    tiles: str = "OpenStreetMap"  # 'OpenStreetMap', 'Stamen Terrain', etc.
    radius: int = 15  # For heatmap
    blur: int = 15  # For heatmap
    max_zoom: int = 18
    min_zoom: int = 2


@dataclass
class GraphConfig:
    """Configuration for a graph."""
    graph_type: str  # 'network', 'tree', 'directed', 'undirected'
    title: str = ""
    node_size: int = 10
    node_color: str = "#3B82F6"
    edge_color: str = "#9CA3AF"
    edge_width: float = 1.0
    layout: str = "spring"  # 'spring', 'circular', 'random', 'kamada_kawai'
    width: int = 800
    height: int = 600
    show_labels: bool = True
    show_arrows: bool = False  # For directed graphs


class VisualizationGenerator:
    """
    Generates various visualizations from data.
    """
    
    def __init__(self):
        """Initialize the visualization generator."""
        self.cache: Dict[str, Any] = {}
    
    def generate_chart(self, data: Dict[str, Any], config: ChartConfig = None) -> Dict[str, Any]:
        """
        Generate a chart from data.
        
        Args:
            data: Data for the chart.
            config: Chart configuration.
            
        Returns:
            Dictionary with chart data and image.
        """
        config = config or ChartConfig(chart_type='line')
        
        if not MATPLOTLIB_AVAILABLE:
            return {'error': 'Matplotlib not available'}
        
        try:
            fig, ax = plt.subplots(figsize=(config.width / 100, config.height / 100))
            
            if config.chart_type == 'line':
                self._generate_line_chart(ax, data, config)
            elif config.chart_type == 'bar':
                self._generate_bar_chart(ax, data, config)
            elif config.chart_type == 'pie':
                self._generate_pie_chart(ax, data, config)
            elif config.chart_type == 'doughnut':
                self._generate_doughnut_chart(ax, data, config)
            elif config.chart_type == 'scatter':
                self._generate_scatter_chart(ax, data, config)
            else:
                return {'error': f'Chart type {config.chart_type} not supported'}
            
            # Set title and labels
            if config.title:
                ax.set_title(config.title)
            if config.x_label:
                ax.set_xlabel(config.x_label)
            if config.y_label:
                ax.set_ylabel(config.y_label)
            
            # Set grid
            ax.grid(config.grid)
            
            # Convert to image
            image_data = self._fig_to_image(fig)
            
            plt.close(fig)
            
            return {
                'type': 'chart',
                'chart_type': config.chart_type,
                'image': image_data,
                'config': {
                    'title': config.title,
                    'x_label': config.x_label,
                    'y_label': config.y_label,
                },
            }
        
        except Exception as e:
            return {'error': f'Failed to generate chart: {str(e)}'}
    
    def _generate_line_chart(self, ax, data: Dict[str, Any], config: ChartConfig):
        """Generate a line chart."""
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        for dataset in datasets:
            values = dataset.get('data', [])
            label = dataset.get('label', '')
            color = dataset.get('borderColor', '#3B82F6')
            
            ax.plot(labels, values, label=label, color=color, linewidth=2)
        
        if config.show_legend and len(datasets) > 1:
            ax.legend(loc=config.legend_position)
    
    def _generate_bar_chart(self, ax, data: Dict[str, Any], config: ChartConfig):
        """Generate a bar chart."""
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        if len(datasets) == 1:
            # Single dataset
            values = datasets[0].get('data', [])
            color = datasets[0].get('backgroundColor', '#3B82F6')
            
            if config.horizontal:
                ax.barh(labels, values, color=color)
            else:
                ax.bar(labels, values, color=color)
        else:
            # Multiple datasets
            width = 0.8 / len(datasets)
            for i, dataset in enumerate(datasets):
                values = dataset.get('data', [])
                label = dataset.get('label', '')
                color = dataset.get('backgroundColor', '#3B82F6')
                offset = (i - len(datasets) / 2 + 0.5) * width
                
                if config.horizontal:
                    ax.barh([x + offset for x in range(len(labels))], values, 
                           width=width, label=label, color=color)
                else:
                    ax.bar([x + offset for x in range(len(labels))], values, 
                          width=width, label=label, color=color)
        
        if config.show_legend and len(datasets) > 1:
            ax.legend(loc=config.legend_position)
    
    def _generate_pie_chart(self, ax, data: Dict[str, Any], config: ChartConfig):
        """Generate a pie chart."""
        labels = data.get('labels', [])
        values = data.get('data', [])
        colors = data.get('backgroundColor', config.colors or ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'])
        
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
        
        if config.show_legend:
            ax.legend(loc=config.legend_position)
    
    def _generate_doughnut_chart(self, ax, data: Dict[str, Any], config: ChartConfig):
        """Generate a doughnut chart."""
        labels = data.get('labels', [])
        values = data.get('data', [])
        colors = data.get('backgroundColor', config.colors or ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'])
        
        # Create a pie chart with a hole
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
        circle = plt.Circle((0, 0), 0.3, color='white')
        ax.add_artist(circle)
        
        if config.show_legend:
            ax.legend(loc=config.legend_position)
        
        ax.set_aspect('equal')
    
    def _generate_scatter_chart(self, ax, data: Dict[str, Any], config: ChartConfig):
        """Generate a scatter chart."""
        datasets = data.get('datasets', [])
        
        for dataset in datasets:
            x_values = dataset.get('x', [])
            y_values = dataset.get('y', [])
            label = dataset.get('label', '')
            color = dataset.get('borderColor', '#3B82F6')
            
            ax.scatter(x_values, y_values, label=label, color=color, alpha=0.6)
        
        if config.show_legend and len(datasets) > 1:
            ax.legend(loc=config.legend_position)
    
    def generate_map(self, data: Dict[str, Any], config: MapConfig = None) -> Dict[str, Any]:
        """
        Generate a map visualization.
        
        Args:
            data: Data for the map.
            config: Map configuration.
            
        Returns:
            Dictionary with map data and HTML.
        """
        config = config or MapConfig(map_type='markers')
        
        if not FOLIUM_AVAILABLE:
            return {'error': 'Folium not available'}
        
        try:
            if config.map_type == 'heatmap':
                return self._generate_heatmap(data, config)
            elif config.map_type == 'markers':
                return self._generate_marker_map(data, config)
            else:
                return {'error': f'Map type {config.map_type} not supported'}
        
        except Exception as e:
            return {'error': f'Failed to generate map: {str(e)}'}
    
    def _generate_heatmap(self, data: Dict[str, Any], config: MapConfig) -> Dict[str, Any]:
        """Generate a heatmap."""
        locations = data.get('locations', [])
        
        # Create map centered on the first location or config center
        if locations and config.center == (0, 0):
            first_loc = locations[0]
            config.center = (first_loc[0], first_loc[1])
        
        m = folium.Map(location=config.center, zoom_start=config.zoom, 
                      tiles=config.tiles, min_zoom=config.min_zoom, max_zoom=config.max_zoom)
        
        # Add heatmap
        HeatMap(locations, radius=config.radius, blur=config.blur).add_to(m)
        
        # Save to HTML
        html = m._repr_html_()
        
        return {
            'type': 'map',
            'map_type': 'heatmap',
            'html': html,
            'center': config.center,
            'zoom': config.zoom,
        }
    
    def _generate_marker_map(self, data: Dict[str, Any], config: MapConfig) -> Dict[str, Any]:
        """Generate a marker map."""
        markers = data.get('markers', [])
        
        # Create map
        if markers and config.center == (0, 0):
            first_marker = markers[0]
            config.center = (first_marker.get('lat', 0), first_marker.get('lon', 0))
        
        m = folium.Map(location=config.center, zoom_start=config.zoom, 
                      tiles=config.tiles, min_zoom=config.min_zoom, max_zoom=config.max_zoom)
        
        # Add markers
        for marker in markers:
            lat = marker.get('lat', 0)
            lon = marker.get('lon', 0)
            popup = marker.get('popup', '')
            color = marker.get('color', 'blue')
            icon = marker.get('icon', 'info-sign')
            
            folium.Marker(
                location=[lat, lon],
                popup=popup,
                icon=folium.Icon(color=color, icon=icon, prefix='fa'),
            ).add_to(m)
        
        # Add marker cluster if many markers
        if len(markers) > 50:
            marker_cluster = MarkerCluster().add_to(m)
            for marker in markers:
                lat = marker.get('lat', 0)
                lon = marker.get('lon', 0)
                popup = marker.get('popup', '')
                
                folium.Marker(
                    location=[lat, lon],
                    popup=popup,
                ).add_to(marker_cluster)
        
        # Save to HTML
        html = m._repr_html_()
        
        return {
            'type': 'map',
            'map_type': 'markers',
            'html': html,
            'center': config.center,
            'zoom': config.zoom,
            'marker_count': len(markers),
        }
    
    def generate_graph(self, data: Dict[str, Any], config: GraphConfig = None) -> Dict[str, Any]:
        """
        Generate a graph visualization.
        
        Args:
            data: Data for the graph.
            config: Graph configuration.
            
        Returns:
            Dictionary with graph data and image.
        """
        config = config or GraphConfig(graph_type='network')
        
        if not NETWORKX_AVAILABLE:
            return {'error': 'NetworkX not available'}
        
        if not MATPLOTLIB_AVAILABLE:
            return {'error': 'Matplotlib not available'}
        
        try:
            if config.graph_type == 'network':
                return self._generate_network_graph(data, config)
            else:
                return {'error': f'Graph type {config.graph_type} not supported'}
        
        except Exception as e:
            return {'error': f'Failed to generate graph: {str(e)}'}
    
    def _generate_network_graph(self, data: Dict[str, Any], config: GraphConfig) -> Dict[str, Any]:
        """Generate a network graph."""
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        # Create graph
        if config.graph_type == 'directed':
            G = nx.DiGraph()
        else:
            G = nx.Graph()
        
        # Add nodes
        for node in nodes:
            node_id = node.get('id', '')
            label = node.get('label', node_id)
            size = node.get('size', config.node_size)
            color = node.get('color', config.node_color)
            
            G.add_node(node_id, label=label, size=size, color=color)
        
        # Add edges
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            weight = edge.get('weight', config.edge_width)
            color = edge.get('color', config.edge_color)
            
            G.add_edge(source, target, weight=weight, color=color)
        
        # Set layout
        if config.layout == 'spring':
            pos = nx.spring_layout(G, k=0.15, iterations=50)
        elif config.layout == 'circular':
            pos = nx.circular_layout(G)
        elif config.layout == 'random':
            pos = nx.random_layout(G)
        elif config.layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        # Draw graph
        fig, ax = plt.subplots(figsize=(config.width / 100, config.height / 100))
        
        # Get node colors and sizes
        node_colors = [G.nodes[n].get('color', config.node_color) for n in G.nodes()]
        node_sizes = [G.nodes[n].get('size', config.node_size) * 10 for n in G.nodes()]
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, 
                               node_size=node_sizes, alpha=0.8)
        
        # Draw edges
        edge_colors = [G.edges[e].get('color', config.edge_color) for e in G.edges()]
        edge_widths = [G.edges[e].get('weight', config.edge_width) for e in G.edges()]
        
        if config.graph_type == 'directed' and config.show_arrows:
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, 
                                   width=edge_widths, arrows=True, arrowsize=15)
        else:
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, 
                                   width=edge_widths)
        
        # Draw labels
        if config.show_labels:
            labels = {n: G.nodes[n].get('label', n) for n in G.nodes()}
            nx.draw_networkx_labels(G, pos, ax=ax, labels=labels, font_size=8)
        
        # Set title
        if config.title:
            ax.set_title(config.title)
        
        ax.axis('off')
        
        # Convert to image
        image_data = self._fig_to_image(fig)
        
        plt.close(fig)
        
        return {
            'type': 'graph',
            'graph_type': config.graph_type,
            'image': image_data,
            'node_count': len(nodes),
            'edge_count': len(edges),
        }
    
    def generate_table(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a table visualization.
        
        Args:
            data: Data for the table.
            
        Returns:
            Dictionary with table data.
        """
        columns = data.get('columns', [])
        rows = data.get('rows', [])
        title = data.get('title', '')
        
        return {
            'type': 'table',
            'title': title,
            'columns': columns,
            'rows': rows,
            'row_count': len(rows),
        }
    
    def _fig_to_image(self, fig) -> str:
        """
        Convert a matplotlib figure to a base64-encoded image.
        
        Args:
            fig: Matplotlib figure.
            
        Returns:
            Base64-encoded image string.
        """
        # Save figure to bytes
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Encode to base64
        image_data = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        
        return f"data:image/png;base64,{image_data}"
    
    def generate_plotly_chart(self, data: Dict[str, Any], config: ChartConfig = None) -> Dict[str, Any]:
        """
        Generate a Plotly chart.
        
        Args:
            data: Data for the chart.
            config: Chart configuration.
            
        Returns:
            Dictionary with Plotly figure data.
        """
        if not PLOTLY_AVAILABLE:
            return {'error': 'Plotly not available'}
        
        try:
            config = config or ChartConfig(chart_type='line')
            
            if config.chart_type == 'line':
                fig = self._generate_plotly_line_chart(data, config)
            elif config.chart_type == 'bar':
                fig = self._generate_plotly_bar_chart(data, config)
            elif config.chart_type == 'pie':
                fig = self._generate_plotly_pie_chart(data, config)
            else:
                return {'error': f'Chart type {config.chart_type} not supported'}
            
            # Convert to JSON
            fig_json = fig.to_json()
            
            return {
                'type': 'plotly_chart',
                'chart_type': config.chart_type,
                'figure': fig_json,
            }
        
        except Exception as e:
            return {'error': f'Failed to generate Plotly chart: {str(e)}'}
    
    def _generate_plotly_line_chart(self, data: Dict[str, Any], config: ChartConfig):
        """Generate a Plotly line chart."""
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        fig = go.Figure()
        
        for dataset in datasets:
            values = dataset.get('data', [])
            label = dataset.get('label', '')
            color = dataset.get('borderColor', '#3B82F6')
            
            fig.add_trace(go.Scatter(
                x=labels,
                y=values,
                name=label,
                mode='lines+markers',
                line=dict(color=color, width=2),
                marker=dict(size=6),
            ))
        
        fig.update_layout(
            title=config.title,
            xaxis_title=config.x_label,
            yaxis_title=config.y_label,
            showlegend=config.show_legend,
            hovermode='x unified',
        )
        
        return fig
    
    def _generate_plotly_bar_chart(self, data: Dict[str, Any], config: ChartConfig):
        """Generate a Plotly bar chart."""
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        fig = go.Figure()
        
        if len(datasets) == 1:
            values = datasets[0].get('data', [])
            color = datasets[0].get('backgroundColor', '#3B82F6')
            label = datasets[0].get('label', '')
            
            if config.horizontal:
                fig.add_trace(go.Bar(
                    y=labels,
                    x=values,
                    name=label,
                    marker_color=color,
                ))
            else:
                fig.add_trace(go.Bar(
                    x=labels,
                    y=values,
                    name=label,
                    marker_color=color,
                ))
        else:
            # Grouped bar chart
            for dataset in datasets:
                values = dataset.get('data', [])
                label = dataset.get('label', '')
                color = dataset.get('backgroundColor', '#3B82F6')
                
                if config.horizontal:
                    fig.add_trace(go.Bar(
                        y=labels,
                        x=values,
                        name=label,
                        marker_color=color,
                    ))
                else:
                    fig.add_trace(go.Bar(
                        x=labels,
                        y=values,
                        name=label,
                        marker_color=color,
                    ))
        
        fig.update_layout(
            title=config.title,
            xaxis_title=config.x_label,
            yaxis_title=config.y_label,
            showlegend=config.show_legend,
            barmode='group' if len(datasets) > 1 else 'relative',
        )
        
        return fig
    
    def _generate_plotly_pie_chart(self, data: Dict[str, Any], config: ChartConfig):
        """Generate a Plotly pie chart."""
        labels = data.get('labels', [])
        values = data.get('data', [])
        colors = data.get('backgroundColor', ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'])
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.3 if config.chart_type == 'doughnut' else 0,
        )])
        
        fig.update_layout(
            title=config.title,
            showlegend=config.show_legend,
        )
        
        return fig
    
    def export_visualization(self, visualization: Dict[str, Any], format: str = 'png', 
                           filename: str = None) -> Dict[str, Any]:
        """
        Export a visualization to a file.
        
        Args:
            visualization: Visualization data.
            format: Export format ('png', 'jpg', 'svg', 'pdf', 'html').
            filename: Optional filename.
            
        Returns:
            Dictionary with export data.
        """
        if not filename:
            filename = f"visualization_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        if visualization.get('type') == 'chart' and MATPLOTLIB_AVAILABLE:
            return self._export_chart(visualization, format, filename)
        elif visualization.get('type') == 'map' and FOLIUM_AVAILABLE:
            return self._export_map(visualization, format, filename)
        elif visualization.get('type') == 'graph' and MATPLOTLIB_AVAILABLE:
            return self._export_graph(visualization, format, filename)
        else:
            return {'error': f'Cannot export visualization of type {visualization.get("type")}'}
    
    def _export_chart(self, visualization: Dict[str, Any], format: str, filename: str) -> Dict[str, Any]:
        """Export a chart visualization."""
        # Recreate the chart from the data
        data = visualization.get('data', {})
        config = ChartConfig(
            chart_type=visualization.get('chart_type', 'line'),
            title=visualization.get('config', {}).get('title', ''),
            x_label=visualization.get('config', {}).get('x_label', ''),
            y_label=visualization.get('config', {}).get('y_label', ''),
        )
        
        result = self.generate_chart(data, config)
        
        if 'error' in result:
            return result
        
        # Save to file
        image_data = result.get('image', '')
        if image_data.startswith('data:image/png;base64,'):
            image_data = image_data[21:]  # Remove the prefix
        
        # Decode and save
        import base64
        image_bytes = base64.b64decode(image_data)
        
        file_ext = 'png' if format == 'png' else format
        filepath = f"/tmp/{filename}.{file_ext}"
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        return {
            'filepath': filepath,
            'format': format,
            'size': len(image_bytes),
        }
    
    def _export_map(self, visualization: Dict[str, Any], format: str, filename: str) -> Dict[str, Any]:
        """Export a map visualization."""
        if format != 'html':
            return {'error': 'Maps can only be exported as HTML'}
        
        html = visualization.get('html', '')
        filepath = f"/tmp/{filename}.html"
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        return {
            'filepath': filepath,
            'format': 'html',
            'size': len(html.encode()),
        }
    
    def _export_graph(self, visualization: Dict[str, Any], format: str, filename: str) -> Dict[str, Any]:
        """Export a graph visualization."""
        # Similar to chart export
        return self._export_chart(visualization, format, filename)


# Global visualization generator instance
visualization_generator = VisualizationGenerator()
