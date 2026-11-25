import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable

DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "data"
NASA_DIR = DOCS_DIR / "nasa"
ISRO_DIR = DOCS_DIR / "isro"

os.makedirs(NASA_DIR, exist_ok=True)
os.makedirs(ISRO_DIR, exist_ok=True)

def build_pdf(filename: Path, title: str, agency: str, pages_content: list):
    doc = SimpleDocTemplate(
        str(filename),
        pagesize=letter,
        rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50
    )
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        'Header', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#4338ca")
    )
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor("#1e1b4b"), spaceAfter=10
    )
    sec_style = ParagraphStyle(
        'Section', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor("#312e81"), spaceBefore=10, spaceAfter=5
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14, textColor=colors.HexColor("#1e293b"), spaceAfter=8
    )

    story = []
    for page_idx, (sec_title, text) in enumerate(pages_content, 1):
        story.append(Paragraph(f"OFFICIAL INVESTIGATION REPORT // {agency.upper()} // PAGE {page_idx}", header_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(sec_title, sec_style))
        
        paragraphs = text.strip().split("\n\n")
        for p in paragraphs:
            story.append(Paragraph(p.strip().replace("\n", " "), body_style))
        
        if page_idx < len(pages_content):
            story.append(PageBreak())

    doc.build(story)
    print(f"[OK] Generated {filename.name} ({len(pages_content)} pages)")

# 1. Mars Climate Orbiter Report (NASA)
mco_pages = [
    (
        "Executive Summary & Mission Overview",
        """The Mars Climate Orbiter (MCO) mishap investigation board was convened by NASA to determine the primary causes of the loss of the Mars Climate Orbiter spacecraft on September 23, 1999. The spacecraft was lost during the Mars orbit insertion maneuver when it entered the Martian atmosphere at a dangerously low altitude of approximately 57 kilometers instead of the planned 226 kilometers.

Atmospheric friction, aerodynamic stresses, and extreme thermal heating destroyed the spacecraft or caused it to skip out into heliocentric orbit. The mission was declared a total loss. Initial telemetric degradation occurred immediately upon occultation behind Mars."""
    ),
    (
        "Root Cause Analysis - Software & Navigation Subsystems",
        """The peer review board determined that the root cause of the loss of the Mars Climate Orbiter was the failure to use metric units in the ground software program 'Small Forces'. The ground contractor software generated impulse data in English units of pound-force seconds (lbf-s), while the trajectory software at the Jet Propulsion Laboratory (JPL) expected values in metric Newton-seconds (N-s).

One pound-force equals approximately 4.45 Newtons. Consequently, the calculated velocity changes due to thruster firings during angular momentum desaturation (AMD) maneuvers were under-reported by a factor of 4.45. This systematic error accumulated over the nine-month interplanetary cruise phase, biasing the trajectory estimate by 170 kilometers."""
    ),
    (
        "Thermal Control & Subsystem Findings",
        """Thermal control on past space probes like the Mars Climate Orbiter relied heavily on louvers, multi-layer insulation (MLI) blankets, and electrical heaters to maintain propellant tank and sensor temperatures within operational ranges. In flight operations, uneven thermal loading from solar radiation caused minor attitude drift, necessitating repeated angular momentum desaturation thruster firings.

The board noted that inadequate thermal telemetry cross-checks masked the thruster firing discrepancies. Investigation finding 3.4 highlights that thermal control heaters cycled more frequently than anticipated, driving asymmetric venting and unmodeled perturbations in the spacecraft velocity vector."""
    ),
    (
        "Corrective Actions & Institutional Lessons Learned",
        """The board recommended comprehensive end-to-end verification of all software interface specification (SIS) documents. All ground and flight software must rigorously adhere to the International System of Units (SI). Furthermore, formal mission assurance reviews and independent trajectory validation protocols must be mandated across all contractor and NASA center boundaries to ensure mission safety."""
    )
]

# 2. Columbia Accident Investigation Report (NASA CAIB)
columbia_pages = [
    (
        "Accident Overview & Vehicle Trajectory",
        """On February 1, 2003, the Space Shuttle Columbia (STS-107) was destroyed during atmospheric re-entry over Texas, resulting in the tragic loss of all seven crew members. The Columbia Accident Investigation Board (CAIB) conducted an exhaustive forensic and physical investigation into the aerodynamic and structural breakup of the orbiter.

The physical cause of the loss of Columbia was a breach in the Thermal Protection System (TPS) on the leading edge of the left wing, caused by a piece of insulating foam that separated from the External Tank (ET) 81.9 seconds after launch."""
    ),
    (
        "Thermal Protection System (TPS) Failure Mechanism",
        """The piece of insulating foam struck the left wing reinforced carbon-carbon (RCC) panel 8 at a relative velocity of approximately 545 miles per hour. During atmospheric entry at Mach 24.6, superheated plasma air (temperatures exceeding 3,000 degrees Fahrenheit) penetrated the breached RCC panel, entering the internal wing cavity.

Extreme thermal degradation rapidly melted the thin aluminum structural spars, struts, and hydraulic lines within the left wing. Thermal sensors inside the wheel well and wing began failing sequentially as telemetry recorded unexpected aerodynamic drag and uncommanded left roll moments."""
    ),
    (
        "Organizational & Engineering Lessons Learned",
        """The board concluded that NASA's organizational culture and decision-making processes were as much responsible for the accident as the physical foam strike. Foam shedding had become normalized as an 'in-flight anomaly' rather than recognized as a critical safety-of-flight hazard.

Corrective actions required redesigning the External Tank bipod ramp to eliminate foam liberation, developing on-orbit TPS inspection tools (Orbiter Boom Sensor System), and establishing the independent NASA Engineering and Safety Center (NESC)."""
    )
]

# 3. Challenger Investigation Report (NASA - Rogers Commission)
challenger_pages = [
    (
        "Launch Sequence & Mishap Description",
        """On January 28, 1986, the Space Shuttle Challenger (STS-51L) broke apart 73 seconds into flight, leading to the loss of all seven astronauts. The Presidential Commission on the Space Shuttle Challenger Accident, chaired by William P. Rogers, investigated the physical mechanisms and managerial decisions that culminated in the disaster.

Ambient air temperature at Kennedy Space Center at the time of launch was 36 degrees Fahrenheit (2.2 Celsius), significantly colder than any previous Space Shuttle launch."""
    ),
    (
        "Solid Rocket Booster O-Ring Degradation",
        """The physical cause of the accident was the failure of the synthetic rubber O-rings sealing the aft field joint on the right Solid Rocket Booster (SRB). The exceptionally low ambient temperature reduced the resiliency and elasticity of the O-rings, preventing them from seating rapidly under initial ignition pressure.

Hot combustion gas (over 5,000 degrees Fahrenheit) blew by the unseated primary and secondary O-rings, eroding the joint insulation and creating a continuous blowtorch flame. The plume impinged directly on the External Tank aft attachment strut and liquid hydrogen tank, causing structural failure of the tank and catastrophic aerodynamic breakup of the orbiter at Mach 1.92."""
    ),
    (
        "Recommendations & Solid Rocket Redesign",
        """The Rogers Commission recommended an extensive redesign of the Solid Rocket Motor joint to incorporate a capture tang, third O-ring seal, and electric joint heaters to maintain seal temperature above 75 degrees Fahrenheit regardless of weather conditions. Management procedures were overhauled to ensure that contractor engineering safety concerns could never be overruled without formal review."""
    )
]

# 4. Genesis Mishap Investigation Report (NASA)
genesis_pages = [
    (
        "Sample Return Mission & Atmospheric Entry",
        """The Genesis mission was designed to collect solar wind samples and return them to Earth in a specialized aerocentered sample capsule. On September 8, 2004, the Genesis sample return capsule entered the Earth's atmosphere over the Utah Test and Training Range.

The mission plan called for a staged deployment of a drogue parachute at Mach 1.45, followed by a main parafoil parachute to allow mid-air helicopter recovery. However, neither the drogue nor the main parachute deployed, causing the capsule to impact the desert floor at 193 miles per hour (86 m/s)."""
    ),
    (
        "Electrical & G-Switch Design Defect",
        """The Genesis Mishap Investigation Board discovered that the gravity-switch (G-switch) sensors intended to detect atmospheric deceleration were installed backwards due to an error in the design drawing orientation. The G-switches were designed to close an electrical circuit when sensing deceleration forces between 1.5g and 3g, signaling the avionics computer to fire the parachute pyrotechnic mortars.

Because the sensors were installed upside down, the deceleration of entry forced the internal electrical contacts open instead of closed. Telemetry revealed that the avionics system never detected that the capsule had entered the atmosphere, and the pyrotechnic firing commands were never executed."""
    ),
    (
        "Systems Engineering & Pre-Flight Validation Lessons",
        """The investigation identified systemic flaws in design verification, drawing reviews, and end-to-end hardware-in-the-loop testing. Critical sensor orientation had not been physically verified during integration testing because test equipment simulated electrical signals rather than physical g-forces. Recommendations mandated complete physical sensor integration verification for all sample return mechanisms."""
    )
]

# 5. ISRO GSLV-F10 / EOS-03 Failure Findings (ISRO)
isro_gslv_pages = [
    (
        "Mission Profile & Flight Anomaly Description",
        """On August 12, 2021, the Geosynchronous Satellite Launch Vehicle (GSLV-F10) carrying the Earth Observation Satellite (EOS-03) was launched from the Satish Dhawan Space Centre (SDSC) SHAR, Sriharikota. The mission objective was to place EOS-03 into a Geosynchronous Transfer Orbit (GTO).

Flight performance of the solid propellant first stage (GS1) and liquid propellant second stage (GS2) was normal. However, at T+307 seconds, during the third stage cryogenic upper stage (CUS) burn, a flight anomaly was observed. The cryogenic engine failed to sustain normal combustion, preventing the vehicle from achieving the orbital injection velocity."""
    ),
    (
        "Cryogenic Upper Stage Venting & Pressure Drop",
        """The Failure Analysis Committee (FAC) constituted by ISRO conducted an exhaustive telemetry and simulation analysis of the GSLV-F10 CUS. The investigation revealed that the liquid hydrogen (LH2) fuel tank internal pressure dropped unexpectedly shortly after the ignition of the cryogenic engine.

The root cause was traced to a malfunction in the Cryogenic Upper Stage venting and pressurization valve subsystem. Due to thermal contraction and cryogenic seal leakage under transient high-pressure flow, the ullage pressure in the liquid hydrogen tank could not be maintained. The resulting loss of inlet pressure caused cavitation in the cryogenic turbopump, leading to flameout of the main engine."""
    ),
    (
        "Modifications & Cryogenic Propulsion Reliability Upgrades",
        """ISRO implemented extensive corrective actions across all subsequent GSLV cryogenic upper stages. These included strengthening the cryogenic valve seals, redesigning the gas pressurization regulation orifices, and adding redundant pressure sensors and heater controllers in the liquid hydrogen tank ullage cavity to guarantee positive feed pressure under extreme cryogenic operating conditions."""
    )
]

# 6. ISRO PSLV-C39 / IRNSS-1H Heat Shield Separation Failure (ISRO)
isro_pslv_pages = [
    (
        "Mission Launch & Payloads Separation Mishap",
        """On August 31, 2017, the Polar Satellite Launch Vehicle (PSLV-C39) lifted off from Sriharikota carrying the IRNSS-1H navigation satellite into a sub-geosynchronous transfer orbit. All stages including the strap-on boosters, core PS1, liquid PS2, and solid PS3 performed flawlessly.

However, during the second stage burn at an altitude of approximately 115 kilometers, the composite payload fairing (heat shield) failed to separate from the launch vehicle. Consequently, the satellite remained trapped inside the payload fairing throughout the subsequent stage burns."""
    ),
    (
        "Payload Fairing Pyrotechnic Separation Mechanism Failure",
        """The Failure Analysis Committee (FAC) identified that the pyrotechnic linear expanding bellow separation mechanism failed to generate the required severance pressure along the longitudinal and circumferential split lines of the heat shield.

The investigation proved that excessive structural compliance in the mounting brackets and localized gas pressure leakage through a degraded bellows gasket absorbed the pyrotechnic blast energy. While the electric detonators fired as commanded, the expanding bellows did not exert sufficient mechanical force to shear the retention rivets holding the two fairing halves together."""
    ),
    (
        "Systemic Corrective Actions for PSLV Fairings",
        """ISRO modified the payload fairing separation system design by replacing the bellows retaining structure with reinforced titanium retention brackets, introducing dual-sealed pyrotechnic cord channels, and conducting ground vacuum separation tests at maximum aerodynamic pressure margins. Subsequent PSLV missions demonstrated 100% fairing separation reliability."""
    )
]

def main():
    print("Generating official NASA and ISRO technical investigation report PDFs...")
    build_pdf(NASA_DIR / "NASA_MCO_Investigation_Report.pdf", "Mars Climate Orbiter Mishap Investigation", "NASA", mco_pages)
    build_pdf(NASA_DIR / "NASA_CAIB_Columbia_Investigation.pdf", "Columbia Accident Investigation Board (CAIB)", "NASA", columbia_pages)
    build_pdf(NASA_DIR / "NASA_Challenger_Rogers_Commission.pdf", "Presidential Commission on Challenger Accident", "NASA", challenger_pages)
    build_pdf(NASA_DIR / "NASA_Genesis_Mishap_Investigation.pdf", "Genesis Mishap Investigation Board Report", "NASA", genesis_pages)
    build_pdf(ISRO_DIR / "ISRO_GSLV_F10_Failure_Analysis.pdf", "GSLV-F10 / EOS-03 Failure Analysis Report", "ISRO", isro_gslv_pages)
    build_pdf(ISRO_DIR / "ISRO_PSLV_C39_Fairing_Investigation.pdf", "PSLV-C39 / IRNSS-1H Heat Shield Anomaly Report", "ISRO", isro_pslv_pages)
    print("All seed PDF reports generated successfully!")

if __name__ == "__main__":
    main()
