"""
Experiment 1 — Physics-Derived TGC vs Linear TGC
=================================================
Compare gain vs range, corrected dynamic range, saturation point.

Deliverable: docs/exp01_tgc.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sys, os
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Simul", "python"))
from acoustic_model import alpha_dB_per_m, sound_speed_mackenzie, DEFAULT_ENV
from tgc_generator  import generate_tgc_db, MIN_TGC_DB, MAX_TGC_DB

ENV = DEFAULT_ENV
c   = sound_speed_mackenzie(ENV["temperature_C"], ENV["salinity_ppt"], ENV["depth_m"])
N   = 512; FS = 100_000.0
MODES = [
    {"id": 0, "name": "450 kHz (High Res)", "f": 450_000, "color": "#00F0FF"},
    {"id": 1, "name": "250 kHz (Balanced)", "f": 250_000, "color": "#00FFA3"},
    {"id": 2, "name": "100 kHz (Deep Pen)", "f": 100_000, "color": "#FFB800"},
]

plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=180)
fig.patch.set_facecolor('#020B18')
for ax in axs.flat:
    ax.set_facecolor('#071526')
    ax.grid(True, color='#152840', linestyle='--', alpha=0.5)

# --- Panel 1: Gain vs Range ---
ax = axs[0, 0]
sample_idx = np.arange(1, N+1)
ranges_m = c * (sample_idx / FS) / 2.0
linear_gain = np.linspace(MIN_TGC_DB, MAX_TGC_DB, N)
ax.plot(ranges_m, linear_gain, color='#FF2E63', lw=2, ls='--', label='Linear (empirical) ramp')

for m in MODES:
    R, theory, clipped = generate_tgc_db(lambda f: alpha_dB_per_m(f, **ENV), m["f"], N, FS, c)
    ax.plot(R, clipped, color=m["color"], lw=1.8, label=f"Physics TGC — {m['name']}")
    ax.plot(R, theory, color=m["color"], lw=0.8, ls=':', alpha=0.4)

ax.axhline(MAX_TGC_DB, color='#FF2E63', ls=':', alpha=0.5, label=f'AFE limit = {MAX_TGC_DB:.0f} dB (AD8331 VGA max)')
ax.set_title('1A. TGC Gain Profile: Physics vs Linear', color='#00F0FF', fontsize=11, fontweight='bold')
ax.set_xlabel('One-Way Range R [m]', color='#8EA4C1')
ax.set_ylabel('Gain Compensation [dB]', color='#8EA4C1')
ax.legend(fontsize=7.5, facecolor='#020B18', edgecolor='#152840')
ax.annotate('Dotted = theoretical TL\nSolid = hardware-clipped gain',
            xy=(ranges_m[-1]*0.5, MAX_TGC_DB*0.5), color='#AAAAAA', fontsize=8,
            bbox=dict(boxstyle='round', fc='#020B18', ec='#333'))

# --- Panel 2: Divergence at high frequency ---
ax = axs[0, 1]
for m in MODES:
    R, theory, clipped = generate_tgc_db(lambda f: alpha_dB_per_m(f, **ENV), m["f"], N, FS, c)
    alpha_val = alpha_dB_per_m(m["f"], **ENV)
    ax.plot(R, theory - clipped, color=m["color"], lw=1.8,
            label=f"{m['name']}  α={alpha_val*1e3:.1f}dB/km")
ax.set_title('1B. Clipping Loss: Theory − Hardware Ramp\n(energy that cannot be recovered)', color='#FFB800', fontsize=11, fontweight='bold')
ax.set_xlabel('One-Way Range R [m]', color='#8EA4C1')
ax.set_ylabel('Unrecoverable TL [dB]', color='#8EA4C1')
ax.legend(fontsize=8, facecolor='#020B18', edgecolor='#152840')

# --- Panel 3: Corrected echo amplitude (simulated target at constant reflectivity) ---
ax = axs[1, 0]
TARGET_STRENGTH = 0.0   # dB, unit reflector
SL = 160.0              # dB re 1 µPa @ 1m (source level — arbitrary for comparison)
NL = 60.0               # dB ambient noise level
R_test = np.linspace(0.1, ranges_m[-1], 500)

for m in MODES:
    alpha_val = alpha_dB_per_m(m["f"], **ENV)
    TL = 40*np.log10(np.maximum(R_test, 0.05)) + 2*alpha_val*R_test
    echo_amplitude = SL + TARGET_STRENGTH - TL
    # With physics TGC (corrects up to MAX_TGC_DB):
    tgc_applied = np.minimum(TL, MAX_TGC_DB)
    echo_corrected = echo_amplitude + tgc_applied
    # With linear TGC:
    linear = np.linspace(MIN_TGC_DB, MAX_TGC_DB, len(R_test))
    echo_linear = echo_amplitude + linear
    ax.plot(R_test, echo_corrected, color=m["color"], lw=1.8, label=f"Physics TGC — {m['name']}")
    ax.plot(R_test, echo_linear,   color=m["color"], lw=1.0, ls='--', alpha=0.5)

ax.set_title('1C. Corrected Echo Amplitude vs Range\n(solid=physics TGC, dashed=linear TGC)', color='#00FFA3', fontsize=11, fontweight='bold')
ax.set_xlabel('One-Way Range R [m]', color='#8EA4C1')
ax.set_ylabel('Corrected Echo [dB re µPa]', color='#8EA4C1')
ax.legend(fontsize=7.5, facecolor='#020B18', edgecolor='#152840')

# --- Panel 4: Dynamic range improvement table ---
ax = axs[1, 1]
ax.axis('off')
rows = [['Mode', 'α [dB/km]', 'TL@max_R [dB]', 'Clipped at [dB]', 'Unrecov. loss']]
for m in MODES:
    R, theory, clipped = generate_tgc_db(lambda f: alpha_dB_per_m(f, **ENV), m["f"], N, FS, c)
    alpha_val = alpha_dB_per_m(m["f"], **ENV)
    rows.append([m['name'],
                 f"{alpha_val*1e3:.1f}",
                 f"{theory[-1]:.1f}",
                 f"{MAX_TGC_DB:.0f}",
                 f"{max(0, theory[-1]-MAX_TGC_DB):.1f}"])

tbl = ax.table(cellText=rows[1:], colLabels=rows[0], cellLoc='center', loc='center',
               bbox=[0.0, 0.2, 1.0, 0.7])
tbl.auto_set_font_size(False); tbl.set_fontsize(9)
for (r,c_), cell in tbl.get_celld().items():
    cell.set_facecolor('#071526' if r > 0 else '#152840')
    cell.set_edgecolor('#152840')
    cell.set_text_props(color='white')
ax.set_title('1D. TGC Coverage Summary\n(replace MAX_TGC_DB with measured AFE limit)', color='#FF2E63', fontsize=11, fontweight='bold')

plt.suptitle('EXPERIMENT 1 — Physics-Derived TGC vs Linear Empirical Ramp\n'
             f'TL = 40·log₁₀(R) + 2α(f)·R  |  Env: T={ENV["temperature_C"]}°C S={ENV["salinity_ppt"]}ppt',
             color='white', fontsize=12, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])

out = os.path.join(os.path.dirname(__file__), '../docs/exp01_tgc.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='#020B18')
print(f"EXP01 saved: {os.path.abspath(out)}")
