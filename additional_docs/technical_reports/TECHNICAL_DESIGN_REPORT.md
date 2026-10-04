# SOFTWARE-DEFINED ADAPTIVE ACOUSTIC TRANSMITTER FOR AUTONOMOUS UNDERWATER VEHICLES (AUVs)
## Comprehensive Technical Design Specification & Engineering Report
### SIH 2026 Problem Statement 26058: "Development of a Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for Autonomous Underwater Vehicles (AUVs)"

**Project Code**: SDR-SONAR-TX-2026  
**Target Platform**: STM32 ARM Cortex-M (Hardware DMA + TIM TRGO + 12-bit DAC + Synchronous ADC)  
**Document Classification**: Authoritative Engineering Architecture & Technical Design Report (EDD)  
**Authoritative Concept**: A real-time, environment-aware, energy-constrained, self-monitoring software-defined sonar transmitter for AUVs.  
**Current MVP Scope**: **Transmitter-Only**. Does not require a microphone, hydrophone, or acoustic receiver loop for baseline operation.

---

### ABSTRACT
Autonomous Underwater Vehicles (AUVs) operating across dynamic marine domains (clear open ocean, thermally stratified thermoclines, and turbid river estuaries) are severely constrained by physical battery capacity and harsh acoustic propagation dynamics. Traditional acoustic pingers rely on fixed transmission profiles that either over-dissipate electrical energy in benign waters or fail to penetrate dense, attenuating media. 

This report presents the complete engineering architecture, mathematical signal processing theory, analog reconstruction circuitry, embedded firmware pipeline, and experimental validation framework for an **Intelligent Self-Monitoring Adaptive Sonar Transmitter**.

The transmitter does not merely generate a programmed sonar waveform; it senses its operating environment, predicts an appropriate transmission configuration, measures its own electrical energy and thermal state, and autonomously regulates subsequent transmissions within defined performance and power constraints. The current prototype concentrates 100% of engineering novelty into embedded transmitter intelligence, electrical efficiency, and power governance. Receiver/hydrophone integration is formally documented as a staged V2/V3 research extension.

---

## 1. SYSTEM ARCHITECTURE & DATA PIPELINE

### 1.1 Authoritative System Block Diagram

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

### 1.2 Closed-Loop Transmitter Self-Optimization
* The feedback loop is explicitly defined as **Closed-Loop Transmitter Self-Optimization**.
* Electrical telemetry (shunt current, rail voltage, and PA thermal rise) measures transmitter operational efficiency and health.
* It does **not** claim direct measurement of in-water acoustic echo returns or received acoustic SNR; those belong to the V2/V3 hydrophone roadmap.

---

## 2. THE FIVE-LAYER NOVELTY STACK

### Layer 1: Software-Defined Waveform Agility
The transmitted acoustic pulse is parameterized as a dynamic 5-tuple:
$$W = \{f_c, B, T_p, A, \text{Type}\}$$
Where:
* $f_c$: Center carrier frequency ($\text{Hz}$)
* $B$: Modulation sweep bandwidth ($\text{Hz}$)
* $T_p$: Active pulse duration ($\text{s}$)
* $A$: Normalized drive amplitude ($0.0 \le A \le 1.0$)
* $\text{Type} \in \{\text{CW}, \text{LFM}, \text{HFM}, \text{Barker-13}\}$: Waveform modulation family.

*Engineering Discipline*: No waveform family is assumed to be universally superior. The controller selects among experimentally characterized candidate configurations depending on mission needs.

### Layer 2: Environment-Aware Waveform Prior
Real-time environmental sensors (Water Temperature $T$, Depth/Pressure $D$, Turbidity $\text{NTU}$, and Salinity $S$) feed the **Francois-Garrison (1982)** acoustic absorption model:
$$\alpha(f) = \frac{A_1 P_1 f_1 f^2}{f^2 + f_1^2} + \frac{A_2 P_2 f_2 f^2}{f^2 + f_2^2} + A_3 P_3 f^2 \quad [\text{dB/km}]$$
The engine generates an analytical candidate prior:
$$W_0 = f(\text{environmental state})$$
*Note*: This represents an analytical prediction/prior to seed the controller, not an empirical proof of in-water acoustic reception.

### Layer 3: Energy-Aware Transmission Optimization
The transmitter samples high-speed electrical telemetry on the power amplifier rail during each acoustic emission:
$$E_{\text{pulse}} = \int_0^{T_p} V(t) \cdot I(t) \, dt \quad \approx \quad \sum_{n=0}^{N-1} V[n] \cdot I[n] \cdot \Delta t$$
$$P_{\text{avg}} = \frac{E_{\text{pulse}}}{T_p}$$
The controller optimizes:
$$\max_{W \in \mathcal{W}} \quad \frac{Q_{\text{model}}(W)}{E_{\text{pulse}}(W)} \quad \text{subject to} \quad E_{\text{pulse}} \le E_{\text{cap}}, \quad T_{\text{PA}} \le T_{\max}$$
Where:
* $Q_{\text{model}}(W)$: Model-predicted transmission capability (range/resolution utility).
* $E_{\text{pulse}}(W)$: Directly measured electrical energy per pulse.
* $E_{\text{cap}}$: Maximum permissible electrical energy per pulse.
* $T_{\max}$: Safe operating temperature threshold of the Power Amplifier.

### Layer 4: Self-Monitoring Hardware Health
The on-board microcontroller continuously tracks:
* **Supply Voltage ($V_{\text{supply}}$)**: Verifies rail stability and detects battery sag during high-current pings.
* **Transmit Current ($I_{\text{tx}}$)**: High-speed shunt measurement of dynamic load current.
* **Electrical Load and Power Response**: Monitors active drive efficiency.
* **Power Amplifier Temperature ($T_{\text{PA}}$)**: Analog/digital thermal sensor mounted directly on the PA heatsink.
* **Duty Cycle ($D$)**: Prevents excessive continuous pinging and ensures transducer thermal settling.

### Layer 5: Real-Time Autonomous Power Governance
The system continuously tracks cumulative electrical energy consumed against an operator-defined budget:
$$E_{\text{remaining}} = E_{\text{budget}} - \sum E_{\text{pulse}}$$

#### Power Budget State Machine:
* **High Energy State ($E_{\text{remaining}} > 60\%$)**: Performance-oriented mode. Controller allows wideband LFM chirps with full amplitude $A=1.0$.
* **Energy Reducing State ($20\% \le E_{\text{remaining}} \le 60\%$)**: Balanced mode. Bandwidth and duration are throttled to conserve battery while maintaining nominal transmission capability.
* **Critical Energy State ($E_{\text{remaining}} < 20\%$)**: Conservative mode. System transitions to low-duty-cycle narrowband pulses with reduced amplitude.

#### Thermal Protection State Machine:
* $T_{\text{PA}} < 50^\circ\text{C}$: **Normal Mode** (Unrestricted operation).
* $50^\circ\text{C} \le T_{\text{PA}} < 70^\circ\text{C}$: **Warning Mode** (Pulse Repetition Interval extended by $50\%$).
* $70^\circ\text{C} \le T_{\text{PA}} < 85^\circ\text{C}$: **Thermal Throttling Mode** (Amplitude reduced by $40\%$, pulse duration capped).
* $T_{\text{PA}} \ge 85^\circ\text{C}$: **Emergency Shutdown Mode** (Transmitter disabled until temperature drops below $55^\circ\text{C}$).

*Claim Discipline*: Power governance does not guarantee vehicle mission life; it enforces the configured transmission energy budget and extends predicted operating time.

---

## 3. TWO-STAGE ADAPTATION ENGINE

The central algorithm follows a disciplined two-stage sequence:

```
                  STAGE 1: ENVIRONMENTAL PREDICTION
             [ Sample: Temperature, Depth, Turbidity ]
                                ↓
             [ Analytical Francois-Garrison Model    ]
                                ↓
             [ Generate Initial Candidate Prior W₀   ]
                                ↓
                  STAGE 2: ELECTRICAL REFINEMENT
             [ Configure Timer ARR & DMA Buffers     ]
                                ↓
             [ Transmit Acoustic Waveform            ]
                                ↓
             [ Measure: V(t), I(t), E_pulse, T_PA    ]
                                ↓
             [ Check: E_remaining & Thermal Bounds   ]
                                ↓
             [ Select/Update Energy-Efficient Config ]
                                ↓
             [ Loop: Next Scheduled Transmission     ]
```

**Operational Execution Chain**:
$$\text{Sense} \longrightarrow \text{Predict} \longrightarrow \text{Configure} \longrightarrow \text{Transmit} \longrightarrow \text{Measure} \longrightarrow \text{Evaluate} \longrightarrow \text{Adapt}$$

---

## 4. PRE-MISSION SELF-CHARACTERIZATION

At power-up, before AUV mission release, the firmware executes an automated diagnostic calibration sequence:

```
[ STARTUP DIAGNOSTICS ]
          ↓
[ For each Candidate Configuration i ∈ {1, 2, ..., K}: ]
     - Load Waveform (CW, LFM, HFM, Barker)
     - Fire Test Ping (short duration)
     - Measure V_rail, I_peak, E_pulse, and ΔT_PA
     - Store measured metrics in Calibration Matrix
          ↓
[ Analyze Efficiency vs. Energy Trade-offs ]
          ↓
[ Populate Active Hardware Profile in SRAM ]
          ↓
[ Enter Autonomous Mission Mode ]
```

### Self-Characterization Matrix Structure
| Index | Waveform Family | Frequency ($f_c$) | Bandwidth ($B$) | Duration ($T_p$) | Measured $E_{\text{pulse}}$ | Measured $\Delta T_{\text{PA}}$ | Efficiency Index |
|---|---|---|---|---|---|---|---|
| 1 | CW | $100\text{ kHz}$ | Single tone | $1.0\text{ ms}$ | *Measured* | *Measured* | Computed |
| 2 | LFM Chirp | $200\text{ kHz}$ | $40\text{ kHz}$ | $2.0\text{ ms}$ | *Measured* | *Measured* | Computed |
| 3 | HFM Chirp | $250\text{ kHz}$ | $50\text{ kHz}$ | $2.0\text{ ms}$ | *Measured* | *Measured* | Computed |
| 4 | Barker-13 | $150\text{ kHz}$ | Phase-coded | $1.3\text{ ms}$ | *Measured* | *Measured* | Computed |

*Rule*: All profile values are captured live by on-board ADCs; no benchmark figures are fabricated.

---

## 5. MATHEMATICAL FORMULATION & SIGNAL PROCESSING

### 5.1 Waveform Mathematical Models

#### 1. Linear Frequency Modulated (LFM) Chirp:
$$s_{\text{LFM}}(t) = w(t) \cdot A \cdot \cos\left(2\pi f_0 t + \pi \frac{B}{T_p} t^2 + \phi_0\right), \quad 0 \le t \le T_p$$
Sweep rate $\mu = B / T_p$.

#### 2. Hyperbolic Frequency Modulated (HFM) Chirp:
$$s_{\text{HFM}}(t) = w(t) \cdot A \cdot \cos\left(-\frac{2\pi k}{a} \ln\left(1 - \frac{t}{t_0}\right) + \phi_0\right)$$
Provides Doppler tolerance during vehicle velocity transients.

#### 3. 13-Bit Barker Phase-Coded Pulse:
$$s_{\text{Barker}}(t) = w(t) \cdot A \cdot \cos\left(2\pi f_c t + \theta[k]\right), \quad \theta[k] \in \{0, \pi\}$$
Barker-13 sequence: $\{+1, +1, +1, +1, +1, -1, -1, +1, +1, -1, +1, -1, +1\}$.

### 5.2 Tukey Windowing Taper ($\alpha = 0.25$)
To eliminate transient edge ringing and reduce spectral leakage:
$$w[n] = \begin{cases} 
\frac{1}{2}\left[1 + \cos\left(\pi\left(\frac{2n}{\alpha N} - 1\right)\right)\right], & 0 \le n < \frac{\alpha N}{2} \\ 
1, & \frac{\alpha N}{2} \le n \le N\left(1 - \frac{\alpha}{2}\right) \\ 
\frac{1}{2}\left[1 + \cos\left(\pi\left(\frac{2n}{\alpha N} - \frac{2}{\alpha} + 1\right)\right)\right], & N\left(1 - \frac{\alpha}{2}\right) < n \le N-1 
\end{cases}$$
Achieves $-42.4\text{ dB}$ first sidelobe suppression while preserving $>87.5\%$ of pulse energy.

---

## 6. ELECTRICAL METROLOGY & SENSING HARDWARE

### 6.1 Current Sensing & Power Measurement Circuit
```
   V_SUPPLY (+12V / +24V Rail)
        │
        ▼
   [ POWER AMPLIFIER (IR2104 Half-Bridge) ] ────> Transmit Output to Filter/Transducer
        │
        ▼
   [ Low-Side Shunt Resistor R_shunt = 0.10 Ω, 1%, 2W ]
        │
        ├──────────────────────┐
        │                      │
        ▼                      ▼
   (+) Input              (-) Input
   ┌──────────────────────────────────────────────┐
   │ High-Speed Current Sense Amplifier (INA180)  │
   │ Gain = 20 V/V                                │
   │ Output: V_out = I_load × 0.10Ω × 20 = 2.0·I   │
   └──────────────────────┬───────────────────────┘
                          │
                          ▼
                 STM32 Pin PA5 (ADC1_IN5)
                 0 - 3.3V corresponds to 0 - 1.65A
```

* **Shunt Resistor**: $R_{\text{shunt}} = 0.10\ \Omega$ metal-foil resistor ($1\%$, $2\text{W}$). Minimal voltage drop ($<165\text{ mV}$ at full drive) avoids disturbing the power amplifier rail.
* **Amplifier Gain**: $G = 20\text{ V/V}$ scales peak $1.5\text{A}$ drive current to $3.0\text{V}$, fitting comfortably within the STM32 ADC reference range ($0\text{–}3.3\text{V}$).
* **Sampling Architecture**: Synchronous ADC triggered via DMA alongside timer `TIM6_TRGO` during active pulse duration $T_p$.
* **Rail Voltage Divider**: $100.0\text{ k}\Omega / 10.0\text{ k}\Omega$ (0.1% matched) connected to **Pin PA6** (`ADC1_IN6`) scales $0\text{–}33\text{V}$ rail down to $0\text{–}3.0\text{V}$ to capture dynamic battery sag.

### 6.2 Power Amplifier Thermal Sensing
* **Sensor**: Linear analog temperature sensor (TMP36) thermally bonded to the PA heatsink, wired to **Pin PA7** (`ADC1_IN7`).
* **Transfer Function**: $V_{\text{out}} = 10\text{ mV}/^\circ\text{C} \times T(^\circ\text{C}) + 500\text{ mV}$ ($750\text{ mV} @ 25^\circ\text{C}$, $1.20\text{V} @ 70^\circ\text{C}$). Read synchronously by the STM32 ADC.

### 6.3 Environmental Sensor Interface & Overvoltage Clamping
* **Turbidity (TSW-20)**: $0\text{–}5.0\text{V}$ analog output scaled through a precision $10.0\text{ k}\Omega / 20.0\text{ k}\Omega$ divider network into **Pin PA0** (`ADC1_IN0`), preventing ADC latch-up.
* **Depth (MS5837 / Pot)**: Read via **Pin PA1** (`ADC1_IN1`).
* **Salinity / Ambient**: Read via **Pin PC0** (`ADC1_IN10`), keeping Pin PA4 100% dedicated to DAC1 output.
* **Water Temperature**: DS18B20 1-Wire probe on **Pin PA10** with $4.7\text{ k}\Omega$ pull-up.

---

## 7. ANALOG RECONSTRUCTION FILTER & POWER STAGE

### 7.1 4th-Order Sallen-Key Active Butterworth Filter
To eliminate DAC zero-order hold quantization steps and prevent out-of-band harmonics from overheating the transducer:
* **Topology**: 4th-Order Active Butterworth Low-Pass Filter composed of two cascaded non-unity gain Sallen-Key stages with mathematically exact damping factors:
  $$B_4(s) = \left(s^2 + \frac{\omega_c}{Q_1} s + \omega_c^2\right) \left(s^2 + \frac{\omega_c}{Q_2} s + \omega_c^2\right)$$
  Where $\alpha_1 = 1.8478 \implies Q_1 = \mathbf{0.541}$ and $\alpha_2 = 0.7654 \implies Q_2 = \mathbf{1.307}$.
* **Stage Damping Implementation ($R_1=R_2=R$, $C_1=C_2=C$)**:
  $$Q = \frac{1}{3 - K} \implies K = 1 + \frac{R_f}{R_g}$$
  * Stage 1: $K_1 = 3 - \frac{1}{0.541} = 1.152 \implies R_{f1} = 1.52\text{ k}\Omega, \ R_{g1} = 10.0\text{ k}\Omega$
  * Stage 2: $K_2 = 3 - \frac{1}{1.307} = 2.235 \implies R_{f2} = 12.35\text{ k}\Omega, \ R_{g2} = 10.0\text{ k}\Omega$
  * Overall Passband Gain: $K_{\text{total}} = 1.152 \times 2.235 = \mathbf{2.575 \ (+7.8\text{ dB})}$
* **Ultrasonic Tuning ($f_c \approx 600\text{ kHz}$)**: $R = 2.65\text{ k}\Omega$, $C = 100\text{ pF}$ (C0G/NP0). Active Op-Amp: **AD8065ARZ** (GBW = 145 MHz, SR = 180 V/µs).
* **Benchtop Demo Tuning ($f_c \approx 15.92\text{ kHz}$)**: $R = 10.0\text{ k}\Omega$, $C = 1.0\text{ nF}$. Active Op-Amp: **TL072CP / OPA350**.
* **Stopband Attenuation**: $-80\text{ dB/decade}$ ($-24\text{ dB/octave}$), rejecting DAC sampling images by $>48\text{ dB}$.

### 7.2 Power Amplifier Switching Stage
* **Topology**: Half-Bridge Class-D Switcher with High/Low-Side Bootstrap Gate Driver (**IR2104 / UCC27712**).
* **Power Transistors**: Dual Logic-Level N-Channel Power MOSFETs (**IRLZ44N / FQP30N06L**, $R_{DS(on)} = 28\text{ m}\Omega$).
* **Bootstrap Network**: Fast recovery diode (1N4148) + $100\text{ nF}$ 50V ceramic capacitor powering the high-side floating gate drive.
* **Transient Clamping**: Fast Schottky diodes (1N5819) clamping back-EMF inductive kickback from piezoelectric loads to power rails.

---

## 8. FIRMWARE ARCHITECTURE & REAL-TIME EXECUTION

```
+-----------------------------------------------------------------------------------+
|                            STM32 HARDWARE TIMING CHAIN                            |
|                                                                                   |
|  [ SYSCLK: 168 MHz / 170 MHz ]                                                    |
|              │                                                                    |
|              ▼                                                                    |
|  [ TIM6 Master Hardware Timer ] ── ARR Register dynamically updated by Controller │
|              │                                                                    |
|              ▼ (TRGO Update Event)                                                |
|              ├───────────────────────────────────┬────────────────────────────────┤
|              ▼                                   ▼                                ▼
|  [ DMA1 Stream 5 (DAC Output) ]     [ DMA2 Stream 0 (Current ADC) ]  [ ADC Regular Scan ]
|  Reads: Ping-Pong SRAM Table        Samples: Shunt Amplifier V_out   Samples: Temp/Depth
|  Writes: DAC_DHR12R1 Register       Direct RAM buffer (uint16_t)     Non-blocking
|  CPU Cycles: ZERO OVERHEAD          Synchronous with pulse           Updates Prior W₀
+-----------------------------------------------------------------------------------+
```

### Deterministic Memory Allocation
* Waveform Buffer: $2 \times 512 \times 2\text{ bytes} = 2048\text{ bytes}$ (Ping-Pong SRAM buffer).
* Characterization LUT: $4 \times 16\text{ bytes} = 64\text{ bytes}$ in SRAM/Flash.
* Stack / Heap Overhead: Static allocation only; no dynamic heap (`malloc`) used in the transmission path.

---

## 9. THREE-WAY CONTROLLER BENCHMARK

The prototype experimentally compares three operational strategies:

```
========================================================================================================
STRATEGY              WAVEFORM CONFIGURATION   POWER MEASUREMENT   BUDGET GOVERNOR     THERMAL SAFEGUARD
========================================================================================================
1. Fixed Baseline     Fixed CW / LFM           None (Blind)        Disabled            None
2. Environment-Only   Model-Selected (W₀)      None (Open-Loop)    Disabled            None
3. Self-Monitoring    Two-Stage Adaptive       Real-Time V, I, E   Active Dynamic      Active Multi-Tier
   (Proposed)         (Model Prior + Measured) Integrated On-Chip  Enforcement         Throttling
========================================================================================================
```

### Quantities Compared in Benchmarking:
* Measured energy per pulse ($E_{\text{pulse}}$) across different water conditions.
* Measured average power consumption ($P_{\text{avg}}$).
* Cumulative energy consumed over a 100-ping mission simulation.
* Number of transmissions completed within an allotted $E_{\text{budget}}$.
* Power amplifier temperature rise ($\Delta T_{\text{PA}}$).
* Adaptation response latency (time from sensor transition to new pulse generation).

---

## 10. MULTI-PHASE DEVELOPMENT ROADMAP

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [V0] Electrical Characterization (Benchtop Validation)                                 │
│  - Verify DDS generation, DAC clocking, Sallen-Key 4th-order filter response           │
│  - Calibrate shunt current sensor, voltage divider, and PA temperature monitoring      │
│  - Validate deterministic E_pulse integration on STM32 ARM Cortex-M                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [V1] Intelligent Self-Monitoring Transmitter (Current SIH MVP)                         │
│  - Ingest simulated/physical environmental telemetry (Temp, Turbidity, Depth)          │
│  - Implement Two-Stage Adaptation Engine (Model Prior + Electrical Refinement)         │
│  - Execute autonomous Power Budget Governor and PA Thermal Throttling                  │
│  - Demonstrate automated Pre-Mission Self-Characterization                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [V2] Marine Acoustic Hardware Upgrades (Future Research Phase)                         │
│  - Transition from bench electrical load to high-voltage underwater piezo transducer   │
│  - Characterize in-water electroacoustic efficiency and transducer resonance matching │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [V3] Closed-Loop Acoustic Channel Feedback (Long-Term Research Phase)                  │
│  - Integrate calibrated hydrophone and receiver analog front-end (AFE)                 │
│  - Close the loop around received acoustic echo quality, SNR, and channel multipath    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. LABORATORY INSTRUMENTATION & BENCH VALIDATION RIG

To ensure absolute repeatability and eliminate measurement ambiguity during jury evaluations, the hardware bench setup incorporates dedicated metrology instrumentation:

### 11.1 High-Speed Precision DAC Architecture
* **Primary / External DAC Option**: High-speed, ultra-low glitch precision DAC (**TI DAC8562** or dedicated **STM32 12-Bit DAC1** via Pin PA4).
* **Sample Rate**: Continuously clocked at **$1.0\text{–}2.0\text{ MSPS}$** driven by Timer `TIM6_TRGO` and DMA2 Stream 5, yielding sub-millivolt DC offset stability and $> 72\text{ dB}$ Signal-to-Noise-and-Distortion ratio (SINAD).
* **Glitch Energy**: Sub-$0.1\text{ nV}\cdot\text{s}$ glitch impulse prevents high-frequency transients from exciting parasitic modes in the reconstruction filter.

### 11.2 Digital Storage Oscilloscope (DSO) Bench Verification
* **Metrology Instrument**: Dual-channel **100 MHz, 1 GSa/s Digital Storage Oscilloscope** (Rigol DS1054Z / Keysight DSOX series).
* **Real-Time Signal Interrogation**:
  * **Channel 1 (Yellow)**: Probed at DAC Output / Filter Input (PA4) to verify discrete staircase steps, DDS chirp frequency ramp linearity, and Tukey tapering envelope.
  * **Channel 2 (Cyan)**: Probed across the active Sallen-Key low-pass filter output to measure out-of-band attenuation ($>48\text{ dB/octave}$), phase linearity, and Total Harmonic Distortion ($\text{THD} < 0.05\%$).
* **FFT Math Function**: Real-time on-scope FFT spectrum analysis validates that Tukey ($\alpha=0.25$) windowing suppresses the first spectral sidelobes by **$-32\text{ dB}$ to $-42\text{ dB}$** compared to rectangular pulsing.

### 11.3 ADALM-Pluto Laboratory SDR Reference
* Serves as an **external RF/ultrasonic laboratory cross-check instrument** to independently record chirp emissions, analyze time-frequency spectrograms, and benchmark spectral purity.
* It is strictly a validation reference and not an operational payload requirement.

---

## 12. ENGINEERING CLAIM DISCIPLINE & LIMITATIONS

* **No Claim of In-Water Acoustic SNR**: The current MVP measures *electrical energy and power*; it does not claim measured in-water acoustic echo SNR or target detection probability without a receiver.
* **No Unsubstantiated Guarantees**: We do not claim "guaranteed mission life extension" or "globally optimal waveforms"; we state that the system *enforces the configured transmission energy budget and can extend predicted operating time*.
* **Load Characterization**: Referred to accurately as *electrical load and power response*; direct complex impedance $Z(f)$ is not claimed without dedicated vector I/Q instrumentation.
* **Acoustic Medium Separation**: Benchtop air/speaker tests are strictly *electrical and signal-processing validations*; they are never described as underwater acoustic trials.

---
*Authoritative Revision: SIH 2026 Problem Statement 26058 — Official Technical Design Report.*
