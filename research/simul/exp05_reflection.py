"""
Experiment 5 — Acoustic Reflection Model Validation
====================================================
Theoretical BL vs synthetic echo BL.
Measure E_BL = BL_measured - BL_model for each reference material.

Phase 1 (now):   model → synthetic echo → estimated BL → compare to theory
Phase 2 (later): real transducer → real echo → estimated BL → compare

Do NOT promise ±2 dB. Quantify the error; let the data speak.

Deliverable: docs/exp05_reflection.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Simul", "python"))
import numpy as np
import matplotlib.pyplot as plt
from acoustic_model import alpha_dB_per_m, sound_speed_mackenzie, DEFAULT_ENV
from seabed_model   import (theoretical_bl_table, classify_nearest_reference,
                             SEABED_DISCLAIMER, WATER_REF)

ENV = DEFAULT_ENV
c   = sound_speed_mackenzie(ENV["temperature_C"], ENV["salinity_ppt"], ENV["depth_m"])
FS  = 100_000.0; N = 512; T_p = N / FS
FC  = 250_000.0  # carrier for this experiment
alpha = alpha_dB_per_m(FC, **ENV)

# Reference table
ref_table = theoretical_bl_table()
material_names = list(ref_table.keys())

# --- Synthetic echo model ---
# Synthesise an echo: attenuate a reference pulse by Rp and by propagation loss
# then run "BL estimation" to recover BL and compare to theory.
R_TEST = 2.0   # m — test range

def synthesise_echo(Rp_true, noise_std=0.01):
    """
    Synthesise a received echo for a target at R_TEST with reflection coeff Rp_true.
    Returns (tx_amplitude, echo_amplitude) with additive Gaussian noise.
    """
    TL = 40*np.log10(max(R_TEST, 0.05)) + 2*alpha*R_TEST
    echo_amp = abs(Rp_true) * 10**(-TL/20.0)   # linear scale
    echo_amp += np.random.randn() * noise_std
    tx_amp = 1.0
    return tx_amp, max(echo_amp, 1e-9)

def estimate_bl_from_echo(tx_amp, echo_amp, R, alpha_one_way):
    """
    Estimate bottom loss from measured echo amplitude after propagation correction.
    BL_estimated = -20*log10(echo_amp/tx_amp) - TL_2way
    => reflects only the interface reflection loss.
    """
    raw_loss = -20*np.log10(echo_amp / tx_amp)   # total measured loss [dB]
    TL = 40*np.log10(max(R, 0.05)) + 2*alpha_one_way*R
    BL_est = raw_loss - TL
    return BL_est

# Run synthetic experiment
np.random.seed(42)
N_TRIALS = 50   # repeated measurements to estimate variability

theory_bl  = []
est_bl_mean = []
est_bl_std  = []

for name in material_names:
    ref = ref_table[name]
    bl_theory = ref.BL_dB
    theory_bl.append(bl_theory)
    trials = []
    for _ in range(N_TRIALS):
        tx, echo = synthesise_echo(ref.Rp, noise_std=0.005)
        bl_est = estimate_bl_from_echo(tx, echo, R_TEST, alpha)
        trials.append(bl_est)
    est_bl_mean.append(np.mean(trials))
    est_bl_std.append(np.std(trials))

errors = [m - t for m, t in zip(est_bl_mean, theory_bl)]

plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=180)
fig.patch.set_facecolor('#020B18')
for ax in axs.flat:
    ax.set_facecolor('#071526')
    ax.grid(True, color='#152840', linestyle='--', alpha=0.5)

COLORS = ["#1A6B8A", "#12A074", "#D4A017", "#C0392B", "#8E44AD"]

# Panel A: Theory vs Estimated BL
ax = axs[0, 0]
x = np.arange(len(material_names))
ax.bar(x - 0.2, theory_bl,   0.35, color='#00F0FF', alpha=0.85, label='BL_theoretical [dB]')
ax.bar(x + 0.2, est_bl_mean, 0.35, color='#FFB800', alpha=0.85, label=f'BL_estimated (n={N_TRIALS})')
ax.errorbar(x + 0.2, est_bl_mean, yerr=est_bl_std, fmt='none', color='white', capsize=4, lw=1.5)
ax.set_xticks(x)
ax.set_xticklabels(material_names, rotation=20, fontsize=8.5, color='#AAAAAA')
ax.set_title(f'A. Theoretical vs Estimated BL at R={R_TEST}m\n(synthetic echo, noise_std=0.005)',
             color='#00F0FF', fontsize=11, fontweight='bold')
ax.set_ylabel('Bottom Loss [dB]', color='#8EA4C1')
ax.legend(fontsize=8.5, facecolor='#020B18', edgecolor='#152840')

# Panel B: Error E_BL
ax = axs[0, 1]
bar_colors = ['#00FFA3' if abs(e) < 1.0 else '#FFB800' if abs(e) < 3.0 else '#FF2E63' for e in errors]
ax.bar(x, errors, color=bar_colors, alpha=0.85)
ax.errorbar(x, errors, yerr=est_bl_std, fmt='none', color='white', capsize=4, lw=1.5)
ax.axhline(0,    color='white',   ls='--', lw=1.2)
ax.axhline(+2.0, color='#FFB800', ls=':',  lw=1.0, label='±2 dB target (verify with real data)')
ax.axhline(-2.0, color='#FFB800', ls=':',  lw=1.0)
ax.set_xticks(x)
ax.set_xticklabels(material_names, rotation=20, fontsize=8.5, color='#AAAAAA')
ax.set_title('B. Error: E_BL = BL_estimated − BL_theoretical\n(quantify, do not promise ±2 dB without hardware test)',
             color='#FFB800', fontsize=11, fontweight='bold')
ax.set_ylabel('BL Error [dB]', color='#8EA4C1')
ax.legend(fontsize=8, facecolor='#020B18', edgecolor='#152840')

# Panel C: Classification result
ax = axs[1, 0]
correct = 0
rows = []
for i, (name, bl_est) in enumerate(zip(material_names, est_bl_mean)):
    result = classify_nearest_reference(bl_est)
    is_correct = result.candidate_name == name
    if is_correct: correct += 1
    rows.append([name,
                 f"{theory_bl[i]:.1f}",
                 f"{bl_est:.1f}±{est_bl_std[i]:.2f}",
                 result.candidate_name,
                 "✓" if is_correct else "✗"])
    color = '#00FFA3' if is_correct else '#FF2E63'
    ax.barh(i, 1, color=color, alpha=0.3)
    ax.text(0.5, i, f"{name}  →  {result.candidate_name}", ha='center', va='center',
            color=color, fontsize=9)
ax.set_xlim(0, 1); ax.set_yticks([]); ax.set_xticks([])
ax.set_title(f'C. Nearest-Reference Classification Result\n({correct}/{len(material_names)} correct in simulation)',
             color='#00FFA3', fontsize=11, fontweight='bold')
ax.annotate(SEABED_DISCLAIMER[:80] + '...', xy=(0.01, -0.15), xycoords='axes fraction',
            color='#888888', fontsize=6.5, wrap=True)

# Panel D: Full results table
ax = axs[1, 1]
ax.axis('off')
header = ['Material', 'BL_theory', 'BL_estimated', 'Classified as', 'Correct?']
tbl = ax.table(cellText=rows, colLabels=header, cellLoc='center', loc='center',
               bbox=[0.0, 0.1, 1.0, 0.85])
tbl.auto_set_font_size(False); tbl.set_fontsize(8)
for (r,c_), cell in tbl.get_celld().items():
    cell.set_facecolor('#071526' if r > 0 else '#152840')
    cell.set_edgecolor('#152840')
    cell.set_text_props(color='white')
ax.set_title('D. Full Simulation Results\n(Phase 2: replace with real echo measurements)', color='#FF2E63', fontsize=10, fontweight='bold')

plt.suptitle('EXPERIMENT 5 — Acoustic Reflection Model: Theoretical vs Estimated BL\n'
             'PHASE 1 (SIMULATION) — measure real echoes in Phase 2 to validate error bounds',
             color='white', fontsize=12, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])
out = os.path.join(os.path.dirname(__file__), '../docs/exp05_reflection.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='#020B18')
print(f"EXP05 saved: {os.path.abspath(out)}")
