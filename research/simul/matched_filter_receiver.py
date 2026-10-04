"""
Hydroacoustic Receiver DSP: Matched Filtering & Pulse Compression Simulation
Research Extension (V3 Roadmap: In-Water Echo Feedback & Matched Filtering)
=============================================================================
Key Functional Deliverables:
1. Pulse Compression Sidelobe Suppression (Tukey vs Rectangular).
2. Cross-Correlation Matched-Filter Delta Spike Analysis.
3. Range Resolution & Signal-to-Noise Ratio (SNR) Gain Calculation.
4. Export high-resolution verification plot.
"""

import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# 1. System Parameters
# -------------------------------------------------------------
FS = 100000.0          # 100 kHz Sampling Frequency
N_SAMPLES = 512        # 512 discrete LUT samples
T_P = N_SAMPLES / FS   # 5.12 ms Pulse Duration
F0 = 1000.0            # Start frequency: 1 kHz
F1 = 20000.0           # End frequency: 20 kHz
BANDWIDTH = F1 - F0    # 19 kHz Bandwidth
C_SOUND = 1500.0       # Speed of sound in seawater: 1500 m/s

t = np.linspace(0, T_P, N_SAMPLES, endpoint=False)
mu = (F1 - F0) / T_P   # Chirp sweep rate (Hz/s)

# -------------------------------------------------------------
# 2. Synthesize Rectangular vs Tukey-Windowed Chirps
# -------------------------------------------------------------
# Raw unwindowed LFM Chirp
chirp_raw = np.sin(2.0 * np.pi * (F0 * t + 0.5 * mu * t**2))

# Tukey Window (alpha = 0.25)
alpha = 0.25
tukey_win = np.ones(N_SAMPLES)
edge_len = int(alpha * (N_SAMPLES - 1) / 2.0)
for i in range(edge_len):
    pos = i / (N_SAMPLES - 1)
    tukey_win[i] = 0.5 * (1.0 + np.cos(np.pi * (2.0 * pos / alpha - 1.0)))
    tukey_win[-(i + 1)] = tukey_win[i]

chirp_tukey = chirp_raw * tukey_win

# -------------------------------------------------------------
# 3. Matched Filter (Auto-Correlation) Computation
# -------------------------------------------------------------
corr_raw = np.correlate(chirp_raw, chirp_raw, mode='full')
corr_tukey = np.correlate(chirp_tukey, chirp_tukey, mode='full')

# Normalize to 0 dB at peak
corr_raw_norm = corr_raw / np.max(corr_raw)
corr_tukey_norm = corr_tukey / np.max(corr_tukey)

# Convert to Decibels (dB) with -70 dB noise floor
db_raw = 20.0 * np.log10(np.maximum(1e-4, np.abs(corr_raw_norm)))
db_tukey = 20.0 * np.log10(np.maximum(1e-4, np.abs(corr_tukey_norm)))

# Time lags in milliseconds
lags_ms = (np.arange(len(corr_raw)) - (N_SAMPLES - 1)) / FS * 1000.0

# -------------------------------------------------------------
# 4. Calculate Key Sonar DSP Metrics
# -------------------------------------------------------------
time_bandwidth_product = BANDWIDTH * T_P
pulse_compression_gain_db = 10.0 * np.log10(time_bandwidth_product)
raw_range_res_m = (C_SOUND * T_P) / 2.0
compressed_range_res_m = C_SOUND / (2.0 * BANDWIDTH)
res_improvement = raw_range_res_m / compressed_range_res_m

# Find Peak Sidelobe Level (excluding main lobe center)
mainlobe_width_bins = int(FS / BANDWIDTH * 2)
center_idx = N_SAMPLES - 1
sidelobe_region = np.copy(db_tukey)
sidelobe_region[center_idx - mainlobe_width_bins : center_idx + mainlobe_width_bins] = -100.0
pslr_db = np.max(sidelobe_region)

print("=" * 65)
print("🎯 HYDROACOUSTIC RECEIVER: MATCHED-FILTER & PULSE COMPRESSION METRICS")
print("=" * 65)
print(f"• Pulse Duration (T_p)         : {T_P * 1000:.2f} ms ({N_SAMPLES} samples @ {FS/1000:.0f} kHz)")
print(f"• Chirp Bandwidth (B)          : {BANDWIDTH/1000:.1f} kHz ({F0/1000:.1f} kHz -> {F1/1000:.1f} kHz)")
print(f"• Time-Bandwidth Product (TB)  : {time_bandwidth_product:.2f}")
print(f"• Pulse Compression Gain (G)   : +{pulse_compression_gain_db:.2f} dB SNR boost")
print(f"• Uncompressed Range Res (ΔR0) : {raw_range_res_m:.3f} m ({raw_range_res_m*100:.1f} cm)")
print(f"• Compressed Range Res (ΔR)    : {compressed_range_res_m:.4f} m ({compressed_range_res_m*100:.2f} cm)")
print(f"• Range Resolution Improvement : {res_improvement:.1f}x sharper target detection!")
print(f"• Peak Sidelobe Level (PSLR)   : {pslr_db:.2f} dB (Tukey alpha = {alpha})")
print("=" * 65)

# -------------------------------------------------------------
# 5. Plot 4-Panel Verification Figure for Presentation Slide 3/4
# -------------------------------------------------------------
plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(14, 9), dpi=200)
fig.patch.set_facecolor('#050B14')

for ax in axs.flat:
    ax.set_facecolor('#0A1628')
    ax.grid(True, color='#1B355A', linestyle='--', alpha=0.6)

# Panel 1: Time Domain Tukey Waveform
axs[0, 0].plot(t * 1000, chirp_raw, color='#4A6572', linestyle=':', alpha=0.5, label='Raw Rectangular')
axs[0, 0].plot(t * 1000, tukey_win, color='#FFB800', linestyle='--', alpha=0.8, label='Tukey Envelope (a=0.25)')
axs[0, 0].plot(t * 1000, chirp_tukey, color='#00F0FF', linewidth=1.5, label='Windowed LFM Chirp')
axs[0, 0].set_title('1. Synthesized 12-Bit LFM Chirp Waveform', color='#00F0FF', fontsize=11, fontweight='bold')
axs[0, 0].set_xlabel('Time (ms)', color='#8EA4C1')
axs[0, 0].set_ylabel('Normalized Amplitude', color='#8EA4C1')
axs[0, 0].legend(loc='upper right', fontsize=8, facecolor='#050B14', edgecolor='#1B355A')

# Panel 2: Instantaneous Frequency Ramp
inst_freq_khz = (F0 + mu * t) / 1000.0
axs[0, 1].plot(t * 1000, inst_freq_khz, color='#00FFA3', linewidth=2.0)
axs[0, 1].set_title('2. Linear Frequency Ramp (Time-Frequency Spectrogram)', color='#00FFA3', fontsize=11, fontweight='bold')
axs[0, 1].set_xlabel('Time (ms)', color='#8EA4C1')
axs[0, 1].set_ylabel('Instantaneous Frequency (kHz)', color='#8EA4C1')
axs[0, 1].annotate(f'f0 = {F0/1000:.1f} kHz', xy=(0, F0/1000), xytext=(0.5, 4),
                   arrowprops=dict(arrowstyle='->', color='#00FFA3'), color='#00FFA3', fontsize=9)
axs[0, 1].annotate(f'f1 = {F1/1000:.1f} kHz', xy=(T_P*1000, F1/1000), xytext=(T_P*1000 - 1.8, 17),
                   arrowprops=dict(arrowstyle='->', color='#00FFA3'), color='#00FFA3', fontsize=9)

# Panel 3: Matched Filter Sidelobe Suppression (dB)
axs[1, 0].plot(lags_ms, db_raw, color='#FF2E63', linestyle=':', alpha=0.7, label='Rectangular Window (PSLR: -13.2 dB)')
axs[1, 0].plot(lags_ms, db_tukey, color='#00FFA3', linewidth=1.8, label=f'Tukey Window (PSLR: {pslr_db:.1f} dB)')
axs[1, 0].axhline(-13.2, color='#FF2E63', linestyle='--', alpha=0.4)
axs[1, 0].axhline(pslr_db, color='#00FFA3', linestyle='--', alpha=0.4)
axs[1, 0].set_xlim(-T_P * 1000, T_P * 1000)
axs[1, 0].set_ylim(-60, 5)
axs[1, 0].set_title('3. Matched-Filter Pulse Compression (Sidelobe Suppression)', color='#00FFA3', fontsize=11, fontweight='bold')
axs[1, 0].set_xlabel('Time Lag τ (ms)', color='#8EA4C1')
axs[1, 0].set_ylabel('Correlation Output (dB)', color='#8EA4C1')
axs[1, 0].legend(loc='upper right', fontsize=8, facecolor='#050B14', edgecolor='#1B355A')

# Panel 4: Zoomed Mainlobe Peak & Range Resolution
zoom_mask = np.abs(lags_ms) <= 0.4
axs[1, 1].plot(lags_ms[zoom_mask] * 1000, db_tukey[zoom_mask], color='#00F0FF', linewidth=2.0, label='Mainlobe Spike')
axs[1, 1].axvline(0, color='#FFB800', linestyle='--', alpha=0.6)
axs[1, 1].set_title(f'4. Zoomed Echo Peak (Compressed Res: {compressed_range_res_m*100:.2f} cm)', color='#00F0FF', fontsize=11, fontweight='bold')
axs[1, 1].set_xlabel('Lag Error (microseconds µs)', color='#8EA4C1')
axs[1, 1].set_ylabel('Normalized Amplitude (dB)', color='#8EA4C1')
axs[1, 1].annotate(f'Resolution: {compressed_range_res_m*100:.2f} cm\nSNR Gain: +{pulse_compression_gain_db:.1f} dB',
                   xy=(0, 0), xytext=(80, -15),
                   arrowprops=dict(arrowstyle='->', color='#00F0FF'), color='#00F0FF', fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='#050B14', edgecolor='#00F0FF'))

plt.suptitle('AUTONOMOUS SDR SONAR — HYDROACOUSTIC RECEIVER MATCHED FILTER VERIFICATION', 
             color='#FFFFFF', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
docs_dir = os.path.join(script_dir, '../docs')
os.makedirs(docs_dir, exist_ok=True)
output_filename = os.path.join(docs_dir, 'matched_filter_verification.png')
plt.savefig(output_filename, dpi=200, bbox_inches='tight')
print(f"🖼️ Saved verification graph to: '{output_filename}'")
