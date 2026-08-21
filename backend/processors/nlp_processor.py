"""
NLP Processor for OpenLens

Uses spaCy for entity extraction (people, organizations, locations, dates, etc.)
and text analysis (keywords, sentiment, etc.).

Dependencies:
- spacy: For NLP processing
- en_core_web_sm: spaCy English language model
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import spacy
from spacy.tokens import Span


# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    nlp = None


@dataclass
class ExtractedEntity:
    """Represents an extracted entity from text."""
    text: str
    label: str
    start: int
    end: int
    confidence: Optional[float] = None


@dataclass
class NLPResult:
    """Represents the result of NLP processing."""
    text: str
    entities: List[ExtractedEntity]
    people: List[str]
    organizations: List[str]
    locations: List[str]
    dates: List[str]
    keywords: List[str]
    sentiment: Optional[Dict[str, Any]] = None
    language: str = "en"


class NLPProcessor:
    """
    Processes text using NLP to extract entities, keywords, and other metadata.
    """

    # Entity labels to extract
    ENTITY_LABELS = [
        "PERSON",      # People
        "ORG",         # Organizations
        "GPE",         # Geo-political entities (countries, cities, states)
        "LOC",         # Non-GPE locations (mountains, rivers, etc.)
        "DATE",        # Dates
        "TIME",        # Times
        "MONEY",       # Monetary values
        "PERCENT",     # Percentages
        "WORK_OF_ART", # Titles of works (books, songs, etc.)
        "EVENT",       # Named events
        "LAW",         # Legal entities
        "LANGUAGE",    # Languages
        "NORP",        # Nationalities or religious/political groups
        "FAC",         # Facilities (buildings, airports, etc.)
    ]

    def __init__(self):
        """Initialize the NLP processor."""
        if nlp is None:
            raise ImportError("spaCy model not loaded. Run: python -m spacy download en_core_web_sm")

    def extract_entities(self, text: str) -> NLPResult:
        """
        Extract entities from text using spaCy.
        
        Args:
            text: Input text.
            
        Returns:
            NLPResult object with extracted entities and metadata.
        """
        doc = nlp(text)
        
        entities = []
        people = []
        organizations = []
        locations = []
        dates = []
        
        for ent in doc.ents:
            entity = ExtractedEntity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
            )
            entities.append(entity)
            
            # Categorize entities
            if ent.label_ == "PERSON":
                people.append(ent.text)
            elif ent.label_ == "ORG":
                organizations.append(ent.text)
            elif ent.label_ in ["GPE", "LOC", "FAC"]:
                locations.append(ent.text)
            elif ent.label_ == "DATE":
                dates.append(ent.text)
        
        # Extract keywords (nouns and proper nouns)
        keywords = self._extract_keywords(doc)
        
        return NLPResult(
            text=text,
            entities=entities,
            people=people,
            organizations=organizations,
            locations=locations,
            dates=dates,
            keywords=keywords,
        )

    def _extract_keywords(self, doc) -> List[str]:
        """
        Extract keywords (nouns and proper nouns) from a spaCy doc.
        
        Args:
            doc: spaCy Doc object.
            
        Returns:
            List of keywords.
        """
        keywords = []
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and token.text.lower() not in spacy.lang.en.stop_words.STOP_WORDS:
                keywords.append(token.text)
        return list(set(keywords))  # Remove duplicates

    def extract_people(self, text: str) -> List[str]:
        """
        Extract person names from text.
        
        Args:
            text: Input text.
            
        Returns:
            List of person names.
        """
        result = self.extract_entities(text)
        return result.people

    def extract_organizations(self, text: str) -> List[str]:
        """
        Extract organization names from text.
        
        Args:
            text: Input text.
            
        Returns:
            List of organization names.
        """
        result = self.extract_entities(text)
        return result.organizations

    def extract_locations(self, text: str) -> List[str]:
        """
        Extract location names from text.
        
        Args:
            text: Input text.
            
        Returns:
            List of location names.
        """
        result = self.extract_entities(text)
        return result.locations

    def extract_dates(self, text: str) -> List[str]:
        """
        Extract dates from text.
        
        Args:
            text: Input text.
            
        Returns:
            List of dates.
        """
        result = self.extract_entities(text)
        return result.dates

    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Input text.
            
        Returns:
            List of keywords.
        """
        result = self.extract_entities(text)
        return result.keywords

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis.
        
        Args:
            text: Input text.
            
        Returns:
            Dictionary with analysis results.
        """
        result = self.extract_entities(text)
        
        # Count tokens and sentences
        doc = nlp(text)
        token_count = len(doc)
        sentence_count = len(list(doc.sents))
        
        # Calculate average sentence length
        avg_sentence_length = token_count / sentence_count if sentence_count > 0 else 0
        
        return {
            "text": text,
            "entities": [
                {"text": e.text, "label": e.label, "start": e.start, "end": e.end}
                for e in result.entities
            ],
            "people": result.people,
            "organizations": result.organizations,
            "locations": result.locations,
            "dates": result.dates,
            "keywords": result.keywords,
            "token_count": token_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "language": result.language,
        }

    def extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract potential relationships between entities in text.
        
        Args:
            text: Input text.
            
        Returns:
            List of relationship dictionaries (subject, verb, object).
        """
        relationships = []
        doc = nlp(text)
        
        for sent in doc.sents:
            # Look for subject-verb-object patterns
            for token in sent:
                if token.dep_ == "nsubj" and token.head.dep_ == "ROOT":
                    subject = token.text
                    verb = token.head.text
                    
                    # Find objects
                    for child in token.head.children:
                        if child.dep_ in ["dobj", "pobj", "attr"]:
                            relationships.append({
                                "subject": subject,
                                "verb": verb,
                                "object": child.text,
                                "sentence": sent.text,
                            })
        
        return relationships

    def normalize_text(self, text: str) -> str:
        """
        Normalize text (lowercase, remove extra spaces, etc.).
        
        Args:
            text: Input text.
            
        Returns:
            Normalized text.
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Convert to lowercase
        text = text.lower()
        return text


# Singleton instance for easy use
nlp_processor = NLPProcessor() if nlp else None
