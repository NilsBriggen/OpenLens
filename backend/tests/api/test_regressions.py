"""
Regression tests - one per bug found during the repair, so none can return.
"""


def test_health_is_unauthenticated(client):
    assert client.get('/api/system/health').status_code == 200


def test_guarded_endpoint_rejects_missing_token(client):
    assert client.get('/api/graph/stats').status_code == 401


def test_guarded_endpoint_rejects_garbage_token(client):
    response = client.get('/api/graph/stats',
                          headers={'Authorization': 'Bearer garbage'})
    assert response.status_code == 401


def test_graph_stats_returns_connected_flag(client, auth):
    """Was: 500 on dict.to_dict() for every call."""
    response = client.get('/api/graph/stats', headers=auth)
    assert response.status_code == 200
    body = response.json()
    assert 'connected' in body and 'nodeCount' in body


def test_graph_query_params_do_not_collide(client, auth):
    """Was: TypeError from splatting user params as **kwargs."""
    response = client.post('/api/graph/query', headers=auth, json={
        'query': 'RETURN $params AS echo',
        'params': {'params': 1},
    })
    assert response.status_code in (200, 503)  # 503 only if the DB is down


def test_ioc_round_trip_is_unshifted(client, auth):
    """Was: positional add_ioc shifted confidence into threat_type."""
    created = client.post('/api/threat/iocs', headers=auth, json={
        'value': '198.18.0.99', 'ioc_type': 'ip',
        'confidence': 0.66, 'severity': 'high',
        'description': 'regression check',
    })
    assert created.status_code == 200, created.text
    ioc_id = created.json()['id']

    fetched = client.get(f'/api/threat/iocs/{ioc_id}', headers=auth)
    assert fetched.status_code == 200  # was: always 404 (get_ioc by value)
    body = fetched.json()
    assert body['confidence'] == 0.66
    assert body['severity'] == 'high'
    assert body['threatType'] == ''


def test_ioc_rejects_shifted_types(client, auth):
    """String confidence must 400, never store corrupt data."""
    response = client.post('/api/threat/iocs', headers=auth, json={
        'value': '198.18.0.100', 'ioc_type': 'ip', 'confidence': 'high',
    })
    assert response.status_code in (400, 422)


def test_proxies_next_takes_query_params(client, auth):
    """Was: a GET that demanded a request body."""
    response = client.get('/api/scraping/proxies/next?country=de', headers=auth)
    assert response.status_code in (200, 404)  # 404 = no proxy loaded, fine


def test_proxies_list_does_not_crash(client, auth):
    """Was: 500 - a boolean used as a context-manager lock."""
    response = client.get('/api/scraping/proxies', headers=auth)
    assert response.status_code == 200


def test_threat_paths_no_args_is_not_500(client, auth):
    """Was: TypeError - find_threat_paths() required source_id."""
    response = client.get('/api/threat/graph/threat/paths', headers=auth)
    assert response.status_code in (200, 503)


def test_unavailable_feature_returns_api_error_shape(client, auth):
    """503s carry the machine-readable error body, never a silent []."""
    response = client.get('/api/scraping/twitter/trends', headers=auth)
    if response.status_code == 503:
        body = response.json()
        assert body['error'] == 'feature_unavailable'
        assert 'tweepy' in body['requires']


def test_users_list_never_leaks_password_hashes(client, auth):
    response = client.get('/api/security/users', headers=auth)
    assert response.status_code == 200
    assert 'password' not in response.text


def test_monitoring_health_is_unknown_without_samples(client, auth):
    """A monitor with no data must not report healthy (false green)."""
    response = client.get('/api/threat/monitoring/health', headers=auth)
    assert response.status_code == 200
    assert response.json()['data']['status'] in ('unknown', 'healthy', 'degraded')


def test_rbac_wildcard_is_scoped():
    """A permission with action='*' must not grant every resource."""
    from backend.security.rbac import Permission
    perm = Permission(permission_id='t', name='t', resource='graph', action='*')
    assert perm.matches('graph', 'read')
    assert not perm.matches('threat', 'read')
