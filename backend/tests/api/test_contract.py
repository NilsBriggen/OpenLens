"""
Contract tests: the two invariants that guard the whole API surface.

1. Every response schema is camelCase (request models stay snake_case).
2. Every endpoint the frontend's apiClient.ts declares resolves to a mounted
   route - the test that would have caught the fifteen 404/405 endpoints.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

CAMEL = re.compile(r'^[a-z][a-zA-Z0-9]*$')


def test_every_response_schema_is_camel_case(app):
    schemas = app.openapi()['components']['schemas']
    violations = []
    for name, schema in schemas.items():
        if name.endswith(('Create', 'Request', 'In', 'Update')) or name.startswith('Body_'):
            continue  # request models keep snake_case by design
        if name in ('HTTPValidationError', 'ValidationError', 'TokenOut'):
            continue  # TokenOut is the OAuth2 contract (snake_case by spec)
        for prop in schema.get('properties', {}):
            if not CAMEL.fullmatch(prop):
                violations.append(f'{name}.{prop}')
    assert not violations, f'snake_case leaked into responses: {violations}'


def test_every_frontend_endpoint_resolves(app):
    src = (REPO_ROOT / 'frontend/src/lib/apiClient.ts').read_text()
    endpoints = sorted(set(re.findall(r"'(/api/[a-z0-9/{}\-]+)'", src)))
    paths = app.openapi()['paths']

    unresolved = []
    for endpoint in endpoints:
        if endpoint.startswith('/api/ws'):
            continue  # websocket routes are not in the OpenAPI paths
        if endpoint in paths:
            continue
        matched = any(
            re.fullmatch(re.sub(r'\{[^}]+\}', '[^/]+', path), endpoint)
            for path in paths
        )
        if not matched:
            unresolved.append(endpoint)
    assert not unresolved, f'frontend calls unmounted endpoints: {unresolved}'
