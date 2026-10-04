# 📌 Master Hardware Pin Map & Interface Specification
**Target Platform**: STM32 Nucleo-64 (STM32G474RE / STM32F446RE / STM32F401RE)  
**Project**: Intelligent Self-Monitoring Adaptive Sonar Transmitter for AUVs (SIH 2026 — PS 26058)  
**Status**: **FROZEN HARDWARE CONTRACT** (All schematics, BOM, firmware, and documentation adhere strictly to this mapping)

---

## 1. Authoritative Physical Pin Mapping

| STM32 Pin | Morpho / Arduino Header | Peripheral Function | Subsystem Domain | Electrical Characteristics | Connection Target & Circuit Details |
|:---|:---|:---|:---|:---|:---|
| **PA0** | CN8:Pin 1 (A0) | `ADC1_IN0` | Environmental Sensing | Analog In ($0\text{–}3.3\text{V}$) | **Optical Turbidity Sensor (TSW-20)** via $10\text{ k}\Omega / 20\text{ k}\Omega$ voltage divider ($0\text{–}5\text{V} \rightarrow 0\text{–}3.3\text{V}$) |
| **PA1** | CN8:Pin 2 (A1) | `ADC1_IN1` | Environmental Sensing | Analog In ($0\text{–}3.3\text{V}$) | **Hydrostatic Depth Sensor (MS5837)** or Precision Benchtop Depth Simulation Potentiometer |
| **PC0** | CN8:Pin 6 (A5) | `ADC1_IN10` | Environmental Sensing | Analog In ($0\text{–}3.3\text{V}$) | **Salinity / Ambient Test Potentiometer** *(Relocated from PA4 to keep DAC dedicated)* |
| **PA10**| CN10:Pin 33 (D2)| `GPIO_OD` | Environmental Sensing | 3.3V Digital Open-Drain | **Seawater Temperature Probe (DS18B20 1-Wire)** with onboard $4.7\text{ k}\Omega$ pull-up to $+3.3\text{V}$ |
| **PA4** | CN8:Pin 5 (A2) | **`DAC1_OUT1`** | **Acoustic Transmitter** | **Analog Out ($0.2\text{–}3.1\text{V}$)** | **True 12-bit DAC Signal to 4th-Order Sallen-Key Active Low-Pass Reconstruction Filter** |
| **PA5** | CN10:Pin 11 (D13)| **`ADC1_IN5`** | **Electrical Metrology** | **Analog In ($0\text{–}3.3\text{V}$)** | **Transmit Current Sense Input from INA180 Differential Amplifier** ($V_{\text{out}} = 20 \times 0.1\Omega \times I_{\text{tx}} = 2.0 \cdot I_{\text{tx}}$) |
| **PA6** | CN10:Pin 13 (D12)| **`ADC1_IN6`** | **Electrical Metrology** | **Analog In ($0\text{–}3.3\text{V}$)** | **Supply Rail Voltage Monitor** via $100\text{ k}\Omega / 10\text{ k}\Omega$ precision divider ($0\text{–}33\text{V} \rightarrow 0\text{–}3.0\text{V}$) |
| **PA7** | CN10:Pin 15 (D11)| **`ADC1_IN7`** | **Hardware Health** | **Analog In ($0\text{–}2.0\text{V}$)** | **Power Amplifier Heatsink Thermal Sensor (TMP36)** ($10\text{ mV}/^\circ\text{C}$, $750\text{ mV} @ 25^\circ\text{C}$) |
| **PB6** | CN10:Pin 17 (D10)| `TIM4_CH1` | Bench Audio Demo | Digital PWM (Square wave) | **Audible Speaker Output** for human acoustic perception during live bench demonstrations |
| **PB8** | CN10:Pin 3 (D15)| `I2C1_SCL` | Subsea HUD / Display | 3.3V Digital Open-Drain | **0.96" Monochrome I2C OLED Display (SSD1306)** Clock Line |
| **PB9** | CN10:Pin 5 (D14)| `I2C1_SDA` | Subsea HUD / Display | 3.3V Digital Open-Drain | **0.96" Monochrome I2C OLED Display (SSD1306)** Data Line |
| **PA2** | CN10:Pin 35 (D1) | `USART2_TX` | Telemetry Link | 3.3V LVTTL Serial | **ST-Link Virtual COM Port TX** (115200 baud to Web Ground Station) |
| **PA3** | CN10:Pin 37 (D0) | `USART2_RX` | Telemetry Link | 3.3V LVTTL Serial | **ST-Link Virtual COM Port RX** (115200 baud from Web Ground Station commands) |
| **PC13**| Onboard Button | `GPIO_Input` | Local Control | Digital Active-Low | **User Pushbutton B1** (Short: Mission Plume Demo; Long: Audio Demonstration Mode) |

---

## 2. Signal Routing Chain & Electrical Protection

```
  [ TSW-20 Turbidity (0-5V) ] ──> [ 10k/20k Divider ] ──> [ RC LPF (100nF) ] ───> STM32 Pin PA0 (ADC1_IN0)
  [ MS5837 / Depth Pot (0-3.3V) ] ──────────────────────> [ RC LPF (100nF) ] ───> STM32 Pin PA1 (ADC1_IN1)
  [ Salinity Pot (0-3.3V) ] ────────────────────────────> [ RC LPF (100nF) ] ───> STM32 Pin PC0 (ADC1_IN10)
  [ DS18B20 1-Wire Temp ] ──> [ 4.7k Pullup to 3.3V ] ──────────────────────────> STM32 Pin PA10 (GPIO_OD)

  [ STM32 TIM6_TRGO + DMA ] ──> [ DAC1_OUT1 ] (Pin PA4)
                                      │
                                      ▼
                      ┌──────────────────────────────┐
                      │ 4th-Order Sallen-Key LPF     │ (Cutoff fc: 15.9 kHz / 600 kHz)
                      │ + 100 kHz RLC Notch Trap     │ (Attenuates DAC clock spurs >48 dB)
                      └──────────────┬───────────────┘
                                      │
                                      ▼
                           [ Power Amplifier Stage ]
                           (Half-Bridge Switcher)
                                      │
                                      ▼
                        [ Load / Ultrasonic Transducer ]
                                      │
                                      ▼
                        [ 0.10 Ω 1% 2W Shunt Resistor ]
                                      │
                                      ▼
                        [ INA180 Current Sense Amp ]
                                      │
                                      ▼
                        [ RC LPF (100 Ω / 10 nF) ] ──> Anti-Aliasing Filter (fc ≈ 159 kHz)
                                      │
                                      ▼
                               STM32 Pin PA5 (ADC1_IN5)

  [ +12V/+24V Supply Rail ] ──> [ 100k/10k Divider ] ──> [ RC LPF (100nF) ] ───> STM32 Pin PA6 (ADC1_IN6)
  [ Heatsink TMP36 ] ──────────> [ RC LPF (100 Ω / 100 nF) ] ──────────────────> STM32 Pin PA7 (ADC1_IN7)
```

---

## 3. Peripheral Hardware Conflict Resolution Summary

1. **PA4 Conflict Resolved**: PA4 was previously used as an ADC channel for Salinity in Nucleo firmware while documented as DAC output. Salinity is now permanently assigned to **PC0** (Arduino header A5). **PA4 is 100% reserved for DAC1_OUT1**.
2. **PA5 Conflict Resolved**: PA5 was used as the onboard Green LED (LD2) in Nucleo firmware while documented as Current Sense input. The LED is now moved to software heartbeat on PC8 or PB13, freeing **PA5 exclusively for high-speed ADC1_IN5 (INA180 current sense)**.
3. **PB6 Conflict Resolved**: PB6 was claimed for USART1_TX in the datasheet and TIM4 speaker PWM in firmware. USART telemetry is standardized on **USART2 (PA2/PA3)** via the ST-Link USB VCP, freeing **PB6 for the demonstration speaker**.
4. **Turbidity Pin Safety**: Added mandatory $10\text{ k}\Omega / 20\text{ k}\Omega$ resistive divider on PA0 to prevent TSW-20 $4.5\text{–}5.0\text{V}$ signals from overvoltaging the STM32 ADC.

---

## 4. Bench Metrology & Laboratory Oscilloscope Test Points

To allow real-time jury and evaluator verification during live demonstrations, dedicated test points (TP) are routed to a **100 MHz Digital Storage Oscilloscope (DSO)**:

| Test Point | Signal Name | Physical Location | DSO Channel | Verification Target |
|:---|:---|:---|:---|:---|
| **TP_DAC** | `DAC_RAW_OUT` | Header CN8:Pin 5 (PA4) | **DSO CH1 (Yellow)** | 12/16-Bit DDS Chirp output, discrete staircase steps, and Tukey ($\alpha=0.25$) envelope tapering |
| **TP_FLT** | `FILTER_OUT` | Sallen-Key Stage 2 Op-Amp Pin 7 | **DSO CH2 (Cyan)** | Active 4th-order reconstruction filter output ($>48\text{ dB/oct}$ DAC image spur rejection, $\text{THD} < 0.05\%$) |
| **TP_CURR** | `ISENSE_AMP` | Header CN10:Pin 11 (PA5) | **DSO CH3 (Magenta)** | Dynamic transmit current $I_{\text{tx}}(t)$ via INA180 ($2.0\text{ V/A}$) for instantaneous $V \times I$ power math |
| **TP_TRIG** | `PULSE_SYNC` | Timer `TIM6_TRGO` Testpad | **DSO Ext Trig** | Zero-latency hardware trigger pulse at the start of each acoustic ping transmission |

