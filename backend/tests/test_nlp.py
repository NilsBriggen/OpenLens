"""
Unit Tests for NLP Module

Tests for:
- Sentiment analysis
- Topic modeling
- Keyphrase extraction
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.sentiment_analyzer import (
    SentimentAnalyzer, SentimentResult, analyze_sentiment, analyze_sentiment_batch
)
from nlp.topic_modeler import (
    TopicModeler, TopicResult, KeyphraseResult, extract_topics, extract_keyphrases
)


class TestSentimentAnalyzer(unittest.TestCase):
    """Test sentiment analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = SentimentAnalyzer()
    
    def test_analyze_positive_text(self):
        """Test analyzing positive text."""
        result = self.analyzer.analyze("I love this product! It's amazing.")
        
        self.assertIsInstance(result, SentimentResult)
        self.assertEqual(result.text, "I love this product! It's amazing.")
        self.assertEqual(result.sentiment, 'positive')
        self.assertGreater(result.compound, 0)
        self.assertGreater(result.confidence, 0)
    
    def test_analyze_negative_text(self):
        """Test analyzing negative text."""
        result = self.analyzer.analyze("I hate this product. It's terrible.")
        
        self.assertIsInstance(result, SentimentResult)
        self.assertEqual(result.sentiment, 'negative')
        self.assertLess(result.compound, 0)
    
    def test_analyze_neutral_text(self):
        """Test analyzing neutral text."""
        result = self.analyzer.analyze("This is a neutral statement.")
        
        self.assertIsInstance(result, SentimentResult)
        self.assertEqual(result.sentiment, 'neutral')
        self.assertAlmostEqual(result.compound, 0, delta=0.1)
    
    def test_analyze_empty_text(self):
        """Test analyzing empty text."""
        result = self.analyzer.analyze("")
        
        self.assertIsInstance(result, SentimentResult)
        self.assertEqual(result.sentiment, 'neutral')
        self.assertEqual(result.compound, 0.0)
    
    def test_analyze_batch(self):
        """Test analyzing a batch of texts."""
        texts = [
            "I love this!",
            "I hate this!",
            "This is okay."
        ]
        
        results = self.analyzer.analyze_batch(texts)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].sentiment, 'positive')
        self.assertEqual(results[1].sentiment, 'negative')
        self.assertEqual(results[2].sentiment, 'neutral')
    
    def test_get_sentiment_distribution(self):
        """Test getting sentiment distribution."""
        texts = [
            "I love this!",
            "I love this too!",
            "I hate this!",
            "This is okay.",
            "Another neutral statement."
        ]
        
        distribution = self.analyzer.get_sentiment_distribution(texts)
        
        self.assertEqual(distribution['positive'], 2)
        self.assertEqual(distribution['negative'], 1)
        self.assertEqual(distribution['neutral'], 2)
    
    def test_get_average_sentiment(self):
        """Test getting average sentiment."""
        texts = [
            "I love this!",
            "I love this too!",
            "I hate this!"
        ]
        
        result = self.analyzer.get_average_sentiment(texts)
        
        self.assertIsInstance(result, SentimentResult)
        # Average should be positive (2 positive, 1 negative)
        self.assertGreater(result.compound, 0)
    
    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = self.analyzer.analyze("Test text")
        result_dict = result.to_dict()
        
        self.assertIn('text', result_dict)
        self.assertIn('sentiment', result_dict)
        self.assertIn('compound', result_dict)
        self.assertIn('positive', result_dict)
        self.assertIn('negative', result_dict)
        self.assertIn('neutral', result_dict)
        self.assertIn('confidence', result_dict)


class TestTopicModeler(unittest.TestCase):
    """Test topic modeling functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.modeler = TopicModeler(method='lda', num_topics=3)
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        text = "This is a TEST text with URLs: https://example.com and special chars!"
        
        tokens = self.modeler.preprocess_text(text)
        
        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)
        # URLs should be removed
        self.assertNotIn('https', tokens)
        # Should be lowercase
        self.assertEqual(tokens, [t.lower() for t in tokens])
    
    def test_extract_keyphrases_simple(self):
        """Test simple keyphrase extraction."""
        text = "This is a test text about natural language processing and machine learning."
        
        result = self.modeler.extract_keyphrases_simple(text, num_keyphrases=5)
        
        self.assertIsInstance(result, KeyphraseResult)
        self.assertEqual(result.text, text)
        self.assertIsInstance(result.keyphrases, list)
        self.assertIsInstance(result.top_keyphrases, list)
        self.assertEqual(len(result.top_keyphrases), 5)
    
    def test_extract_keyphrases(self):
        """Test keyphrase extraction with fallback."""
        text = "This is a test text about natural language processing and machine learning."
        
        result = self.modeler.extract_keyphrases(text, method='simple', num_keyphrases=5)
        
        self.assertIsInstance(result, KeyphraseResult)
        self.assertEqual(result.text, text)


class TestTopicModelerNMF(unittest.TestCase):
    """Test NMF topic modeling."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use NMF method which requires sklearn
        try:
            self.modeler = TopicModeler(method='nmf', num_topics=2)
        except RuntimeError:
            # Skip if sklearn not available
            self.skipTest("scikit-learn not available")
    
    def test_extract_topics_nmf(self):
        """Test NMF topic extraction."""
        documents = [
            "This is a document about machine learning and artificial intelligence.",
            "Another document about deep learning and neural networks.",
            "This document is about natural language processing.",
            "Yet another document about computer vision and image recognition."
        ]
        
        results = self.modeler.extract_topics_nmf(documents, num_topics=2)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 4)
        
        for result in results:
            self.assertIsInstance(result, TopicResult)
            self.assertIsInstance(result.topics, list)
            self.assertIn('dominant_topic', result.to_dict())


class TestSentimentAnalyzerFunctions(unittest.TestCase):
    """Test sentiment analyzer convenience functions."""
    
    def test_analyze_sentiment(self):
        """Test analyze_sentiment function."""
        result = analyze_sentiment("I love this!")
        
        self.assertIsInstance(result, SentimentResult)
        self.assertEqual(result.sentiment, 'positive')
    
    def test_analyze_sentiment_batch(self):
        """Test analyze_sentiment_batch function."""
        texts = ["I love this!", "I hate this!"]
        results = analyze_sentiment_batch(texts)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].sentiment, 'positive')
        self.assertEqual(results[1].sentiment, 'negative')


class TestTopicModelerFunctions(unittest.TestCase):
    """Test topic modeler convenience functions."""
    
    def test_extract_keyphrases(self):
        """Test extract_keyphrases function."""
        result = extract_keyphrases(
            "This is a test text about natural language processing.",
            method='simple',
            num_keyphrases=3
        )
        
        self.assertIsInstance(result, KeyphraseResult)
        self.assertEqual(len(result.top_keyphrases), 3)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_document_list(self):
        """Test with empty document list."""
        modeler = TopicModeler()
        
        # Should handle empty list gracefully
        result = modeler.extract_keyphrases_simple("", num_keyphrases=5)
        self.assertIsInstance(result, KeyphraseResult)
    
    def test_very_short_text(self):
        """Test with very short text."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("a")
        self.assertIsInstance(result, SentimentResult)
    
    def test_special_characters(self):
        """Test with special characters."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("Test with special chars: !@#$%^&*()")
        self.assertIsInstance(result, SentimentResult)
    
    def test_unicode_text(self):
        """Test with unicode text."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("This is a test with unicode: \u2764\ufe0f")
        self.assertIsInstance(result, SentimentResult)


if __name__ == '__main__':
    unittest.main()
