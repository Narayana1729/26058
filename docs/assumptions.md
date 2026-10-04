# Modelling Assumptions, Claim Discipline & Engineering Baseline

This document formally records every model, environmental, and hardware assumption in the simulation, firmware, and evaluation framework. Any change to an assumption here triggers a re-run of the affected test bench.

---

## 1. Authoritative Project Identity & Scope

* **Identity**: A real-time, environment-aware, energy-constrained, self-monitoring software-defined sonar transmitter for AUVs (SIH 2026 Problem Statement 26058).
* **Current Prototype Scope**: **Transmitter-Only MVP**.
* **Future Extension (V2/V3)**: Hydrophone / acoustic receiver feedback for closed-loop acoustic echo evaluation. It is NOT a dependency of the current MVP.
* **Core Loop**:
  $$\text{Sense} \longrightarrow \text{Predict} \longrightarrow \text{Configure} \longrightarrow \text{Transmit} \longrightarrow \text{Measure} \longrightarrow \text{Evaluate} \longrightarrow \text{Adapt}$$
* **Feedback Mechanism**: Defined strictly as **Closed-Loop Transmitter Self-Optimization** (measuring transmitter electrical efficiency, load/power response, and thermal health), NOT measured acoustic feedback.

---

## 2. Taxonomy of Quantities: Measured vs. Predicted

To maintain rigorous scientific and engineering claim discipline, quantities are strictly categorized:

| Category | Specific Parameters | Notes & Verification Domain |
|---|---|---|
| **Measured Electrical Quantities** | Supply Voltage $V_{\text{supply}}(t)$, Transmit Current $I_{\text{tx}}(t)$, Pulse Energy $E_{\text{pulse}} = \int_0^{T_p} V(t)I(t) dt$, Average Power $P_{\text{avg}}$, PA Temperature $T_{\text{PA}}$, Duty Cycle, Pulse Duration | Sampled directly via calibrated STM32 ADC channels, shunt amplifier, and thermal sensor. Real, physical data. |
| **Model-Predicted Quantities** | Acoustic Attenuation $\alpha(f)$, Transmission Loss $TL(R, f)$, Spatial Resolution $\Delta R_{\text{model}} = \frac{c}{2B}$, Predicted Quality Metric $Q_{\text{model}}(W)$ | Derived mathematically from empirical ocean acoustic models (e.g., Francois-Garrison 1982). Serves as an environmental **Prior**, not empirical acoustic proof. |
| **Operational Control States** | Waveform Vector $W = \{f_c, B, T_p, A, \text{Type}\}$, Power Budget $E_{\text{budget}}$, Energy Remaining $E_{\text{remaining}} = E_{\text{budget}} - \sum E_{\text{pulse}}$ | Dynamic control states updated in real time by the on-board STM32 firmware governor. |

---

## 3. Propagation & Environmental Model Assumptions (Stage 1 Prior)

| Parameter | Model / Formulation | Operating Assumptions & Limitations |
|---|---|---|
| **Acoustic Absorption** | Francois-Garrison (1982) | Predicts chemical relaxation of Boric Acid $\text{B(OH)}_3$ and Magnesium Sulfate $\text{MgSO}_4$ + pure water viscosity. Validated over $10\text{–}500\text{ kHz}$. Used as an analytical prior for $W_0$. |
| **Sound Speed $c$** | Mackenzie (1981) | Function of Temperature ($T$), Salinity ($S$), and Depth ($D$). Used for time-of-flight scaling in models. |
| **Spreading Loss Model** | $40 \log_{10}(R)$ | Two-way spherical spreading reference model for simulation testbenches. Point target, monostatic. |
| **Environmental Reference** | $T = 20^\circ\text{C}, S = 35\text{ ppt}, \text{pH} = 8.0, D = 10\text{ m}$ | Reference defaults for simulation. Physical sensors override these at runtime. |
| **Model Boundary** | Homogeneous medium assumption | Does not simulate micro-turbulence, internal ocean waves, or biological clutter layers. |

---

## 4. Hardware & Circuit Assumptions (Stage 2 Electrical Optimization)

| Subsystem | Baseline Model / Value | Engineering Notes |
|---|---|---|
| **Pin Mapping Contract** | [MASTER_PIN_MAP.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/MASTER_PIN_MAP.md) | Authoritative hardware contract: PA4 is dedicated 12-bit DAC1; PA5 is INA180 current sense; PA6 is rail divider; PA7 is TMP36 thermal; PC0 is Salinity. |
| **Frequency Architecture** | Dual-Band Scaling Strategy | **Mission Target**: 100–450 kHz Ultrasonic AUV Sonar ($F_s = 2.5\text{ MSPS}$, $f_c \approx 600\text{ kHz}$ LPF). **Benchtop Demo**: 500 Hz – 25 kHz Audio-Scaled Mode for safe laboratory human audibility and direct oscilloscope inspection. |
| **Current Sense Topology** | Low-side Precision Shunt ($0.10\,\Omega, 1\%$) | INA180 amplifier (Gain = 20 V/V) maps $0\text{–}1.65\text{A}$ to $0\text{–}3.3\text{V}$ on Pin PA5; discrete energy integration $\sum V[n]I[n]\Delta t \approx \int V(t)I(t)dt$. |
| **Voltage Sense Topology** | $100\text{ k}\Omega / 10\text{ k}\Omega$ Precision Divider | Monitors $0\text{–}33\text{V}$ battery rail on Pin PA6 to record dynamic supply sag during transmit bursts. |
| **PA Thermal Topology** | TMP36 Analog Sensor on Heatsink | Bonded to PA transistor tab ($10\text{ mV}/^\circ\text{C}$) on Pin PA7; feeds multi-tier thermal throttling state machine ($50^\circ, 70^\circ, 85^\circ\text{C}$). |
| **Power Stage Topology** | Half-Bridge Class-D Switcher | High/Low-Side Bootstrap Driver (IR2104) driving logic-level N-FETs (IRLZ44N/FQP30N06L) with fast Schottky clamping. |
| **Microcontroller Platform** | STM32 ARM Cortex-M (Cortex-M4 / G4) | Master Timer (`TIM6_TRGO`), circular DMA streaming to 12-bit DAC (`PA4`), zero-CPU transmit overhead. |
| **Analog Filter** | 4th-Order Non-Unity Sallen-Key LPF | Butterworth alignment with exact stage Q-factors ($Q_1=0.541, Q_2=1.307$, $+7.8\text{ dB}$ gain) suppressing DAC images by $>48\text{ dB}$. |

---

## 5. Explicit Claim Discipline & Communication Rules

Every document, presentation slide, and code docstring must strictly adhere to the following negative and positive constraints:

### ❌ Strict Prohibitions (Do NOT Claim)
1. **DO NOT claim measured acoustic SNR or echo quality** — the current MVP does not have a hydrophone/receiver.
2. **DO NOT claim that a 3.2 kHz benchtop tone is a 250 kHz ultrasonic carrier** — explicitly identify it as the *audio-scaled demonstration mode* of the mathematical DDS engine.
3. **DO NOT claim guaranteed target detection improvement or guaranteed AUV mission-life extension** — claim instead that it *enforces the configured transmission energy budget and can extend predicted operating time*.
4. **DO NOT claim a "globally optimal" waveform** — the controller selects among *experimentally characterized candidate configurations*.
5. **DO NOT claim direct complex transducer impedance measurement** — use the accurate term: *electrical load and power response*.
6. **DO NOT claim underwater acoustic performance from an air/benchtop speaker experiment** — air tests are *benchtop electrical and signal-processing validations*.
7. **DO NOT claim ultrasonic acoustic performance when evaluating an audible transducer**.

### ✅ Approved Terminology (DO Use)
* *Model-predicted acoustic behavior* (for theoretical range/resolution/absorption).
* *Measured electrical energy* ($E_{\text{pulse}}$) and *measured average power* ($P_{\text{avg}}$).
* *Measured transmitter efficiency* and *electrical load response*.
* *Energy-constrained waveform selection*.
* *Closed-loop transmitter self-optimization*.
* *Real-time power budget governor* and *thermal throttling*.
* *Benchtop electrical validation* and *future underwater acoustic validation*.

---

## 6. Primary Success Criteria (MVP Sign-Off Matrix)

The MVP is objectively successful if it experimentally demonstrates with real hardware:

1. **Software-Defined Agility**: Multiple software-defined waveforms (CW, LFM chirp, HFM chirp, coded pulses) generated digitally via DDS/LUT and DMA.
2. **Environmental Sensitivity**: Environmental inputs dynamically modify the selected candidate transmission parameters ($W_0$).
3. **Reliable Electrical Metrology**: Real-time measurement of supply voltage and transmit current via calibrated ADC/DMA sampling.
4. **Experimental Energy Calculation**: Deterministic calculation of per-pulse electrical energy $E_{\text{pulse}} = \int V(t)I(t)dt$ and average power $P_{\text{avg}}$.
5. **Active Power Budget Governance**: Autonomous enforcement of a user-defined energy budget ($E_{\text{remaining}} = E_{\text{budget}} - \sum E_{\text{pulse}}$), transitioning from performance to conservative modes.
6. **Thermal Protection**: Autonomous throttling of duty cycle / pulse energy when the Power Amplifier temperature approaches defined thresholds.
7. **Automated Self-Characterization**: Execution of an automated startup sequence across candidate configurations to generate an electrical efficiency profile.
8. **Energy-Efficient Selection**: Autonomous selection of an energy-efficient configuration based on measured electrical behavior.
9. **Real-Time On-Chip Execution**: All sensing, modeling, power governance, and adaptation algorithms execute deterministically on the STM32 microcontroller.
10. **Rigorous Three-Way Benchmark**: Experimental comparison between **Fixed Baseline**, **Environment-Only**, and **Self-Monitoring Adaptive** strategies using measured electrical quantities.

---
*Authoritative Revision: SIH 2026 — Master Specification (Transmitter-Only Self-Monitoring MVP).*
