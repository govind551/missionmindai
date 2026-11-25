import math
import re

def compute_lexical_overlap(query: str, text: str) -> float:
    """Calculates normalized token overlap between query and chunk"""
    # Extract lowercase alphanumeric terms, ignoring common stop words
    stop_words = {
        "what", "went", "wrong", "with", "on", "past", "in", "the", "a", "an", "and", "or",
        "is", "was", "were", "to", "of", "for", "by", "about", "did", "how", "why", "our"
    }
    query_tokens = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', query.lower())) - stop_words
    if not query_tokens:
        return 0.0
    
    text_lower = text.lower()
    matches = sum(1 for token in query_tokens if token in text_lower)
    return matches / len(query_tokens)

def calculate_retrieval_confidence(dense_score: float, lexical_score: float) -> float:
    """
    Combines dense cosine similarity (0 to 1) and lexical keyword overlap (0 to 1).
    Weights: 65% dense vector semantic similarity, 35% lexical token coverage.
    """
    dense_clamped = max(0.0, min(1.0, dense_score))
    lexical_clamped = max(0.0, min(1.0, lexical_score))
    
    combined = (0.65 * dense_clamped) + (0.35 * lexical_clamped)
    return round(combined, 4)
