"""
Sentiment Analyzer for OpenLens

Provides sentiment analysis functionality using:
- VADER (Valence Aware Dictionary and sEntiment Reasoner)
- TextBlob (for more nuanced sentiment)
- Custom sentiment lexicons

Dependencies:
- vaderSentiment: For VADER sentiment analysis
- textblob: For TextBlob sentiment analysis (optional)
- nltk: For natural language processing (optional)
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json

# Try to import optional dependencies
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("VADER not available. Install with: pip install vaderSentiment")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("TextBlob not available. Install with: pip install textblob")

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer as NLTKSentimentAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available. Install with: pip install nltk")


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    text: str
    sentiment: str  # 'positive', 'neutral', 'negative'
    compound: float  # Compound score (-1 to 1)
    positive: float  # Positive score (0 to 1)
    negative: float  # Negative score (0 to 1)
    neutral: float  # Neutral score (0 to 1)
    confidence: float  # Confidence score (0 to 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'sentiment': self.sentiment,
            'compound': self.compound,
            'positive': self.positive,
            'negative': self.negative,
            'neutral': self.neutral,
            'confidence': self.confidence,
        }


class SentimentAnalyzer:
    """
    Analyzes text sentiment using various methods.
    """
    
    def __init__(self, method: str = 'vader'):
        """
        Initialize sentiment analyzer.
        
        Args:
            method: Sentiment analysis method ('vader', 'textblob', 'nltk').
        """
        self.method = method
        self._initialize()
    
    def _initialize(self):
        """Initialize the sentiment analyzer."""
        if self.method == 'vader' and VADER_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()
        elif self.method == 'textblob' and TEXTBLOB_AVAILABLE:
            # TextBlob doesn't need initialization
            pass
        elif self.method == 'nltk' and NLTK_AVAILABLE:
            # Download VADER lexicon if not already downloaded
            try:
                nltk.data.find('sentiment/vader_lexicon.zip')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)
            self.analyzer = NLTKSentimentAnalyzer()
        else:
            # Fall back to VADER if available
            if VADER_AVAILABLE:
                self.method = 'vader'
                self.analyzer = SentimentIntensityAnalyzer()
            else:
                raise RuntimeError(
                    f"Sentiment analysis method '{self.method}' not available. "
                    "Install required packages or use 'vader' method."
                )
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze the sentiment of a text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            SentimentResult object.
        """
        if not text or not text.strip():
            return SentimentResult(
                text=text,
                sentiment='neutral',
                compound=0.0,
                positive=0.0,
                negative=0.0,
                neutral=1.0,
                confidence=0.0,
            )
        
        if self.method == 'vader':
            return self._analyze_vader(text)
        elif self.method == 'textblob':
            return self._analyze_textblob(text)
        elif self.method == 'nltk':
            return self._analyze_nltk(text)
        else:
            # Fall back to VADER
            return self._analyze_vader(text)
    
    def _analyze_vader(self, text: str) -> SentimentResult:
        """Analyze sentiment using VADER."""
        scores = self.analyzer.polarity_scores(text)
        
        # Determine sentiment label
        compound = scores.get('compound', 0)
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence
        confidence = abs(compound)
        
        return SentimentResult(
            text=text,
            sentiment=sentiment,
            compound=compound,
            positive=scores.get('pos', 0.0),
            negative=scores.get('neg', 0.0),
            neutral=scores.get('neu', 0.0),
            confidence=confidence,
        )
    
    def _analyze_textblob(self, text: str) -> SentimentResult:
        """Analyze sentiment using TextBlob."""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine sentiment label
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Map to VADER-like scores
        compound = polarity
        positive = max(0, polarity)
        negative = max(0, -polarity)
        neutral = 1 - (positive + negative)
        confidence = abs(polarity)
        
        return SentimentResult(
            text=text,
            sentiment=sentiment,
            compound=compound,
            positive=positive,
            negative=negative,
            neutral=neutral,
            confidence=confidence,
        )
    
    def _analyze_nltk(self, text: str) -> SentimentResult:
        """Analyze sentiment using NLTK VADER."""
        scores = self.analyzer.polarity_scores(text)
        
        # Determine sentiment label
        compound = scores.get('compound', 0)
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence
        confidence = abs(compound)
        
        return SentimentResult(
            text=text,
            sentiment=sentiment,
            compound=compound,
            positive=scores.get('pos', 0.0),
            negative=scores.get('neg', 0.0),
            neutral=scores.get('neu', 0.0),
            confidence=confidence,
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze sentiment for a batch of texts.
        
        Args:
            texts: List of texts to analyze.
            
        Returns:
            List of SentimentResult objects.
        """
        return [self.analyze(text) for text in texts]
    
    def get_sentiment_distribution(self, texts: List[str]) -> Dict[str, int]:
        """
        Get sentiment distribution for a list of texts.
        
        Args:
            texts: List of texts to analyze.
            
        Returns:
            Dictionary with sentiment counts.
        """
        results = self.analyze_batch(texts)
        distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for result in results:
            distribution[result.sentiment] += 1
        
        return distribution
    
    def get_average_sentiment(self, texts: List[str]) -> SentimentResult:
        """
        Get average sentiment for a list of texts.
        
        Args:
            texts: List of texts to analyze.
            
        Returns:
            SentimentResult with average scores.
        """
        if not texts:
            return SentimentResult(
                text='',
                sentiment='neutral',
                compound=0.0,
                positive=0.0,
                negative=0.0,
                neutral=1.0,
                confidence=0.0,
            )
        
        results = self.analyze_batch(texts)
        
        # Calculate averages
        total = len(results)
        avg_compound = sum(r.compound for r in results) / total
        avg_positive = sum(r.positive for r in results) / total
        avg_negative = sum(r.negative for r in results) / total
        avg_neutral = sum(r.neutral for r in results) / total
        avg_confidence = sum(r.confidence for r in results) / total
        
        # Determine average sentiment
        if avg_compound >= 0.05:
            sentiment = 'positive'
        elif avg_compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return SentimentResult(
            text=f"{total} texts",
            sentiment=sentiment,
            compound=avg_compound,
            positive=avg_positive,
            negative=avg_negative,
            neutral=avg_neutral,
            confidence=avg_confidence,
        )


# Singleton instance
sentiment_analyzer = SentimentAnalyzer()


def analyze_sentiment(text: str, method: str = 'vader') -> SentimentResult:
    """
    Analyze sentiment of a text.
    
    Args:
        text: Text to analyze.
        method: Sentiment analysis method ('vader', 'textblob', 'nltk').
        
    Returns:
        SentimentResult object.
    """
    analyzer = SentimentAnalyzer(method)
    return analyzer.analyze(text)


def analyze_sentiment_batch(texts: List[str], method: str = 'vader') -> List[SentimentResult]:
    """
    Analyze sentiment for a batch of texts.
    
    Args:
        texts: List of texts to analyze.
        method: Sentiment analysis method.
        
    Returns:
        List of SentimentResult objects.
    """
    analyzer = SentimentAnalyzer(method)
    return analyzer.analyze_batch(texts)
