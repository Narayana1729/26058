# 📄 INDUSTRIAL DATASHEET: SDR-SONAR-TX-V1.0
## Software-Defined Adaptive Acoustic Transmitter Payload for Autonomous Underwater Vehicles (AUVs)

**Document ID**: DS-SDR-SONAR-2026-REV2.0  
**Classification**: Marine Surveying & Autonomous Robotics Specification  
**Compliance Standards**: IEEE 12207 (Software Lifecycle), IPC-2221 (PCB Design), MIL-STD-810H (Environmental Verification)  
**Authoritative Hardware Contract**: Aligned 100% with [MASTER_PIN_MAP.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/MASTER_PIN_MAP.md)

---

## 1. GENERAL DESCRIPTION

The **SDR-SONAR-TX-V1.0** is an intelligent, mixed-signal software-defined acoustic transmitter payload subsystem designed for Autonomous Underwater Vehicles (AUVs), benthic survey crawlers, and oceanographic buoys.

The module features a hardware-triggered direct memory access (DMA) streaming pipeline driving an internal 12-bit digital-to-analog converter (DAC1, Pin PA4), coupled with a 4th-order active Sallen-Key reconstruction filter. 

Transmission configurations are governed by an embedded two-stage engine:
1. **Stage 1 (Environmental Prior)**: Ingests real-time water turbidity, hydrostatic depth, temperature, and salinity to evaluate the **Francois-Garrison (1982)** ocean absorption model and seed candidate waveform parameters ($W_0$).
2. **Stage 2 (Electrical Refinement & Power Governance)**: High-speed current and voltage metrology measures real electrical dissipation ($E_{\text{pulse}} = \int V \cdot I dt$), enforcing an operator-configured mission energy budget ($E_{\text{remaining}}$) and multi-tier thermal throttling.

---

## 2. OPERATING FREQUENCY ARCHITECTURE & DUAL-BAND NARRATIVE

The payload architecture explicitly distinguishes between the **Ultrasonic Mission Band** and the **Laboratory Demonstration Mode**:

| Operating Mode | Carrier Frequency Range | Modulation Sweep ($B$) | Output Interface | Primary Purpose |
|:---|:---|:---|:---|:---|
| **Ultrasonic Mission Band (Design Target)** | **100 kHz – 450 kHz** | Up to $400\text{ kHz}$ | Hardware 12-bit DAC (Pin PA4) $\rightarrow$ 600 kHz AFE $\rightarrow$ Half-Bridge $\rightarrow$ Piezo | Deep benthic penetration vs. high-resolution subsea mapping in ocean water column |
| **Laboratory Demonstration Mode (Benchtop Rig)** | **500 Hz – 25 kHz** | $1\text{ kHz} \leftrightarrow 20\text{ kHz}$ | Scaled DAC output / Audible Speaker (`TIM4_CH1`, Pin PB6) | Safe benchtop human acoustic perception, audible Doppler verification, and direct oscilloscope debugging |

---

## 3. KEY PERFORMANCE FEATURES & ELECTRICAL RATINGS

### 🌟 Key Performance Features
* **Zero-CPU Core Streaming**: Master Timer `TIM6_TRGO` triggering circular DMA transfers to 12-bit DAC1 (`PA4`) with $<5\text{ ns}$ timing jitter.
* **Multi-Waveform Agility**: Real-time Linear Frequency Modulation (LFM), Doppler-Invariant Hyperbolic Frequency Modulation (HFM), Continuous Wave (CW), and 13-bit Barker Phase-Coded Pulses.
* **Harmonic Purity**: 4th-Order Sallen-Key Low-Pass Active Filter delivering $-80\text{ dB/decade}$ out-of-band rejection and $\text{THD} < 0.15\%$.
* **Sidelobe Suppression**: Digital Tukey ($\alpha=0.25$) taper providing $\ge 42.4\text{ dB}$ range sidelobe suppression while preserving $>87.5\%$ of pulse energy.
* **On-Board Electrical Metrology**: Low-side $0.10\,\Omega$ precision shunt with INA180 amplifier (Gain = 20 V/V) and $100\text{k}/10\text{k}$ rail divider directly sensing $I_{\text{tx}}$ and $V_{\text{supply}}$.
* **Autonomous Power Governor**: Dynamic mode transitions (Performance, Balanced, Conservative) based on cumulative battery budget expenditure.

---

### ⚡ Absolute Maximum Ratings
*Stresses beyond those listed under "Absolute Maximum Ratings" may cause permanent damage to the device.*

| Parameter | Symbol | Min | Max | Unit |
|:---|:---|:---|:---|:---|
| Digital Logic Supply Voltage | $V_{DD}$ | $-0.3$ | $+3.6$ | $\text{V}$ |
| High-Voltage Power Amplifier Rail | $V_{\text{PA}}$ | $0.0$ | $+30.0$ | $\text{V}$ |
| Analog Input Pin Voltage (PA0–PA7, PC0) | $V_{IN}$ | $-0.3$ | $V_{DD} + 0.3$ | $\text{V}$ |
| Transmit Current (Continuous Pulse) | $I_{\text{tx}}$ | — | $2.5$ | $\text{A}$ |
| Operating Heatsink Temperature | $T_{\text{PA}}$ | $-20$ | $+85$ | $^\circ\text{C}$ |
| Hydrostatic Pressure (Target Pod) | $P_{MAX}$ | $0$ | $30$ | $\text{bar}$ ($300\text{ m}$) |

---

## 4. PIN CONFIGURATION & INTERFACE SPECIFICATIONS

```
                    ┌─────────────────────────┐
             3.3V ──┤ 1  [VDD]       [GND] 20 ├── GND
       (Turbidity) ──┤ 2  [PA0_ADC]   [PC13] 19 ├── USER_BUTTON_B1
           (Depth) ──┤ 3  [PA1_ADC]   [PA10] 18 ├── DS18B20_ONEWIRE (Temp)
     (DAC Chirp) ──┤ 4  [PA4_DAC]   [PC0]  17 ├── SALINITY_POT_ADC
   (Current Sense) ──┤ 5  [PA5_ADC]   [PB9]  16 ├── I2C1_SDA (OLED HUD)
     (Rail Sense) ──┤ 6  [PA6_ADC]   [PB8]  15 ├── I2C1_SCL (OLED HUD)
   (PA Temp TMP36) ──┤ 7  [PA7_ADC]   [PB6]  14 ├── TIM4_SPEAKER_PWM
    (Telemetry TX) ──┤ 8  [PA2_TX]    [PA3]  13 ├── USART2_RX (Telemetry RX)
                    └─────────────────────────┘
```

### Complete Pin Function Table

| Pin | Designator | Type | Connected Peripheral & Circuit Function |
|:---|:---|:---|:---|
| **PA0** | `ADC1_IN0` | Analog In | Nephelometric Turbidity Sensor via $10\text{k}/20\text{k}$ divider ($0\text{–}5\text{V} \rightarrow 0\text{–}3.3\text{V}$). |
| **PA1** | `ADC1_IN1` | Analog In | Hydrostatic Depth Sensor / Precision Multi-Turn Simulator Potentiometer ($0\text{–}3.3\text{V}$). |
| **PC0** | `ADC1_IN10`| Analog In | Salinity / Water Conductivity Calibration Potentiometer ($0\text{–}3.3\text{V}$). |
| **PA10**| `GPIO_OD` | Digital I/O| DS18B20 1-Wire Digital Seawater Temperature Probe ($4.7\text{ k}\Omega$ pull-up to 3.3V). |
| **PA4** | **`DAC1_OUT1`**| **Analog Out**| **12-bit Hardware DAC Transmitted Chirp to Sallen-Key Reconstruction Filter.** |
| **PA5** | **`ADC1_IN5`** | **Analog In** | **Transmit Current Sense Input from INA180 Amplifier ($0\text{–}1.65\text{A} \rightarrow 0\text{–}3.3\text{V}$).** |
| **PA6** | **`ADC1_IN6`** | **Analog In** | **Power Amplifier Rail Voltage Monitor via $100\text{k}/10\text{k}$ Divider network.** |
| **PA7** | **`ADC1_IN7`** | **Analog In** | **Power Amplifier Heatsink Temperature Sensor (TMP36, $10\text{ mV}/^\circ\text{C}$).** |
| **PB6** | `TIM4_CH1` | Digital Out| Benchtop Audio Demonstration Transducer / Speaker Output. |
| **PB8** | `I2C1_SCL` | Digital I/O| 0.96" Monochrome OLED Telemetry HUD Clock Line. |
| **PB9** | `I2C1_SDA` | Digital I/O| 0.96" Monochrome OLED Telemetry HUD Data Line. |
| **PA2** | `USART2_TX`| Digital Out| ST-Link Virtual COM Port NMEA Telemetry Stream (`$SONAR`, 115200 8-N-1). |
| **PA3** | `USART2_RX`| Digital In | ST-Link Virtual COM Port Interactive Ground Station Command Receiver. |
| **PC13**| `GPIO_IN` | Digital In | User Pushbutton B1 (Short press: Plume demo; Long press: Audio engine toggle). |

---

## 5. ANALOG FILTER SPECIFICATION & TRANSFER MATHEMATICS

The analog reconstruction filter is a **4th-Order Active Butterworth Low-Pass Filter** consisting of two cascaded Sallen-Key 2nd-order stages designed with correct non-unity gain damping factors:

$$B_4(s) = \left(s^2 + \frac{\omega_c}{Q_1} s + \omega_c^2\right) \left(s^2 + \frac{\omega_c}{Q_2} s + \omega_c^2\right)$$
Where:
* Stage 1 Damping: $\alpha_1 = 1.8478 \implies Q_1 = \frac{1}{\alpha_1} = \mathbf{0.541}$
* Stage 2 Damping: $\alpha_2 = 0.7654 \implies Q_2 = \frac{1}{\alpha_2} = \mathbf{1.307}$

In an equal-resistor/equal-capacitor ($R_1=R_2=R$, $C_1=C_2=C$) Sallen-Key topology:
$$Q = \frac{1}{3 - K}, \quad \text{where } K = 1 + \frac{R_f}{R_g}$$
* **Stage 1 Gain**: $K_1 = 3 - \frac{1}{0.541} = 1.152 \implies R_{f1} = 1.52\text{ k}\Omega, \ R_{g1} = 10.0\text{ k}\Omega$
* **Stage 2 Gain**: $K_2 = 3 - \frac{1}{1.307} = 2.235 \implies R_{f2} = 12.35\text{ k}\Omega, \ R_{g2} = 10.0\text{ k}\Omega$
* **Overall Passband Voltage Gain**: $K_{\text{total}} = 1.152 \times 2.235 = 2.575 \ (\mathbf{+7.8\text{ dB}})$

### Component Tuning Values:
* **Ultrasonic Sonar Band ($f_c \approx 600\text{ kHz}$)**: $R = 2.65\text{ k}\Omega \ (0.1\%), \ C = 100\text{ pF} \ (\text{C0G/NP0})$. Active Op-Amp: **AD8065** ($\text{GBW} = 145\text{ MHz}$).
* **Benchtop Demo Band ($f_c \approx 15.92\text{ kHz}$)**: $R = 10.0\text{ k}\Omega \ (0.1\%), \ C = 1.0\text{ nF} \ (\text{C0G/NP0})$. Active Op-Amp: **TL072 / OPA350**.

---

## 6. ELECTRICAL METROLOGY & POWER GOVERNOR STATE MACHINE

```
[ Active Ping Transmit: 12-bit DAC DMA Stream ]
                       │
                       ▼
[ Synchronous ADC1 Sampling: PA5 (I_tx) & PA6 (V_supply) ]
                       │
                       ▼
[ Numerical Discrete Energy Integration ]
  E_pulse = Σ V_rail[n] · I_tx[n] · Δt
                       │
                       ▼
[ Cumulative Energy Budget Accounting ]
  E_remaining = E_budget - Σ E_pulse
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
[ Energy Budget Tiers ]     [ PA Thermal State (PA7 TMP36) ]
  > 60%: Performance Mode     < 50°C: Normal
  20 - 60%: Balanced Mode     50 - 70°C: Warning (PRI +50%)
  < 20%: Conservative Mode    70 - 85°C: Throttling (Amp -40%)
                              ≥ 85°C: Protective Cutoff
```

---
*Authoritative Revision: SIH 2026 Problem Statement 26058 — Official Industrial Datasheet.*
