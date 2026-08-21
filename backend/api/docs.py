"""
API Documentation Module for OpenLens

Provides Swagger/OpenAPI documentation endpoints.
"""

from flask import Flask, Blueprint, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import os

# Create a blueprint for API documentation
docs_bp = Blueprint('docs', __name__, url_prefix='/docs')


def init_docs(app: Flask):
    """
    Initialize API documentation endpoints.
    
    Args:
        app: Flask application.
    """
    # Serve OpenAPI specification
    @docs_bp.route('/openapi.yaml')
    def serve_openapi_yaml():
        """Serve the OpenAPI specification in YAML format."""
        spec_path = os.path.join(os.path.dirname(__file__), 'openapi_spec.yaml')
        return send_from_directory(os.path.dirname(__file__), 'openapi_spec.yaml')
    
    @docs_bp.route('/openapi.json')
    def serve_openapi_json():
        """Serve the OpenAPI specification in JSON format."""
        import yaml
        spec_path = os.path.join(os.path.dirname(__file__), 'openapi_spec.yaml')
        
        with open(spec_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        return jsonify(spec)
    
    @docs_bp.route('/')
    def docs_index():
        """Redirect to Swagger UI."""
        return jsonify({
            'message': 'OpenLens API Documentation',
            'swagger_ui': '/docs/swagger',
            'openapi_spec_yaml': '/docs/openapi.yaml',
            'openapi_spec_json': '/docs/openapi.json'
        })
    
    # Initialize Swagger UI
    SWAGGER_URL = '/docs/swagger'
    API_URL = '/docs/openapi.yaml'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "OpenLens API",
            'docExpansion': 'none',
            'persistAuthorization': True
        }
    )
    
    # Register blueprints
    app.register_blueprint(docs_bp)
    app.register_blueprint(swaggerui_blueprint)
    
    print(f"API documentation available at: {SWAGGER_URL}")
