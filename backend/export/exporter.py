"""
Data Exporter for OpenLens

Provides functionality to export data in various formats:
- CSV (for tabular data)
- JSON (for structured data)
- PDF (for reports)

Dependencies:
- pandas: For CSV export
- json: For JSON export
- reportlab: For PDF export (optional)
- weasyprint: For HTML to PDF conversion (optional)
"""

import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from io import StringIO, BytesIO
import tempfile

# Try to import optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class DataExporter:
    """
    Exports data in various formats.
    """
    
    def __init__(self):
        """Initialize the data exporter."""
        pass
    
    # --- CSV Export ---
    
    def export_to_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str = None,
        columns: List[str] = None,
        include_header: bool = True,
    ) -> Union[str, bytes]:
        """
        Export data to CSV format.
        
        Args:
            data: List of dictionaries to export.
            filename: Optional filename (without extension).
            columns: Optional list of columns to include.
            include_header: Whether to include header row.
            
        Returns:
            CSV string or bytes if filename is provided.
        """
        if not data:
            return ""
        
        # Determine columns
        if columns is None:
            columns = list(data[0].keys()) if data else []
        
        # Create output
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction='ignore')
        
        if include_header:
            writer.writeheader()
        
        for row in data:
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        # Save to file if filename provided
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)
            return f"CSV file saved to {filename}".encode()
        
        return csv_content
    
    def export_posts_to_csv(
        self,
        posts: List[Dict[str, Any]],
        filename: str = None,
    ) -> Union[str, bytes]:
        """
        Export posts to CSV format.
        
        Args:
            posts: List of post dictionaries.
            filename: Optional filename (without extension).
            
        Returns:
            CSV string or bytes if filename is provided.
        """
        columns = [
            'id',
            'platform',
            'content',
            'author_name',
            'author_username',
            'timestamp',
            'likes',
            'reposts',
            'views',
            'comments',
            'url',
        ]
        
        return self.export_to_csv(posts, filename, columns)
    
    def export_users_to_csv(
        self,
        users: List[Dict[str, Any]],
        filename: str = None,
    ) -> Union[str, bytes]:
        """
        Export users to CSV format.
        
        Args:
            users: List of user dictionaries.
            filename: Optional filename (without extension).
            
        Returns:
            CSV string or bytes if filename is provided.
        """
        columns = [
            'id',
            'username',
            'email',
            'full_name',
            'role',
            'is_active',
            'is_verified',
            'created_at',
            'last_login',
        ]
        
        return self.export_to_csv(users, filename, columns)
    
    # --- JSON Export ---
    
    def export_to_json(
        self,
        data: Any,
        filename: str = None,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> Union[str, bytes]:
        """
        Export data to JSON format.
        
        Args:
            data: Data to export (list, dict, etc.).
            filename: Optional filename (without extension).
            indent: JSON indentation level.
            ensure_ascii: Whether to escape non-ASCII characters.
            
        Returns:
            JSON string or bytes if filename is provided.
        """
        json_content = json.dumps(
            data,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=str,
        )
        
        # Save to file if filename provided
        if filename:
            if not filename.endswith('.json'):
                filename += '.json'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_content)
            return f"JSON file saved to {filename}".encode()
        
        return json_content
    
    def export_posts_to_json(
        self,
        posts: List[Dict[str, Any]],
        filename: str = None,
    ) -> Union[str, bytes]:
        """
        Export posts to JSON format.
        
        Args:
            posts: List of post dictionaries.
            filename: Optional filename (without extension).
            
        Returns:
            JSON string or bytes if filename is provided.
        """
        return self.export_to_json(posts, filename)
    
    def export_report_to_json(
        self,
        report: Dict[str, Any],
        filename: str = None,
    ) -> Union[str, bytes]:
        """
        Export a report to JSON format.
        
        Args:
            report: Report dictionary.
            filename: Optional filename (without extension).
            
        Returns:
            JSON string or bytes if filename is provided.
        """
        return self.export_to_json(report, filename)
    
    # --- PDF Export ---
    
    def export_to_pdf(
        self,
        data: Any,
        filename: str = None,
        title: str = 'OpenLens Report',
        template: str = 'default',
    ) -> Union[bytes, str]:
        """
        Export data to PDF format.
        
        Args:
            data: Data to export.
            filename: Optional filename (without extension).
            title: Report title.
            template: Template to use ('default', 'simple', 'detailed').
            
        Returns:
            PDF bytes or error message.
        """
        if REPORTLAB_AVAILABLE:
            return self._export_to_pdf_reportlab(data, filename, title, template)
        elif WEASYPRINT_AVAILABLE:
            return self._export_to_pdf_weasyprint(data, filename, title, template)
        else:
            return "PDF export requires reportlab or weasyprint. Install with: pip install reportlab or pip install weasyprint"
    
    def _export_to_pdf_reportlab(
        self,
        data: Any,
        filename: str = None,
        title: str = 'OpenLens Report',
        template: str = 'default',
    ) -> bytes:
        """
        Export data to PDF using ReportLab.
        
        Args:
            data: Data to export.
            filename: Optional filename (without extension).
            title: Report title.
            template: Template to use.
            
        Returns:
            PDF bytes.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        # Create a buffer for the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Add title
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 0.25 * inch))
        
        # Add generation date
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
        story.append(Spacer(1, 0.25 * inch))
        
        # Handle different data types
        if isinstance(data, list):
            # If it's a list of posts
            if data and isinstance(data[0], dict) and 'content' in data[0]:
                self._add_posts_to_pdf(story, data, styles)
            else:
                # Generic table
                self._add_table_to_pdf(story, data, styles)
        elif isinstance(data, dict):
            # If it's a report
            self._add_report_to_pdf(story, data, styles)
        
        # Build PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Save to file if filename provided
        if filename:
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            with open(filename, 'wb') as f:
                f.write(pdf_content)
        
        return pdf_content
    
    def _add_posts_to_pdf(self, story: list, posts: List[Dict], styles):
        """Add posts to PDF story."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch
        
        story.append(Paragraph(f"Total Posts: {len(posts)}", styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))
        
        for post in posts:
            # Post header
            story.append(Paragraph(f"Post ID: {post.get('id', 'N/A')}", styles['Heading3']))
            story.append(Paragraph(f"Platform: {post.get('platform', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Author: {post.get('author_name', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Date: {post.get('timestamp', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.05 * inch))
            
            # Post content
            story.append(Paragraph(f"Content: {post.get('content', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
            
            # Metrics
            story.append(Paragraph(
                f"Likes: {post.get('likes', 0)} | Reposts: {post.get('reposts', 0)} | Views: {post.get('views', 0)} | Comments: {post.get('comments', 0)}",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.2 * inch))
    
    def _add_table_to_pdf(self, story: list, data: List[List], styles, title: str = None):
        """Add a table to PDF story."""
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        
        if title:
            story.append(Paragraph(title, styles['Heading2']))
        
        if not data:
            return
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table)
    
    def _add_report_to_pdf(self, story: list, report: Dict, styles):
        """Add a report to PDF story."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch
        
        for section, content in report.items():
            story.append(Paragraph(section, styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            story.append(Paragraph(f"{key}: {value}", styles['Normal']))
                    else:
                        story.append(Paragraph(str(item), styles['Normal']))
            elif isinstance(content, dict):
                for key, value in content.items():
                    story.append(Paragraph(f"{key}: {value}", styles['Normal']))
            else:
                story.append(Paragraph(str(content), styles['Normal']))
            
            story.append(Spacer(1, 0.1 * inch))
    
    def _export_to_pdf_weasyprint(
        self,
        data: Any,
        filename: str = None,
        title: str = 'OpenLens Report',
        template: str = 'default',
    ) -> bytes:
        """
        Export data to PDF using WeasyPrint.
        
        Args:
            data: Data to export.
            filename: Optional filename (without extension).
            title: Report title.
            template: Template to use.
            
        Returns:
            PDF bytes.
        """
        # Create HTML template
        html_content = self._create_html_template(data, title, template)
        
        # Convert to PDF
        pdf_content = HTML(string=html_content).write_pdf()
        
        # Save to file if filename provided
        if filename:
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            with open(filename, 'wb') as f:
                f.write(pdf_content)
        
        return pdf_content
    
    def _create_html_template(self, data: Any, title: str, template: str) -> str:
        """Create HTML template for PDF export."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #555; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th {{ background-color: #f2f2f2; padding: 8px; text-align: left; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                .post {{ margin-bottom: 20px; padding: 10px; border: 1px solid #eee; }}
                .metadata {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        """
        
        if isinstance(data, list):
            if data and isinstance(data[0], dict) and 'content' in data[0]:
                html += self._create_posts_html(data)
            else:
                html += self._create_table_html(data)
        elif isinstance(data, dict):
            html += self._create_report_html(data)
        
        html += "</body></html>"
        return html
    
    def _create_posts_html(self, posts: List[Dict]) -> str:
        """Create HTML for posts."""
        html = f"""
        <h2>Posts ({len(posts)})</h2>
        """
        
        for post in posts:
            html += f"""
            <div class="post">
                <h3>Post ID: {post.get('id', 'N/A')}</h3>
                <p class="metadata">
                    Platform: {post.get('platform', 'N/A')} | 
                    Author: {post.get('author_name', 'N/A')} | 
                    Date: {post.get('timestamp', 'N/A')}
                </p>
                <p>{post.get('content', 'N/A')}</p>
                <p class="metadata">
                    Likes: {post.get('likes', 0)} | 
                    Reposts: {post.get('reposts', 0)} | 
                    Views: {post.get('views', 0)} | 
                    Comments: {post.get('comments', 0)}
                </p>
            </div>
            """
        
        return html
    
    def _create_table_html(self, data: List[List]) -> str:
        """Create HTML for a table."""
        if not data:
            return ""
        
        html = "<table>"
        
        # Header
        if data:
            html += "<tr>"
            for header in data[0]:
                html += f"<th>{header}</th>"
            html += "</tr>"
        
        # Rows
        for row in data:
            html += "<tr>"
            for cell in row:
                html += f"<td>{cell}</td>"
            html += "</tr>"
        
        html += "</table>"
        return html
    
    def _create_report_html(self, report: Dict) -> str:
        """Create HTML for a report."""
        html = ""
        
        for section, content in report.items():
            html += f"<h2>{section}</h2>"
            
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        html += "<table>"
                        for key, value in item.items():
                            html += f"<tr><th>{key}</th><td>{value}</td></tr>"
                        html += "</table>"
                    else:
                        html += f"<p>{item}</p>"
            elif isinstance(content, dict):
                html += "<table>"
                for key, value in content.items():
                    html += f"<tr><th>{key}</th><td>{value}</td></tr>"
                html += "</table>"
            else:
                html += f"<p>{content}</p>"
        
        return html
    
    # --- Bulk Export ---
    
    def export_all(self, data: Dict[str, Any], format: str = 'json', filename: str = None) -> Union[str, bytes]:
        """
        Export all data in the specified format.
        
        Args:
            data: Dictionary containing all data to export.
            format: Export format ('csv', 'json', 'pdf').
            filename: Optional filename (without extension).
            
        Returns:
            Exported data in the specified format.
        """
        if format == 'csv':
            # Export each section as CSV
            results = {}
            for section, content in data.items():
                if isinstance(content, list):
                    results[section] = self.export_to_csv(content)
            return results
        elif format == 'json':
            return self.export_to_json(data, filename)
        elif format == 'pdf':
            return self.export_to_pdf(data, filename)
        else:
            return f"Unsupported format: {format}"


# Singleton instance
exporter = DataExporter()


# Convenience functions
def export_to_csv(data: List[Dict], filename: str = None, columns: List[str] = None) -> Union[str, bytes]:
    """Export data to CSV."""
    return exporter.export_to_csv(data, filename, columns)


def export_to_json(data: Any, filename: str = None, indent: int = 2) -> Union[str, bytes]:
    """Export data to JSON."""
    return exporter.export_to_json(data, filename, indent)


def export_to_pdf(data: Any, filename: str = None, title: str = 'OpenLens Report') -> Union[bytes, str]:
    """Export data to PDF."""
    return exporter.export_to_pdf(data, filename, title)
