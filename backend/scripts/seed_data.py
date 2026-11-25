import os
import sys
import shutil
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal, init_db
from app.models.document import Document
from app.models.mission import Mission
from app.models.failure_incident import FailureIncident
from app.models.failure_event import FailureEvent
from app.models.document_chunk import DocumentChunk
from app.services.document_processor import DocumentProcessor
from app.core.config import settings
from app.core.logging import logger

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
NASA_DIR = DATA_DIR / "nasa"
ISRO_DIR = DATA_DIR / "isro"

# Curated seed document registry
DOCUMENTS_METADATA = [
    {
        "filename": "NASA_MCO_Investigation_Report.pdf",
        "folder": NASA_DIR,
        "title": "Mars Climate Orbiter Mishap Investigation Board Phase I Report",
        "mission_name": "Mars Climate Orbiter",
        "space_agency": "NASA",
        "publication_year": 1999,
        "document_type": "Mishap Investigation Board Report",
        "source_url": "https://ntrs.nasa.gov/citations/20000021270",
        "licence": "Public Domain (NASA Technical Reports Server)",
        "subsystem": "Software / Guidance & Navigation",
        "root_cause": "Failure to use metric units (Newton-seconds) in ground software 'Small Forces', resulting in 4.45x under-reporting of angular momentum thruster impulses.",
        "failure_mode": "Navigation Metric Unit Mismatch",
        "mission_phase": "Mars Orbit Insertion",
        "mission_impact": "Total Loss of Spacecraft",
        "corrective_action": "Strict enforcement of SI units in all software interface specifications (SIS) and mandatory multi-center peer trajectory reviews.",
        "source_page": 2,
        "events": [
            {
                "order": 1,
                "title": "Ground Software Metric Unit Inconsistency",
                "desc": "Ground contractor code exported thruster impulse in English pound-force seconds while JPL trajectory software expected metric Newton-seconds.",
                "type": "Root Cause",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T-9 Months (Launch Phase)"
            },
            {
                "order": 2,
                "title": "Accumulated Trajectory Perturbation Bias",
                "desc": "Each angular momentum desaturation (AMD) maneuver introduced unmodeled velocity discrepancies, accumulating 170 km trajectory error.",
                "type": "Cascading Anomaly",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "Cruise Phase Day 120-280"
            },
            {
                "order": 3,
                "title": "Dangerous Atmospheric Trajectory Insertion",
                "desc": "Spacecraft entered Martian atmosphere at 57 km periapsis instead of safe 226 km target altitude.",
                "type": "Cascading Anomaly",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "September 23, 1999 (09:00 UTC)"
            },
            {
                "order": 4,
                "title": "Aerodynamic Breakup & Mission Termination",
                "desc": "Extreme aerodynamic drag, friction, and thermal loading destroyed orbiter during Martian atmospheric occultation.",
                "type": "Mission Loss",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "September 23, 1999 (09:04 UTC)"
            }
        ]
    },
    {
        "filename": "NASA_CAIB_Columbia_Investigation.pdf",
        "folder": NASA_DIR,
        "title": "Columbia Accident Investigation Board (CAIB) Report - Volume I",
        "mission_name": "Space Shuttle Columbia (STS-107)",
        "space_agency": "NASA",
        "publication_year": 2003,
        "document_type": "Accident Investigation Board Report",
        "source_url": "https://www.nasa.gov/columbia/caib/PDFS/VOL1/PART01.PDF",
        "licence": "Public Domain (Official Presidential & NASA CAIB Release)",
        "subsystem": "Thermal Protection System (TPS) / Aerodynamics",
        "root_cause": "External Tank left bipod ramp foam liberation striking reinforced carbon-carbon (RCC) panel 8 on left wing, breaching thermal barrier.",
        "failure_mode": "Thermal Barrier Plasma Penetration",
        "mission_phase": "Atmospheric Re-entry",
        "mission_impact": "Total Vehicle & Crew Loss",
        "corrective_action": "External Tank bipod redesign, on-orbit boom sensor inspection, and creation of the NASA Engineering and Safety Center (NESC).",
        "source_page": 2,
        "events": [
            {
                "order": 1,
                "title": "External Tank Insulating Foam Separation",
                "desc": "Left bipod ramp insulating foam shed from External Tank 81.9 seconds after launch.",
                "type": "Physical Trigger",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "T+81.9 Seconds (Ascent)"
            },
            {
                "order": 2,
                "title": "High-Velocity Impact on RCC Panel 8",
                "desc": "Foam fragment struck left wing leading edge Reinforced Carbon-Carbon panel 8 at ~545 mph, creating structural breach.",
                "type": "Structural Breach",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T+82.1 Seconds"
            },
            {
                "order": 3,
                "title": "Superheated Atmospheric Plasma Ingestion",
                "desc": "During re-entry at Mach 24.6, 3,000°F atmospheric plasma entered wing cavity, rapidly melting internal aluminum spars.",
                "type": "Thermal Structural Failure",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "EI+13 Minutes (Re-entry)"
            },
            {
                "order": 4,
                "title": "Loss of Vehicle Control & Breakup",
                "desc": "Aerodynamic asymmetry and progressive wing failure led to orbiter breakup over Texas.",
                "type": "Mission Loss",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "09:00:18 EST (Feb 1, 2003)"
            }
        ]
    },
    {
        "filename": "NASA_Challenger_Rogers_Commission.pdf",
        "folder": NASA_DIR,
        "title": "Report of the Presidential Commission on the Space Shuttle Challenger Accident",
        "mission_name": "Space Shuttle Challenger (STS-51L)",
        "space_agency": "NASA",
        "publication_year": 1986,
        "document_type": "Presidential Commission Report",
        "source_url": "https://history.nasa.gov/rogersrep/genindex.htm",
        "licence": "Public Domain (Official U.S. Government Report)",
        "subsystem": "Propulsion / Solid Rocket Boosters",
        "root_cause": "Failure of Solid Rocket Booster field joint O-rings due to extreme cold ambient temperature (36°F), enabling hot combustion gas blow-by.",
        "failure_mode": "Cryo-Thermal Seal Blow-by",
        "mission_phase": "Ascent",
        "mission_impact": "Total Vehicle & Crew Loss",
        "corrective_action": "Redesign of field joint with capture tang, third O-ring, and electric heating blankets.",
        "source_page": 2,
        "events": [
            {
                "order": 1,
                "title": "Sub-Freezing Ambient Launch Temperature",
                "desc": "Ambient launch temperature of 36°F caused synthetic rubber O-rings to lose resiliency and elasticity.",
                "type": "Environmental Condition",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "T-0 (Launch Pad 39B)"
            },
            {
                "order": 2,
                "title": "O-Ring Seal Gas Blow-By",
                "desc": "Hot 5,000°F combustion gas breached aft field joint of right Solid Rocket Booster at ignition.",
                "type": "Seal Failure",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T+0.678 Seconds"
            },
            {
                "order": 3,
                "title": "Continuous Flame Plume Impingement",
                "desc": "Exhaust plume impinged directly upon External Tank aft attachment strut and liquid hydrogen tank.",
                "type": "Cascading Failure",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T+58.788 Seconds"
            },
            {
                "order": 4,
                "title": "External Tank Rupture & Vehicle Loss",
                "desc": "Structural collapse of tank dome caused massive aerodynamic breakup at Mach 1.92.",
                "type": "Mission Loss",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "T+73 Seconds"
            }
        ]
    },
    {
        "filename": "NASA_Genesis_Mishap_Investigation.pdf",
        "folder": NASA_DIR,
        "title": "Genesis Mishap Investigation Board Final Report",
        "mission_name": "Genesis Solar Wind Sample Return",
        "space_agency": "NASA",
        "publication_year": 2004,
        "document_type": "Mishap Investigation Board Report",
        "source_url": "https://www.nasa.gov/pdf/136015main_genesis_mib.pdf",
        "licence": "Public Domain (NASA Mishap Investigation Release)",
        "subsystem": "Electrical / Avionics / Recovery Mechanism",
        "root_cause": "G-switch deceleration sensors installed upside down due to drawing orientation error, preventing circuit closure and parachute mortar firing.",
        "failure_mode": "Sensor Inversion Failure",
        "mission_phase": "Atmospheric Recovery & Descent",
        "mission_impact": "Hard Ground Impact & Capsule Rupture",
        "corrective_action": "Mandatory physical gravity-bench verification and hardware-in-the-loop sensor orientation testing.",
        "source_page": 2,
        "events": [
            {
                "order": 1,
                "title": "Engineering Drawing Sensor Inversion",
                "desc": "Deceleration G-switches drawn and assembled in inverted orientation without mechanical keying.",
                "type": "Design Drawing Defect",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "Design & Integration Phase"
            },
            {
                "order": 2,
                "title": "Deceleration Reversal of Contact Pins",
                "desc": "Atmospheric entry deceleration held electrical contacts open instead of closing them.",
                "type": "Physical Malfunction",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T+Entry (Utah Test Range)"
            },
            {
                "order": 3,
                "title": "Drogue and Main Parachute Mortar Failure",
                "desc": "Avionics computer never detected entry deceleration; pyrotechnic parachute cutters never commanded.",
                "type": "Cascading Inaction",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "Altitude 33 km to Surface"
            },
            {
                "order": 4,
                "title": "High-Velocity Capsule Ground Impact",
                "desc": "Sample return capsule impacted Utah desert floor at 193 mph, fracturing science collectors.",
                "type": "Mission Impact",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "09:58 AM MDT (Sept 8, 2004)"
            }
        ]
    },
    {
        "filename": "ISRO_GSLV_F10_Failure_Analysis.pdf",
        "folder": DATA_DIR / "isro",
        "title": "ISRO GSLV-F10 / EOS-03 Flight Anomaly & Failure Analysis Committee Report",
        "mission_name": "GSLV-F10 / EOS-03",
        "space_agency": "ISRO",
        "publication_year": 2021,
        "document_type": "Failure Analysis Committee Report",
        "source_url": "https://www.isro.gov.in/GSLV-F10_EOS-03_FAC.html",
        "licence": "Official ISRO Public Release & Parliamentary Record",
        "subsystem": "Propulsion / Cryogenic Upper Stage (CUS)",
        "root_cause": "Malfunction of cryogenic vent and pressurization valve causing liquid hydrogen tank pressure drop and turbopump cavitation.",
        "failure_mode": "Cryogenic Tank Pressure Decay & Engine Flameout",
        "mission_phase": "Cryogenic Third Stage Burn",
        "mission_impact": "Failure to Achieve Orbital Injection",
        "corrective_action": "Strengthened cryogenic valve seals, redesigned gas pressurization regulation orifices, and added redundant tank pressure telemetry.",
        "source_page": 2,
        "events": [
            {
                "order": 1,
                "title": "Cryogenic Upper Stage Valve Contraction",
                "desc": "Transient high-pressure flow and extreme cryogenic temperatures degraded vent valve sealing.",
                "type": "Root Cause",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T+307 Seconds (CUS Ignition)"
            },
            {
                "order": 2,
                "title": "Liquid Hydrogen (LH2) Tank Pressure Drop",
                "desc": "Internal ullage pressure in the liquid hydrogen fuel tank decayed rapidly below threshold.",
                "type": "Pressure Decay",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T+320 Seconds"
            },
            {
                "order": 3,
                "title": "Cryogenic Turbopump Cavitation & Flameout",
                "desc": "Fuel starvation and cavitation in the high-speed cryogenic turbopump led to main engine flameout.",
                "type": "Propulsion Loss",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "T+340 Seconds"
            },
            {
                "order": 4,
                "title": "Failure to Reach Orbital Velocity",
                "desc": "Vehicle failed to achieve nominal orbital velocity and re-entered over the Indian Ocean.",
                "type": "Mission Loss",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "T+500 Seconds"
            }
        ]
    },
    {
        "filename": "ISRO_PSLV_C39_Fairing_Investigation.pdf",
        "folder": DATA_DIR / "isro",
        "title": "ISRO PSLV-C39 / IRNSS-1H Heat Shield Separation Failure Investigation",
        "mission_name": "PSLV-C39 / IRNSS-1H",
        "space_agency": "ISRO",
        "publication_year": 2017,
        "document_type": "Failure Analysis Committee Report",
        "source_url": "https://www.isro.gov.in/PSLV_C39_FAC_Summary.html",
        "licence": "Official ISRO Press Release & Parliamentary Information",
        "subsystem": "Structures / Payload Fairing Separation",
        "root_cause": "Pyrotechnic linear expanding bellow separation mechanism failed to sever composite retention brackets due to structural compliance and gasket gas leakage.",
        "failure_mode": "Heat Shield Non-Separation",
        "mission_phase": "Stage 2 Burn / Exo-Atmospheric Flight",
        "mission_impact": "Satellite Trapped Inside Fairing in Sub-Nominal Orbit",
        "corrective_action": "Replaced bellows retaining structure with reinforced titanium retention brackets and dual pyrotechnic cord seals.",
        "source_page": 2,
        "events": [
            {
                "order": 1,
                "title": "Pyrotechnic Expanding Bellow Pressure Dissipation",
                "desc": "Localized gas leakage through bellow gasket dissipated explosive severance energy.",
                "type": "Mechanical / Pyrotechnic Failure",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T+202 Seconds (Altitude 115 km)"
            },
            {
                "order": 2,
                "title": "Heat Shield Severance Rivets Intact",
                "desc": "Insufficient mechanical expansion force failed to shear circumferential retention rivets.",
                "type": "Structural Anomaly",
                "relationship": "Confirmed Causal",
                "page": 2,
                "timestamp": "T+204 Seconds"
            },
            {
                "order": 3,
                "title": "Deadweight Trapped Satellite Payload",
                "desc": "One-ton composite payload fairing remained attached, severely reducing subsequent stages Delta-V.",
                "type": "Performance Degradation",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "Stage 3 & 4 Burns"
            },
            {
                "order": 4,
                "title": "Sub-Orbital Injection of Trapped Satellite",
                "desc": "IRNSS-1H satellite separated inside closed heat shield into unusable low elliptical orbit.",
                "type": "Mission Loss",
                "relationship": "Confirmed Causal",
                "page": 1,
                "timestamp": "T+19 Minutes"
            }
        ]
    }
]

def run_seed_ingestion():
    init_db()
    db = SessionLocal()
    try:
        print("=" * 70)
        print("  MISSIONMIND AI - REPRODUCIBLE SEED DATA INGESTION PIPELINE")
        print("=" * 70)

        total_ingested = 0
        for item in DOCUMENTS_METADATA:
            source_pdf = item["folder"] / item["filename"]
            if not source_pdf.exists():
                print(f"[WARN] File not found: {source_pdf}. Skipping.")
                continue

            # Copy PDF into upload directory
            dest_pdf = Path(settings.UPLOAD_DIRECTORY) / item["filename"]
            shutil.copyfile(source_pdf, dest_pdf)

            # Ensure Mission record exists
            mission = db.query(Mission).filter(Mission.mission_name == item["mission_name"]).first()
            if not mission:
                mission = Mission(
                    mission_name=item["mission_name"],
                    space_agency=item["space_agency"],
                    launch_year=item["publication_year"],
                    mission_description=f"Official investigation findings for {item['mission_name']}.",
                    outcome="Failure"
                )
                db.add(mission)
                db.commit()
                db.refresh(mission)

            # Check if Document already exists
            doc = db.query(Document).filter(
                Document.title == item["title"],
                Document.mission_name == item["mission_name"]
            ).first()

            if not doc:
                doc = Document(
                    title=item["title"],
                    mission_name=item["mission_name"],
                    space_agency=item["space_agency"],
                    publication_year=item["publication_year"],
                    document_type=item["document_type"],
                    source_url=item["source_url"],
                    licence=item["licence"],
                    file_path=str(dest_pdf),
                    processing_status="pending"
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)

            # Run PyMuPDF chunking & embedding pipeline
            result = DocumentProcessor.process_pdf_document(db, doc.id)
            print(f"[INGESTED] #{doc.id} {doc.title} -> {result['total_pages']} pages, {result['total_chunks']} chunks")

            # Check if FailureIncident already exists
            incident = db.query(FailureIncident).filter(
                FailureIncident.document_id == doc.id
            ).first()

            if not incident:
                incident = FailureIncident(
                    mission_id=mission.id,
                    document_id=doc.id,
                    failure_description=f"Investigation into {item['mission_name']} anomaly.",
                    subsystem=item["subsystem"],
                    failure_mode=item["failure_mode"],
                    trigger="Flight Telemetry Anomaly",
                    root_cause=item["root_cause"],
                    mission_phase=item["mission_phase"],
                    mission_impact=item["mission_impact"],
                    corrective_action=item["corrective_action"],
                    source_page=item["source_page"]
                )
                db.add(incident)
                db.commit()
                db.refresh(incident)

                # Add Chronological Failure Events
                for ev in item.get("events", []):
                    # Link to first chunk matching source page
                    chunk = db.query(DocumentChunk).filter(
                        DocumentChunk.document_id == doc.id,
                        DocumentChunk.page_number == ev["page"]
                    ).first()

                    fe = FailureEvent(
                        incident_id=incident.id,
                        event_order=ev["order"],
                        event_title=ev["title"],
                        event_description=ev["desc"],
                        event_type=ev["type"],
                        relationship_type=ev["relationship"],
                        event_timestamp=ev.get("timestamp"),
                        source_page=ev["page"],
                        evidence_chunk_id=chunk.id if chunk else None
                    )
                    db.add(fe)
                db.commit()

            total_ingested += 1

        print("=" * 70)
        print(f"[SUCCESS] Ingested {total_ingested} official NASA & ISRO investigation reports.")
        print(f"Total Chunks in Vector DB: {db.query(DocumentChunk).count()}")
        print(f"Total Failure Incidents:   {db.query(FailureIncident).count()}")
        print(f"Total Failure Events:      {db.query(FailureEvent).count()}")
        print("=" * 70)
    finally:
        db.close()

if __name__ == "__main__":
    run_seed_ingestion()
