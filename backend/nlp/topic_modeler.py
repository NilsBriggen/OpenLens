"""
Topic Modeler for OpenLens

Provides topic modeling functionality using:
- LDA (Latent Dirichlet Allocation)
- NMF (Non-Negative Matrix Factorization)
- BERTopic (for advanced topic modeling)
- Keyphrase extraction (YAKE, RAKE)

Dependencies:
- gensim: For LDA and NMF
- sklearn: For NMF and text vectorization
- nltk: For text preprocessing
- bertopic: For BERTopic (optional)
- yake: For keyphrase extraction (optional)
- rake-nltk: For RAKE keyphrase extraction (optional)
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import numpy as np

# Try to import optional dependencies
try:
    from gensim import corpora
    from gensim.models import LdaModel, CoherenceModel
    from gensim.utils import simple_preprocess
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False
    print("Gensim not available. Install with: pip install gensim")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.decomposition import NMF, LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Scikit-learn not available. Install with: pip install scikit-learn")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available. Install with: pip install nltk")

try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False
    print("BERTopic not available. Install with: pip install bertopic")

try:
    import yake
    YAKE_AVAILABLE = True
except ImportError:
    YAKE_AVAILABLE = False
    print("YAKE not available. Install with: pip install yake")

try:
    from rake_nltk import Rake
    RAKE_AVAILABLE = True
except ImportError:
    RAKE_AVAILABLE = False
    print("RAKE not available. Install with: pip install rake-nltk")


@dataclass
class TopicResult:
    """Result of topic modeling."""
    text: str
    topics: List[Dict[str, Any]]  # List of topics with words and scores
    dominant_topic: int
    dominant_topic_label: str
    topic_distribution: Dict[int, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'topics': self.topics,
            'dominant_topic': self.dominant_topic,
            'dominant_topic_label': self.dominant_topic_label,
            'topic_distribution': self.topic_distribution,
        }


@dataclass
class KeyphraseResult:
    """Result of keyphrase extraction."""
    text: str
    keyphrases: List[Tuple[str, float]]  # List of (keyphrase, score) tuples
    top_keyphrases: List[str]  # Top keyphrases
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'keyphrases': [{'phrase': kp[0], 'score': kp[1]} for kp in self.keyphrases],
            'top_keyphrases': self.top_keyphrases,
        }


class TopicModeler:
    """
    Performs topic modeling on text data.
    """
    
    def __init__(self, method: str = 'lda', num_topics: int = 5):
        """
        Initialize topic modeler.
        
        Args:
            method: Topic modeling method ('lda', 'nmf', 'bertopic').
            num_topics: Number of topics to extract.
        """
        self.method = method
        self.num_topics = num_topics
        self._initialize()
    
    def _initialize(self):
        """Initialize the topic modeler."""
        if self.method == 'lda' and not GENSIM_AVAILABLE:
            raise RuntimeError("LDA requires gensim. Install with: pip install gensim")
        elif self.method == 'nmf' and not SKLEARN_AVAILABLE:
            raise RuntimeError("NMF requires scikit-learn. Install with: pip install scikit-learn")
        elif self.method == 'bertopic' and not BERTOPIC_AVAILABLE:
            raise RuntimeError("BERTopic requires bertopic. Install with: pip install bertopic")
        
        # Download NLTK data if available
        if NLTK_AVAILABLE:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                nltk.download('wordnet', quiet=True)
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text for topic modeling.
        
        Args:
            text: Text to preprocess.
            
        Returns:
            List of preprocessed tokens.
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Tokenize
        if NLTK_AVAILABLE:
            tokens = word_tokenize(text)
        else:
            tokens = text.split()
        
        # Remove stopwords
        if NLTK_AVAILABLE:
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token not in stop_words]
        
        # Lemmatize
        if NLTK_AVAILABLE:
            lemmatizer = WordNetLemmatizer()
            tokens = [lemmatizer.lemmatize(token) for token in tokens]
        
        # Remove short tokens
        tokens = [token for token in tokens if len(token) > 2]
        
        return tokens
    
    def extract_topics_lda(self, documents: List[str], num_topics: int = None) -> List[TopicResult]:
        """
        Extract topics using LDA.
        
        Args:
            documents: List of document texts.
            num_topics: Number of topics to extract.
            
        Returns:
            List of TopicResult objects.
        """
        if not GENSIM_AVAILABLE:
            return []
        
        num_topics = num_topics or self.num_topics
        
        # Preprocess documents
        processed_docs = [self.preprocess_text(doc) for doc in documents]
        
        # Create dictionary and corpus
        dictionary = corpora.Dictionary(processed_docs)
        corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
        
        # Train LDA model
        lda_model = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            random_state=42,
            passes=10,
        )
        
        # Get topics for each document
        results = []
        for i, doc in enumerate(documents):
            # Get topic distribution for this document
            bow = dictionary.doc2bow(processed_docs[i])
            topic_dist = lda_model.get_document_topics(bow, minimum_probability=0.0)
            
            # Get top topics
            topics = []
            for topic_id, prob in topic_dist:
                # Get top words for this topic
                words = lda_model.show_topic(topic_id, topn=5)
                topics.append({
                    'id': topic_id,
                    'probability': prob,
                    'words': [word for word, _ in words],
                })
            
            # Sort topics by probability
            topics.sort(key=lambda x: x['probability'], reverse=True)
            
            # Get dominant topic
            dominant_topic = topics[0]['id'] if topics else 0
            dominant_topic_label = f"Topic {dominant_topic}"
            
            # Create topic distribution dict
            topic_distribution = {t['id']: t['probability'] for t in topics}
            
            results.append(TopicResult(
                text=doc,
                topics=topics,
                dominant_topic=dominant_topic,
                dominant_topic_label=dominant_topic_label,
                topic_distribution=topic_distribution,
            ))
        
        return results
    
    def extract_topics_nmf(self, documents: List[str], num_topics: int = None) -> List[TopicResult]:
        """
        Extract topics using NMF.
        
        Args:
            documents: List of document texts.
            num_topics: Number of topics to extract.
            
        Returns:
            List of TopicResult objects.
        """
        if not SKLEARN_AVAILABLE:
            return []
        
        num_topics = num_topics or self.num_topics
        
        # Preprocess documents
        processed_docs = [' '.join(self.preprocess_text(doc)) for doc in documents]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(processed_docs)
        
        # Train NMF model
        nmf_model = NMF(
            n_components=num_topics,
            random_state=42,
            max_iter=1000,
        )
        nmf_features = nmf_model.fit_transform(tfidf_matrix)
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Get topics for each document
        results = []
        for i, doc in enumerate(documents):
            # Get topic distribution for this document
            topic_dist = nmf_features[i]
            
            # Get top topics
            topics = []
            for topic_id in range(num_topics):
                prob = topic_dist[topic_id]
                if prob > 0.01:  # Only include significant topics
                    # Get top words for this topic
                    top_indices = nmf_model.components_[topic_id].argsort()[-5:][::-1]
                    words = [feature_names[idx] for idx in top_indices]
                    topics.append({
                        'id': topic_id,
                        'probability': float(prob),
                        'words': words,
                    })
            
            # Sort topics by probability
            topics.sort(key=lambda x: x['probability'], reverse=True)
            
            # Get dominant topic
            dominant_topic = topics[0]['id'] if topics else 0
            dominant_topic_label = f"Topic {dominant_topic}"
            
            # Create topic distribution dict
            topic_distribution = {t['id']: t['probability'] for t in topics}
            
            results.append(TopicResult(
                text=doc,
                topics=topics,
                dominant_topic=dominant_topic,
                dominant_topic_label=dominant_topic_label,
                topic_distribution=topic_distribution,
            ))
        
        return results
    
    def extract_topics(self, documents: List[str], num_topics: int = None) -> List[TopicResult]:
        """
        Extract topics from documents.
        
        Args:
            documents: List of document texts.
            num_topics: Number of topics to extract.
            
        Returns:
            List of TopicResult objects.
        """
        if self.method == 'lda':
            return self.extract_topics_lda(documents, num_topics)
        elif self.method == 'nmf':
            return self.extract_topics_nmf(documents, num_topics)
        elif self.method == 'bertopic' and BERTOPIC_AVAILABLE:
            return self.extract_topics_bertopic(documents, num_topics)
        else:
            # Fall back to LDA
            return self.extract_topics_lda(documents, num_topics)
    
    def extract_topics_bertopic(self, documents: List[str], num_topics: int = None) -> List[TopicResult]:
        """
        Extract topics using BERTopic.
        
        Args:
            documents: List of document texts.
            num_topics: Number of topics to extract.
            
        Returns:
            List of TopicResult objects.
        """
        if not BERTOPIC_AVAILABLE:
            return []
        
        num_topics = num_topics or self.num_topics
        
        # Initialize BERTopic
        topic_model = BERTopic(nr_topics=num_topics)
        
        # Fit the model
        topics, probs = topic_model.fit_transform(documents)
        
        # Get topic info
        topic_info = topic_model.get_topic_info()
        
        # Get topics for each document
        results = []
        for i, doc in enumerate(documents):
            topic_id = topics[i]
            prob = probs[i]
            
            # Get topic label
            topic_row = topic_info[topic_info['Topic'] == topic_id]
            if not topic_row.empty:
                topic_label = topic_row.iloc[0]['Name']
                words = [word for word in topic_label.split('_') if word]
            else:
                topic_label = f"Topic {topic_id}"
                words = []
            
            topics = [{
                'id': topic_id,
                'probability': float(prob),
                'words': words,
                'label': topic_label,
            }]
            
            results.append(TopicResult(
                text=doc,
                topics=topics,
                dominant_topic=topic_id,
                dominant_topic_label=topic_label,
                topic_distribution={topic_id: float(prob)},
            ))
        
        return results
    
    def extract_keyphrases_yake(self, text: str, num_keyphrases: int = 10) -> KeyphraseResult:
        """
        Extract keyphrases using YAKE.
        
        Args:
            text: Text to analyze.
            num_keyphrases: Number of keyphrases to extract.
            
        Returns:
            KeyphraseResult object.
        """
        if not YAKE_AVAILABLE:
            return KeyphraseResult(text=text, keyphrases=[], top_keyphrases=[])
        
        # Initialize YAKE
        language = "en"
        max_ngram_size = 3
        deduplication_threshold = 0.9
        deduplication_algo = 'seqm'
        windowSize = 1
        numOfKeywords = num_keyphrases
        
        extractor = yake.KeywordExtractor(
            lan=language,
            n=max_ngram_size,
            dedupLim=deduplication_threshold,
            dedupFunc=deduplication_algo,
            windowsSize=windowSize,
            top=numOfKeywords,
            features=None,
        )
        
        # Extract keyphrases
        keywords = extractor.extract_keywords(text)
        
        # Sort by score
        keywords.sort(key=lambda x: x[1], reverse=True)
        
        # Get top keyphrases
        top_keyphrases = [kw[0] for kw in keywords[:num_keyphrases]]
        
        return KeyphraseResult(
            text=text,
            keyphrases=keywords,
            top_keyphrases=top_keyphrases,
        )
    
    def extract_keyphrases_rake(self, text: str, num_keyphrases: int = 10) -> KeyphraseResult:
        """
        Extract keyphrases using RAKE.
        
        Args:
            text: Text to analyze.
            num_keyphrases: Number of keyphrases to extract.
            
        Returns:
            KeyphraseResult object.
        """
        if not RAKE_AVAILABLE:
            return KeyphraseResult(text=text, keyphrases=[], top_keyphrases=[])
        
        # Initialize RAKE
        r = Rake(
            min_length=1,
            max_length=3,
            stopwords=stopwords.words('english') if NLTK_AVAILABLE else None,
        )
        
        # Extract keyphrases
        r.extract_keywords_from_text(text)
        keywords = r.get_ranked_phrases_with_scores()
        
        # Sort by score
        keywords.sort(key=lambda x: x[1], reverse=True)
        
        # Get top keyphrases
        top_keyphrases = [kw[0] for kw in keywords[:num_keyphrases]]
        
        return KeyphraseResult(
            text=text,
            keyphrases=keywords,
            top_keyphrases=top_keyphrases,
        )
    
    def extract_keyphrases(self, text: str, method: str = 'rake', num_keyphrases: int = 10) -> KeyphraseResult:
        """
        Extract keyphrases from text.
        
        Args:
            text: Text to analyze.
            method: Keyphrase extraction method ('rake', 'yake').
            num_keyphrases: Number of keyphrases to extract.
            
        Returns:
            KeyphraseResult object.
        """
        if method == 'yake' and YAKE_AVAILABLE:
            return self.extract_keyphrases_yake(text, num_keyphrases)
        elif method == 'rake' and RAKE_AVAILABLE:
            return self.extract_keyphrases_rake(text, num_keyphrases)
        elif RAKE_AVAILABLE:
            return self.extract_keyphrases_rake(text, num_keyphrases)
        elif YAKE_AVAILABLE:
            return self.extract_keyphrases_yake(text, num_keyphrases)
        else:
            # Fall back to simple word frequency
            return self.extract_keyphrases_simple(text, num_keyphrases)
    
    def extract_keyphrases_simple(self, text: str, num_keyphrases: int = 10) -> KeyphraseResult:
        """
        Extract keyphrases using simple word frequency.
        
        Args:
            text: Text to analyze.
            num_keyphrases: Number of keyphrases to extract.
            
        Returns:
            KeyphraseResult object.
        """
        # Tokenize and count
        tokens = self.preprocess_text(text)
        word_counts = Counter(tokens)
        
        # Get top words
        top_words = word_counts.most_common(num_keyphrases)
        
        # Convert to keyphrase format
        keyphrases = [(word, count) for word, count in top_words]
        top_keyphrases = [word for word, _ in top_words]
        
        return KeyphraseResult(
            text=text,
            keyphrases=keyphrases,
            top_keyphrases=top_keyphrases,
        )


# Singleton instance
topic_modeler = TopicModeler()


def extract_topics(documents: List[str], method: str = 'lda', num_topics: int = 5) -> List[TopicResult]:
    """
    Extract topics from documents.
    
    Args:
        documents: List of document texts.
        method: Topic modeling method ('lda', 'nmf', 'bertopic').
        num_topics: Number of topics to extract.
        
    Returns:
        List of TopicResult objects.
    """
    modeler = TopicModeler(method, num_topics)
    return modeler.extract_topics(documents)


def extract_keyphrases(text: str, method: str = 'rake', num_keyphrases: int = 10) -> KeyphraseResult:
    """
    Extract keyphrases from text.
    
    Args:
        text: Text to analyze.
        method: Keyphrase extraction method ('rake', 'yake').
        num_keyphrases: Number of keyphrases to extract.
        
    Returns:
        KeyphraseResult object.
    """
    modeler = TopicModeler()
    return modeler.extract_keyphrases(text, method, num_keyphrases)
