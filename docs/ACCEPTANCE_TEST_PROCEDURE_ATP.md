# 📋 FORMAL ACCEPTANCE TEST PROCEDURE (ATP) & QUALIFICATION PROTOCOL
## Intelligent Self-Monitoring Adaptive Sonar Transmitter Payload for AUVs
### SIH 2026 Problem Statement 26058: "Development of a Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for Autonomous Underwater Vehicles (AUVs)"

**Document ID**: ATP-SDR-SONAR-TX-2026-REV2  
**Standard Compliance**: IEEE Std 829-2008 (Test Documentation) & MIL-STD-810H (Environmental Verification)  
**System Under Test (SUT)**: Intelligent Self-Monitoring Sonar Transmitter Payload (Transmitter-Only MVP)  
**Hardware Contract**: Aligned 100% with [MASTER_PIN_MAP.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/MASTER_PIN_MAP.md)

---

## 1. PURPOSE & SCOPE

This document defines the formal Acceptance Test Procedure (ATP) and Verification & Validation (V&V) matrix for the **Intelligent Self-Monitoring Adaptive Sonar Transmitter Payload**. 

* **Current Prototype Scope**: **Transmitter-Only MVP**. Focuses entirely on software-defined waveform synthesis, environmental prediction prior ($W_0$), real-time electrical current/voltage sensing, discrete energy calculation ($E_{\text{pulse}}$), power budget governance ($E_{\text{remaining}}$), and thermal protection.
* **Acoustic Receiver Scope**: Hydrophone and in-water acoustic feedback are formally documented in `research/` as a staged V2/V3 research phase and are **not** an acceptance gate for the Phase 1 transmitter payload.
* **Verification Categorization**: To maintain uncompromising academic and scientific integrity, all acceptance criteria are explicitly partitioned into **Verified (Simulation & Testbench)** and **Qualification Procedure (Benchtop Hardware Target)**.

---

## 2. TEST EQUIPMENT & INSTRUMENTATION REQUIREMENTS

| Equipment Designation | Required Minimum Specification | Function in Acceptance Testing |
|:---|:---|:---|
| **High-Precision DAC Module** | 16-Bit / 12-Bit Dual-Channel, $\ge 2.0\text{ MSPS}$ (TI DAC8562 / STM32 On-Chip DAC1) | Synthesizes continuous analog baseband acoustic chirps with $<0.1\text{ nV}\cdot\text{s}$ glitch energy |
| **Digital Storage Oscilloscope (DSO / MSO)** | $\ge 100\text{ MHz}$ Bandwidth, $1\text{ GSa/s}$, 4 Channels, Math FFT & Area Integration ($V \times I$) | Verifies DAC staircase antialiasing, Tukey envelope taper, harmonic distortion ($\text{THD} < 0.05\%$), and pulse energy |
| **Current Probe / Sense Circuit** | Calibrated shunt amplifier ($0.10\,\Omega$, Gain = 20 V/V) or active DC–10 MHz current probe | Verifies instantaneous transmit current $I_{\text{tx}}(t)$ and pulse energy $E_{\text{pulse}}$ |
| **Precision Multimeter** | 6.5 Digit True-RMS DMM (Keysight / Fluke) | Measures supply rail DC voltage and static current draw |
| **Logic Analyzer** | 16-channel, $\ge 100\text{ MHz}$ sampling rate | Measures `TIM6_TRGO` and DMA transfer timing consistency |
| **Thermal Chamber / Heat Probe** | Controllable heating element and calibrated thermocouple | Validates Power Amplifier thermal throttling state machine ($50^\circ\text{C} \leftrightarrow 85^\circ\text{C}$) |
| **Virtual Co-Simulation Testbench** | Proteus VSM 8.16 + LTspice 24 + Python 3.11 Automated Harness | Validates algorithms and electrical filters before hardware sign-off |

---

## 3. VERIFICATION & VALIDATION (V&V) ACCEPTANCE MATRIX

| Test ID | Test Description | Target Nominal | Acceptable Margin | Verification Method & Reference | Status |
|:---|:---|:---|:---|:---|:---|
| **ATP-DSP-01** | Tukey Window Taper ($\alpha=0.25$) Sidelobe Attenuation | $-42.4\text{ dB}$ | $\le -40.0\text{ dB}$ | Numerical FFT in `simulation/waveform_generator.py` | ✅ **VERIFIED (Simulation)** |
| **ATP-DSP-02** | Multi-Waveform Generation (CW, LFM, HFM, Barker-13) | 4 Families | 4 Families | Waveform synthesis verified in `simulation/python/` | ✅ **VERIFIED (Simulation)** |
| **ATP-AFE-01** | Sallen-Key Low-Pass Filter Cutoff ($f_c$) | $15.92\text{ kHz}$ demo / $600\text{ kHz}$ ultrasonic | $\pm 5\%$ | AC Bode sweep in `hardware/docs/walkthrough.md` | ✅ **VERIFIED (LTspice)** |
| **ATP-AFE-02** | Filter Stopband Roll-Off Rate | $-80\text{ dB/dec}$ | $\le -75\text{ dB/dec}$ | Frequency sweep verified in `simulation/simulate_filter_bode.py` | ✅ **VERIFIED (Simulation)** |
| **ATP-AFE-03** | Total Harmonic Distortion ($\text{THD}$) | $<0.15\%$ | $\le 0.20\%$ | Transient Fourier analysis in LTspice | ✅ **VERIFIED (LTspice)** |
| **ATP-GOV-01** | Power Budget Governor Multi-Tier State Machine | 3 Active Tiers ($>60\%, 20\text{–}60\%, <20\%$) | Deterministic state switch | Automated C harness in `firmware/tests/test_two_stage_power_governor.c` | ✅ **VERIFIED (Host C Harness)** |
| **ATP-THM-01** | PA Thermal Throttling State Machine ($50^\circ, 70^\circ, 85^\circ\text{C}$) | Derate @ 70°C, Cutoff @ 85°C | $\pm 2.0^\circ\text{C}$ | Automated C harness in `firmware/tests/test_two_stage_power_governor.c` | ✅ **VERIFIED (Host C Harness)** |
| **ATP-FW-01** | DMA Transfer Jitter (Zero-CPU Streaming) | $0\text{ ns}$ (ideal) | $< 10\text{ ns}$ | Logic analyzer on `DAC1_OUT1` (Pin PA4) | 🔄 **BENCH QUALIFICATION READY** |
| **ATP-MET-01** | Transmit Current Shunt Measurement Accuracy | $0\text{–}1.65\text{A}$ range | $\pm 3.0\%$ | Calibrate INA180 on PA5 against MSO current probe | 🔄 **BENCH QUALIFICATION READY** |
| **ATP-MET-02** | Pulse Energy Integration ($E_{\text{pulse}} = \int V \cdot I dt$) | Bench Calibrated | $\pm 4.5\%$ | Compare STM32 on-chip sum with MSO math area integration | 🔄 **BENCH QUALIFICATION READY** |
| **ATP-CAL-01** | Pre-Mission Automated Startup Self-Characterization | 4 Waveform Profiles | 4 Profiles | Step through candidate pings, record V, I, E to SRAM | 🔄 **BENCH QUALIFICATION READY** |

---

## 4. DETAILED STEP-BY-STEP HARDWARE ACCEPTANCE PROCEDURES

### 🔬 Test Case ATP-MET-02: Real-Time Electrical Energy Integration ($E_{\text{pulse}}$)
1. **Objective**: Confirm that the STM32 ADC synchronous current-voltage integration accurately calculates active electrical energy dissipated during transmission:
   $$E_{\text{pulse}} = \int_0^{T_p} V(t) \cdot I(t) \, dt \quad \approx \quad \sum_{n=0}^{N-1} V_{\text{rail}}[n] \cdot I_{\text{tx}}[n] \cdot \Delta t$$
2. **Procedure**:
   - Connect Channel 1 of the MSO across the power amplifier supply rail ($V_{\text{supply}}$, Pin PA6 divider).
   - Connect Channel 2 of the MSO to the current-sense amplifier output (Pin PA5, $V_{\text{sense}} = 20 \times I_{\text{tx}} \times 0.1\Omega$).
   - Configure MSO Math channel to compute $M(t) = \text{Ch1}(t) \times \frac{\text{Ch2}(t)}{2.0}$, and enable area integration across active pulse duration $T_p$.
   - Read the firmware computed $E_{\text{pulse}}$ value via UART NMEA telemetry (`$SONAR` packet).
3. **Pass Criteria**: Firmware calculated energy matches oscilloscope integrated energy within $\pm 4.5\%$.

---

### 🔬 Test Case ATP-GOV-01: Power Budget Governor Mode Transition
1. **Objective**: Validate that the transmitter autonomously transitions between operating modes based on remaining energy:
   $$E_{\text{remaining}} = E_{\text{budget}} - \sum E_{\text{pulse}}$$
2. **Procedure**:
   - Initialize the system with a mission energy budget $E_{\text{budget}} = 1.0\text{ J}$ (scaled for 25-ping demo).
   - Fire consecutive pings under High-Res LFM chirp mode ($E_{\text{pulse}} \approx 0.04\text{ J}$).
   - Observe OLED telemetry and oscilloscope output as $E_{\text{remaining}}$ decrements.
3. **Pass Criteria**:
   - When $E_{\text{remaining}} > 60\%$: Full bandwidth, $100\%$ amplitude.
   - When $20\% \le E_{\text{remaining}} \le 60\%$: Pulse duration throttled by $25\%$.
   - When $E_{\text{remaining}} < 20\%$: System automatically transitions to conservative mode (amplitude scaled to $60\%$, pulse duration cut by $50\%$).

---

### 🔬 Test Case ATP-THM-01: Power Amplifier Thermal Safeguard
1. **Objective**: Prove that the transmitter protects the power amplifier from thermal runaway inside an unventilated pod.
2. **Procedure**:
   - Heat the power amplifier heatsink using a controlled heat source while transmitting periodic pings.
   - Monitor the internal TMP36 temperature telemetry on Pin PA7 and the transmitted output pulse amplitude.
3. **Pass Criteria**:
   - At $T_{\text{PA}} \ge 50^\circ\text{C}$: System enters Warning Mode; Pulse Repetition Interval increases by $50\%$.
   - At $T_{\text{PA}} \ge 70^\circ\text{C}$: System enters Thermal Throttling; pulse amplitude drops by $40\%$.
   - At $T_{\text{PA}} \ge 85^\circ\text{C}$: System initiates protective shutdown until temperature recovers below $55^\circ\text{C}$.

---

## 5. SIGN-OFF & QUALIFICATION RECORD

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1 ACCEPTANCE SIGN-OFF & CERTIFICATION                     │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ Role                     │ Name                        │ Review Verdict & Notes        │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ Lead DSP & Physics Eng   │ Srimannarayana Deevi        │ [ SIMULATION VERIFIED ]       │
│ Embedded Firmware Lead   │ Firmware Team               │ [ PROTOCOL READY FOR BENCH ]  │
│ Mixed-Signal Hardware    │ Hardware Team               │ [ AFE VERIFIED IN LTSPICE ]   │
│ Faculty Review Guide     │ Mrs. Jalaja Ma'am           │ [ REVIEWED & APPROVED ]       │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```
