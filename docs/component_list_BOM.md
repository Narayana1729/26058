# 🔩 Complete Bill of Materials (BOM) — Intelligent Self-Monitoring Sonar Transmitter
## Mixed-Signal Software-Defined Acoustic Subsystem (SIH 2026 — Problem Statement 26058)
**Authoritative Hardware Contract**: Aligned 100% with [MASTER_PIN_MAP.md](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/MASTER_PIN_MAP.md)

---

## 🧠 A. THE BRAIN (Microcontroller & DSP Engine)

| # | Component | Exact Part / Specification | Pin / Function in Subsystem | Qty | Unit Cost (₹) |
|:--|:----------|:---------------------------|:----------------------------|:---:|--------------:|
| 1 | STM32 Microcontroller | **STM32G474RET6 / STM32F446RE** (Nucleo-64) | Core Controller — 170 MHz ARM Cortex-M4, DMA1/2, TIM6_TRGO, 12-bit DAC1 (PA4), 12-bit Synchronous ADC1 | 1 | 650 |
| 2 | Hardware Debugger Link | **ST-LINK / V2** (Integrated on Nucleo) | SWD debug port + Virtual COM Port USART2 (PA2/PA3 @ 115200 baud) to Ground Station | 1 | 240 |
| 3 | USB Interconnect | **USB-C Shielded Data Cable** | High-speed data telemetry + 5V VBUS power rail | 1 | 80 |

---

## 🎛️ B. ENVIRONMENTAL SENSORY STAGE (Stage 1 Prior Generation)

| # | Component | Exact Part / Specification | Pin / Function in Subsystem | Qty | Unit Cost (₹) |
|:--|:----------|:---------------------------|:----------------------------|:---:|--------------:|
| 4 | Optical Turbidity Sensor | **TSW-20M / SEN0189** ($0\text{–}4.5\text{V}$ Analog Out) | Measures water column clarity (0–250+ NTU) to select acoustic carrier frequency $f_c$ | 1 | 520 |
| 5 | Turbidity Voltage Divider | **10.0 kΩ + 20.0 kΩ (0.1% Metal Film)** | **Hardware Protection**: Scales $0\text{–}5.0\text{V}$ sensor output down to $0\text{–}3.3\text{V}$ at **Pin PA0** (`ADC1_IN0`) | 2 | 10 |
| 6 | Depth / Pressure Sensor | **MS5837-30BA** / Piezoresistive Transducer | Hydrostatic depth input (seeds pulse duration $T_p$ from 2.0 to 20.0 ms) at **Pin PA1** (`ADC1_IN1`) | 1 | 1,200 |
| 7 | Water Temperature Probe | **DS18B20 Waterproof 1-Wire Probe** | Real-time water temperature at **Pin PA10** (`GPIO_OD` with $4.7\text{k}\Omega$ pull-up) for Francois-Garrison model | 1 | 120 |
| 8 | Benchtop Sensor Simulators| **Bourns 10kΩ Precision Multi-Turn Pots** | Bench simulators for Depth (PA1) and Salinity (**Pin PC0**, `ADC1_IN10`) parameter perturbations | 3 | 75 |
| 9 | Calibration Knobs | **Anodized Knurled Aluminum Dials** | Color-coded user dials for live bench jury demonstrations (Turbidity, Depth, Salinity) | 3 | 45 |

---

## ⚡ C. HIGH-SPEED ANALOG RECONSTRUCTION FILTER (AFE)

| # | Component | Exact Part / Specification | Pin / Function in Subsystem | Qty | Unit Cost (₹) |
|:--|:----------|:---------------------------|:----------------------------|:---:|--------------:|
| 10| High-Speed Active Op-Amp | **AD8065ARZ / OPA350EA** (or TL072 for audio demo)| Dual High-Speed FastFET Op-Amp: GBW = 145 MHz / 38 MHz, Slew Rate = 180 V/µs, THD < 0.0002% | 2 | 220 |
| 11| Filter Frequency Resistors| **2.65 kΩ (0.1% Thin-Film, 25 ppm/°C)** | Frequency-determining resistors for 600 kHz ultrasonic cutoff ($10\text{ k}\Omega$ for audio demo) | 4 | 24 |
| 12| Filter Capacitors | **100 pF C0G/NP0 Dielectric (±1%, 50V)** | Low-loss, zero-voltage-coefficient capacitors for 600 kHz cutoff ($1\text{ nF}$ for audio demo) | 4 | 28 |
| 13| Stage Q-Factor Resistors | **Rf1 = 1.52 kΩ, Rf2 = 12.35 kΩ, Rg = 10.0 kΩ** | Sets exact Butterworth damping factors: Stage 1 $Q_1 = 0.541$, Stage 2 $Q_2 = 1.307$ (+7.8 dB gain) | 4 | 24 |
| 14| High-Frequency Bypass Caps| **100 nF C0G Ceramic + 10 µF Tantalum** | Ultra-low ESR power rail decoupling placed directly across op-amp supply pins | 6 | 36 |
| 15| Virtual Ground Bias Network| **10.0 kΩ (0.1% Matched Pair) + 10 µF Cap** | Creates ultra-stable $V_{DD}/2 = 1.65\text{V}$ virtual analog ground reference for single-supply rails | 2 | 16 |
| 16| Fast Transient Clamp Diodes| **1N5819 Schottky Diodes (40V, 1A, Vf=0.3V)** | Output protection clamping transducer back-EMF spikes to supply rails | 2 | 14 |

---

## 🔍 D. ELECTRICAL METROLOGY & TRANSMITTER SELF-MONITORING (Stage 2 Feedback)

| # | Component | Exact Part / Specification | Pin / Function in Subsystem | Qty | Unit Cost (₹) |
|:--|:----------|:---------------------------|:----------------------------|:---:|--------------:|
| 17| Precision Shunt Resistor | **0.10 Ω (1% Tolerance, 2W, Metal-Foil)** | Senses instantaneous transmit current $I_{\text{tx}}(t)$ on low-side ground return (<165 mV drop) | 1 | 45 |
| 18| Current-Sense Amplifier | **Texas Instruments INA180A2 (Gain = 20 V/V)** | Scales shunt voltage to STM32 ADC window ($0\text{–}1.65\text{A} \rightarrow 0\text{–}3.3\text{V}$) at **Pin PA5** (`ADC1_IN5`) | 1 | 90 |
| 19| PA Heatsink Thermal Sensor| **Analog TMP36 / 10k NTC Thermistor** | Directly thermally bonded to PA heatsink ($10\text{ mV}/^\circ\text{C}$, $750\text{ mV} @ 25^\circ\text{C}$) at **Pin PA7** (`ADC1_IN7`)| 1 | 35 |
| 20| Supply Rail Voltage Divider| **100.0 kΩ / 10.0 kΩ (0.1% Matched Divider)** | Monitors supply rail ($0\text{–}33\text{V} \rightarrow 0\text{–}3.0\text{V}$) at **Pin PA6** (`ADC1_IN6`) to track battery sag during ping | 2 | 15 |

---

## 🔊 E. POWER AMPLIFIER & TRANSDUCER EMISSION STAGE

| # | Component | Exact Part / Specification | Pin / Function in Subsystem | Qty | Unit Cost (₹) |
|:--|:----------|:---------------------------|:----------------------------|:---:|--------------:|
| 21| Half-Bridge Gate Driver | **International Rectifier IR2104 / UCC27712** | High- and Low-Side 600V Bootstrap Gate Driver with integrated dead-time control | 1 | 110 |
| 22| Bootstrap Diode & Cap | **1N4148 Fast Diode + 100 nF 50V Ceramic** | Powers the high-side floating N-MOSFET gate drive network | 2 | 15 |
| 23| Power MOSFET Switching Pair| **IRLZ44N / FQP30N06L (Logic-Level N-MOSFET)**| Low $R_{DS(on)}$ ($28\text{ m}\Omega$) switching half-bridge delivering acoustic pulse energy | 2 | 65 |
| 24| Benchtop Test Load & Audio| **50 Ω 10W Power Resistor + 8Ω Test Speaker** | Safe benchtop electrical load + audible speaker at **Pin PB6** (`TIM4_CH1`) for live acoustic demos | 1 | 95 |
| 25| Ultrasonic Piezo Transducer| **40 kHz / 200 kHz Piezoceramic Disc** | Electroacoustic projector demonstrating ultrasonic acoustic emission | 1 | 250 |
| 26| BNC Panel-Mount Connector | **Amphenol 50 Ω PCB/Panel BNC Female** | Low-loss, shielded test connection directly to lab oscilloscope & spectrum analyzer | 1 | 65 |

---

## 🛡️ F. MECHANICAL PACKAGING & SUBSEA HUD

| # | Component | Exact Part / Specification | Pin / Function in Subsystem | Qty | Unit Cost (₹) |
|:--|:----------|:---------------------------|:----------------------------|:---:|--------------:|
| 27| 0.96" Monochrome OLED | **SSD1306 128×64 I2C OLED Display** | Live subsea HUD: Mode, $E_{\text{remaining}}$, $T_{\text{PA}}$, Carrier $f_c$, Duration $T_p$ (**Pins PB8/PB9**) | 1 | 180 |
| 28| Subsea Enclosure (Target) | **CNC 6061-T6 Anodized Aluminum Cylinder** | IP68 / 30 Bar (300m depth) marine-grade housing with internal heatsink thermal coupling block | 1 | 1,800 |
| 29| Sealing O-Rings | **Dual 70-Durometer Viton O-Rings** | Double-barrier radial seal against hydrostatic ocean pressure | 2 | 60 |
| 30| Bulkhead Feedthrough | **Subsea IP68 Cable Gland / 4-Pin Wet Connector**| Watertight marine penetrator for external battery power and sensor tether | 1 | 350 |

---

## 💰 DUAL-TIER BUDGET RECONCILIATION

To maintain absolute academic and financial integrity during faculty review and jury defense:

| Subsystem Tier | Component Scope | Intended Environment | Subtotal (₹) |
|:---------------|:----------------|:---------------------|-------------:|
| **Tier 1: Benchtop Mixed-Signal Demonstrator** | STM32 Nucleo, Potentiometers, AFE Filters, INA180 Shunt Metrology, TMP36, Half-Bridge Driver, Test Load & OLED | Tabletop Demonstration Rig for Hackathon Jury | **₹1,980 (~$24 USD)** |
| **Tier 2: Subsea Pressure-Rated Payload Target** | Tier 1 Core + Submersible MS5837 Depth Sensor + TSW-20 Turbidity + 6061-T6 Machined Pod + Viton Seals + Wet Penetrator | Production AUV Hull Slot (30 Bar / 300m Rating) | **₹5,840 (~$70 USD)** |

---
*Authoritative Revision: Aligned with Master Pin Contract and Verified Electrical Metrology.*
