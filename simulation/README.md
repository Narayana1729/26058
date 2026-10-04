# 🔬 Underwater Acoustic Simulation & Waveform Synthesis
### SIH 2026 — Problem Statement 26058: Numerical Modeling & Verification

This directory contains the computational acoustic models, Python verification scripts, lookup-table generators, and scientific experiments used to validate the software-defined sonar transmitter before embedded deployment.

---

## 📁 Directory Organization

```
simulation/
├── waveform_generator.py       # LFM chirp generation, Tukey tapering & 12-bit quantization
├── ocean_propagation_model.py  # Mackenzie sound speed & Francois-Garrison absorption curves
├── filter_design_baseband.py   # Sallen-Key low-pass filter Butterworth component solver
├── simulate_filter_bode.py     # NumPy/SciPy synthetic Bode frequency response plotter
├── docs/                       # Verification plots & spectral waterfalls
├── export/                     # Exported tables and intermediate simulation artifacts
└── python/
    ├── models/acoustic_model.py# Core oceanographic physics module (c(T,S,D), α(f))
    ├── generate_luts.py        # Automated generator for multi-modulation C header tables
    ├── experiments/
    │   ├── exp02_frequency.py  # Frequency selection vs. water turbidity study
    │   ├── exp03_closed_loop.py# Simulation of two-stage adaptation state machine
    │   └── exp04_hfm_lfm.py    # Doppler tolerance comparison: LFM vs. HFM chirps
    └── tests/
        └── test_acoustic_model.py # Unit tests for physical models (7/7 passing)
```

---

## 🚀 Running Verification & Tests

To execute the scientific unit test suite:
```bash
python3 simulation/python/tests/test_acoustic_model.py
```

To run the scientific experiment studies:
```bash
python3 simulation/python/experiments/exp02_frequency.py
python3 simulation/python/experiments/exp03_closed_loop.py
python3 simulation/python/experiments/exp04_hfm_lfm.py
```
*(All plots are exported to `docs/` as high-resolution figures for technical reports).*
