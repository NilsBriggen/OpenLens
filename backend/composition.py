"""
Composition root for OpenLens backend services.

Every service module ends with a zero-argument singleton
(`network_analyzer = NetworkAnalyzer()`), which leaves all collaborator
attributes None. This module is the single place those collaborators are
wired together.

Mechanism: attribute assignment on the already-constructed singletons.
Routers import the singleton objects, so mutating attributes propagates
everywhere, whereas rebinding the module names would not.

Location: deliberately a standalone module rather than per-package
__init__ wiring. backend.ai needs backend.threat_intelligence collaborators
and vice versa, which would be a hard import cycle if wiring lived inside
the package inits. Nothing imports composition back, so there is no cycle.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_configured = False

# service name -> list of collaborator attribute names wired here.
# health() introspects this so "wired" is a positive assertion.
_EDGES: Dict[str, List[str]] = {
    # graph
    'network_analyzer': ['graph_engine'],
    'path_finder': ['graph_engine'],
    'community_detector': ['graph_engine'],
    'graph_visualizer': ['graph_engine'],
    'temporal_analyzer': ['graph_engine'],
    # ai
    'anomaly_detector': ['graph_engine'],
    'entity_resolver': ['graph_engine'],
    'predictive_analyzer': ['graph_engine'],
    'similarity_matcher': ['graph_engine'],
    'cluster_analyzer': ['graph_engine'],
    'graph_ml': ['graph_engine'],
    'ai_threat_intelligence': ['ioc_manager', 'threat_analyzer',
                               'alert_manager', 'graph_engine'],
    # scraping
    'scraper': ['proxy_manager', 'user_agent_manager'],
    'distributed_scraper': ['proxy_manager', 'user_agent_manager',
                            'rate_limiter', 'result_cache', 'celery_app'],
    # threat intelligence
    'ioc_manager': ['threat_feed_manager'],
    'threat_analyzer': ['ioc_manager', 'graph_engine'],
    'alert_manager': ['ioc_manager', 'threat_analyzer'],
    'threat_hunter': ['graph_engine', 'ioc_manager', 'anomaly_detector'],
    'threat_intel_sharing': ['ioc_manager', 'threat_feed_manager'],
    'threat_graph': ['graph_engine', 'ioc_manager', 'threat_analyzer'],
    'threat_monitor': ['graph_engine', 'ioc_manager', 'threat_analyzer',
                       'alert_manager', 'threat_feed_manager'],
    # security
    'authentication_service': ['rbac_service'],
    'authorization_service': ['rbac_service', 'audit_logger'],
}

SERVICES: Dict[str, Any] = {}


def configure_services(force: bool = False) -> Dict[str, Any]:
    """
    Wire all service singletons together. Idempotent; cheap (attribute
    assignments only - the Neo4j driver connects lazily on first use).
    """
    global _configured
    if _configured and not force:
        return SERVICES

    from backend.config import load_environment
    load_environment()

    from backend.graph import (
        graph_engine, network_analyzer, path_finder, community_detector,
        graph_visualizer, temporal_analyzer,
    )
    from backend.ai import anomaly_detector, entity_resolver, predictive_analyzer
    from backend.scraping import (
        scraper, distributed_scraper, proxy_manager, user_agent_manager,
        rate_limiter, result_cache, celery_app, scrapy_integration,
    )
    from backend.threat_intelligence import (
        threat_feed_manager, ioc_manager, threat_analyzer, alert_manager,
        threat_hunter, threat_intel_sharing, threat_graph, threat_monitor,
    )
    from backend.security import (
        rbac, audit_logger, authentication_service, authorization_service,
    )

    # graph analytics -> engine
    network_analyzer.graph_engine = graph_engine
    path_finder.graph_engine = graph_engine
    community_detector.graph_engine = graph_engine
    graph_visualizer.graph_engine = graph_engine
    temporal_analyzer.graph_engine = graph_engine

    # ai -> engine
    anomaly_detector.graph_engine = graph_engine
    entity_resolver.graph_engine = graph_engine
    predictive_analyzer.graph_engine = graph_engine

    # scraping
    scraper.proxy_manager = proxy_manager
    scraper.user_agent_manager = user_agent_manager
    distributed_scraper.proxy_manager = proxy_manager
    distributed_scraper.user_agent_manager = user_agent_manager
    distributed_scraper.rate_limiter = rate_limiter
    distributed_scraper.result_cache = result_cache
    distributed_scraper.celery_app = celery_app
    scrapy_integration.proxy_manager = proxy_manager
    scrapy_integration.user_agent_manager = user_agent_manager

    # threat intelligence
    ioc_manager.threat_feed_manager = threat_feed_manager
    threat_analyzer.ioc_manager = ioc_manager
    threat_analyzer.graph_engine = graph_engine
    alert_manager.ioc_manager = ioc_manager
    alert_manager.threat_analyzer = threat_analyzer
    threat_hunter.graph_engine = graph_engine
    threat_hunter.ioc_manager = ioc_manager
    threat_hunter.anomaly_detector = anomaly_detector
    threat_intel_sharing.ioc_manager = ioc_manager
    threat_intel_sharing.threat_feed_manager = threat_feed_manager
    threat_graph.graph_engine = graph_engine
    threat_graph.ioc_manager = ioc_manager
    threat_graph.threat_analyzer = threat_analyzer
    threat_monitor.graph_engine = graph_engine
    threat_monitor.ioc_manager = ioc_manager
    threat_monitor.threat_analyzer = threat_analyzer
    threat_monitor.alert_manager = alert_manager
    threat_monitor.threat_feed_manager = threat_feed_manager

    # security (moved here from backend/security/__init__.py so there is
    # exactly one wiring site)
    authentication_service.rbac_service = rbac
    authorization_service.rbac_service = rbac
    authorization_service.audit_logger = audit_logger

    # ai threat-intelligence facade. Imported from the submodule explicitly:
    # the package attribute of the same name is the singleton, but being
    # explicit avoids depending on the __init__'s rebinding order.
    from backend.ai.threat_intelligence import threat_intelligence as ai_threat_intel
    ai_threat_intel.ioc_manager = ioc_manager
    ai_threat_intel.threat_analyzer = threat_analyzer
    ai_threat_intel.alert_manager = alert_manager
    ai_threat_intel.graph_engine = graph_engine

    # ai helpers that read the graph
    from backend.ai.similarity_matching import similarity_matcher
    from backend.ai.clustering import cluster_analyzer
    from backend.ai.graph_ml import graph_ml
    similarity_matcher.graph_engine = graph_engine
    cluster_analyzer.graph_engine = graph_engine
    graph_ml.graph_engine = graph_engine

    SERVICES.update({
        'similarity_matcher': similarity_matcher,
        'cluster_analyzer': cluster_analyzer,
        'graph_ml': graph_ml,
        'ai_threat_intelligence': ai_threat_intel,
        'graph_engine': graph_engine,
        'network_analyzer': network_analyzer,
        'path_finder': path_finder,
        'community_detector': community_detector,
        'graph_visualizer': graph_visualizer,
        'temporal_analyzer': temporal_analyzer,
        'anomaly_detector': anomaly_detector,
        'entity_resolver': entity_resolver,
        'predictive_analyzer': predictive_analyzer,
        'scraper': scraper,
        'distributed_scraper': distributed_scraper,
        'proxy_manager': proxy_manager,
        'user_agent_manager': user_agent_manager,
        'rate_limiter': rate_limiter,
        'result_cache': result_cache,
        'threat_feed_manager': threat_feed_manager,
        'ioc_manager': ioc_manager,
        'threat_analyzer': threat_analyzer,
        'alert_manager': alert_manager,
        'threat_hunter': threat_hunter,
        'threat_intel_sharing': threat_intel_sharing,
        'threat_graph': threat_graph,
        'threat_monitor': threat_monitor,
        'rbac': rbac,
        'audit_logger': audit_logger,
        'authentication_service': authentication_service,
        'authorization_service': authorization_service,
    })

    _configured = True
    logger.info('OpenLens services wired (%d edges)', sum(len(v) for v in _EDGES.values()))
    return SERVICES


def is_configured() -> bool:
    """True once configure_services() has run."""
    return _configured


def service_graph() -> Dict[str, List[str]]:
    """The declared collaborator edges, for documentation and tests."""
    return {k: list(v) for k, v in _EDGES.items()}


def health() -> Dict[str, Any]:
    """
    Positive wiring assertion: for every declared edge, report whether the
    collaborator attribute is actually set on the singleton.
    """
    configure_services()

    services_report: Dict[str, Any] = {}
    for name, attrs in _EDGES.items():
        obj = SERVICES.get(name)
        if obj is None:
            services_report[name] = {'present': False, 'unwired': attrs}
            continue
        unwired = [attr for attr in attrs if getattr(obj, attr, None) is None]
        services_report[name] = {'present': True, 'unwired': unwired}

    graph_engine = SERVICES.get('graph_engine')
    return {
        'configured': _configured,
        'services': services_report,
        'graph_db_connected': bool(graph_engine and graph_engine.is_connected()),
    }
