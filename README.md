# 🌊 Intelligent Self-Monitoring Adaptive Sonar Transmitter for AUVs
### Smart India Hackathon (SIH 2026) — Problem Statement 26058
**"Development of a Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for Autonomous Underwater Vehicles (AUVs)"**

[![Architecture: Closed-Loop Transmitter Self-Optimization](https://img.shields.io/badge/Architecture-Closed--Loop%20Transmitter%20Self--Optimization-0052CC.svg)](#)
[![Hardware: STM32 ARM Cortex-M](https://img.shields.io/badge/MCU-STM32%20ARM%20Cortex--M-002E5F.svg)](#)
[![Validation: Benchtop Electrical Metrology](https://img.shields.io/badge/Metrology-Real--Time%20Power%20%26%20Thermal-2E7D32.svg)](#)
[![Scope: Transmitter-Only MVP](https://img.shields.io/badge/Scope-Transmitter--Only%20MVP-orange.svg)](#)

---

## 📌 Authoritative Project Identity & Summary

> **Core Concept**:  
> **A real-time, environment-aware, energy-constrained, self-monitoring software-defined sonar transmitter for AUVs.**

Autonomous Underwater Vehicles (AUVs) operate under severe environmental variability and rigid energy limitations. Traditional acoustic pingers rely on fixed transmission profiles that either waste critical battery capacity or fail to provide adequate signal penetration when water properties shift.

### Short Innovation Statement
> **The transmitter does not merely generate a programmed sonar waveform; it senses its operating environment, predicts an appropriate transmission configuration, measures its own electrical energy and thermal state, and autonomously regulates subsequent transmissions within defined performance and power constraints.**

### Scope of Current MVP: Transmitter-Only
* **Current Prototype**: **100% Transmitter-Only**. Focused entirely on embedded waveform synthesis, environmental prediction, real-time electrical power measurement, power budget governance, thermal protection, and pre-mission self-characterization.
* **No Acoustic Receiver Dependency**: Does **not** require a microphone, hydrophone, external acoustic receiver, or acoustic feedback loop for its core operation.
* **Feedback Mechanism**: Defined strictly as **Closed-Loop Transmitter Self-Optimization** (measuring internal electrical efficiency and thermal health), not measured acoustic echo quality.
* **Future Extension**: Acoustic receiver and hydrophone feedback remain a planned **V2/V3 research phase** for validating in-water acoustic returns.

---

## 🏛️ Authoritative System Architecture

```
                  OCEAN CONDITIONS
       (Temp T, Depth D, Turbidity NTU, Salinity S)
                        │
                        ▼
              ┌──────────────────┐
              │  Adaptive Engine │  ← [Francois-Garrison Absorption Model]
              │  (Physical Prior)│    [Mackenzie Sound Speed Profile]
              └────────┬─────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Frequency   Pulse Width   Amplitude
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                WAVEFORM ENGINE
           (DDS / Circular DMA Engine)
           [Tukey Digital Windowing α=0.25]
                       │
                       ▼
                 DAC CONVERTER
             (STM32 12-Bit DAC1 @ PA4)
                       │
                       ▼
           ┌───────────────────────┐
           │ RECONSTRUCTION FILTER │ ← [4th-Order Active Sallen-Key LPF]
           │    + RLC NOTCH TRAP   │   (Attenuates DAC clock spurs >48 dB)
           └───────────┬───────────┘
                       │
                       ▼
                  POWER STAGE
            (Half-Bridge Switching PA)
            (Dual Logic-Level N-FETs)
                       │
                       ▼
               ACOUSTIC TRANSDUCER
            (Piezo Projector / BVD Load)
                       │
                       ▼
                 ACOUSTIC PULSE
                       │
                       │ [Coupled Electrical & Thermal Dynamics]
                       ▼
           ┌───────────────────────┐
           │ SENSOR RC LPF FILTERS │ ← [Anti-Aliasing & Switching Glitch Filters]
           └───────────┬───────────┘   (Low-pass fc ≈ 159 kHz on metrology lines)
                       │
                       ▼
               ┌───────────────┐
               │  SELF MONITOR │ ← [Synchronous 6-Ch ADC DMA Engine]
               │  V / I / T_PA │   (PA5: INA180 Shunt, PA6: V_rail, PA7: Heatsink)
               └───────┬───────┘
                       │
                       ▼
                 POWER GOVERNOR
            (E_pulse = ∫ V·I dt)
            (E_rem Mission Budget Tracker)
            (Autonomous Thermal State Machine)
                       │
                       └───────────────────→ ADAPT
                                 (Feedback into Adaptive Engine)
```

---

## 💎 The Five-Layer Novelty Stack

### Layer 1: Software-Defined Waveform Agility
The transmitted acoustic pulse is parameterized as a dynamic vector:
$$W = \{f_c, B, T_p, A, \text{Type}\}$$
* **Parameters**: Center Frequency ($f_c$), Modulation Bandwidth ($B$), Pulse Duration ($T_p$), Normalized Amplitude ($A$), and Waveform Family ($\text{Type}$).
* **Supported Waveform Families**:
  * **Continuous Wave (CW)**: High spectral purity, baseline Doppler measurement.
  * **Linear Frequency Modulation (LFM Chirp)**: High pulse compression ratio ($PCR = B \cdot T_p$) with Tukey envelope ($\alpha = 0.25$) for sidelobe suppression.
  * **Hyperbolic Frequency Modulation (HFM Chirp)**: Doppler-tolerant logarithmic sweeps.
  * **Barker-Coded Pulses**: Discrete 13-bit bi-phase modulated pulses for high peak autocorrelation.
* *Note*: No single waveform is claimed to be universally superior; the controller selects among experimentally characterized candidates.

### Layer 2: Environment-Aware Waveform Prior
Environmental sensors provide real-time water column telemetry:
* **Inputs**: Water Temperature ($T$), Hydrostatic Depth ($D$), Turbidity ($\text{NTU}$), and Salinity ($S$).
* **Propagation Model**: The embedded engine evaluates the **Francois-Garrison (1982)** absorption formulation ($\alpha(f)$ in $\text{dB/km}$) to predict high-frequency attenuation.
* **Acoustic Prior Generation**:
  $$W_0 = f(\text{environmental state})$$
  *Note*: This output serves as a *model-predicted candidate prior*, not an empirical claim of measured in-water acoustic return.

### Layer 3: Energy-Aware Transmission Optimization
The transmitter directly measures the electrical energy dissipated during each acoustic ping:
$$E_{\text{pulse}} = \int_0^{T_p} V(t) \cdot I(t) \, dt \quad \approx \quad \sum_{n=0}^{N-1} V[n] \cdot I[n] \cdot \Delta t$$
$$P_{\text{avg}} = \frac{E_{\text{pulse}}}{T_p}$$
The controller solves an on-chip constrained optimization objective:
$$\max_{W \in \mathcal{W}} \quad \frac{Q_{\text{model}}(W)}{E_{\text{pulse}}(W)} \quad \text{subject to} \quad E_{\text{pulse}} \le E_{\text{cap}}, \quad T_{\text{PA}} \le T_{\max}$$
* $Q_{\text{model}}(W)$: Model-predicted transmission capability (range/resolution trade-off).
* $E_{\text{pulse}}(W)$: Directly measured electrical energy per pulse.

### Layer 4: Self-Monitoring Hardware Health
The on-board hardware continuously samples electrical and thermal telemetry via dedicated ADC/DMA channels:
* **Supply Voltage**: Monitors battery sag under heavy acoustic drive.
* **Transmit Current**: High-speed shunt resistor with differential amplifier sensing instantaneous load current.
* **Electrical Load and Power Response**: Monitors active drive efficiency.
* **PA Thermal State**: Direct temperature sensor mounted on the power stage heatsink.
* **Duty Cycle**: Enforces safe acoustic recovery periods between consecutive pulses.

### Layer 5: Real-Time Autonomous Power Governance
The transmitter actively monitors cumulative mission energy expenditure against a user-configured budget:
$$E_{\text{remaining}} = E_{\text{budget}} - \sum E_{\text{pulse}}$$
* **Autonomous Operating States**:
  * **High Energy Available ($> 60\%$)**: Performance-oriented waveforms (wideband LFM chirps, full amplitude).
  * **Energy Reducing ($20\% - 60\%$)**: Energy-efficient waveforms (balanced bandwidth, reduced pulse duration).
  * **Critical Energy ($< 20\%$)**: Conservative transmission mode (narrowband pulses, throttled amplitude to conserve battery).
* **Thermal Protection State Machine**:
  $$\text{Normal} \longrightarrow \text{Warning} \longrightarrow \text{Thermal Throttling (reduced duty cycle / pulse energy)} \longrightarrow \text{Safe Shutdown}$$

---

## ⚡ Two-Stage Adaptation Engine

The core decision pipeline executes in real time on the STM32 ARM Cortex-M core:

```
[ SENSE ]    Sample Temperature, Depth, Turbidity, Salinity
    ↓
[ PREDICT ]  Evaluate Francois-Garrison Acoustic Absorption Model
             Generate Candidate Waveform Prior W₀
    ↓
[ CONFIGURE ]Load Timer Auto-Reload (ARR) & Waveform DDS Pointers
    ↓
[ TRANSMIT ] Zero-CPU Circular DMA Streaming (TIM_TRGO → DAC → AFE → PA)
    ↓
[ MEASURE ]  Sample Shunt Current & Supply Voltage during pulse
             Sample Power Amplifier Temperature
    ↓
[ EVALUATE ] Compute E_pulse = ∫ V·I dt and update E_remaining
             Check Thermal & Power Budget Constraints
    ↓
[ ADAPT ]    Update Waveform Vector W for Subsequent Transmission
```

---

## 🔍 Pre-Mission Self-Characterization Routine

Before embarking on an autonomous mission, the transmitter executes an automated electrical diagnostics and calibration sweep:

```
SYSTEM STARTUP
     ↓
Hardware Rail & Health Diagnostics
     ↓
Transmit Candidate Waveform 1 (e.g., CW @ 100 kHz)
     ↓ Measure V, I, E_pulse, and Temperature Rise
Transmit Candidate Waveform 2 (e.g., LFM @ 200 kHz)
     ↓ Measure V, I, E_pulse, and Temperature Rise
Transmit Candidate Waveform 3 (e.g., Barker @ 300 kHz)
     ↓ Measure V, I, E_pulse, and Temperature Rise
     ↓
Build Measured Hardware Efficiency Table (in Flash/SRAM)
     ↓
Select Valid Operating Region
     ↓
Enter Autonomous Mission Mode
```

### Empirical Calibration Profile (Benchtop Measured Structure)
| Waveform Type | Frequency ($f_c$) | Amplitude ($A$) | Pulse Duration ($T_p$) | Measured $E_{\text{pulse}}$ | Measured $\Delta T_{\text{PA}}$ |
|---|---|---|---|---|---|
| **CW** | *Measured* | *Measured* | *Measured* | *Measured* | *Measured* |
| **LFM Chirp** | *Measured* | *Measured* | *Measured* | *Measured* | *Measured* |
| **HFM Chirp** | *Measured* | *Measured* | *Measured* | *Measured* | *Measured* |
| **Barker Coded** | *Measured* | *Measured* | *Measured* | *Measured* | *Measured* |

*Claim Discipline: All values in the operational firmware are generated through live electrical calibration, never fabricated.*

---

## 📊 Three-Way Controller Benchmark

| Parameter / Feature | Baseline 1: Fixed Transmitter | Baseline 2: Environment-Only | Proposed: Self-Monitoring Adaptive |
|---|---|---|---|
| **Waveform Selection** | Static (Pre-configured) | Dynamically Selected (Model Prior) | **Dynamically Selected & Electrically Refined** |
| **Frequency & Bandwidth** | Fixed | Environment-Driven | **Environment-Driven with Power Optimization** |
| **Pulse Duration ($T_p$)** | Fixed | Static Rule | **Adaptive to Power Budget & Constraints** |
| **Amplitude ($A$)** | Fixed (100%) | Static Rule | **Throttled Dynamically based on $E_{\text{remaining}}$** |
| **Energy Budget Tracking** | ❌ Not Considered | ❌ Not Considered | **✅ Enforced ($E_{\text{budget}} - \sum E_{\text{pulse}}$)** |
| **PA Thermal Protection** | ❌ None | ❌ None | **✅ Active Duty Cycle / Energy Throttling** |
| **Electrical Self-Monitoring**| ❌ Open-Loop Blind | ❌ Open-Loop Blind | **✅ Real-Time Voltage, Current & Power Sensing** |
| **Real-Time On-Chip Loop** | ❌ None | Static Switch-Case | **✅ Real-Time Closed-Loop Self-Optimization** |

---

## 🗺️ Multi-Phase Development Roadmap

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [V0] Electrical Characterization (Benchtop Validation)                                 │
│  - Verify DDS generation, DAC/PWM clocking, Sallen-Key 4th-order filter response        │
│  - Calibrate shunt current sensor, voltage divider, and PA temperature monitoring      │
│  - Validate deterministic E_pulse integration on STM32 ARM Cortex-M                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [V1] Intelligent Self-Monitoring Transmitter (Current SIH MVP)                         │
│  - Ingest simulated/physical environmental telemetry (Temp, Turbidity, Depth)           │
│  - Implement Two-Stage Adaptation Engine (Model Prior + Electrical Refinement)         │
│  - Execute autonomous Power Budget Governor and PA Thermal Throttling                  │
│  - Demonstrate automated Pre-Mission Self-Characterization                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [V2] Marine Acoustic Hardware Upgrades (Future Extension)                              │
│  - Transition from bench electrical load to high-voltage underwater piezo transducer   │
│  - Characterize in-water electroacoustic efficiency and transducer resonance matching  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [V3] Closed-Loop Acoustic Channel Feedback (Long-Term Research Extension)             │
│  - Integrate calibrated hydrophone and receiver analog front-end (AFE)                 │
│  - Close the loop around received acoustic echo quality, SNR, and channel multipath    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Organization & Directory Map

The repository is strictly structured into modular engineering domains, adhering to the pin contract defined in [MASTER_PIN_MAP.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/MASTER_PIN_MAP.md):

```
SIH Hardware/
├── MASTER_PIN_MAP.md                  # Authoritative Pin Contract (STM32 Nucleo-64)
├── README.md                          # Master Technical Dossier & System Architecture
│
├── firmware/                          # Production Embedded C Firmware & Testbenches
│   ├── README.md                      # Industrial Build, Flash, and Testing Guide
│   ├── stm32_cubeide/                 # Bare-Metal C Project for STM32 Nucleo-64
│   │   ├── main.c                     # Full Firmware (DAC DMA, 6-Ch ADC, Governor, HUD)
│   │   ├── main.h                     # Hardware Pin Mappings & Function Prototypes
│   │   └── DEPLOYMENT_GUIDE.md        # Wiring & Flashing Instructions
│   ├── modular_stack/                 # Modular C Driver Pipeline (HAL, DSP, Control)
│   ├── include/                       # 12-Bit DAC Waveform Tables & Ocean Adaptation Rules
│   │   ├── chirp_lut.h                # 6-Profile Multi-Modulation Waveform Bank
│   │   ├── chirp_lut_8bit.h           # Laboratory 8-Bit Demonstration Audio Table
│   │   └── ocean_adaptation_table.h   # Turbidity Thresholds & Operating Profiles
│   └── tests/                         # Host-Compiled Unit Test Suite (100% Pass)
│       ├── test_two_stage_power_governor.c  # Energy Budgeting & Thermal State Machine
│       ├── test_adaptation.c          # Turbidity / Environmental Adaptation Logic
│       └── test_sonar_stack.c         # End-to-End Modular C Pipeline Verification
│
├── hardware/                          # Electrical Schematics, SPICE Models & Analog Front-End
│   ├── README.md                      # Circuit Topology, Component Ratings & Filter Theory
│   ├── spice/                         # LTspice 4th-Order Butterworth Filter Schematics (.asc)
│   │   ├── sallen_key_4th_order.asc   # Base 4th-Order Sallen-Key Active Filter
│   │   ├── sallen_key_4th_order_piezo.asc # Filter with Piezoelectric Transducer BVD Model
│   │   ├── TL072.sub                  # Macromodel for Op-Amp Stages
│   │   └── bode_plot_ultrasonic.png   # Passband & Stopband Attenuation Verification
│   └── docs/                          # Hardware Presentation & Technical Briefs
│       ├── walkthrough.md             # Theoretical Derivations & Sallen-Key Filter Design
│       └── analog_filter_design_brief.md # Technical Design Brief & Load Stability Analysis
│
├── simulation/                        # Numerical Modeling & Python Verification Engine
│   ├── README.md                      # Ocean Acoustics & Waveform Synthesis Documentation
│   ├── waveform_generator.py          # LFM Chirp & Cosine-Tapered Tukey Window Generator
│   ├── ocean_propagation_model.py     # Mackenzie (1981) & Francois-Garrison (1982) Solver
│   ├── filter_design_baseband.py      # Butterworth Filter Component & Cutoff Calculation
│   ├── simulate_filter_bode.py        # SPICE Netlist Parser & Bode Response Plotter
│   └── python/                        # Hydroacoustic Ocean Engine & Experiment Suite
│       ├── experiments/               # Empirical Waveform Studies (Exp 02-04)
│       ├── models/                    # Physical Absorption & Noise Attenuation Models
│       ├── tests/                     # Automated Python Unit Tests (test_acoustic_model.py)
│       └── utils/                     # Acoustic Signal Processing Utilities
│
├── ground_station/                    # Operator Telemetry, HUD & Interactive Workbench
│   ├── README.md                      # Ground Station User Guide & Protocol Definition
│   ├── sdr_sonar_ground_station.html  # Live Web-Serial Telemetry Display (115200 Baud)
│   └── sonar_dashboard/               # React 19 + Vite Interactive Acoustics Workbench
│
├── research/                          # V2/V3 Forward-Looking Research & Receiver Archive
│   ├── README.md                      # Research Roadmap Scope (Transmitter MVP vs V2 Receiver)
│   ├── docs/                          # Transceiver Research Plots, Impedance Maps & Tables
│   ├── legacy_dashboards/             # Early Visualizer Prototypes (acoustic_visualizer_v1.html)
│   └── simul/                         # Time-Gain Compensation (TGC) & Seabed Classification
│
└── docs/                              # Technical Engineering Reports & Datasheets
    ├── README.md                      # Index of Engineering Documentation
    ├── TECHNICAL_DESIGN_REPORT.md     # Full Engineering Dossier & System Architecture
    ├── ACCEPTANCE_TEST_PROCEDURE_ATP.md # Formal V&V Acceptance Test Matrix
    ├── DATASHEET_SDR_SONAR_PAYLOAD_V1.md # Hardware Ratings, Pinouts & Electrical Envelopes
    ├── component_list_BOM.md          # Bill of Materials (BOM) with MPNs & Pricing
    ├── DESIGN_METHODOLOGY.md          # System Modeling & Simulation Methodology
    ├── LTSPICE_SIMULATION_ANALYSIS.md # Detailed Guide to LTspice AC/Transient Verification
    ├── SIMULATION_ARCHITECTURE_GUIDE.md # Architectural Guide & Subsea Enclosure Visuals
    ├── assumptions.md                 # Scientific & Channel Assumptions
    └── assets/                        # Schematics, Co-Simulation & Hardware CAD Models
```

---

## 🛠️ Hardware Stack & Development Tools
**Authoritative Hardware Contract**: Adheres 100% to [MASTER_PIN_MAP.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/MASTER_PIN_MAP.md).

* **Target Microcontroller**: 32-bit ARM Cortex-M4/G4 (STM32 Nucleo-64 @ 170 MHz) running bare-metal C with hardware `TIM6_TRGO` and circular DMA streaming directly to 12-bit DAC1 (`PA4`).
* **Operating Frequency Architecture**:
  * **Ultrasonic Mission Band (Target)**: $100\text{ kHz} \leftrightarrow 450\text{ kHz}$ acoustic carrier via 2.5 MSPS DAC DMA into $600\text{ kHz}$ active reconstruction filter ($R=2.65\text{ k}\Omega, C=100\text{ pF}$) with high-speed AD8065 op-amp.
  * **Laboratory Demonstrator Mode (Benchtop Rig)**: $500\text{ Hz} \leftrightarrow 25\text{ kHz}$ audio-scaled mode operating on the identical mathematical DDS engine, enabling live human acoustic perception on benchtop speaker (`PB6`) and safe oscilloscope measurement.
* **Analog Reconstruction Filter**: 4th-Order Active Butterworth Low-Pass Filter with exact damping factors ($Q_1=0.541, Q_2=1.307$, $+7.8\text{ dB}$ passband gain) rejecting DAC sampling images by $>48\text{ dB}$.
* **Power Amplifier Stage**: Half-bridge switching driver (IR2104 / UCC27712) with fast bootstrap network and dual logic-level N-FETs (IRLZ44N/FQP30N06L) delivering pulse bursts to test load / piezo projector.
* **Electrical Metrology & Health Sensing**:
  * Shunt Resistor: $R_{\text{shunt}} = 0.10\,\Omega$ $1\%$ metal-foil on low-side ground return.
  * Current Sense Amplifier: Texas Instruments INA180A2 (Gain = 20 V/V) mapping $0\text{–}1.65\text{A}$ to $0\text{–}3.3\text{V}$ on **Pin PA5** (`ADC1_IN5`).
  * Rail Voltage Monitor: $100\text{k}\Omega / 10\text{k}\Omega$ matched divider monitoring battery sag on **Pin PA6** (`ADC1_IN6`).
  * Thermal Monitoring: Linear TMP36 sensor ($10\text{ mV}/^\circ\text{C}$) mounted directly to PA heatsink on **Pin PA7** (`ADC1_IN7`).
  * Sensor Protection: $10\text{k}\Omega / 20\text{k}\Omega$ divider scaling Turbidity ($0\text{–}5\text{V} \rightarrow 0\text{–}3.3\text{V}$) on **Pin PA0**.
* **Role of ADALM-Pluto (If Present)**: Treated strictly as an **optional reference/bench instrument** for spectral verification and RF/DSP cross-checking; it is **not** part of the final low-power embedded AUV transmitter payload.

---

## 🎯 Primary Success Criteria (MVP Verification)

1. Multiple software-defined waveforms (CW, LFM, HFM, Barker) generated via DMA streaming without CPU stalling.
2. Environmental inputs dynamically alter candidate transmission parameters ($W_0$).
3. Electrical voltage and current measured reliably on the power path.
4. Pulse energy ($E_{\text{pulse}}$) calculated deterministically on-chip.
5. The controller autonomously enforces a configured energy budget ($E_{\text{remaining}}$).
6. The controller detects rising PA temperature and throttles duty cycle / energy.
7. The system completes an automated startup self-characterization sequence.
8. The system selects an energy-efficient configuration using measured electrical data.
9. All sensing, adaptation, and power-monitoring logic executes in real time on the MCU.
10. Fixed, environment-only, and self-monitoring adaptive modes are experimentally compared on bench telemetry.

---

## 👥 Engineering Roles & Mentorship
* **Lead Embedded Systems, DSP & Acoustic Physics (Person 1)**: Srimannarayana Deevi (Team Lead)
* **Firmware Architecture & Hardware DMA Streaming (Person 2)**: Embedded Firmware Lead
* **Analog Front-End & Mixed-Signal Hardware (Person 3)**: Analog Hardware Lead
* **Faculty Review Mentor**: Mrs. Jalaja Ma'am
