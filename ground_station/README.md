# 🎛️ Ground Station & Operator Telemetry Tools
### SIH 2026 — Problem Statement 26058: AUV Adaptive Sonar Payload

This directory contains the operator interfaces used during benchtop testing, mission monitoring, and waveform synthesis for the Adaptive Sonar Transmitter.

---

## 📂 Interfaces Overview

| Tool | Type | Purpose | Primary Protocol |
|---|---|---|---|
| **`sdr_sonar_ground_station.html`** | Standalone Single-File GUI | Real-time hardware telemetry display, NMEA sentence parser, power budget tracking, PA thermal monitoring, and oscilloscope/waterfall visualization. | **Web Serial API** (USB-UART @ 115200 baud) |
| **`sonar_dashboard/`** | React 19 + Vite Application | Hydroacoustic physical simulation (Mackenzie 1981, Francois-Garrison 1982), dynamic multi-frequency chirp synthesis, audio sonification, and C-header table generation. | Local Browser Simulation / Clipboard Export |

---

## 1. Real-Time Hardware Ground Station (`sdr_sonar_ground_station.html`)

### How to Use:
1. Connect the STM32 Nucleo-64 board to your PC via USB cable.
2. Open `sdr_sonar_ground_station.html` in Google Chrome, Microsoft Edge, or Opera (browsers supporting the Web Serial API).
3. Click **"Connect Serial Port"** and select the ST-LINK Virtual COM Port (`115200 baud, 8-N-1`).
4. The dashboard automatically parses incoming 24-field `$SONAR` NMEA telemetry packets:
   ```text
   $SONAR,142,0,450000,100000,2.00,1.00,12.42,0.85,0.021,48.25,82.4,28.4,1,14.2,25.0,15.2,35.0,2048,0,0,0,0*7F
   ```
5. **Real-Time Indicators**:
   * **Power Governor Status**: Displays `PERFORMANCE`, `BALANCED`, or `CONSERVATIVE` based on remaining energy budget.
   * **Thermal Protection Bar**: Visualizes PA heatsink temperature with Warning ($>70^\circ\text{C}$) and Critical Cutoff ($>85^\circ\text{C}$) thresholds.
   * **Electrical Metrology**: Real-time display of instantaneous battery voltage, load current, pulse energy ($E_{\text{pulse}}$ in Joules), and cumulative mission energy consumption.
   * **Live Oscilloscope & Spectrogram**: Canvas-rendered waveform monitor displaying synthesized ping buffers.

---

## 2. Ocean Acoustics & Waveform Synthesis Workbench (`sonar_dashboard/`)

### How to Run:
```bash
cd ground_station/sonar_dashboard
npm install
npm run dev
```
Open `http://localhost:5173` to explore interactive sound speed profiles, acoustic attenuation curves, and listen to audible-scaled chirp sonifications.
