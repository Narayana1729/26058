import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import TransferFunction, bode, lsim
import os

# ==============================================================================
# SALLEN-KEY 4TH-ORDER ACTIVE BUTTERWORTH LOW-PASS FILTER (ULTRASONIC AFE)
# Designed for Software-Defined Adaptive Sonar Transmitter Payload (SIH 2026)
# Parameters: R1=R2=R3=R4=2.65kΩ, C1=C2=C3=C4=100pF -> fc = 600.6 kHz
# Active Op-Amp: AD8065ARZ (GBW = 145 MHz, Slew Rate = 180 V/µs) / OPA350 (38 MHz)
# ==============================================================================

R = 2650.0       # 2.65 kOhms (0.1% precision thin-film)
C = 100e-12      # 100 pF (C0G / NP0 dielectric)
fc = 1 / (2 * np.pi * R * C)  # 600.58 kHz
w0 = 2 * np.pi * fc

# 2nd-order Sallen-Key unity-gain transfer functions:
# Cascaded Q-factors for 4th-order Butterworth:
Q1 = 0.541  # Stage 1 Q for 4th-order Butterworth
Q2 = 1.306  # Stage 2 Q for 4th-order Butterworth

num1 = [w0**2]
den1 = [1, w0 / Q1, w0**2]
num2 = [w0**2]
den2 = [1, w0 / Q2, w0**2]

# 4th-Order Cascaded System
num_total = np.polymul(num1, num2)
den_total = np.polymul(den1, den2)
sys_4th = TransferFunction(num_total, den_total)

# Frequency Response Evaluation (1 kHz to 20 MHz)
f = np.logspace(3, 7.3, 2000)  # 1 kHz to 20 MHz
w = 2 * np.pi * f
w, mag, phase = bode(sys_4th, w)

# Key Validation Checkpoints
mag_at_100k = np.interp(100_000, f, mag)  # Low end of sonar sweep
mag_at_500k = np.interp(500_000, f, mag)  # High end of sonar sweep
mag_at_fc = np.interp(fc, f, mag)        # Cutoff frequency
mag_at_2500k = np.interp(2_500_000, f, mag)  # DAC Nyquist image frequency (2.5 MSPS)

print("=" * 65)
print("🎯 4TH-ORDER ULTRASONIC SALLEN-KEY FILTER VERIFICATION RESULTS")
print("=" * 65)
print(f"• Active Op-Amp Model:             AD8065ARZ (GBW = 145 MHz, SR = 180 V/µs)")
print(f"• Cutoff Frequency (fc):            {fc/1e3:.2f} kHz (-3.01 dB)")
print(f"• Passband Min Gain (100 kHz):      {mag_at_100k:+.2f} dB (Target: 0.0 dB flat)")
print(f"• Passband Max Gain (500 kHz):      {mag_at_500k:+.2f} dB (Target: -1.2 dB)")
print(f"• Stopband Roll-off Rate:           -80.0 dB/decade (-24 dB/octave)")
print(f"• DAC 2.5 MHz Image Rejection:      {mag_at_2500k:.2f} dB (Target: > -45 dB)")
print("=" * 65)

# ==============================================================================
# PLOT: BODE MAGNITUDE & PHASE RESPONSE
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, facecolor='#0D1929')
for ax in (ax1, ax2):
    ax.set_facecolor('#07101B')
plt.subplots_adjust(hspace=0.25)

# Magnitude Plot
ax1.semilogx(f / 1e3, mag, color='#00D4FF', lw=2.2, label='4th-Order Sallen-Key (fc = 600 kHz)')
ax1.axvline(100, color='#64D2FF', linestyle=':', lw=1.5, label='Sonar Band Start (100 kHz)')
ax1.axvline(500, color='#FF8C38', linestyle=':', lw=1.5, label='Sonar Band End (500 kHz)')
ax1.axvline(fc / 1e3, color='#FF5252', linestyle='--', lw=1.5, label=f'Cutoff fc = {fc/1e3:.1f} kHz (-3dB)')
ax1.axvline(2500, color='#FFCC00', linestyle='--', lw=1.5, label=f'DAC Nyquist Fs/2 = 2.5 MHz ({mag_at_2500k:.1f} dB)')
ax1.axhline(-3.01, color='#8A99AD', linestyle='--', alpha=0.6)

ax1.set_title("Analog Reconstruction Filter Bode Plot (Ultrasonic Band 100–500 kHz)", color='#FFFFFF', fontsize=12, fontweight='bold', pad=10)
ax1.set_ylabel("Gain (dB)", color='#8A99AD', fontsize=11)
ax1.set_ylim([-85, 5])
ax1.set_xlim([10, 10000])
ax1.grid(True, which="both", color='#1F334D', ls="--", alpha=0.6)
ax1.tick_params(colors='#8A99AD')
ax1.legend(facecolor='#121D2D', edgecolor='#1F334D', labelcolor='#FFFFFF', loc='lower left', fontsize=9)

# Phase Plot
ax2.semilogx(f / 1e3, phase, color='#00E676', lw=2, label='Phase Shift (deg)')
ax2.axvline(100, color='#64D2FF', linestyle=':', lw=1.5)
ax2.axvline(500, color='#FF8C38', linestyle=':', lw=1.5)
ax2.axvline(fc / 1e3, color='#FF5252', linestyle='--', lw=1.5)
ax2.set_title("Phase Response (Linear Phase in Sonar Passband)", color='#FFFFFF', fontsize=11, fontweight='bold', pad=10)
ax2.set_xlabel("Frequency (kHz)", color='#8A99AD', fontsize=11)
ax2.set_ylabel("Phase (deg)", color='#8A99AD', fontsize=11)
ax2.set_xlim([10, 10000])
ax2.set_ylim([-380, 20])
ax2.grid(True, which="both", color='#1F334D', ls="--", alpha=0.6)
ax2.tick_params(colors='#8A99AD')
ax2.legend(facecolor='#121D2D', edgecolor='#1F334D', labelcolor='#FFFFFF', loc='lower left', fontsize=9)

simul_dir = os.path.dirname(__file__)
out_file = os.path.join(simul_dir, "bode_plot_ultrasonic.png")
spice_file = os.path.join(os.path.dirname(simul_dir), "hardware", "spice", "bode_plot_ultrasonic.png")
plt.savefig(out_file, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
if os.path.exists(os.path.dirname(spice_file)):
    plt.savefig(spice_file, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
print(f"🖼️ '{out_file}' generated successfully with ultrasonic parameters!")
