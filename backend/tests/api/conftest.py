"""Fixtures for the API gateway test suite."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope='session')
def app():
    from backend.api.main import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope='session')
def client(app):
    return TestClient(app)


@pytest.fixture(scope='session')
def auth(client):
    """Admin bearer header (rbac seeds admin/admin123)."""
    response = client.post(
        '/api/security/token',
        data={'username': 'admin', 'password': 'admin123',
              'grant_type': 'password'},
    )
    assert response.status_code == 200, response.text
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
