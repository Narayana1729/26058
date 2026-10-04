"""
Experiment 2 — Frequency Selection: TL(R,f) and Predicted SNR
=============================================================
Compute TL vs range at several ranges for candidate frequencies.
Compute SNR_pred = SL - TL(f,R) - NL + PG where PG=10*log10(TBW).
Identify predicted best frequency at each range.

Deliverable: docs/exp02_frequency.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from acoustic_model import alpha_dB_per_m, sound_speed_mackenzie, DEFAULT_ENV

ENV = DEFAULT_ENV
c   = sound_speed_mackenzie(ENV["temperature_C"], ENV["salinity_ppt"], ENV["depth_m"])

# Candidate frequencies matching Mode 0-2
FREQS = {
    "100 kHz (Mode 2)": 100_000,
    "250 kHz (Mode 1)": 250_000,
    "450 kHz (Mode 0)": 450_000,
}
COLORS = ["#FFB800", "#00FFA3", "#00F0FF"]

# Sonar equation reference parameters (Standard Acoustic Baseline, Urick 1983)
SL   = 160.0   # dB re 1µPa @ 1m — nominal source level
NL   = 55.0    # dB re 1µPa — ambient noise level (Sea State 2, Wenz curve)
TS   = -20.0   # dB — reference target strength (canonical planar target)
B    = 19_000  # Hz — bandwidth (Mode 1 baseband)
T_p  = 0.00512 # s  — pulse duration
PG   = 10 * np.log10(B * T_p)  # pulse compression gain [dB]

R_eval  = np.logspace(np.log10(0.1), np.log10(50.0), 400)  # 0.1 to 50 m

plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=180)
fig.patch.set_facecolor('#020B18')
for ax in axs.flat:
    ax.set_facecolor('#071526')
    ax.grid(True, color='#152840', linestyle='--', alpha=0.5)

# --- Panel 1: TL vs Range for each frequency ---
ax = axs[0, 0]
for (name, f_hz), col in zip(FREQS.items(), COLORS):
    alpha = alpha_dB_per_m(f_hz, **ENV)
    TL = 40*np.log10(np.maximum(R_eval, 0.05)) + 2*alpha*R_eval
    ax.plot(R_eval, TL, color=col, lw=2.0, label=f"{name}  α={alpha*1e3:.1f}dB/km")
ax.set_xscale('log')
ax.set_title('2A. Two-Way Propagation Loss TL(R,f)\n= 40·log₁₀(R) + 2α(f)·R', color='#00F0FF', fontsize=11, fontweight='bold')
ax.set_xlabel('Range R [m]', color='#8EA4C1')
ax.set_ylabel('TL [dB]', color='#8EA4C1')
ax.legend(fontsize=8, facecolor='#020B18', edgecolor='#152840')
ax.annotate('Higher freq → faster divergence\n→ use lower freq at longer range',
            xy=(5, 50), color='#AAAAAA', fontsize=8.5,
            bbox=dict(boxstyle='round', fc='#020B18', ec='#333'))

# --- Panel 2: Alpha(f) frequency sweep ---
ax = axs[0, 1]
f_sweep = np.logspace(3, 6.5, 500)
alpha_sweep = np.array([alpha_dB_per_m(f, **ENV)*1e3 for f in f_sweep])
ax.loglog(f_sweep/1e3, alpha_sweep, color='white', lw=2.0)
for (name, f_hz), col in zip(FREQS.items(), COLORS):
    a = alpha_dB_per_m(f_hz, **ENV)*1e3
    ax.axvline(f_hz/1e3, color=col, ls='--', alpha=0.7)
    ax.scatter([f_hz/1e3], [a], color=col, s=80, zorder=5)
    ax.annotate(f"{name}\n{a:.2f} dB/km",
                xy=(f_hz/1e3, a), xytext=(f_hz/1e3*1.3, a*2.0),
                color=col, fontsize=7.5,
                arrowprops=dict(arrowstyle='->', color=col, lw=0.8),
                bbox=dict(boxstyle='round,pad=0.2', fc='#020B18', ec=col, alpha=0.8))
ax.set_title('2B. Francois-Garrison α(f) — One-Way\nT=20°C S=35ppt pH=8.0 D=10m', color='#00FFA3', fontsize=11, fontweight='bold')
ax.set_xlabel('Frequency [kHz]', color='#8EA4C1')
ax.set_ylabel('α [dB/km]', color='#8EA4C1')

# --- Panel 3: SNR_pred vs Range ---
ax = axs[1, 0]
best_f_at_R = []
for (name, f_hz), col in zip(FREQS.items(), COLORS):
    alpha = alpha_dB_per_m(f_hz, **ENV)
    TL = 40*np.log10(np.maximum(R_eval, 0.05)) + 2*alpha*R_eval
    SNR = SL + TS - TL - NL + PG
    ax.plot(R_eval, SNR, color=col, lw=2.0, label=f"{name}")
ax.axhline(0, color='#FF2E63', ls='--', alpha=0.7, label='0 dB detection threshold')
ax.axhline(8, color='#FFB800', ls=':', alpha=0.6, label='8 dB reliable threshold')
ax.set_xscale('log')
ax.set_title(f'2C. Predicted SNR vs Range\nSNR = SL({SL:.0f}) + TS({TS:.0f}) − TL − NL({NL:.0f}) + PG({PG:.1f}dB)',
             color='#FFB800', fontsize=11, fontweight='bold')
ax.set_xlabel('Range R [m]', color='#8EA4C1')
ax.set_ylabel('Predicted SNR [dB]', color='#8EA4C1')
ax.set_ylim(-40, 80)
ax.legend(fontsize=8, facecolor='#020B18', edgecolor='#152840')
ax.annotate(f'PG = 10·log₁₀(B·Tp)\n= 10·log₁₀({B/1e3:.0f}k × {T_p*1000:.1f}ms)\n= {PG:.1f} dB',
            xy=(0.15, NL-SL-TS+5), color='#AAAAAA', fontsize=8,
            bbox=dict(boxstyle='round', fc='#020B18', ec='#333'))

# --- Panel 4: Best frequency at each range ---
ax = axs[1, 1]
snr_matrix = []
f_list = list(FREQS.values())
for f_hz in f_list:
    alpha = alpha_dB_per_m(f_hz, **ENV)
    TL = 40*np.log10(np.maximum(R_eval, 0.05)) + 2*alpha*R_eval
    snr_matrix.append(SL + TS - TL - NL + PG)
snr_matrix = np.array(snr_matrix)
best_mode = np.argmax(snr_matrix, axis=0)
f_names = list(FREQS.keys())
for i, (name, col) in enumerate(zip(f_names, COLORS)):
    mask = best_mode == i
    ax.fill_between(R_eval, 0, 1, where=mask, color=col, alpha=0.35, label=f"Best: {name}")
for i, (name, col) in enumerate(zip(f_names, COLORS)):
    ax.plot(R_eval, snr_matrix[i], color=col, lw=1.5)
ax.set_xscale('log')
ax.set_ylim(0, 1)
ax.set_yticks([])
ax.set_title('2D. Predicted Best Frequency by Range\n(argmax SNR_pred)', color='white', fontsize=11, fontweight='bold')
ax.set_xlabel('Range R [m]', color='#8EA4C1')
ax.legend(fontsize=8, facecolor='#020B18', edgecolor='#152840', loc='upper right')
ax.annotate('Acoustic Reference Baseline\nUrick (1983) Parameters\nSL=160dB, NL=55dB, TS=-20dB',
            xy=(0.98, 0.5), xycoords='axes fraction', ha='right', color='#00F0FF', fontsize=8.5,
            bbox=dict(boxstyle='round', fc='#020B18', ec='#00F0FF', alpha=0.85))

plt.suptitle('EXPERIMENT 2 — Frequency Selection: TL(R,f) and Predicted SNR\n'
             f'Env defaults: T={ENV["temperature_C"]}°C S={ENV["salinity_ppt"]}ppt pH={ENV["pH"]} D={ENV["depth_m"]}m',
             color='white', fontsize=12, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])
out = os.path.join(os.path.dirname(__file__), '../../../docs/exp02_frequency.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='#020B18')
print(f"EXP02 saved: {os.path.abspath(out)}")
