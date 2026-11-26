import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.research_message import ResearchMessage
from app.models.document import Document
from app.core.logging import logger

MISSION_CATALOG = [
    {
        "canonical_name": "Mars Polar Lander / Deep Space 2",
        "keywords": ["mars polar lander", "polar lander", "mpl", "deep space 2", "ds2", "ds-2"],
        "agency": "NASA / JPL",
        "display_name": "Mars Polar Lander / Deep Space 2 (1999)"
    },
    {
        "canonical_name": "Space Shuttle Challenger (STS-51L)",
        "keywords": ["challenger", "sts-51-l", "sts-51l", "sts 51-l", "sts 51l", "sts-51", "51-l", "rogers commission"],
        "agency": "NASA",
        "display_name": "Space Shuttle Challenger, STS-51-L (1986)"
    },
    {
        "canonical_name": "Space Shuttle Columbia (STS-107)",
        "keywords": ["columbia", "sts-107", "sts 107", "sts107", "caib"],
        "agency": "NASA",
        "display_name": "Space Shuttle Columbia, STS-107 (2003)"
    },
    {
        "canonical_name": "Boeing CST-100 Starliner (CFT)",
        "keywords": ["starliner", "cft", "boeing cst-100", "cst-100", "crewed flight test"],
        "agency": "NASA",
        "display_name": "Boeing CST-100 Starliner (CFT) (2024)"
    },
    {
        "canonical_name": "Antares / Orb-3 (2014)",
        "keywords": ["antares", "orb-3", "orb 3", "orb–3", "aj26", "aj-26", "orbital atk"],
        "agency": "NASA",
        "display_name": "Antares / Orb-3 (2014)"
    },
    {
        "canonical_name": "ISRO GSLV-F10 EOS-03 (2021)",
        "keywords": ["gslv-f10", "gslv f10", "eos-03", "eos 03", "gslv", "cus-05"],
        "agency": "ISRO",
        "display_name": "ISRO GSLV-F10 EOS-03 (2021)"
    },
    {
        "canonical_name": "SpaceX CRS-7 Falcon 9 (2015)",
        "keywords": ["crs-7", "crs 7", "falcon 9", "spacex crs-7"],
        "agency": "NASA",
        "display_name": "SpaceX CRS-7 Falcon 9 (2015)"
    },
    {
        "canonical_name": "Ariane 5 Flight 501 (1996)",
        "keywords": ["ariane 5", "flight 501", "ariane 501", "ariane-5", "ariane"],
        "agency": "ESA / CNES",
        "display_name": "Ariane 5 Flight 501 (1996)"
    },
    {
        "canonical_name": "CONTOUR (Comet Nucleus Tour)",
        "keywords": ["contour", "comet nucleus", "star 30bp"],
        "agency": "NASA",
        "display_name": "CONTOUR - Comet Nucleus Tour (2002)"
    },
    {
        "canonical_name": "Mars Climate Orbiter",
        "keywords": ["climate orbiter", "mco", "mars climate"],
        "agency": "NASA",
        "display_name": "Mars Climate Orbiter (1999)"
    },
    {
        "canonical_name": "Genesis Solar Wind Sample Return",
        "keywords": ["genesis", "solar wind", "sample return"],
        "agency": "NASA",
        "display_name": "Genesis Solar Wind Sample Return (2004)"
    },
    {
        "canonical_name": "PSLV-C39 / IRNSS-1H",
        "keywords": ["pslv-c39", "pslv c39", "irnss-1h", "irnss", "pslv"],
        "agency": "ISRO",
        "display_name": "ISRO PSLV-C39 / IRNSS-1H (2017)"
    }
]

def detect_missions_from_text(query: str) -> List[str]:
    """
    Detects canonical mission names mentioned in a query using word boundary matching.
    """
    if not query:
        return []
    q_low = query.lower()
    detected = []
    for item in MISSION_CATALOG:
        for kw in item["keywords"]:
            pattern = r'(?:\b|_)' + re.escape(kw) + r'(?:\b|_)'
            if re.search(pattern, q_low):
                if item["canonical_name"] not in detected:
                    detected.append(item["canonical_name"])
                break
    return detected

def detect_query_intent(query: str) -> str:
    """
    Classifies the user's intent to optimize evidence reranking and response structuring.
    """
    q_low = query.lower()
    if any(w in q_low for w in [
        'impact', 'outcome', 'consequence', 'what happened to', 'loss of', 'casualt',
        'crew', 'fatalit', 'damage', 'end of mission', 'fail to attain', 'failed to reach',
        'destroy', 'breakup', 'result of the failure', 'how did it end'
    ]):
        return "mission_impact"
    if any(w in q_low for w in [
        'root cause', 'why did', 'what caused', 'cause of', 'failure mechanism',
        'proximate cause', 'fault trigger', 'what went wrong', 'origin of'
    ]):
        return "root_cause"
    if any(w in q_low for w in [
        'corrective', 'recommendation', 'action', 'lessons learned', 'prevent', 'fix',
        'redesign', 'return to flight'
    ]):
        return "corrective_action"
    if any(w in q_low for w in [
        'telemetry', 'timeline', 'chronology', 'sequence', 'seconds after', 't-0', 't+',
        'countdown', 'flight day'
    ]):
        return "telemetry_sequence"
    return "general"

def is_comparison_query(query: str) -> bool:
    """
    Checks if query requests a multi-mission comparison.
    """
    q_low = query.lower()
    comparison_triggers = ['compare', 'comparison', 'difference', 'versus', ' vs ', ' vs.', 'differ between', 'both']
    return any(t in q_low for t in comparison_triggers)

def get_active_mission_from_session(db: Session, session_id: Optional[int]) -> Optional[str]:
    """
    Recovers the active mission context from prior conversation messages in the session.
    """
    if not session_id:
        return None

    recent_messages = db.query(ResearchMessage).filter(
        ResearchMessage.session_id == session_id
    ).order_by(ResearchMessage.id.desc()).limit(8).all()

    for msg in recent_messages:
        # Check citations first
        if msg.citations and isinstance(msg.citations, list):
            for cit in msg.citations:
                if isinstance(cit, dict) and cit.get("mission_name"):
                    c_name = cit["mission_name"]
                    # Map to canonical
                    for m in MISSION_CATALOG:
                        if m["canonical_name"].lower() in c_name.lower() or c_name.lower() in m["canonical_name"].lower():
                            return m["canonical_name"]

        # Check message text
        detected = detect_missions_from_text(msg.message_text)
        if len(detected) == 1:
            return detected[0]

    return None

def resolve_query_missions(
    db: Session,
    query: str,
    session_id: Optional[int] = None,
    explicit_mission: Optional[str] = None
) -> Dict[str, Any]:
    """
    Central resolution of query mission context:
    1. Explicit filter passed by UI/caller
    2. Multi-mission comparison detected in query
    3. Single mission detected in query
    4. Mission context preserved from session history
    5. Ambiguous / Unclear query -> triggers clarification prompt
    """
    # 1. Explicit mission provided
    if explicit_mission:
        matched = detect_missions_from_text(explicit_mission)
        canonical = matched[0] if matched else explicit_mission
        return {
            "mode": "single",
            "missions": [canonical],
            "source": "explicit",
            "query_intent": detect_query_intent(query)
        }

    detected = detect_missions_from_text(query)

    # 2. Multi-mission comparison in query
    if len(detected) >= 2 or (len(detected) == 2 and is_comparison_query(query)):
        return {
            "mode": "comparison",
            "missions": detected,
            "source": "query_comparison",
            "query_intent": detect_query_intent(query)
        }

    # 3. Single mission detected directly in query
    if len(detected) == 1:
        return {
            "mode": "single",
            "missions": detected,
            "source": "query_direct",
            "query_intent": detect_query_intent(query)
        }

    # 4. Check session context for follow-up questions
    session_mission = get_active_mission_from_session(db, session_id)
    if session_mission:
        logger.info(f"Preserving mission context from session #{session_id}: {session_mission}")
        return {
            "mode": "single",
            "missions": [session_mission],
            "source": "session_context",
            "query_intent": detect_query_intent(query)
        }

    # 5. Check if query is an aerospace incident inquiry with an unspecified mission
    mission_inquiry_keywords = [
        'mission', 'flight', 'launch', 'incident', 'accident', 'mishap',
        'failure', 'anomaly', 'disaster', 'vehicle', 'spacecraft', 'rocket', 'shuttle', 'crash',
        'telemetry', 'o-ring', 'propulsion', 'loss'
    ]
    is_mission_inquiry = any(k in query.lower() for k in mission_inquiry_keywords)

    if is_mission_inquiry:
        available_display = [m["display_name"] for m in MISSION_CATALOG[:7]]
        return {
            "mode": "unclear",
            "missions": [],
            "source": "none",
            "query_intent": detect_query_intent(query),
            "available_missions": available_display
        }

    # 6. Query is not an aerospace incident inquiry (out-of-scope / unsupported topic)
    return {
        "mode": "unsupported_or_global",
        "missions": [],
        "source": "none",
        "query_intent": "general"
    }
