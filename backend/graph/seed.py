"""
Demo data seeding for OpenLens.

Populates Neo4j with a graph shaped so the analytics endpoints return
non-empty results, and the IOC manager with matching indicators. The sizes
are dictated by thresholds elsewhere in the code:

- >= 30 nodes with numeric properties: the statistical anomaly detector uses
  population std with a |z| > 3 test, and the maximum attainable |z| over n
  samples is sqrt(n - 1) - with fewer than ~12 points an anomaly is
  arithmetically impossible.
- >= 100 non-adjacent node pairs for link prediction training.
- A 'label' property on >= 10 nodes across >= 2 classes for node
  classification.
- At least one node with is_threat for threat prediction.
- Deliberate near-duplicate people for entity resolution.
- An 'indicator' property matching IOC.indicator exactly, so IOC-based hunts
  and the threat graph can join graph nodes to the IOC store.
- Timestamps on a subset for temporal analysis.

Usage:
    python -m backend.graph.seed [--reset]
"""

import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

SEED_MARKER = {'_seed': 'demo'}

_COUNTRIES = ['US', 'DE', 'RU', 'CN', 'BR', 'NL', 'FR']
_BASE_TIME = datetime(2026, 8, 1, 12, 0, 0)


def _demo_nodes() -> List[Dict[str, Any]]:
    """~48 nodes: people (with near-duplicates), orgs, IPs, domains, accounts."""
    rng = random.Random(42)
    nodes: List[Dict[str, Any]] = []

    # People - risk_score is the numeric anomaly axis; two deliberate outliers.
    people = [
        ('John Smith', 'j.smith@example.com', 'analyst'),
        ('Jon Smith', 'j.smith@example.com', 'analyst'),          # near-duplicate of John
        ('Maria Garcia', 'm.garcia@example.com', 'analyst'),
        ('Mariah Garcia', 'm.garcia@example.com', 'analyst'),     # near-duplicate of Maria
        ('Wei Chen', 'w.chen@example.com', 'engineer'),
        ('Aisha Khan', 'a.khan@example.com', 'engineer'),
        ('Lars Nielsen', 'l.nielsen@example.com', 'engineer'),
        ('Sofia Rossi', 's.rossi@example.com', 'manager'),
        ('Peter Novak', 'p.novak@example.com', 'manager'),
        ('Elena Petrova', 'e.petrova@example.com', 'analyst'),
        ('Omar Haddad', 'o.haddad@example.com', 'engineer'),
        ('Nina Berg', 'n.berg@example.com', 'analyst'),
    ]
    for i, (name, email, role) in enumerate(people):
        nodes.append({
            'id': f'person-{i}',
            'labels': ['Person'],
            'properties': {
                'name': name, 'email': email, 'label': role,
                'risk_score': round(rng.uniform(10, 30), 1),
                'timestamp': (_BASE_TIME + timedelta(hours=i)).isoformat(),
            },
        })
    # Outliers: far outside the 10-30 band.
    nodes[10]['properties']['risk_score'] = 96.0
    nodes[11]['properties']['risk_score'] = 88.5

    for i in range(6):
        nodes.append({
            'id': f'org-{i}',
            'labels': ['Organization'],
            'properties': {
                'name': f'Org {chr(65 + i)}', 'label': 'organization',
                'risk_score': round(rng.uniform(15, 35), 1),
                'country': _COUNTRIES[i % len(_COUNTRIES)],
            },
        })

    # IPs - some are threat indicators matching the seeded IOC store.
    threat_ips = ['203.0.113.7', '198.51.100.23', '192.0.2.146']
    benign_ips = [f'10.0.{i}.{i * 7 % 250 + 1}' for i in range(9)]
    for i, ip in enumerate(threat_ips + benign_ips):
        is_threat = ip in threat_ips
        nodes.append({
            'id': f'ip-{i}',
            'labels': ['IPAddress'],
            'properties': {
                'name': ip, 'indicator': ip, 'label': 'infrastructure',
                'is_threat': is_threat,
                'risk_score': round(rng.uniform(70, 95), 1) if is_threat else round(rng.uniform(5, 25), 1),
                'country': _COUNTRIES[i % len(_COUNTRIES)],
                'timestamp': (_BASE_TIME + timedelta(hours=i * 3)).isoformat(),
            },
        })

    threat_domains = ['malware-drop.example.net', 'phish-login.example.org']
    benign_domains = ['docs.example.com', 'mail.example.com', 'cdn.example.com',
                      'api.example.com', 'shop.example.com']
    for i, domain in enumerate(threat_domains + benign_domains):
        is_threat = domain in threat_domains
        nodes.append({
            'id': f'domain-{i}',
            'labels': ['Domain'],
            'properties': {
                'name': domain, 'indicator': domain, 'label': 'infrastructure',
                'is_threat': is_threat,
                'risk_score': round(rng.uniform(65, 92), 1) if is_threat else round(rng.uniform(5, 20), 1),
            },
        })

    for i in range(11):
        nodes.append({
            'id': f'account-{i}',
            'labels': ['Account'],
            'properties': {
                'name': f'acct_{i:03d}', 'label': 'account',
                'risk_score': round(rng.uniform(8, 28), 1),
                'timestamp': (_BASE_TIME + timedelta(days=i % 5, hours=i)).isoformat(),
            },
        })

    for node in nodes:
        node['properties'].update(SEED_MARKER)
    return nodes


def _demo_edges() -> List[Tuple[str, str, str, Dict[str, Any]]]:
    """(source_id, target_id, type, properties) - a hub-and-cluster topology."""
    rng = random.Random(43)
    edges: List[Tuple[str, str, str, Dict[str, Any]]] = []

    def add(src: str, dst: str, rel: str, **props):
        props.update(SEED_MARKER)
        edges.append((src, dst, rel, props))

    # People to orgs (employment clusters)
    for i in range(12):
        add(f'person-{i}', f'org-{i % 6}', 'WORKS_FOR', since=2020 + i % 5)
    # People know each other within clusters + some bridges
    for i in range(11):
        add(f'person-{i}', f'person-{i + 1}', 'KNOWS', weight=rng.randint(1, 9))
    add('person-0', 'person-5', 'KNOWS', weight=3)
    add('person-2', 'person-8', 'KNOWS', weight=2)
    add('person-4', 'person-10', 'KNOWS', weight=5)
    # Accounts owned by people
    for i in range(11):
        add(f'person-{i % 12}', f'account-{i}', 'OWNS')
    # Accounts touching IPs (the threat IPs get heavy fan-in -> high centrality)
    for i in range(11):
        add(f'account-{i}', f'ip-{i % 12}', 'CONNECTED_FROM',
            count=rng.randint(1, 40))
    for i in range(6):
        add(f'account-{i}', 'ip-0', 'CONNECTED_FROM', count=rng.randint(20, 90))
    # Domains resolving to IPs
    for i in range(7):
        add(f'domain-{i}', f'ip-{(i * 2) % 12}', 'RESOLVES_TO')
    # Orgs hosting domains
    for i in range(5):
        add(f'org-{i}', f'domain-{i}', 'HOSTS')

    return edges


def _demo_iocs() -> List[Dict[str, Any]]:
    """IOCs whose indicators match the seeded graph nodes exactly."""
    return [
        {'indicator': '203.0.113.7', 'indicator_type': 'ip', 'threat_type': 'c2',
         'confidence': 0.95, 'severity': 'critical',
         'description': 'Known C2 server (demo)', 'source': 'demo-seed',
         'tags': ['demo', 'c2']},
        {'indicator': '198.51.100.23', 'indicator_type': 'ip', 'threat_type': 'scanner',
         'confidence': 0.8, 'severity': 'high',
         'description': 'Mass scanner (demo)', 'source': 'demo-seed',
         'tags': ['demo', 'scanner']},
        {'indicator': '192.0.2.146', 'indicator_type': 'ip', 'threat_type': 'botnet',
         'confidence': 0.7, 'severity': 'high',
         'description': 'Botnet member (demo)', 'source': 'demo-seed',
         'tags': ['demo', 'botnet']},
        {'indicator': 'malware-drop.example.net', 'indicator_type': 'domain',
         'threat_type': 'malware', 'confidence': 0.9, 'severity': 'critical',
         'description': 'Malware distribution (demo)', 'source': 'demo-seed',
         'tags': ['demo', 'malware']},
        {'indicator': 'phish-login.example.org', 'indicator_type': 'domain',
         'threat_type': 'phishing', 'confidence': 0.85, 'severity': 'high',
         'description': 'Credential phishing (demo)', 'source': 'demo-seed',
         'tags': ['demo', 'phishing']},
        {'indicator': 'a3f5c1d9e7b2468013579bdf2468ace0', 'indicator_type': 'hash',
         'threat_type': 'malware', 'confidence': 0.9, 'severity': 'high',
         'description': 'Dropper MD5 (demo)', 'source': 'demo-seed',
         'tags': ['demo', 'malware']},
        {'indicator': 'billing@phish-login.example.org', 'indicator_type': 'email',
         'threat_type': 'phishing', 'confidence': 0.75, 'severity': 'medium',
         'description': 'Phishing sender (demo)', 'source': 'demo-seed',
         'tags': ['demo', 'phishing']},
        {'indicator': 'http://malware-drop.example.net/payload.bin',
         'indicator_type': 'url', 'threat_type': 'malware', 'confidence': 0.9,
         'severity': 'high', 'description': 'Payload URL (demo)',
         'source': 'demo-seed', 'tags': ['demo', 'malware']},
        {'indicator': '203.0.113.99', 'indicator_type': 'ip', 'threat_type': 'scanner',
         'confidence': 0.5, 'severity': 'low',
         'description': 'Suspicious scanner (demo)', 'source': 'demo-seed',
         'tags': ['demo']},
        {'indicator': 'tracker.example.info', 'indicator_type': 'domain',
         'threat_type': 'adware', 'confidence': 0.4, 'severity': 'low',
         'description': 'Ad tracker (demo)', 'source': 'demo-seed', 'tags': ['demo']},
        {'indicator': '198.51.100.200', 'indicator_type': 'ip', 'threat_type': 'c2',
         'confidence': 0.65, 'severity': 'medium',
         'description': 'Possible C2 (demo)', 'source': 'demo-seed', 'tags': ['demo', 'c2']},
        {'indicator': 'deadbeefcafe00112233445566778899', 'indicator_type': 'hash',
         'threat_type': 'malware', 'confidence': 0.6, 'severity': 'medium',
         'description': 'Suspicious binary (demo)', 'source': 'demo-seed',
         'tags': ['demo']},
    ]


def clear_demo_graph(engine=None) -> int:
    """Remove all seeded nodes (and their relationships)."""
    if engine is None:
        from backend.graph import graph_engine as engine
    before = engine.execute_scalar(
        "MATCH (n {_seed: 'demo'}) RETURN count(n) AS c", default=0) or 0
    engine.execute_query("MATCH (n {_seed: 'demo'}) DETACH DELETE n", use_cache=False)
    return int(before)


def is_seeded(engine=None) -> bool:
    """True when demo nodes are present."""
    if engine is None:
        from backend.graph import graph_engine as engine
    count = engine.execute_scalar(
        "MATCH (n {_seed: 'demo'}) RETURN count(n) AS c", default=0)
    return bool(count)


def seed_demo_graph(engine=None, reset: bool = False) -> Dict[str, int]:
    """
    Seed the demo graph. Idempotent: skips when already seeded unless reset.

    Returns:
        {'nodes': ..., 'edges': ...} counts actually created.
    """
    if engine is None:
        from backend.graph import graph_engine as engine

    if not engine.is_connected():
        raise RuntimeError('Neo4j is not reachable; cannot seed')

    if is_seeded(engine):
        if not reset:
            return {'nodes': 0, 'edges': 0, 'skipped': 1}
        clear_demo_graph(engine)

    created_nodes = 0
    for node in _demo_nodes():
        props = dict(node['properties'])
        props['id'] = node['id']
        label_str = ':'.join(node['labels'])
        result = engine.execute_query(
            f"CREATE (n:{label_str} $props) RETURN n", {'props': props},
            use_cache=False,
        )
        if result and result.nodes:
            created_nodes += 1

    created_edges = 0
    for source_id, target_id, rel_type, props in _demo_edges():
        result = engine.execute_query(
            f"""
            MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
            CREATE (a)-[r:{rel_type} $props]->(b)
            RETURN count(r) AS c
            """,
            {'source_id': source_id, 'target_id': target_id, 'props': props},
            use_cache=False,
        )
        if result and result.records and result.records[0].get('c'):
            created_edges += 1

    engine.to_networkx(force_refresh=True)
    return {'nodes': created_nodes, 'edges': created_edges}


def seed_demo_iocs(manager=None) -> int:
    """Seed the IOC store; returns how many IOCs were added (idempotent)."""
    if manager is None:
        from backend.threat_intelligence import ioc_manager as manager

    added = 0
    for spec in _demo_iocs():
        if manager.get_ioc(spec['indicator']):
            continue
        ioc = manager.add_ioc(
            spec['indicator'],
            spec['indicator_type'],
            threat_type=spec.get('threat_type', ''),
            confidence=spec.get('confidence', 0.8),
            severity=spec.get('severity', 'medium'),
            description=spec.get('description', ''),
            source=spec.get('source', 'demo-seed'),
            tags=spec.get('tags'),
        )
        if ioc:
            added += 1
    return added


def main(argv: Optional[List[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    reset = '--reset' in args

    from backend.composition import configure_services
    configure_services()

    from backend.graph import graph_engine

    graph_counts = seed_demo_graph(graph_engine, reset=reset)
    ioc_count = seed_demo_iocs()
    total_nodes = graph_engine.node_count()
    total_edges = graph_engine.relationship_count()
    print(f"seeded: {graph_counts}, iocs added: {ioc_count}")
    print(f"graph now: {total_nodes} nodes, {total_edges} relationships")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
