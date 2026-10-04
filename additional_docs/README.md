# 📁 Additional Docs & Engineering Dossier
### OCEAN-SDR: Autonomous Software-Defined Acoustic Transmitter for AUVs

This directory contains the complete supporting engineering archive, simulation assets, presentation graphics, LTspice circuit models, and verification protocols organized into clear sub-folders.

---

## 🗂️ Folder Structure Overview

```
additional_docs/
├── technical_reports/                       # Comprehensive engineering & mathematical specifications
│   ├── TECHNICAL_DESIGN_REPORT.md           # Master 10-section technical dossier
│   ├── LTSPICE_SIMULATION_ANALYSIS.md       # LTspice simulation analysis & verification
│   ├── analog_filter_design_brief.md        # 4th-order Sallen-Key analog filter brief
│   └── MASTER_PIN_MAP.md                    # Authoritative hardware pin & register mapping
│
├── presentation_slides/                     # Ready-to-insert high-resolution (300 DPI) slide graphics
│   ├── dual_loop_adaptation_clean_white.png # Flagship Dual-Loop Architecture (White Theme)
│   ├── dual_loop_adaptation_slide.png       # Flagship Dual-Loop Architecture (Dark / Cyber Theme)
│   ├── ocean_sdr_flow_chart.png             # Adaptive signal processing & environmental sounding flowchart
│   ├── simple_architecture_clean_white.png  # 5-stage system architecture (White Theme)
│   ├── ocean_sdr_simple_architecture.png    # 5-stage system architecture (Dark / Cyber Theme)
│   ├── simple_architecture_slide.png        # Dual-card hardware + telemetry architecture
│   ├── hardware_and_software_card.png       # Hardware & Software component breakdown card
│   └── technologies_and_sources_slide.png   # Technologies, Tools & Acoustic Data Sources card
│
├── simulation_images/                       # Scientific graphs & acoustic simulation outputs
│   ├── windowing_and_dsp/
│   │   ├── all_windows_benchmark_theme.png  # Windowing benchmark with micro-sparklines
│   │   └── windowing_comparison_theme.png   # Spectral leakage & pulse compression analysis
│   └── hydroacoustics/
│       ├── ocean_absorption_verification.png# Francois-Garrison multi-depth absorption sweeps
│       ├── exp03_closed_loop.png            # In-situ pulse energy & thermal throttling curves
│       ├── exp04_hfm_lfm.png                # Doppler tolerance (LFM vs. HFM chirp)
│       ├── waveform_bank_verification.png   # Time/frequency plots of synthesized acoustic pings
│       ├── filter_baseband_verification.png # Sallen-Key low-pass filter verification
│       └── bode_plot_ultrasonic.png         # Ultrasonic transducer frequency response
│
├── ltspice_testings/                        # Analog circuit simulation testbenches & results
│   ├── schematics/
│   │   ├── sallen_key_4th_order.asc         # 4th-order active reconstruction filter (.asc)
│   │   ├── sallen_key_4th_order_piezo.asc   # Filter + BVD equivalent piezo load (.asc)
│   │   ├── TL072.sub                        # JFET operational amplifier SPICE subcircuit
│   │   └── staircase_sine.txt               # Piecewise linear DAC staircase stimulus
│   └── simulation_plots/
│       ├── sim1_bode.png                    # Magnitude & Phase Bode response (fc = 100 kHz)
│       ├── sim2_passband_1k.png             # 1 kHz sine passband fidelity
│       ├── sim2_passband_10k.png            # 10 kHz passband waveform & harmonic distortion
│       ├── sim3_noise_rejection.png         # 1 MHz DAC quantization switching noise rejection
│       ├── sim4_overvoltage.png             # Rail-to-rail dynamic range & clipping limits
│       ├── sim5_dual_band.png               # Dual-band frequency response test
│       ├── bonus_piezo_load.png             # Transducer BVD reactive loading transient sweep
│       └── bode_plot_ultrasonic.png         # Ultrasonic bandwidth response
│
└── acceptance_testing_and_protocols/        # Hardware Bring-Up, Test Procedures & Flashing
    ├── ACCEPTANCE_TEST_PROCEDURE_ATP.md     # Official ATP test script (DC, Signal, Thermal, Fault)
    └── DEPLOYMENT_GUIDE.md                  # STM32CubeIDE flashing, DMA configuration & ST-LINK guide
```

---

## 📌 Quick File Index

### 1. Technical Reports (`technical_reports/`)
* [TECHNICAL_DESIGN_REPORT.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/technical_reports/TECHNICAL_DESIGN_REPORT.md) — Comprehensive technical documentation of the entire OCEAN-SDR system.
* [LTSPICE_SIMULATION_ANALYSIS.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/technical_reports/LTSPICE_SIMULATION_ANALYSIS.md) — Mathematical and simulated verification of the active Sallen-Key filter.
* [analog_filter_design_brief.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/technical_reports/analog_filter_design_brief.md) — Component selection, cutoff frequency, and damping factor rationale.
* [MASTER_PIN_MAP.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/technical_reports/MASTER_PIN_MAP.md) — Pinout assignment, DMA channels, and timer triggers.

### 2. Presentation Slide Images (`presentation_slides/`)
* [ocean_sdr_flow_chart.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/simulation_images/presentation_slides/ocean_sdr_flow_chart.png) — Presentation flowchart matching your reference diagram.
* [simple_architecture_clean_white.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/simulation_images/presentation_slides/simple_architecture_clean_white.png) — Clean white 5-stage architecture slide graphic.
* [ocean_sdr_simple_architecture.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/simulation_images/presentation_slides/ocean_sdr_simple_architecture.png) — High-tech dark theme architecture slide graphic.
* [hardware_and_software_card.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/simulation_images/presentation_slides/hardware_and_software_card.png) — Bulleted hardware & software card matching your reference.
* [technologies_and_sources_slide.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/simulation_images/presentation_slides/technologies_and_sources_slide.png) — Dual-section tools, models & data sources card.

### 3. DSP & Hydroacoustic Simulations (`simulation_images/`)
* [all_windows_benchmark_theme.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/simulation_images/windowing_and_dsp/all_windows_benchmark_theme.png) — Comprehensive comparison of all tapering windows with individual sparklines.
* [ocean_absorption_verification.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/simulation_images/hydroacoustics/ocean_absorption_verification.png) — Francois-Garrison multi-mechanism chemical absorption model.
* [exp03_closed_loop.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/simulation_images/hydroacoustics/exp03_closed_loop.png) — Closed-loop thermal power throttling experiment.

### 4. LTspice Circuit Testings (`ltspice_testings/`)
* [sallen_key_4th_order.asc](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/ltspice_testings/schematics/sallen_key_4th_order.asc) — Runnable LTspice schematic file.
* [sallen_key_4th_order_piezo.asc](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/ltspice_testings/schematics/sallen_key_4th_order_piezo.asc) — Schematic including Butterworth-Van Dyke (BVD) transducer model.
* [sim1_bode.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/ltspice_testings/simulation_plots/sim1_bode.png) — Frequency sweep confirming -3 dB corner at 100 kHz.
* [bonus_piezo_load.png](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/ltspice_testings/simulation_plots/bonus_piezo_load.png) — Transient response under complex capacitive transducer load.

### 5. Testing & Deployment Protocols (`acceptance_testing_and_protocols/`)
* [ACCEPTANCE_TEST_PROCEDURE_ATP.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/acceptance_testing_and_protocols/ACCEPTANCE_TEST_PROCEDURE_ATP.md) — 4-stage hardware bring-up and acceptance testing protocol.
* [DEPLOYMENT_GUIDE.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/additional_docs/acceptance_testing_and_protocols/DEPLOYMENT_GUIDE.md) — Step-by-step firmware deployment and ST-LINK flashing instructions.
