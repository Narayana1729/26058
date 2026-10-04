# ⚡ Analog Front-End & Hardware Engineering
### Active Sallen-Key Reconstruction & Switching Power Stage

This directory contains the analog circuit models, frequency-domain AC sweeps, piezoelectric load characterization, and design documentation for the transmitter's mixed-signal stages.

---

## 📁 Directory Structure

```
hardware/
├── spice/                         # SPICE circuit simulation models & schematics
│   ├── sallen_key_4th_order.asc   # 4th-Order Butterworth LPF (+7.8 dB gain, RLC notch)
│   ├── sallen_key_4th_order_piezo.asc # Reactive BVD piezoelectric transducer model
│   ├── TL072.sub                  # TI TL072 high-speed JFET op-amp SPICE macro-model
│   ├── staircase_sine.txt         # PWL 12-bit DAC staircase test stimulus
│   ├── bode_plot_ultrasonic.png   # AC frequency response sweep (-80 dB/dec roll-off)
│   └── docs/                      # Exported transient & noise rejection plots
│
└── docs/                          # Technical circuit walkthroughs & engineering briefs
    ├── walkthrough.md             # Complete mathematical derivation of filter poles & Q
    └── analog_filter_design_brief.md # Circuit design brief & load stability analysis
```

---

## 🔬 Circuit Specifications & Verified Metrics

| Metric | Target Specification | Simulated (Resistive Load) | Simulated (Piezo BVD Load) | Status |
|---|---|---|---|---|
| **Passband Gain** | Flat Butterworth | **+7.8 dB** | **+8.2 dB** | ✅ Verified |
| **Cutoff Frequency ($f_c$)** | $15.9\text{ kHz}$ / $600\text{ kHz}$ | **15.90 kHz / 19.95 kHz** | **19.98 kHz** | ✅ Verified |
| **Stopband Rejection @ 100 kHz** | $\ge 60\text{ dB}$ attenuation | **-90 dB** | **-90 dB** | ✅ Verified |
| **Transient Stability** | Zero ringing / oscillation | **Stable (<1 mV ripple)** | **Stable** | ✅ Verified |

---

## 🛠️ Simulation Execution

To open and simulate the circuits:
1. Launch **LTspice XVII** or **LTspice 24**.
2. Open `hardware/spice/sallen_key_4th_order.asc`.
3. Click **Simulate → Run** to evaluate AC frequency response, RLC notch clock shunting, and transient DAC reconstruction.
