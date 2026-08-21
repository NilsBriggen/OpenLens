"""
NLP Module for OpenLens

Provides advanced NLP functionality:
- Sentiment Analysis
- Topic Modeling
- Text Classification
- Keyphrase Extraction

Usage:
    from nlp.sentiment_analyzer import SentimentAnalyzer, analyze_sentiment
    from nlp.topic_modeler import TopicModeler, extract_topics
"""

from .sentiment_analyzer import SentimentAnalyzer, analyze_sentiment
from .topic_modeler import TopicModeler, extract_topics

__all__ = [
    'SentimentAnalyzer',
    'analyze_sentiment',
    'TopicModeler',
    'extract_topics',
]
