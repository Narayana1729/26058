# 📡 V2/V3 Roadmap: In-Water Receiver & Channel Feedback Research Archive

> **Scope Notice**:  
> The current SIH 2026 Phase 1 / MVP prototype is **100% Transmitter-Only** (concentrating novelty on software-defined waveform agility, Francois-Garrison prior prediction, real-time electrical energy integration, power budget governance, and thermal protection).
>
> This directory archives early exploratory research, scripts, and tables developed for **Phases V2 and V3** (staged future extensions incorporating a physical hydrophone, receiver Analog Front-End, Time-Gain Compensation, and in-water seabed classification).

---

## 📁 Archived Components

### 1. Acoustic Receiver & TGC Modeling (`simul/`)
* **`seabed_classifier_tgc.py`**: Physics-derived Time-Gain Compensation (TGC) curve modeling ($Gain(R) = 40\log_{10}(R) + \alpha(f)R$) and seabed reflection coefficient impedance mapping ($Z = \rho \cdot c$).
* **`matched_filter_receiver.py`**: Time-domain matched filtering and cross-correlation simulation on noisy acoustic return signals.
* **`seabed_model.py` & `tgc_generator.py`**: Python modular generators for empirical substrate backscatter and absorption compensation curves.
* **`tests/` & `experiments/`**: Standalone pytest scripts validating TGC curves and synthetic echo reflection.

### 2. Experimental Receiver Plots & Tables (`docs/`)
* **`tgc_lut.h`**: 512-entry DAC lookup table for dynamic receiver gain compensation.
* **`seabed_classification_analysis.png`**: Simulation plot of acoustic impedance vs. substrate classification (Sand, Silt, Gravel, Rock).
* **`matched_filter_verification.png`**: Oscilloscope / simulation verification of matched filter pulse compression ($PCR = B \cdot T_p$).
* **`exp01_tgc.png` & `exp05_reflection.png`**: Synthetic reflection response and TGC curves.

### 3. Early Visualizer Prototypes (`legacy_dashboards/`)
* **`acoustic_visualizer_v1.html`**: Early standalone HTML5 canvas visualizer.
* **`simulation_app/`**: First-generation static demo app (superseded by `ground_station/sonar_dashboard` and `ground_station/sdr_sonar_ground_station.html`).

---
*Maintained as reference research for the post-hackathon underwater acoustic transceiver roadmap.*
