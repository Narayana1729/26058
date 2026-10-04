"""
Experiment 4 — HFM vs LFM Doppler Tolerance
============================================
Simulate matched-filter output for LFM and HFM waveforms at several
radial velocities. Report range error and SNR degradation.

NOTE: This is a SIMULATION. Real measurement will replace these plots.
Do NOT claim a specific dB improvement until hardware is measured.

Deliverable: docs/exp04_hfm_lfm.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import matplotlib.pyplot as plt

FS   = 100_000.0   # Hz
N    = 512
T_p  = N / FS      # 5.12 ms
F0   = 1_000.0     # Hz start
F1   = 20_000.0    # Hz end
B    = F1 - F0     # bandwidth
C    = 1500.0       # sound speed m/s
FC   = 250_000.0   # carrier frequency (for Doppler shift)

t = np.linspace(0, T_p, N, endpoint=False)

# Velocities to test
velocities = [0.0, 0.5, 1.0, 2.0, 2.5]   # m/s

def lfm_chirp(t_arr, f0, f1, T):
    mu = (f1 - f0) / T
    return np.sin(2*np.pi*(f0*t_arr + 0.5*mu*t_arr**2))

def hfm_chirp(t_arr, f0, f1, T):
    """Hyperbolic FM: instantaneous freq = f0*f1*T / (f1*T - (f1-f0)*t)"""
    k = f0 * f1 * T / (f1 - f0)
    phase = 2*np.pi * k * np.log(1.0 - (f1-f0)*t_arr/(f1*T))
    # avoid log(0)
    valid = (1.0 - (f1-f0)*t_arr/(f1*T)) > 0
    sig = np.zeros_like(t_arr)
    sig[valid] = np.sin(phase[valid])
    return sig

def doppler_shift_signal(sig, v_radial, Fs, c):
    """Apply Doppler by resampling (velocity stretch)."""
    alpha = 1.0 + 2*v_radial/c
    n_orig = len(sig)
    t_orig = np.arange(n_orig) / Fs
    t_stretch = np.arange(n_orig) / (Fs * alpha)
    t_stretch = np.clip(t_stretch, t_orig[0], t_orig[-1])
    return np.interp(t_stretch, t_orig, sig)

def peak_snr_and_range_error(ref, echo):
    corr = np.correlate(echo, ref, mode='full')
    peak_idx = np.argmax(np.abs(corr))
    peak_val = np.max(np.abs(corr))
    noise_rms = np.std(corr) + 1e-12
    snr = 20*np.log10(peak_val / noise_rms)
    lag = peak_idx - (len(ref) - 1)
    range_err_m = lag / FS * C / 2.0
    return snr, range_err_m, corr

# Reference waveforms
lfm_ref = lfm_chirp(t, F0, F1, T_p)
hfm_ref = hfm_chirp(t, F0, F1, T_p)

results = {"lfm": {"snr": [], "range_err": []},
           "hfm": {"snr": [], "range_err": []}}

for v in velocities:
    lfm_echo = doppler_shift_signal(lfm_ref, v, FS, C)
    hfm_echo = doppler_shift_signal(hfm_ref, v, FS, C)
    snr_l, re_l, _ = peak_snr_and_range_error(lfm_ref, lfm_echo)
    snr_h, re_h, _ = peak_snr_and_range_error(hfm_ref, hfm_echo)
    results["lfm"]["snr"].append(snr_l)
    results["lfm"]["range_err"].append(re_l)
    results["hfm"]["snr"].append(snr_h)
    results["hfm"]["range_err"].append(re_h)

# Normalise SNR to v=0 reference
snr0_l = results["lfm"]["snr"][0]
snr0_h = results["hfm"]["snr"][0]
snr_deg_lfm = np.array(results["lfm"]["snr"]) - snr0_l
snr_deg_hfm = np.array(results["hfm"]["snr"]) - snr0_h

plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=180)
fig.patch.set_facecolor('#020B18')
for ax in axs.flat:
    ax.set_facecolor('#071526')
    ax.grid(True, color='#152840', linestyle='--', alpha=0.5)

# Panel A: SNR degradation vs velocity
ax = axs[0, 0]
ax.plot(velocities, snr_deg_lfm, color='#FF2E63', lw=2.5, marker='o', ms=8, label='LFM SNR degradation')
ax.plot(velocities, snr_deg_hfm, color='#00FFA3', lw=2.5, marker='s', ms=8, label='HFM SNR degradation')
ax.set_title('A. Matched-Filter SNR Degradation vs Radial Velocity', color='#00F0FF', fontsize=11, fontweight='bold')
ax.set_xlabel('Radial Velocity v [m/s]', color='#8EA4C1')
ax.set_ylabel('SNR Degradation [dB] (0=no loss)', color='#8EA4C1')
ax.legend(fontsize=9, facecolor='#020B18', edgecolor='#152840')
# Annotate difference at max velocity
diff = snr_deg_hfm[-1] - snr_deg_lfm[-1]
ax.annotate(f'Δ = {diff:.1f} dB at v={velocities[-1]}m/s\n(simulation — measure to confirm)',
            xy=(velocities[-1], snr_deg_hfm[-1]), xytext=(velocities[-1]-1.5, snr_deg_hfm[-1]-4),
            color='#FFB800', fontsize=8.5,
            arrowprops=dict(arrowstyle='->', color='#FFB800'),
            bbox=dict(boxstyle='round', fc='#020B18', ec='#FFB800'))

# Panel B: Range error vs velocity
ax = axs[0, 1]
ax.plot(velocities, [r*100 for r in results["lfm"]["range_err"]], color='#FF2E63', lw=2.5, marker='o', ms=8, label='LFM range error')
ax.plot(velocities, [r*100 for r in results["hfm"]["range_err"]], color='#00FFA3', lw=2.5, marker='s', ms=8, label='HFM range error')
ax.set_title('B. Range Error vs Radial Velocity', color='#FFB800', fontsize=11, fontweight='bold')
ax.set_xlabel('Radial Velocity v [m/s]', color='#8EA4C1')
ax.set_ylabel('Range Error [cm]', color='#8EA4C1')
ax.legend(fontsize=9, facecolor='#020B18', edgecolor='#152840')

# Panel C: Correlation output at worst velocity (v=2.5 m/s)
ax = axs[1, 0]
v_worst = velocities[-1]
lfm_echo_w = doppler_shift_signal(lfm_ref, v_worst, FS, C)
hfm_echo_w = doppler_shift_signal(hfm_ref, v_worst, FS, C)
_, _, corr_lfm = peak_snr_and_range_error(lfm_ref, lfm_echo_w)
_, _, corr_hfm = peak_snr_and_range_error(hfm_ref, hfm_echo_w)
lags_ms = (np.arange(len(corr_lfm)) - (N-1)) / FS * 1000
corr_lfm_n = np.abs(corr_lfm) / (np.max(np.abs(corr_lfm)) + 1e-12)
corr_hfm_n = np.abs(corr_hfm) / (np.max(np.abs(corr_hfm)) + 1e-12)
ax.plot(lags_ms, 20*np.log10(np.maximum(corr_lfm_n, 1e-4)), color='#FF2E63', lw=1.8, label=f'LFM @ v={v_worst}m/s')
ax.plot(lags_ms, 20*np.log10(np.maximum(corr_hfm_n, 1e-4)), color='#00FFA3', lw=1.8, label=f'HFM @ v={v_worst}m/s')
ax.set_xlim(-T_p*500, T_p*500)
ax.set_ylim(-60, 5)
ax.set_title(f'C. Matched-Filter Output @ v={v_worst} m/s', color='#00FFA3', fontsize=11, fontweight='bold')
ax.set_xlabel('Lag [ms]', color='#8EA4C1')
ax.set_ylabel('Normalised Amplitude [dB]', color='#8EA4C1')
ax.legend(fontsize=9, facecolor='#020B18', edgecolor='#152840')

# Panel D: Summary table
ax = axs[1, 1]
ax.axis('off')
header = ['v [m/s]', 'LFM SNR deg', 'HFM SNR deg', 'Δ (HFM-LFM)', 'LFM Rerr[cm]', 'HFM Rerr[cm]']
rows = []
for i, v in enumerate(velocities):
    rows.append([f"{v:.1f}",
                 f"{snr_deg_lfm[i]:.2f} dB",
                 f"{snr_deg_hfm[i]:.2f} dB",
                 f"{snr_deg_hfm[i]-snr_deg_lfm[i]:.2f} dB",
                 f"{results['lfm']['range_err'][i]*100:.2f}",
                 f"{results['hfm']['range_err'][i]*100:.2f}"])
tbl = ax.table(cellText=rows, colLabels=header, cellLoc='center', loc='center',
               bbox=[0.0, 0.15, 1.0, 0.75])
tbl.auto_set_font_size(False); tbl.set_fontsize(8.5)
for (r,c_), cell in tbl.get_celld().items():
    cell.set_facecolor('#071526' if r > 0 else '#152840')
    cell.set_edgecolor('#152840')
    cell.set_text_props(color='white')
ax.set_title('D. Simulation Summary\n(SIMULATION — report "measured HFM/LFM improvement\nunder defined test conditions")', color='#FF2E63', fontsize=10, fontweight='bold')

plt.suptitle('EXPERIMENT 4 — HFM vs LFM Doppler Tolerance (SIMULATION)\n'
             'Do NOT quote a specific dB gain until hardware measurement is complete.',
             color='white', fontsize=12, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])
out = os.path.join(os.path.dirname(__file__), '../../../docs/exp04_hfm_lfm.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='#020B18')
print(f"EXP04 saved: {os.path.abspath(out)}")
