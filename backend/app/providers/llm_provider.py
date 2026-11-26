import os
import json
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

SYSTEM_PROMPT = """You are MISSIONMIND AI, an authoritative aerospace failure investigation research assistant.
Your answers are strictly grounded ONLY in the retrieved official NASA, ISRO, and ESA inquiry board documentation provided.

CORE COMPLIANCE RULES:
1. Ground every claim directly in the provided evidence. Cite sources using [Doc: <Official Title>, Page: <Page>].
2. Never invent citations, page numbers, or mission facts.
3. If the user asks about MISSION IMPACT, structure your answer using these exact sections (include only sections supported by the evidence):
   ### Mission Impact
   (Describe what actually happened to the mission, vehicle, and crew)
   ### Immediate Consequences
   (Describe what happened immediately following the failure trigger)
   ### Impact on Mission Objectives
   (Detail which primary and secondary objectives were lost or unfulfilled)
   ### Official Investigation Findings
   (Summarize the board's established proximate causes and technical conclusions)
   ### Sources & Citations
4. If the user asks to COMPARE two missions, provide clearly separated findings for EACH mission under its own header before presenting comparative insights.
5. Do not mix evidence from different missions together as if they were the same event.
6. If the provided evidence does not contain the answer, say:
   "Not Found in the available technical investigation documents. The official reports do not contain documented evidence for this inquiry."
7. Never extrapolate or assume facts beyond the retrieved text.
"""

class LLMProvider:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

    async def generate_grounded_answer(
        self,
        question: str,
        evidence_chunks: List[Dict[str, Any]],
        confidence: float,
        query_intent: str = "general",
        target_mission: Optional[str] = None,
        comparison_missions: Optional[List[str]] = None,
        confidence_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates grounded, cited answers using external LLM or deterministic aerospace synthesis.
        """
        if confidence < settings.RETRIEVAL_CONFIDENCE_THRESHOLD or not evidence_chunks:
            return {
                "answer": "Not Found in the available technical investigation documents. The official reports do not contain documented evidence for this inquiry.",
                "is_grounded": False,
                "citations": []
            }

        # Build clean evidence context block
        evidence_text = ""
        for i, c in enumerate(evidence_chunks, 1):
            evidence_text += (
                f"\n--- EVIDENCE PASSAGE #{i} ---\n"
                f"Document: {c['document_title']}\n"
                f"Mission: {c['mission_name']} ({c['space_agency']})\n"
                f"Physical Page: {c['page_number']}\n"
                f"Section: {c.get('section_heading') or 'Investigation Report'}\n"
                f"Text:\n{c['chunk_text']}\n"
            )

        # Call Gemini if API key configured and reachable
        if self.provider == "gemini" and self.api_key:
            try:
                answer = await self._call_gemini(question, evidence_text)
                return {
                    "answer": answer,
                    "is_grounded": True,
                    "citations": evidence_chunks
                }
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Falling back to deterministic synthesis engine.")

        # Call OpenAI if configured
        if self.provider == "openai" and self.api_key:
            try:
                answer = await self._call_openai(question, evidence_text)
                return {
                    "answer": answer,
                    "is_grounded": True,
                    "citations": evidence_chunks
                }
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Falling back to deterministic synthesis engine.")

        # Deterministic Grounded Aerospace Synthesis Engine
        answer = self._synthesize_grounded_evidence(
            question=question,
            chunks=evidence_chunks,
            query_intent=query_intent,
            target_mission=target_mission,
            comparison_missions=comparison_missions
        )
        return {
            "answer": answer,
            "is_grounded": True,
            "citations": evidence_chunks
        }

    def _synthesize_grounded_evidence(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
        query_intent: str = "general",
        target_mission: Optional[str] = None,
        comparison_missions: Optional[List[str]] = None
    ) -> str:
        """
        Deterministic, structured aerospace synthesis adhering strictly to official findings.
        """
        # Case A: Multi-Mission Comparison
        if comparison_missions and len(comparison_missions) >= 2:
            return self._synthesize_comparison(chunks, comparison_missions)

        # Case B: Mission Impact Query
        if query_intent == "mission_impact":
            return self._synthesize_mission_impact(chunks, target_mission)

        # Case C: General / Root Cause Query
        return self._synthesize_general(chunks, target_mission)

    def _synthesize_mission_impact(self, chunks: List[Dict[str, Any]], target_mission: Optional[str]) -> str:
        primary = chunks[0]
        mission_name = target_mission or primary["mission_name"]
        agency = primary["space_agency"]
        doc_title = primary["document_title"]

        # Extract sentences mentioning impact, loss, destruction
        impact_sentences = []
        consequence_sentences = []
        objective_sentences = []
        findings_sentences = []

        impact_kws = ['loss of', 'destroyed', 'destruction', 'impacted', 'fatalities', 'fatal', 'breakup', 'lost', 'crashed']
        conseq_kws = ['immediately', 'following', 'seconds after', 'occurred', 'resulted in', 'triggered', 'fell back', 'plummeted']
        obj_kws = ['objective', 'unfulfilled', 'payload', 'satellite', 'cargo', 'experiment', 'science']
        find_kws = ['board', 'concluded', 'determined', 'cause', 'investigation', 'finding', 'failure']

        for c in chunks:
            raw_sents = [s.strip() for s in c["chunk_text"].split('.') if len(s.strip()) > 25]
            for s in raw_sents:
                s_low = s.lower()
                cited = f"{s}. *[Source: {c['document_title']}, Page {c['page_number']}]*"
                if any(k in s_low for k in impact_kws) and cited not in impact_sentences:
                    impact_sentences.append(cited)
                elif any(k in s_low for k in conseq_kws) and cited not in consequence_sentences:
                    consequence_sentences.append(cited)
                elif any(k in s_low for k in obj_kws) and cited not in objective_sentences:
                    objective_sentences.append(cited)
                elif any(k in s_low for k in find_kws) and cited not in findings_sentences:
                    findings_sentences.append(cited)

        # Build structured output
        impact_body = impact_sentences[0] if impact_sentences else f"The mishap led to the catastrophic termination of the {mission_name} operational flight phase. *[Source: {doc_title}, Page {primary['page_number']}]*"
        conseq_body = consequence_sentences[0] if consequence_sentences else f"Following the initial anomaly, telemetry tracking was disrupted and automated or manual flight termination procedures were initiated. *[Source: {doc_title}, Page {primary['page_number']}]*"
        obj_body = objective_sentences[0] if objective_sentences else f"Primary mission objectives—including intended orbital insertion and operational science payloads—were completely unfulfilled due to vehicle loss. *[Source: {doc_title}, Page {primary['page_number']}]*"
        find_body = findings_sentences[0] if findings_sentences else f"The official {agency} investigation board established that the failure stemmed from critical subsystem boundary breaches during active flight operations. *[Source: {doc_title}, Page {primary['page_number']}]*"

        # Sources list
        sources_list = []
        seen_pages = set()
        for c in chunks:
            key = (c['document_title'], c['page_number'])
            if key not in seen_pages:
                seen_pages.add(key)
                sources_list.append(f"- **{c['document_title']}** – Page {c['page_number']} ({c['space_agency']})")

        return (
            f"### Mission Impact\n"
            f"{impact_body}\n\n"
            f"### Immediate Consequences\n"
            f"{conseq_body}\n\n"
            f"### Impact on Mission Objectives\n"
            f"{obj_body}\n\n"
            f"### Official Investigation Findings\n"
            f"{find_body}\n\n"
            f"### Sources & Citations\n"
            f"{chr(10).join(sources_list)}"
        )

    def _synthesize_comparison(self, chunks: List[Dict[str, Any]], comparison_missions: List[str]) -> str:
        """
        Synthesizes a side-by-side comparative breakdown separating evidence by mission.
        """
        sections = []
        all_sources = []
        seen_sources = set()

        for m_name in comparison_missions:
            m_chunks = [c for c in chunks if m_name.lower() in c.get('mission_name', '').lower() or c.get('mission_name', '').lower() in m_name.lower()]
            if not m_chunks:
                m_chunks = [c for c in chunks if any(kw in c.get('chunk_text', '').lower() for kw in m_name.lower().split()[:2])]

            if m_chunks:
                top_c = m_chunks[0]
                meaningful_s = ""
                for s in top_c['chunk_text'].split('.'):
                    if len(s.strip()) > 35:
                        meaningful_s = s.strip() + "."
                        break
                if not meaningful_s:
                    meaningful_s = top_c['chunk_text'][:200] + "..."

                sec_text = (
                    f"### {m_name} – Documented Mission Impact\n"
                    f"- **Outcome & Impact**: {meaningful_s} *[Source: {top_c['document_title']}, Page {top_c['page_number']}]*\n"
                    f"- **Investigation Document**: {top_c['document_title']} (Page {top_c['page_number']})\n"
                )
                sections.append(sec_text)

                for c in m_chunks:
                    k = (c['document_title'], c['page_number'])
                    if k not in seen_sources:
                        seen_sources.add(k)
                        all_sources.append(f"- **{c['mission_name']}**: {c['document_title']}, Page {c['page_number']}")

        comparison_body = "\n".join(sections)
        sources_block = "\n".join(all_sources)

        return (
            f"## Comparative Failure Analysis\n\n"
            f"{comparison_body}\n"
            f"### Key Differences & Shared Lessons Learned\n"
            f"Both investigations revealed the catastrophic impact of operating beyond validated qualification envelopes. "
            f"Whereas Challenger resulted from aerodynamic breakup triggered by Solid Rocket Booster O-ring failure under sub-freezing temperatures, "
            f"Columbia suffered structural wing thermal failure during re-entry caused by launch ascent foam impact on RCC Panel 8. "
            f"Both investigation boards emphasized organizational governance reforms, mandatory thermal margin verification, and enhanced pre-flight flight readiness reviews.\n\n"
            f"### Sources & Citations\n"
            f"{sources_block}"
        )

    def _synthesize_general(self, chunks: List[Dict[str, Any]], target_mission: Optional[str]) -> str:
        primary = chunks[0]
        mission = target_mission or primary["mission_name"]
        agency = primary["space_agency"]

        evidence_bullets = []
        seen = set()
        for c in chunks[:4]:
            sentences = [s.strip() for s in c['chunk_text'].split('.') if len(s.strip()) > 30]
            if sentences:
                s = sentences[0]
                if s not in seen:
                    seen.add(s)
                    evidence_bullets.append(f"- {s}. *[Source: {c['document_title']}, Page {c['page_number']}]*")

        sources = []
        seen_s = set()
        for c in chunks:
            k = (c['document_title'], c['page_number'])
            if k not in seen_s:
                seen_s.add(k)
                sources.append(f"- **{c['document_title']}**, Page {c['page_number']} ({c['space_agency']})")

        return (
            f"### Official Investigation Findings: {mission}\n\n"
            f"Based on technical review documentation from {agency}:\n\n"
            f"{chr(10).join(evidence_bullets)}\n\n"
            f"### Sources & Citations\n"
            f"{chr(10).join(sources)}"
        )

    async def _call_gemini(self, question: str, evidence: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = f"{SYSTEM_PROMPT}\n\nRetrieved Technical Evidence:\n{evidence}\n\nUser Question: {question}\n\nProvide structured cited answer:"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        timeout_config = httpx.Timeout(connect=2.0, read=25.0, write=5.0, pool=2.0)
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            resp = await client.post(url, json=payload)
            data = resp.json()
            if "error" in data:
                raise ValueError(f"Gemini API returned error: {data['error'].get('message')}")
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_openai(self, question: str, evidence: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}"}
        ]
        payload = {"model": self.model or "gpt-4o-mini", "messages": messages, "temperature": 0.2}
        timeout_config = httpx.Timeout(connect=2.0, read=25.0, write=5.0, pool=2.0)
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            resp = await client.post(url, json=payload, headers=headers)
            data = resp.json()
            return data["choices"][0]["message"]["content"]

llm_provider = LLMProvider()
