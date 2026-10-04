# 4th-Order Butterworth Sallen-Key Low-Pass Filter Walkthrough

This document outlines the final design, verification, and component values of the DAC Reconstruction Filter for Stage 3 of the SIH 2026 Autonomous Underwater Vehicle (AUV) payload, incorporating the RLC Trap and 74HC4066 dynamic switching.

## 📊 Simulation Performance Summary (RL = 1 kΩ vs. BVD Transducer Load)

The circuit has been verified using LTspice under both a nominal $1\text{ k}\Omega$ resistor load and a realistic **Butterworth-Van Dyke (BVD) transducer load** ($C_0 = 1.8\text{ nF}$ in parallel with a series branch of $L_m = 150\text{ mH}, C_m = 100\text{ pF}, R_m = 50\ \Omega$).

| Metric | Target Value | Simulated (Resistor Load) | Simulated (BVD Transducer Load) | Status |
|--------|--------------|---------------------------|---------------------------------|--------|
| **Passband Gain** | Flat | **+7.8 dB** | **+8.2 dB** | ✅ PASS |
| **Cutoff Frequency ($f_c$)** | ~15.9 kHz / 20 kHz / 38 kHz | **15.90 kHz / 19.95 kHz / 37.58 kHz** | **19.98 kHz** | ✅ PASS |
| **Stopband Rejection @ 100 kHz** | ≥ 60 dB relative drop | **-90 dB** absolute drop | **-90 dB** absolute drop | ✅ PASS |
| **Output Peak-to-Peak ($V_{pp}$)** | ~5 V / 8.48 V | **4.9 V / 8.48 V** | **5.16 V** | ✅ PASS |
| **Transient Stability** | Stable (No Oscillation) | **Stable** | **Stable** (Ripple: < 1 mV) | ✅ PASS |

---

## 🎨 Simulation Results

All generated simulation plots are exported to the project's documentation folder:
1. **Frequency Domain Sweep:** `docs/sim1_bode.png` (Shows flat +7.8 dB gain, 15.9 kHz cutoff, and -100 dB RLC trap notch at 100 kHz).
2. **Passband Transient Response:** `docs/sim2_passband_1k.png` & `docs/sim2_passband_10k.png` (Shows clean peak-to-peak output swing).
3. **100 kHz Noise Attenuation:** `docs/sim3_noise_rejection.png` (Shows steady-state clock ripple crushed to < 1 mV).
4. **Over-Voltage Clamping:** `docs/sim4_overvoltage.png` (Shows input spike clamped to ±5.0 V).
5. **Dual-Band Switching:** `docs/sim5_dual_band.png` (Shows 20 kHz and 38 kHz AC sweeps overlaid).
6. **Piezo Transducer load:** `docs/bonus_piezo_load.png` (Shows stable transient response under BVD reactive load).

---

## 🛠️ Circuit Parameters & Component Values (BOM)

| Component Designators | Quantity | Value / Part | Description |
|-----------------------|----------|--------------|-------------|
| **R1, R2, R3, R4** | 4 | **8 kΩ** | 1% metal film resistors (sets base 20 kHz cutoff) |
| **Rp1, Rp2, Rp3, Rp4** | 4 | **8.8 kΩ** | 1% metal film resistors (switched in parallel for 38 kHz cutoff) |
| **Rf1** | 1 | **1.52 kΩ** | 1% metal film resistor (sets Stage 1 Q = 0.541) |
| **Rf2** | 1 | **12.35 kΩ** | 1% metal film resistor (sets Stage 2 Q = 1.307) |
| **Rg1, Rg2** | 2 | **10 kΩ** | 1% metal film feedback resistors |
| **C1, C2, C3, C4** | 4 | **1 nF** | C0G/NP0 ceramic capacitors (high stability) |
| **Cout** | 1 | **100 µF** | Low ESR bipolar electrolytic / tantalum capacitor |
| **Lt** | 1 | **1 mH** | High-Q power inductor (RLC Trap) |
| **Ct** | 1 | **2.533 nF** | High-stability capacitor (RLC Trap tuned to 100 kHz) |
| **D1, D2** | 2 | **1N5819** | Schottky diodes (fast protection clamping) |
| **Rout** | 1 | **50 Ω** | Output impedance matching resistor |
| **U1, U2** | 1 (dual package) | **TL072** | Dual high-bandwidth op-amp (GBW ≥ 6 MHz) |
| **S1, S2, S3, S4** | 1 (quad package) | **74HC4066** | Quad bilateral CMOS analog switch |
| **RL** | 1 | **1 kΩ** | Nominal test load resistor |

---

## 💡 Engineering Design Details

* **Butterworth Alignment:** Cascaded non-unity gain stages with distinct damping factors ($\alpha_1 = 1.848 \implies Q_1 = 0.541$; $\alpha_2 = 0.765 \implies Q_2 = 1.307$) to achieve a flat Butterworth passband.
* **RLC Trap (Notch Filter):** A series combination of $L_t = 1\text{ mH}$ and $C_t = 2.533\text{ nF}$ connected to Ground forms a notch filter tuned exactly to the $100\text{ kHz}$ DAC clock, shunting the clock frequency to ground while leaving passband signals unattenuated.
* **74HC4066 Bandwidth Control:** When `Vctrl = 0V` (switches open), the cutoff is $20\text{ kHz}$. When `Vctrl = 5V` (switches closed), $8.8\text{ k}\Omega$ resistors are connected in parallel with the base $8\text{ k}\Omega$ resistors, reducing equivalent resistance to $4.19\text{ k}\Omega$ and shifting the cutoff to $38\text{ kHz}$.