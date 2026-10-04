"""
Experiment 3 — Closed-Loop Controller State Machine Trace
==========================================================
Synthetic ping sequence with SNR measurements.
Show: mode selection driven by previous ping SNR, with dwell hysteresis.

Deliverable: docs/exp03_closed_loop.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Controller parameters (must match adaptation_controller.h)
SNR_LOW    =  8.0   # dB
SNR_HIGH   = 22.0   # dB
DWELL_N    =  3     # minimum pings at same mode before re-evaluating

# Mode labels and colours (0=highest freq, 3=lowest)
MODE_LABELS = ["Mode 0\n450kHz\nHigh Res",
               "Mode 1\n250kHz\nBalanced",
               "Mode 2\n100kHz\nDeep Pen",
               "Mode 3\n250kHz\nHFM"]
MODE_COLORS = ["#00F0FF", "#00FFA3", "#FFB800", "#FF2E63"]

# Lookup table — safe mode transitions (matches acoustic_profiles.h)
LOWER_FREQ  = [1, 2, 3, 3]
HIGHER_FREQ = [0, 0, 1, 1]

def select_next(mode, snr_db, dwell_count):
    """SNR threshold controller with dwell hysteresis."""
    if dwell_count < DWELL_N:
        return mode, dwell_count + 1, "DWELL"
    if snr_db < SNR_LOW:
        new = LOWER_FREQ[mode]
        return new, 0, f"SNR<{SNR_LOW:.0f}→lower"
    if snr_db > SNR_HIGH:
        new = HIGHER_FREQ[mode]
        return new, 0, f"SNR>{SNR_HIGH:.0f}→higher"
    return mode, dwell_count + 1, "HOLD"

# --- Synthetic SNR sequence (replicate with real measurements later) ---
synthetic_snrs = [6.0, 7.5, 9.0, 11.0, 4.5, 5.5, 3.0, 24.0, 26.0, 25.0,
                  28.0, 14.0, 12.0, 8.5, 6.0, 5.0, 21.0, 23.0, 19.0, 12.0]

modes   = []
reasons = []
snrs    = synthetic_snrs[:]
mode    = 0   # start at highest frequency
dwell   = 0

for snr in snrs:
    modes.append(mode)
    mode, dwell, reason = select_next(mode, snr, dwell)
    reasons.append(reason)

n_pings = len(snrs)
ping_idx = np.arange(1, n_pings + 1)

plt.style.use('dark_background')
fig, axs = plt.subplots(3, 1, figsize=(15, 11), dpi=180, sharex=True)
fig.patch.set_facecolor('#020B18')
for ax in axs:
    ax.set_facecolor('#071526')
    ax.grid(True, color='#152840', linestyle='--', alpha=0.5, axis='x')

# --- Panel 1: SNR per ping ---
ax = axs[0]
ax.bar(ping_idx, snrs, color=[MODE_COLORS[m] for m in modes], alpha=0.8, width=0.7)
ax.axhline(SNR_LOW,  color='#FF2E63', ls='--', lw=1.5, label=f'Low threshold {SNR_LOW:.0f} dB → lower freq')
ax.axhline(SNR_HIGH, color='#00FFA3', ls='--', lw=1.5, label=f'High threshold {SNR_HIGH:.0f} dB → higher freq')
ax.set_ylabel('Ping SNR [dB]', color='#8EA4C1')
ax.set_title('Experiment 3 — Closed-Loop Waveform Adaptation: SNR per Ping', color='#00F0FF', fontsize=12, fontweight='bold')
ax.legend(fontsize=8.5, facecolor='#020B18', edgecolor='#152840')
ax.set_ylim(0, max(snrs)*1.2)

# --- Panel 2: Mode per ping ---
ax = axs[1]
for i, (m, snr) in enumerate(zip(modes, snrs)):
    ax.bar(ping_idx[i], 3-m, bottom=0, color=MODE_COLORS[m], alpha=0.85, width=0.7)
ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels(["Mode 3\n(Low f)", "Mode 2", "Mode 1", "Mode 0\n(High f)"], color='#AAAAAA', fontsize=8)
ax.set_ylabel('Selected Mode', color='#8EA4C1')
ax.set_title('Active Operating Mode per Ping', color='#FFB800', fontsize=11, fontweight='bold')
legend_patches = [mpatches.Patch(color=c, label=l.replace('\n', ' '))
                  for l, c in zip(MODE_LABELS, MODE_COLORS)]
ax.legend(handles=legend_patches, fontsize=8, facecolor='#020B18', edgecolor='#152840', loc='upper right')

# Annotate mode transitions
prev = modes[0]
for i, m in enumerate(modes[1:], 1):
    if m != prev:
        ax.axvline(ping_idx[i], color='white', ls=':', alpha=0.5, lw=1.2)
    prev = m

# --- Panel 3: Decision trace ---
ax = axs[2]
ax.barh(np.zeros(n_pings), np.ones(n_pings), left=ping_idx-0.5,
        color=[MODE_COLORS[m] for m in modes], alpha=0.5, height=0.7)
for i, (reason, snr, m) in enumerate(zip(reasons, snrs, modes)):
    ax.text(ping_idx[i], 0, f"{reason}\nSNR={snr:.1f}dB",
            ha='center', va='center', fontsize=6.5, color='white', wrap=True)
ax.set_yticks([])
ax.set_ylim(-0.5, 0.5)
ax.set_xlabel('Ping Number', color='#8EA4C1')
ax.set_title('Controller Decision per Ping\n(replace synthetic SNR with real measurements)', color='#00FFA3', fontsize=11, fontweight='bold')
ax.set_xticks(ping_idx)

plt.suptitle(f'EXPERIMENT 3 — Closed-Loop Controller  |  Dwell={DWELL_N} pings  '
             f'|  Low={SNR_LOW:.0f}dB  High={SNR_HIGH:.0f}dB\n'
             'SYNTHETIC DATA — replace with measured ping SNRs after hardware test',
             color='white', fontsize=11, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])
out = os.path.join(os.path.dirname(__file__), '../../../docs/exp03_closed_loop.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='#020B18')
print(f"EXP03 saved: {os.path.abspath(out)}")
