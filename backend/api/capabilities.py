"""
Runtime capability probes for the OpenLens API.

Each capability is a zero-argument callable returning bool. Routes gate on
them via the requires() dependency, which turns a missing capability into a
503 feature_unavailable instead of a silent empty result.
"""

from importlib.util import find_spec
from typing import Callable, Dict, List

from fastapi import Depends

from backend.api.errors import FeatureUnavailable


def _module_probe(name: str) -> Callable[[], bool]:
    def probe() -> bool:
        try:
            return find_spec(name) is not None
        except (ImportError, ValueError):
            return False
    return probe


def _graph_db_probe() -> bool:
    from backend.graph import graph_engine
    return graph_engine.is_connected()


CAPABILITIES: Dict[str, Callable[[], bool]] = {
    'networkx': _module_probe('networkx'),
    'numpy': _module_probe('numpy'),
    'pandas': _module_probe('pandas'),
    'sklearn': _module_probe('sklearn'),
    'rapidfuzz': _module_probe('rapidfuzz'),
    'matplotlib': _module_probe('matplotlib'),
    'pyvis': _module_probe('pyvis'),
    'plotly': _module_probe('plotly'),
    'python-louvain': _module_probe('community'),
    'tweepy': _module_probe('tweepy'),
    'instaloader': _module_probe('instaloader'),
    'scrapy': _module_probe('scrapy'),
    'neo4j': _module_probe('neo4j'),
    'graph-db': _graph_db_probe,
}


def capability_map() -> Dict[str, bool]:
    """Every capability, evaluated. Exposed via GET /api/system/config."""
    return {name: bool(probe()) for name, probe in CAPABILITIES.items()}


def requires(*names: str, feature: str = None):
    """
    FastAPI dependency: 503 unless every named capability is present.

    Usage:
        @router.post("/centrality",
                     dependencies=[requires("networkx", "graph-db")])
    """
    unknown = [n for n in names if n not in CAPABILITIES]
    if unknown:
        raise KeyError(f'unknown capabilities: {unknown}')

    async def _dep() -> None:
        missing = [n for n in names if not CAPABILITIES[n]()]
        if missing:
            raise FeatureUnavailable(
                feature=feature or ','.join(names), requires=missing)

    return Depends(_dep)
