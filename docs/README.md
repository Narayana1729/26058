# 📑 Technical Engineering Documentation
### SIH 2026 — Problem Statement 26058: AUV Software-Defined Sonar Transmitter

This directory contains the formal engineering reports, design specifications, verification procedures, and hardware datasheets for the **Intelligent Self-Monitoring Adaptive Sonar Transmitter Payload**.

---

## 📂 Documentation Directory

| Document | Purpose & Scope |
|---|---|
| [**`TECHNICAL_DESIGN_REPORT.md`**](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/docs/TECHNICAL_DESIGN_REPORT.md) | Comprehensive engineering dossier detailing system requirements, acoustic physics modeling, analog front-end (AFE) reconstruction filter, power stage, embedded ARM firmware architecture, and verification results. |
| [**`ACCEPTANCE_TEST_PROCEDURE_ATP.md`**](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/docs/ACCEPTANCE_TEST_PROCEDURE_ATP.md) | Formal verification and validation (V&V) matrix defining quantitative pass/fail acceptance gates for DSP waveforms, analog filters, electrical metrology, and power budget governance. |
| [**`DATASHEET_SDR_SONAR_PAYLOAD_V1.md`**](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/docs/DATASHEET_SDR_SONAR_PAYLOAD_V1.md) | Engineering hardware datasheet specifying electrical ratings, mechanical dimensions, pin definitions, interface protocols, and thermal envelope limits. |
| [**`component_list_BOM.md`**](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/docs/component_list_BOM.md) | Detailed Bill of Materials (BOM) with manufacturer part numbers, commercial pricing (INR / USD), PCB component footprints, and thermal ratings. |
| [**`DESIGN_METHODOLOGY.md`**](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/docs/DESIGN_METHODOLOGY.md) | System design methodology, simulation workflows (Python, LTspice, Proteus VSM), and hardware-in-the-loop validation pipeline. |
| [**`LTSPICE_SIMULATION_ANALYSIS.md`**](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/docs/LTSPICE_SIMULATION_ANALYSIS.md) | In-depth frequency identification, transient response, noise rejection, and diode clamping guide for LTspice analog filter verification. |
| [**`SIMULATION_ARCHITECTURE_GUIDE.md`**](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/docs/SIMULATION_ARCHITECTURE_GUIDE.md) | Visual subsystem guide detailing multi-layer simulation architecture, testbenches, and subsea enclosure mechanical CAD renderings. |
| [**`assumptions.md`**](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/docs/assumptions.md) | Scientific and engineering assumptions across underwater channel acoustics, transducer resonance, battery discharge profiles, and thermal dynamics. |

---

## 🖼️ Architectural Figures & System Schematics
* **`assets/`**: High-resolution system block diagrams, Proteus VSM co-simulation schematics, and AUV payload pod mechanical CAD renderings.
* **`exp02_frequency.png`**: Frequency selection vs. water turbidity empirical study.
* **`exp03_closed_loop.png`**: Two-stage closed-loop adaptation simulation trace.
* **`exp04_hfm_lfm.png`**: Doppler tolerance comparison between LFM and HFM chirps under relative velocity shifts.
