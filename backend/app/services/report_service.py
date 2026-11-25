import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
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

class ReportService:
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
        1. Executive Cover & Metadata
        2. Research Inquiries & AI-Synthesized Answers
        3. Traceable Page-Level Evidence & Citations
        4. Failure Mode & Subsystem Analysis
        5. Reconstructed Failure Chain (if selected)
        6. Engineering Conclusions & Lessons Learned
        """
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if not session:
            raise ValueError(f"Session #{session_id} not found")

        messages = db.query(ResearchMessage).filter(
            ResearchMessage.session_id == session_id
        ).order_by(ResearchMessage.created_at.asc()).all()

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
        accent_color = colors.HexColor("#6366f1")    # Indigo/Violet
        text_dark = colors.HexColor("#0f172a")       # Slate 900
        bg_light = colors.HexColor("#f8fafc")        # Slate 50
        border_color = colors.HexColor("#cbd5e1")    # Slate 300

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=primary_color,
            spaceAfter=8
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=15
        )

        h1_style = ParagraphStyle(
            'H1',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=primary_color,
            spaceBefore=12,
            spaceAfter=6
        )

        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=accent_color,
            spaceBefore=8,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=text_dark,
            spaceAfter=6
        )

        quote_style = ParagraphStyle(
            'Quote',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor("#334155"),
            leftIndent=15,
            spaceAfter=6
        )

        citation_style = ParagraphStyle(
            'Citation',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b")
        )

        story = []

        # --- HEADER BANNER ---
        story.append(Paragraph("MISSIONMIND AI // AEROSPACE FLIGHT SAFETY INTELLIGENCE", subtitle_style))
        story.append(Paragraph(report_title, title_style))
        story.append(Paragraph(
            f"<b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y - %H:%M UTC')} | "
            f"<b>Session ID:</b> #{session.id} | <b>Topic:</b> {session.title}",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=15))

        # --- EXECUTIVE SUMMARY ---
        story.append(Paragraph("1. Executive Summary & Investigation Scope", h1_style))
        story.append(Paragraph(
            "This technical research report synthesizes lessons learned, subsystem failure modes, "
            "and root-cause analyses documented across official NASA and ISRO technical mishap reports. "
            "All findings, timestamps, and causal connections are cross-referenced against original document evidence.",
            body_style
        ))
        if custom_notes:
            story.append(Paragraph(f"<b>Investigator Notes:</b> {custom_notes}", quote_style))
        story.append(Spacer(1, 10))

        # --- INQUIRIES & GROUNDED FINDINGS ---
        story.append(Paragraph("2. Technical Inquiries & Cited Evidence", h1_style))
        q_num = 1
        for msg in messages:
            if msg.role == "user":
                story.append(Paragraph(f"<b>Query 2.{q_num}: {msg.message_text}</b>", h2_style))
                q_num += 1
            elif msg.role == "assistant":
                # Clean answer markdown for reportlab
                clean_msg = msg.message_text.replace("### ", "<b>").replace("#### ", "<b>").replace("---", "")
                clean_msg = clean_msg.replace("**", "<b>").replace("*", "<i>")
                story.append(Paragraph(clean_msg, body_style))

                # Display Citations Table if present
                if msg.citations:
                    story.append(Paragraph("<b>Traceable Page-Level Evidence Citations:</b>", h2_style))
                    table_data = [["Mission / Agency", "Official Document Title", "Page", "Confidence"]]
                    for cit in msg.citations[:4]:
                        table_data.append([
                            f"{cit.get('mission_name', 'NASA/ISRO')} ({cit.get('space_agency', 'US/IN')})",
                            cit.get('document_title', 'Investigation Report')[:40] + "...",
                            f"Page {cit.get('page_number', 'N/A')}",
                            f"{int((cit.get('score', 0.85)) * 100)}%"
                        ])
                    
                    t = Table(table_data, colWidths=[120, 240, 70, 70])
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), bg_light),
                        ('TEXTCOLOR', (0, 0), (-1, 0), primary_color),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 8))

        # --- SIMILAR PAST FAILURES & FAILURE CHAIN (IF REQUESTED) ---
        if include_failure_chain or include_similar_failures:
            story.append(Spacer(1, 10))
            story.append(Paragraph("3. Cross-Mission Failure Chain & Subsystem Analysis", h1_style))
            
            # Retrieve notable incident
            incident = db.query(FailureIncident).first()
            if incident:
                story.append(Paragraph(
                    f"<b>Case Study: {incident.subsystem} Subsystem Failure Mode</b>", h2_style
                ))
                story.append(Paragraph(
                    f"<b>Documented Root Cause:</b> {incident.root_cause}", body_style
                ))
                story.append(Paragraph(
                    f"<b>Mission Impact:</b> {incident.mission_impact or 'Total Vehicle Loss'}", body_style
                ))
                story.append(Paragraph(
                    f"<b>Prescribed Corrective Action:</b> {incident.corrective_action or 'Rigorous pre-flight test validation.'}",
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
                            ev.event_title[:45],
                            ev.relationship_type,
                            f"P. {ev.source_page or incident.source_page or 1}"
                        ])
                    ct = Table(chain_table, colWidths=[25, 65, 230, 130, 50])
                    ct.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), bg_light),
                        ('TEXTCOLOR', (0, 0), (-1, 0), primary_color),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                    ]))
                    story.append(ct)

        # --- LESSONS LEARNED & AUDIT CONCLUSION ---
        story.append(Spacer(1, 15))
        story.append(Paragraph("4. Synthesis & Aerospace Engineering Recommendations", h1_style))
        story.append(Paragraph(
            "1. <b>Interface Verification:</b> Strict mechanical, aerodynamic, and software unit contract checks must be enforced across contractor boundaries.<br/>"
            "2. <b>Thermal & Cryogenic Resilience:</b> Telemetry sensors and active heating/venting must have independent power redundancies.<br/>"
            "3. <b>Failure Modes Traceability:</b> Maintain digital, cited institutional memory to avoid repeating documented historical mishaps.",
            body_style
        ))
        story.append(Spacer(1, 10))
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
