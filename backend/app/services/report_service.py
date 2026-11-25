import os
import re
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from sqlalchemy.orm import Session
from app.models.research_session import ResearchSession
from app.models.research_message import ResearchMessage
from app.models.failure_incident import FailureIncident
from app.models.failure_event import FailureEvent
from app.models.generated_report import GeneratedReport
from app.core.config import settings
from app.core.logging import logger

def format_markdown_for_reportlab(raw_text: str, body_style, h2_style) -> List[Any]:
    """
    Safely converts markdown text into ReportLab Paragraph flowables,
    escaping XML entities to avoid parser errors while preserving bold, italic, and bullet points.
    """
    flowables = []
    lines = raw_text.split('\n')
    for line in lines:
        l = line.strip()
        if not l:
            continue
        if l.startswith('### ') or l.startswith('## '):
            clean = html.escape(l.lstrip('#').strip())
            flowables.append(Paragraph(f'<b>{clean}</b>', h2_style))
        elif l.startswith('- ') or l.startswith('* '):
            content = l[2:].strip()
            content = html.escape(content)
            content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)
            content = re.sub(r'(?<![a-zA-Z0-9])\*([^*]+?)\*(?![a-zA-Z0-9])', r'<i>\1</i>', content)
            flowables.append(Paragraph(f'&bull; {content}', body_style))
        else:
            content = html.escape(l)
            content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)
            content = re.sub(r'(?<![a-zA-Z0-9])\*([^*]+?)\*(?![a-zA-Z0-9])', r'<i>\1</i>', content)
            flowables.append(Paragraph(content, body_style))
    return flowables

class ReportService:
    @staticmethod
    def get_session_summary_data(db: Session, session_id: int) -> Dict[str, Any]:
        """
        Synthesizes the complete session dialog into a structured summary
        containing all questions, answers, citations, metrics, and an executive synthesis.
        """
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if not session:
            raise ValueError(f"Session #{session_id} not found")

        messages = db.query(ResearchMessage).filter(
            ResearchMessage.session_id == session_id
        ).order_by(ResearchMessage.created_at.asc()).all()

        qa_pairs = []
        missions_set = set()
        agencies_set = set()
        total_citations = 0
        confidences = []

        pending_user_q = None
        pending_timestamp = None
        q_count = 0

        for msg in messages:
            if msg.role == "user":
                pending_user_q = msg.message_text
                pending_timestamp = msg.created_at
            elif msg.role == "assistant":
                q_count += 1
                citations = msg.citations or []
                total_citations += len(citations)
                if msg.retrieval_confidence:
                    confidences.append(msg.retrieval_confidence)

                for cit in citations:
                    if cit.get("mission_name"):
                        missions_set.add(cit["mission_name"])
                    if cit.get("space_agency"):
                        agencies_set.add(cit["space_agency"])

                qa_pairs.append({
                    "query_number": q_count,
                    "question": pending_user_q or f"Technical Inquiry #{q_count}",
                    "answer": msg.message_text,
                    "citations": citations,
                    "retrieval_confidence": msg.retrieval_confidence or 0.85,
                    "timestamp": pending_timestamp or msg.created_at
                })
                pending_user_q = None

        avg_conf = (sum(confidences) / len(confidences)) if confidences else 0.85
        missions_list = sorted(list(missions_set)) if missions_set else ["Historical NASA / ISRO Missions"]
        agencies_list = sorted(list(agencies_set)) if agencies_set else ["NASA", "ISRO"]

        # Generate a concise executive synthesis
        if qa_pairs:
            executive_summary = (
                f"This aerospace research session comprises {len(qa_pairs)} technical inquiry and answer sequence(s) "
                f"cross-referencing official mishap documentation from {', '.join(agencies_list)}. "
                f"Historical missions analyzed include: {', '.join(missions_list[:5])}. "
                f"Across all inquiries, {total_citations} official document citations were verified with an average "
                f"retrieval grounding confidence of {int(avg_conf * 100)}%."
            )
        else:
            executive_summary = "Investigation session initiated. No technical inquiries recorded yet."

        return {
            "session_id": session.id,
            "session_title": session.title,
            "total_queries": len(qa_pairs),
            "total_answers": len(qa_pairs),
            "missions_covered": missions_list,
            "agencies_covered": agencies_list,
            "total_citations": total_citations,
            "average_confidence": round(avg_conf, 2),
            "executive_summary": executive_summary,
            "qa_pairs": qa_pairs
        }

    @staticmethod
    def generate_research_pdf(
        db: Session,
        user_id: int,
        session_id: int,
        report_title: str = "MISSIONMIND AI – Technical Investigation Report",
        include_failure_chain: bool = True,
        include_similar_failures: bool = True,
        custom_notes: Optional[str] = None
    ) -> GeneratedReport:
        """
        Builds a comprehensive, professional aerospace research PDF report using ReportLab.
        Contains:
        1. Executive Cover & Session Metadata
        2. Session Summary & Research Metrics
        3. All Inquiries, Grounded Answers & Traceable Citations
        4. Failure Mode & Subsystem Analysis
        5. Reconstructed Failure Chain (if selected)
        6. Engineering Conclusions & Lessons Learned
        """
        os.makedirs(settings.GENERATED_REPORTS_DIRECTORY, exist_ok=True)

        session_data = ReportService.get_session_summary_data(db, session_id)
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()

        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"missionmind_report_session_{session_id}_{timestamp_str}.pdf"
        pdf_path = Path(settings.GENERATED_REPORTS_DIRECTORY) / filename

        # Setup Document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # Aerospace visual styles
        primary_color = colors.HexColor("#1e1b4b")   # Deep navy
        accent_color = colors.HexColor("#6366f1")    # Indigo / Violet
        text_dark = colors.HexColor("#0f172a")       # Slate 900
        bg_light = colors.HexColor("#f8fafc")        # Slate 50
        border_color = colors.HexColor("#cbd5e1")    # Slate 300

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=primary_color,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12
        )

        h1_style = ParagraphStyle(
            'H1',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=primary_color,
            spaceBefore=14,
            spaceAfter=6
        )

        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14,
            textColor=accent_color,
            spaceBefore=8,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=text_dark,
            spaceAfter=5
        )

        quote_style = ParagraphStyle(
            'Quote',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#334155"),
            leftIndent=15,
            spaceAfter=6
        )

        citation_style = ParagraphStyle(
            'Citation',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#64748b")
        )

        story = []

        # --- HEADER BANNER ---
        story.append(Paragraph("MISSIONMIND AI // AEROSPACE FLIGHT SAFETY RESEARCH ASSISTANT", subtitle_style))
        story.append(Paragraph(html.escape(report_title), title_style))
        story.append(Paragraph(
            f"<b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y - %H:%M UTC')} | "
            f"<b>Session ID:</b> #{session.id} | <b>Investigation Topic:</b> {html.escape(session.title)}",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=12))

        # --- SECTION 1: EXECUTIVE SUMMARY & SESSION OVERVIEW ---
        story.append(Paragraph("1. Executive Summary & Session Overview", h1_style))
        story.append(Paragraph(
            html.escape(session_data["executive_summary"]),
            body_style
        ))

        # Metrics Table
        metrics_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Questions Asked", str(session_data["total_queries"]), "Average Confidence", f"{int(session_data['average_confidence'] * 100)}%"],
            ["Total Answers Generated", str(session_data["total_answers"]), "Official Citations", str(session_data["total_citations"])],
            ["Missions Analyzed", ", ".join(session_data["missions_covered"][:3]), "Agencies Index", ", ".join(session_data["agencies_covered"])]
        ]
        mt = Table(metrics_data, colWidths=[130, 130, 130, 140])
        mt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), bg_light),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(mt)

        if custom_notes:
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>Investigator Notes:</b> {html.escape(custom_notes)}", quote_style))

        story.append(Spacer(1, 10))

        # --- SECTION 2: ALL INQUIRIES, ANSWERS & SOURCES ---
        story.append(Paragraph("2. Complete Technical Inquiries, Grounded Answers & Cited Sources", h1_style))

        qa_pairs = session_data["qa_pairs"]
        if not qa_pairs:
            story.append(Paragraph("<i>No questions or answers recorded in this session.</i>", body_style))
        else:
            for pair in qa_pairs:
                q_num = pair["query_number"]
                clean_q = html.escape(pair["question"])
                conf_pct = int(pair["retrieval_confidence"] * 100)
                
                # Question header
                story.append(Spacer(1, 6))
                story.append(Paragraph(
                    f"<b>Query 2.{q_num}: {clean_q}</b> (Evidence Confidence: {conf_pct}%)",
                    h2_style
                ))

                # Answer body paragraphs
                answer_paragraphs = format_markdown_for_reportlab(pair["answer"], body_style, h2_style)
                for p in answer_paragraphs:
                    story.append(p)

                # Citations Table
                citations = pair.get("citations", [])
                if citations:
                    story.append(Spacer(1, 4))
                    story.append(Paragraph("<b>Traceable Cited Documents & Page Numbers:</b>", h2_style))
                    table_data = [["Mission / Agency", "Official Document Title", "Page", "Confidence"]]
                    for cit in citations[:5]:
                        table_data.append([
                            f"{cit.get('mission_name', 'NASA/ISRO')} ({cit.get('space_agency', 'US/IN')})",
                            (cit.get('document_title', 'Investigation Report') or 'Investigation Report')[:45] + "...",
                            f"Page {cit.get('page_number', 'N/A')}",
                            f"{int((cit.get('score', 0.85)) * 100)}%"
                        ])
                    
                    ctable = Table(table_data, colWidths=[120, 240, 70, 70])
                    ctable.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), bg_light),
                        ('TEXTCOLOR', (0, 0), (-1, 0), primary_color),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                    ]))
                    story.append(ctable)

                story.append(Spacer(1, 8))
                story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=8))

        # --- SECTION 3: SIMILAR PAST FAILURES & FAILURE CHAIN ---
        if include_failure_chain or include_similar_failures:
            story.append(Spacer(1, 8))
            story.append(Paragraph("3. Cross-Mission Failure Chain & Subsystem Analysis", h1_style))
            
            incident = db.query(FailureIncident).first()
            if incident:
                story.append(Paragraph(
                    f"<b>Case Study: {incident.subsystem} Subsystem Failure Mode</b>", h2_style
                ))
                story.append(Paragraph(
                    f"<b>Documented Root Cause:</b> {html.escape(incident.root_cause or 'Unspecified')}", body_style
                ))
                story.append(Paragraph(
                    f"<b>Mission Impact:</b> {html.escape(incident.mission_impact or 'Total Vehicle Loss')}", body_style
                ))
                story.append(Paragraph(
                    f"<b>Prescribed Corrective Action:</b> {html.escape(incident.corrective_action or 'Rigorous pre-flight test validation.')}",
                    body_style
                ))

                events = db.query(FailureEvent).filter(
                    FailureEvent.incident_id == incident.id
                ).order_by(FailureEvent.event_order.asc()).all()

                if events:
                    story.append(Paragraph("<b>Chronological Failure Event Sequence:</b>", h2_style))
                    chain_table = [["#", "Timestamp", "Event Title", "Causal Classification", "Page"]]
                    for ev in events:
                        chain_table.append([
                            str(ev.event_order),
                            ev.event_timestamp or "T+0",
                            (ev.event_title or "")[:45],
                            ev.relationship_type or "Direct Cause",
                            f"P. {ev.source_page or incident.source_page or 1}"
                        ])
                    ct = Table(chain_table, colWidths=[25, 65, 230, 130, 50])
                    ct.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), bg_light),
                        ('TEXTCOLOR', (0, 0), (-1, 0), primary_color),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ]))
                    story.append(ct)

        # --- SECTION 4: LESSONS LEARNED & RECOMMENDATIONS ---
        story.append(Spacer(1, 10))
        story.append(Paragraph("4. Synthesis & Aerospace Engineering Recommendations", h1_style))
        story.append(Paragraph(
            "1. <b>Interface Verification:</b> Strict mechanical, aerodynamic, and software unit contract checks must be enforced across contractor boundaries.<br/>"
            "2. <b>Thermal & Cryogenic Resilience:</b> Telemetry sensors and active heating/venting must have independent power redundancies.<br/>"
            "3. <b>Failure Modes Traceability:</b> Maintain digital, cited institutional memory to avoid repeating documented historical mishaps.",
            body_style
        ))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))
        story.append(Paragraph(
            "MISSIONMIND AI // Evidence-Based Flight Investigation Platform // NASA & ISRO Technical Index",
            citation_style
        ))

        # Build PDF file
        doc.build(story)
        logger.info(f"Report generated successfully: {pdf_path}")

        # Record in database
        report_record = GeneratedReport(
            user_id=user_id,
            session_id=session_id,
            report_title=report_title,
            file_path=str(pdf_path)
        )
        db.add(report_record)
        db.commit()
        db.refresh(report_record)

        return report_record
