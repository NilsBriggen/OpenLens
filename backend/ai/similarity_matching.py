"""
Similarity Matching Module for OpenLens

Provides similarity scoring between records:
- TF-IDF cosine similarity over text fields
- Jaccard similarity over token/tag sets
- Normalised numeric-distance similarity
- Levenshtein similarity (when rapidfuzz is installed)
- Weighted combination across fields
- Graph-neighbour similarity search
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

# Try to import numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available. Install with: pip install numpy")

# Try to import scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available. Install with: pip install scikit-learn")

# Try to import rapidfuzz
try:
    from rapidfuzz import fuzz as rapidfuzz_fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("rapidfuzz not available. Install with: pip install rapidfuzz")


@dataclass
class SimilarityScore:
    """Represents a similarity score between two items."""
    item_id_1: str
    item_id_2: str
    score: float
    method: str = ''
    matching_fields: List[str] = field(default_factory=list)
    field_scores: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'item_id_1': self.item_id_1,
            'item_id_2': self.item_id_2,
            'score': self.score,
            'method': self.method,
            'matching_fields': self.matching_fields,
            'field_scores': self.field_scores,
        }


@dataclass
class SimilarityResult:
    """Result of a similarity matching run."""
    method: str
    matches: List[SimilarityScore] = field(default_factory=list)
    total_items: int = 0
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'method': self.method,
            'matches': [m.to_dict() for m in self.matches],
            'total_items': self.total_items,
            'execution_time': self.execution_time,
        }


@dataclass
class SimilarityConfig:
    """Configuration for similarity matching."""
    methods: List[str] = field(default_factory=lambda: ['cosine', 'jaccard', 'numeric'])
    threshold: float = 0.7
    text_fields: List[str] = field(default_factory=list)
    numeric_fields: List[str] = field(default_factory=list)
    top_k: int = 10

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'methods': self.methods,
            'threshold': self.threshold,
            'text_fields': self.text_fields,
            'numeric_fields': self.numeric_fields,
            'top_k': self.top_k,
        }


class SimilarityMatcher:
    """
    Similarity matcher for OpenLens.

    Scores pairs of records field-by-field and combines the scores. Text
    fields use TF-IDF cosine (sklearn) or Levenshtein (rapidfuzz); list-like
    fields use Jaccard; numeric fields use normalised absolute distance.
    """

    _RESERVED_KEYS = {'id', 'item_id', 'entity_id', 'type', 'entity_type'}

    def __init__(self, graph_engine=None, config: SimilarityConfig = None):
        """
        Initialize the similarity matcher.

        Args:
            graph_engine: GraphEngine instance.
            config: SimilarityConfig.
        """
        self.graph_engine = graph_engine
        self.config = config or SimilarityConfig()

    @staticmethod
    def _item_id(item: Dict[str, Any], index: int) -> str:
        """Best identifier for an item."""
        return str(item.get('id') or item.get('item_id')
                   or item.get('entity_id') or index)

    def _split_fields(self, a: Dict[str, Any], b: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
        """Shared (text, numeric, list) field names for a pair of items."""
        shared = [k for k in a if k in b and k not in self._RESERVED_KEYS]
        text_fields = self.config.text_fields or [
            k for k in shared if isinstance(a.get(k), str) and isinstance(b.get(k), str)]
        numeric_fields = self.config.numeric_fields or [
            k for k in shared
            if isinstance(a.get(k), (int, float)) and isinstance(b.get(k), (int, float))
            and not isinstance(a.get(k), bool)]
        list_fields = [k for k in shared
                       if isinstance(a.get(k), (list, set, tuple))
                       and isinstance(b.get(k), (list, set, tuple))]
        return text_fields, numeric_fields, list_fields

    @staticmethod
    def _jaccard(a, b) -> float:
        """Jaccard similarity of two collections (or token sets of strings)."""
        set_a = set(a.split() if isinstance(a, str) else a)
        set_b = set(b.split() if isinstance(b, str) else b)
        union = set_a | set_b
        return len(set_a & set_b) / len(union) if union else 0.0

    @staticmethod
    def _numeric_similarity(a: float, b: float) -> float:
        """1 - normalised absolute difference."""
        scale = max(abs(a), abs(b))
        if scale == 0:
            return 1.0
        return max(0.0, 1.0 - abs(a - b) / scale)

    def _text_similarity(self, a: str, b: str, method: str) -> float:
        """Text similarity via the requested method."""
        if not a or not b:
            return 0.0
        if a == b:
            return 1.0
        if method == 'levenshtein':
            if not RAPIDFUZZ_AVAILABLE:
                raise RuntimeError(
                    'levenshtein similarity requires rapidfuzz; '
                    'install with: pip install rapidfuzz')
            return rapidfuzz_fuzz.ratio(a, b) / 100.0
        if method == 'cosine' and SKLEARN_AVAILABLE:
            try:
                matrix = TfidfVectorizer(analyzer='char_wb',
                                         ngram_range=(2, 3)).fit_transform([a, b])
                return float(cosine_similarity(matrix[0], matrix[1])[0][0])
            except Exception:
                return self._jaccard(a, b)
        # Fallback: token Jaccard needs no libraries.
        return self._jaccard(a, b)

    def compare(self, a: Dict[str, Any], b: Dict[str, Any],
                method: str = None) -> SimilarityScore:
        """
        Score one pair of items.

        Args:
            a: First item.
            b: Second item.
            method: 'cosine', 'jaccard', 'levenshtein' or 'numeric'
                (None combines all applicable field types).

        Returns:
            SimilarityScore with per-field breakdown.
        """
        method = method or 'combined'
        text_fields, numeric_fields, list_fields = self._split_fields(a, b)

        field_scores: Dict[str, float] = {}
        for key in text_fields:
            text_method = method if method in ('cosine', 'levenshtein', 'jaccard') else 'cosine'
            field_scores[key] = self._text_similarity(str(a[key]), str(b[key]), text_method)
        for key in numeric_fields:
            if method in ('combined', 'numeric'):
                field_scores[key] = self._numeric_similarity(float(a[key]), float(b[key]))
        for key in list_fields:
            field_scores[key] = self._jaccard(a[key], b[key])

        score = sum(field_scores.values()) / len(field_scores) if field_scores else 0.0
        matching = [k for k, v in field_scores.items() if v >= self.config.threshold]

        return SimilarityScore(
            item_id_1=self._item_id(a, 0),
            item_id_2=self._item_id(b, 1),
            score=round(score, 4),
            method=method,
            matching_fields=matching,
            field_scores={k: round(v, 4) for k, v in field_scores.items()},
        )

    def match(self, items: List[Dict[str, Any]],
              method: str = None) -> SimilarityResult:
        """
        Score every pair of items and keep those above the threshold.

        Args:
            items: Items to compare pairwise.
            method: Similarity method (see compare()).

        Returns:
            SimilarityResult.
        """
        started = time.time()
        matches: List[SimilarityScore] = []

        try:
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    score = self.compare(items[i], items[j], method)
                    score.item_id_1 = self._item_id(items[i], i)
                    score.item_id_2 = self._item_id(items[j], j)
                    if score.score >= self.config.threshold:
                        matches.append(score)
        except RuntimeError:
            raise
        except Exception as e:
            print(f"Similarity matching error: {e}")

        return SimilarityResult(
            method=method or 'combined',
            matches=sorted(matches, key=lambda m: m.score, reverse=True),
            total_items=len(items),
            execution_time=time.time() - started,
        )

    def find_similar(self, query: Dict[str, Any],
                     candidates: List[Dict[str, Any]],
                     top_k: int = None) -> List[SimilarityScore]:
        """
        Rank candidates by similarity to a query item.

        Args:
            query: Reference item.
            candidates: Items to rank.
            top_k: How many to return (None for config default).

        Returns:
            Top-k SimilarityScores, best first.
        """
        top_k = top_k or self.config.top_k
        scores = []
        for index, candidate in enumerate(candidates):
            score = self.compare(query, candidate)
            score.item_id_2 = self._item_id(candidate, index)
            scores.append(score)
        return sorted(scores, key=lambda s: s.score, reverse=True)[:top_k]

    def match_texts(self, texts: List[str], method: str = 'cosine') -> SimilarityResult:
        """Pairwise similarity over bare strings."""
        items = [{'id': str(i), 'text': t} for i, t in enumerate(texts)]
        return self.match(items, method)

    def build_similarity_matrix(self, items: List[Dict[str, Any]],
                                method: str = None) -> List[List[float]]:
        """Full pairwise similarity matrix (1.0 on the diagonal)."""
        size = len(items)
        matrix = [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
        for i in range(size):
            for j in range(i + 1, size):
                score = self.compare(items[i], items[j], method).score
                matrix[i][j] = matrix[j][i] = score
        return matrix

    def find_similar_in_graph(self, node_id: str, entity_type: str = None,
                              top_k: int = 10) -> List[SimilarityScore]:
        """
        Rank graph nodes by property similarity to a reference node.

        Returns [] when the graph store is unavailable or the node is unknown.
        """
        if not self.graph_engine:
            return []

        result = self.graph_engine.execute_query(
            "MATCH (n) WHERE n.id = $id RETURN n", {'id': node_id})
        if not result or not result.nodes:
            return []
        reference = {'id': result.nodes[0].node_id, **result.nodes[0].properties}

        if entity_type:
            candidates_result = self.graph_engine.execute_query(
                "MATCH (n) WHERE $label IN labels(n) AND n.id <> $id RETURN n",
                {'label': entity_type, 'id': node_id})
        else:
            candidates_result = self.graph_engine.execute_query(
                "MATCH (n) WHERE n.id <> $id RETURN n", {'id': node_id})
        if not candidates_result:
            return []

        candidates = [{'id': node.node_id, **node.properties}
                      for node in candidates_result.nodes]
        return self.find_similar(reference, candidates, top_k)


# Global similarity matcher instance
similarity_matcher = SimilarityMatcher()
