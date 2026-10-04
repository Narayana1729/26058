# 🌊 Interactive Ocean Acoustics & Waveform Synthesis Workbench
### SIH 2026 — Hardware-in-the-Loop Ground Station & Physical Simulator

A high-performance React + Vite engineering tool for modeling underwater acoustic propagation, calculating ocean absorption losses, synthesizing software-defined sonar waveforms, and exporting calibrated 12-bit DAC lookup tables for STM32 microcontrollers.

---

## 🔬 Core Physics & Mathematical Formulations

### 1. Mackenzie (1981) Sound Speed Equation
Computes local seawater acoustic speed $c$ ($\text{m/s}$) as a 9-term function of temperature $T$ ($^\circ\text{C}$), salinity $S$ ($\text{ppt}$), and hydrostatic depth $D$ ($\text{m}$):
$$c(T, S, D) = 1448.96 + 4.591 T - 5.304 \times 10^{-2} T^2 + 2.374 \times 10^{-4} T^3 + 1.340(S - 35) + 1.630 \times 10^{-2} D + 1.675 \times 10^{-7} D^2 - 1.025 \times 10^{-2} T(S - 35) - 7.139 \times 10^{-13} T D^3$$

### 2. Francois-Garrison (1982) Three-Mechanism Absorption Model
Evaluates acoustic attenuation $\alpha(f)$ in $\text{dB/km}$ across three physical relaxation processes:
$$\alpha(f) = \alpha_{\text{Boric Acid}}(f) + \alpha_{\text{MgSO}_4}(f) + \alpha_{\text{Pure Water}}(f)$$
* **Boric Acid Relaxation**: Dominant between $100\text{ Hz} \leftrightarrow 10\text{ kHz}$.
* **Magnesium Sulfate ($\text{MgSO}_4$)**: Dominant between $10\text{ kHz} \leftrightarrow 500\text{ kHz}$ (critical for sonar operating bands).
* **Pure Water Viscosity**: High-frequency asymptotic attenuation ($>500\text{ kHz}$).

### 3. Tukey-Windowed LFM Chirp Synthesis
Generates 512-point discrete pulse representations with cosine-tapered ends ($\alpha = 0.25$) to eliminate spectral splatter and DAC edge clicks:
$$s(t) = \sin\left(2\pi f_0 t + \pi \frac{B}{T_p} t^2\right) \cdot w_{\text{Tukey}}(t)$$
$$D[n] = \text{round}\left(2047.5 \times (1.0 + s[n])\right) \in [0, 4095]$$

---

## ⚡ Features
- **Real-Time Ocean Hydrophysics**: Live sliders for Temperature ($0\text{–}35^\circ\text{C}$), Salinity ($0\text{–}42\text{ ppt}$), Depth ($0\text{–}200\text{ m}$), and Turbidity ($0\text{–}150\text{ NTU}$).
- **Autonomous Mode Recommendation**: Demonstrates how changing turbidity dynamically transitions transmission profiles between:
  - **Mode 0 (Clear Water)**: $450\text{ kHz}$ carrier, wideband chirp for sub-millimeter bathymetric resolution.
  - **Mode 1 (Balanced Coastal)**: $250\text{ kHz}$ carrier, balanced propagation.
  - **Mode 2 (Turbid/Muddy Water)**: $100\text{ kHz}$ carrier, deep penetrating long-range transmission.
- **Interactive Audio Sonification**: Employs the Web Audio API to scale ultrasonic sweeps down into the human-audible band ($300\text{–}4500\text{ Hz}$), demonstrating the audible difference between rectangular-windowed pulses (harsh clicks) and smooth Tukey-tapered chirps.
- **Direct C-Header Exporter**: Generates and copies ready-to-flash `chirp_lut.h` arrays directly into the clipboard for pasting into STM32CubeIDE.

---

## 🚀 Running the Workbench Locally

```bash
# Navigate to the dashboard directory
cd ground_station/sonar_dashboard

# Install dependencies
npm install

# Launch Vite development server
npm run dev
```

Visit `http://localhost:5173` in any modern web browser (Chrome, Edge, Firefox, Safari).

---

## 📁 Project Structure

```
sonar_dashboard/
├── index.html              # HTML entry point
├── package.json            # Node.js dependencies (React 19, Lucide, Vite)
├── src/
│   ├── App.jsx             # Comprehensive ground station UI & physics engine
│   ├── App.css             # Glassmorphism dark-theme styling
│   ├── index.css           # Global typography & reset rules
│   └── main.jsx            # React root mount
└── vite.config.js          # Vite bundler configuration
```
