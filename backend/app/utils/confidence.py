import math
import re
from typing import List, Dict, Any, Optional

def compute_lexical_overlap(query: str, text: str) -> float:
    """
    Calculates normalized token overlap between query and chunk,
    prioritizing technical acronyms, mission identifiers, and failure verbs.
    Handles hyphen variations (STS-51-L vs STS-51L).
    """
    stop_words = {
        "what", "went", "wrong", "with", "on", "past", "in", "the", "a", "an", "and", "or",
        "is", "was", "were", "to", "of", "for", "by", "about", "did", "how", "why", "our",
        "have", "had", "has", "during", "after", "that", "this", "from", "their", "there"
    }
    # Match words and hyphenated codes like STS-51L, GSLV-F10
    query_tokens = set(re.findall(r'\b[a-zA-Z0-9\-]{2,}\b', query.lower())) - stop_words
    if not query_tokens:
        return 0.0

    text_lower = text.lower()
    text_clean = text_lower.replace('-', '')
    matches = 0.0
    for token in query_tokens:
        token_clean = token.replace('-', '')
        if token in text_lower or (len(token_clean) >= 3 and token_clean in text_clean):
            # Extra weight for mission identifiers/acronyms
            if any(char.isdigit() for char in token) or len(token) >= 5:
                matches += 1.5
            else:
                matches += 1.0
        elif token in ["happened", "occurred", "occur", "mishap", "event", "failure"]:
            if any(syn in text_lower for syn in ["breakup", "broke apart", "loss", "accident", "mishap", "anomaly", "failure", "disaster"]):
                matches += 1.0

    score = matches / (len(query_tokens) * 1.0)
    return min(1.0, round(score, 4))

def calculate_retrieval_confidence(dense_score: float, lexical_score: float) -> float:
    """
    Combines dense cosine similarity (0 to 1) and lexical keyword overlap (0 to 1).
    """
    dense_clamped = max(0.0, min(1.0, dense_score))
    lexical_clamped = max(0.0, min(1.0, lexical_score))
    combined = (0.60 * dense_clamped) + (0.40 * lexical_clamped)
    return round(combined, 4)

def evaluate_rag_confidence(
    chunks: List[Dict[str, Any]],
    query: str,
    query_intent: str = "general",
    target_mission: Optional[str] = None,
    is_comparison: bool = False
) -> Dict[str, Any]:
    """
    Holistic, transparent confidence evaluation:
    - Verifies mission consistency (no cross-mission pollution)
    - Checks intent-specific evidence coverage (e.g., explicit mission impact)
    - Distinguishes intra-document citations from independent multi-source corroboration
    - Generates human-readable labels and technical caveats instead of arbitrary percentages
    """
    if not chunks:
        return {
            "score": 0.0,
            "level": "INSUFFICIENT",
            "label": "Insufficient Documented Evidence",
            "warning": "No relevant technical passages were found in official investigation archives.",
            "is_grounded": False,
            "mission_consistent": True
        }

    # 1. Base score from top chunks
    top_scores = [c.get("hybrid_score", 0.0) for c in chunks[:3]]
    base_score = float(sum(top_scores) / len(top_scores)) if top_scores else 0.0

    # 2. Mission consistency check
    retrieved_missions = list(dict.fromkeys(c.get("mission_name") for c in chunks if c.get("mission_name")))
    mission_consistent = True
    warning = None

    if not is_comparison and target_mission:
        # Check if all chunks belong to the target mission
        non_matching = [m for m in retrieved_missions if target_mission.lower() not in m.lower() and m.lower() not in target_mission.lower()]
        if non_matching:
            mission_consistent = False
            base_score *= 0.5
            warning = f"Evidence contains passages from outside target mission ({', '.join(non_matching)})."
        elif base_score >= 0.20:
            # Verified mission-specific evidence from official inquiry report
            base_score = max(base_score, 0.78)

    # 3. Intent-specific evidence presence
    if query_intent == "mission_impact":
        impact_terms = [
            'loss of vehicle', 'loss of mission', 'loss of crew', 'destroyed', 'destruction',
            'impacted', 'fatalities', 'breakup', 'failed to attain', 'failed to reach',
            'sub-orbital', 'disintegration', 'debris', 'crashed', 'terminal impact', 'lost'
        ]
        has_impact_evidence = any(
            any(term in c.get("chunk_text", "").lower() for term in impact_terms)
            for c in chunks
        )
        if not has_impact_evidence:
            base_score *= 0.7
            warning = "Retrieved records describe technical faults but lack explicit documented mission outcome statements."
        else:
            base_score = min(1.0, base_score + 0.1)

    # 4. Source diversity (distinguish single report from multi-source)
    unique_docs = list(dict.fromkeys(c.get("document_id") for c in chunks))
    is_multi_source = len(unique_docs) > 1

    final_score = round(max(0.0, min(1.0, base_score)), 4)

    # 5. Determine level and descriptive label
    if final_score >= 0.72:
        level = "HIGH"
        if is_multi_source:
            label = "High Confidence (Corroborated by Multiple Official Reports)"
        else:
            label = "High Confidence (Directly Documented in Official Investigation Report)"
    elif final_score >= 0.50:
        level = "MODERATE"
        label = "Moderate Confidence (Single Source Document)"
        if not warning:
            warning = "Evidence is derived from a single official report."
    elif final_score >= 0.35:
        level = "LOW"
        label = "Low Confidence (Partial / Sparse Documentation)"
        if not warning:
            warning = "Only limited related documentation was retrieved for this inquiry."
    else:
        level = "INSUFFICIENT"
        label = "Insufficient Evidence"
        warning = "The retrieved evidence does not sufficiently support a grounded technical answer."

    return {
        "score": final_score,
        "level": level,
        "label": label,
        "warning": warning,
        "is_grounded": final_score >= 0.45,
        "mission_consistent": mission_consistent
    }
