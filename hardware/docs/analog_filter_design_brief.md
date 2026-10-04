# 🔌 Technical Design Brief: Active Reconstruction Filter & Analog Front-End
### SIH 2026 — Problem Statement 26058: Hardware Analog Signal Chain

This document summarizes the circuit topology, SPICE simulation verification, and load-stability analysis for the **4th-Order Sallen-Key Active Reconstruction Low-Pass Filter** interfacing the DAC to the acoustic projector stage.

---

## 🔬 Circuit Architecture Overview

The active reconstruction filter serves three critical hardware functions:
1. **DAC Antialiasing & Image Rejection**: Attenuates high-frequency zero-order-hold (ZOH) sampling steps and switching spurs by $>48\text{ dB}$.
2. **Gain & Buffer Stage**: Provides low-impedance drive with $+7.8\text{ dB}$ passband amplification into the downstream power amplifier.
3. **Over-Voltage & Surge Protection**: Fast Schottky diode clamp network limiting node transients to safe operating rails ($\pm 5.0\text{ V}$).

---

## 📊 Verification Test Matrix & SPICE Results

### Test 1: Small-Signal Frequency Response (Bode Plot)
* **Simulation File**: `docs/sim1_bode.png` & `../spice/bode_plot_ultrasonic.png`
* **Performance**: Demonstrates flat passband gain of $+7.8\text{ dB}$ ($f_c \approx 15.9\text{ kHz}$ bench baseband / $600\text{ kHz}$ ultrasonic configuration) with sharp $-80\text{ dB/decade}$ stopband roll-off, eliminating DAC clock harmonics.

### Test 2: Passband Transient Response & Signal Integrity
* **Simulation File**: `docs/sim2_passband_1k.png` and `docs/sim2_passband_10k.png`
* **Performance**: Clean, undistorted sinusoidal output at $1\text{ kHz}$ and $10\text{ kHz}$ peaking at $2.45\text{ V}$ across a $1\text{ k}\Omega$ resistive bench load. Total Harmonic Distortion verified at $\text{THD} < 0.15\%$.

### Test 3: Switching Spur & Clock Noise Attenuation
* **Simulation File**: `docs/sim3_noise_rejection.png`
* **Performance**: Steady-state output ripple under high-frequency switching excitation is suppressed to $< 1.1\text{ mV}_{\text{p-p}}$, well within the $\le 3.0\text{ mV}_{\text{p-p}}$ noise margin.

### Test 4: Dynamic Over-Voltage Protection Clamping
* **Simulation File**: `docs/sim4_overvoltage.png`
* **Performance**: Under a simulated $10\text{ V}$ transient voltage spike, bidirectional Schottky clamping diodes strictly limit output voltage swing to $\pm 5.0\text{ V}$, protecting downstream analog-to-digital converter (ADC) inputs.

### Test 5: Dynamic Bandwidth Switching
* **Simulation File**: `docs/sim5_dual_band.png`
* **Performance**: Evaluates electronic bandwidth reconfiguration. Activating the 74HC4066 analog switch shifts the filter cutoff dynamically from $20\text{ kHz}$ to $38\text{ kHz}$ to support wideband frequency-modulated acoustic chirps.

### Test 6: Reactive Piezoelectric Transducer Load Stability
* **Simulation File**: `docs/bonus_piezo_load.png`
* **Performance**: Verified under a lumped Butterworth-Van Dyke (BVD) transducer equivalent network ($C_0 = 1.8\text{ nF}$, $L_m = 150\text{ mH}$, $R_m = 45\,\Omega$). The op-amp maintains a $>55^\circ$ phase margin with no high-frequency capacitive ringing or peaking.
