"""
Physics-Derived TGC & Seabed Impedance Classifier Simulation
Research Extension (V3 Roadmap: In-Water Echo Feedback & Substrate Characterization)
====================================================================================
Deliverables:
  1. Francois-Garrison alpha(f) absorption modeling across carrier modes.
  2. TGC gain LUT: gain[i] = 40*log10(R_i) + alpha(f)*R_i  (physics-derived).
  3. Acoustic Impedance Seabed Classification mapping: Z = rho * c.
  4. Export: docs/tgc_lut.h  (512 entries x 4 modes).
  5. Export: docs/seabed_classification_analysis.png.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# -----------------------------------------------------------------------
# 1. FRANCOIS-GARRISON SEAWATER ABSORPTION MODEL (1982, JASA)
#    alpha(f) [dB/m]  -- valid 400 Hz to 1 MHz
# -----------------------------------------------------------------------
def francois_garrison_alpha(f_hz, T_C=20.0, S_ppt=35.0, D_m=10.0, pH=8.0):
    """Returns acoustic absorption coefficient alpha in dB/m."""
    f_khz = f_hz / 1e3

    # Term 1: Boric Acid (B(OH)3)
    A1 = 8.86 / 1e3 * 10**(0.78 * pH - 5.0)
    f1 = 2.8 * np.sqrt(S_ppt / 35.0) * 10**(4.0 - 1245.0 / (T_C + 273.0))
    alpha1 = A1 * f1 * f_khz**2 / (f1**2 + f_khz**2)

    # Term 2: MgSO4
    A2 = 21.44 * S_ppt * (1.0 + 0.025 * T_C) / 1e3
    f2 = (8.17 * 10**(8.0 - 1990.0 / (T_C + 273.0))) / (1.0 + 0.0018 * (S_ppt - 35.0))
    P2 = 1.0 - 1.37e-4 * D_m + 6.2e-9 * D_m**2
    alpha2 = A2 * P2 * f2 * f_khz**2 / (f2**2 + f_khz**2)

    # Term 3: Pure Water viscosity
    if T_C <= 20.0:
        A3 = 4.937e-4 - 2.59e-5*T_C + 9.11e-7*T_C**2 - 1.50e-8*T_C**3
    else:
        A3 = 3.964e-4 - 1.146e-5*T_C + 1.45e-7*T_C**2 - 6.5e-10*T_C**3
    P3 = 1.0 - 3.83e-5 * D_m + 4.9e-10 * D_m**2
    alpha3 = A3 * P3 * f_khz**2

    return (alpha1 + alpha2 + alpha3) / 1000.0  # dB/km -> dB/m

# -----------------------------------------------------------------------
# 2. SYSTEM PARAMETERS
# -----------------------------------------------------------------------
C_SOUND   = 1500.0
FS        = 100000.0
N_SAMPLES = 512
T_SAMPLE  = 1.0 / FS
MAX_RANGE_M = C_SOUND * (N_SAMPLES / FS) / 2.0

CARRIER_MODES = {
    0: {"name": "HIGH_RES_450KHZ",  "f_carrier": 450e3},
    1: {"name": "BALANCED_250KHZ",  "f_carrier": 250e3},
    2: {"name": "DEEP_PEN_100KHZ",  "f_carrier": 100e3},
    3: {"name": "HFM_DOPPLER_250K", "f_carrier": 250e3},
}

TGC_MAX_DB = 80.0
sample_indices = np.arange(1, N_SAMPLES + 1)
ranges_m = (C_SOUND * sample_indices * T_SAMPLE) / 2.0

print("=" * 70)
print("  HYDROACOUSTIC RECEIVER: PHYSICS-DERIVED TGC & SEABED CLASSIFIER")
print("=" * 70)
print(f"  Max range per ping: {MAX_RANGE_M:.2f} m  |  Fs: {FS/1000:.0f} kHz  |  N: {N_SAMPLES}\n")

tgc_luts = {}
alphas_at_carrier = {}

for mode_id, mode in CARRIER_MODES.items():
    fc = mode["f_carrier"]
    a  = francois_garrison_alpha(fc)
    alphas_at_carrier[mode_id] = a
    R_c = np.maximum(ranges_m, 0.1)
    TL  = 40.0 * np.log10(R_c) + a * R_c
    lut = np.clip(np.round(TL / TGC_MAX_DB * 4095), 0, 4095).astype(int)
    tgc_luts[mode_id] = lut
    print(f"  Mode {mode_id} ({mode['name']}):  fc={fc/1e3:.0f}kHz  "
          f"alpha={a*1000:.4f}dB/km  TL@{MAX_RANGE_M:.1f}m={40*np.log10(MAX_RANGE_M)+a*MAX_RANGE_M:.2f}dB")

# -----------------------------------------------------------------------
# 3. SEABED IMPEDANCE TABLE
# -----------------------------------------------------------------------
WATER_Z = 1025.0 * 1500.0

SEABED_TABLE = {
    "Soft Mud":       (1150.0, 1480.0),
    "Sandy Mud":      (1600.0, 1600.0),
    "Sand":           (1900.0, 1700.0),
    "Gravel":         (2000.0, 1800.0),
    "Limestone/Rock": (2700.0, 3500.0),
}

print(f"\n  {'Seabed':<18} {'rho':>8} {'c':>7} {'Z(MRayl)':>10} {'R_coeff':>8} {'BL(dB)':>8}")
print("  " + "-" * 65)
seabed_BL = {}; seabed_Z = {}
for name, (rho, c) in SEABED_TABLE.items():
    Z2 = rho * c
    Rc = (Z2 - WATER_Z) / (Z2 + WATER_Z)
    BL = -20.0 * np.log10(abs(Rc)) if abs(Rc) > 1e-9 else 999.0
    seabed_Z[name] = Z2; seabed_BL[name] = BL
    print(f"  {name:<18} {rho:>8.0f} {c:>7.0f} {Z2/1e6:>10.3f} {Rc:>8.4f} {BL:>8.2f}")

# -----------------------------------------------------------------------
# 4. EXPORT tgc_lut.h
docs_out = os.path.join(os.path.dirname(__file__), "../docs")
os.makedirs(docs_out, exist_ok=True)
with open(os.path.join(docs_out, "tgc_lut.h"), "w") as f:
    f.write("/*\n * Physics-Derived TGC LUT\n")
    f.write(" * Model: Francois & Garrison (1982), JASA 72(3)\n")
    f.write(" * TL(R,f) = 40*log10(R) + alpha(f)*R  [dB, two-way spherical spreading]\n")
    f.write(" * Gain = round(TL / 80.0 * 4095)  [12-bit DAC word]\n */\n\n")
    f.write("#ifndef TGC_LUT_H\n#define TGC_LUT_H\n\n#include <stdint.h>\n\n")

    for mid, mode in CARRIER_MODES.items():
        a = alphas_at_carrier[mid]
        f.write(f"#define ALPHA_MODE{mid}_DB_PER_M_E6  {int(round(a*1e6))}UL"
                f"  /* {mode['name']}: {a*1000:.4f} dB/km */\n")

    f.write("\ntypedef enum {\n"
            "    SEABED_SOFT_MUD  = 0,\n"
            "    SEABED_SANDY_MUD = 1,\n"
            "    SEABED_SAND      = 2,\n"
            "    SEABED_GRAVEL    = 3,\n"
            "    SEABED_ROCK      = 4\n"
            "} SeabedType_t;\n\n")

    f.write("static inline SeabedType_t classify_seabed(int32_t bl_times_100) {\n"
            "    if (bl_times_100 < 150)  return SEABED_SOFT_MUD;\n"
            "    if (bl_times_100 < 350)  return SEABED_SANDY_MUD;\n"
            "    if (bl_times_100 < 650)  return SEABED_SAND;\n"
            "    if (bl_times_100 < 1000) return SEABED_GRAVEL;\n"
            "    return SEABED_ROCK;\n}\n\n")

    f.write("static const uint16_t TGC_LUT[4][512] = {\n")
    for mid in range(4):
        lut = tgc_luts[mid]
        f.write(f"    /* Mode {mid}: {CARRIER_MODES[mid]['name']} */\n    {{\n        ")
        rows = [", ".join(f"{v:4d}" for v in lut[i:i+16]) for i in range(0,512,16)]
        f.write(",\n        ".join(rows))
        f.write("\n    }" + ("," if mid < 3 else "") + "\n")
    f.write("};\n\n#endif /* TGC_LUT_H */\n")

print("\n  EXPORTED: docs/tgc_lut.h")

# -----------------------------------------------------------------------
# 5. PRESENTATION PLOT
# -----------------------------------------------------------------------
plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=200)
fig.patch.set_facecolor('#020B18')
for ax in axs.flat:
    ax.set_facecolor('#071526')
    ax.grid(True, color='#152840', linestyle='--', alpha=0.5)

COLORS = ['#00F0FF', '#00FFA3', '#FFB800', '#FF2E63']

# Panel 1: alpha(f) sweep
f_sweep = np.logspace(2, 6, 500)
alpha_sweep = np.array([francois_garrison_alpha(f)*1000 for f in f_sweep])
axs[0,0].loglog(f_sweep/1e3, alpha_sweep, color='#00F0FF', lw=2, label='alpha(f) @20C,35ppt,10m')
for mid, mode in CARRIER_MODES.items():
    fc = mode["f_carrier"]
    a  = alphas_at_carrier[mid]*1000
    axs[0,0].axvline(fc/1e3, color=COLORS[mid], ls='--', alpha=0.7)
    axs[0,0].scatter([fc/1e3],[a], color=COLORS[mid], s=80, zorder=5)
    axs[0,0].annotate(f"M{mid} {fc/1e3:.0f}kHz\n{a:.2f}dB/km",
                      xy=(fc/1e3, a), xytext=(fc/1e3*1.3, a*1.8),
                      color=COLORS[mid], fontsize=7.5,
                      bbox=dict(boxstyle='round,pad=0.2', fc='#020B18', ec=COLORS[mid], alpha=0.8))
axs[0,0].set_title('1. Francois-Garrison alpha(f) — Seawater 20C', color='#00F0FF', fontsize=11, fontweight='bold')
axs[0,0].set_xlabel('Frequency (kHz)', color='#8EA4C1')
axs[0,0].set_ylabel('Absorption (dB/km)', color='#8EA4C1')
axs[0,0].legend(fontsize=8, facecolor='#020B18', edgecolor='#152840')

# Panel 2: TGC gain ramps
for mid in range(4):
    lut = tgc_luts[mid]
    axs[0,1].plot(ranges_m, lut/4095.0*TGC_MAX_DB, color=COLORS[mid], lw=1.8,
                  label=f"M{mid} {CARRIER_MODES[mid]['name'][:13]}")
axs[0,1].set_title('2. Physics TGC Ramps — 40log10(R) + alpha(f)*R', color='#00FFA3', fontsize=11, fontweight='bold')
axs[0,1].set_xlabel('One-Way Range R (m)', color='#8EA4C1')
axs[0,1].set_ylabel('Gain Compensation (dB)', color='#8EA4C1')
axs[0,1].legend(fontsize=7.5, facecolor='#020B18', edgecolor='#152840')

# Panel 3: Impedance bar chart
names  = list(SEABED_TABLE.keys())
Z_vals = [seabed_Z[n]/1e6 for n in names]
BL_vals= [seabed_BL[n]    for n in names]
x_pos  = np.arange(len(names))
bars_Z  = axs[1,0].bar(x_pos-0.2, Z_vals,  0.35, color='#00F0FF', alpha=0.85, label='Z=rho*c (MRayl)')
bars_BL = axs[1,0].bar(x_pos+0.2, BL_vals, 0.35, color='#FF2E63', alpha=0.85, label='Bottom Loss (dB)')
for b,v in zip(bars_Z,  Z_vals):  axs[1,0].text(b.get_x()+b.get_width()/2, b.get_height()+0.1, f'{v:.2f}', ha='center', fontsize=7.5, color='#00F0FF')
for b,v in zip(bars_BL, BL_vals): axs[1,0].text(b.get_x()+b.get_width()/2, b.get_height()+0.1, f'{v:.1f}',  ha='center', fontsize=7.5, color='#FF2E63')
axs[1,0].set_xticks(x_pos); axs[1,0].set_xticklabels(names, rotation=15, fontsize=8, color='#AAAAAA')
axs[1,0].set_title('3. Acoustic Impedance Z=rho*c & Bottom Loss — Seabed Types', color='#FFB800', fontsize=11, fontweight='bold')
axs[1,0].set_ylabel('Z (MRayl) / BL (dB)', color='#8EA4C1')
axs[1,0].legend(fontsize=8, facecolor='#020B18', edgecolor='#152840')

# Panel 4: Classifier regions
boundaries = [0, 1.5, 3.5, 6.5, 10.0, 25.0]
colors_map = ['#1A6B8A','#12A074','#D4A017','#C0392B','#8E44AD']
labels_map = ['Soft Mud (<1.5)','Sandy Mud (<3.5)','Sand (<6.5)','Gravel (<10)','Rock (>10)']
for i in range(5):
    axs[1,1].axvspan(boundaries[i], boundaries[i+1], alpha=0.35, color=colors_map[i], label=labels_map[i])
for name, bl in seabed_BL.items():
    axs[1,1].axvline(bl, color='white', ls='--', alpha=0.6, lw=1.0)
    axs[1,1].text(bl+0.2, 0.7, name, rotation=90, fontsize=7.5, color='white', alpha=0.9)
axs[1,1].set_xlim(0, 25); axs[1,1].set_ylim(0, 1); axs[1,1].set_yticks([])
axs[1,1].set_title('4. Seabed Classifier — Decision Regions from Z Mismatch', color='#FFB800', fontsize=11, fontweight='bold')
axs[1,1].set_xlabel('Measured Bottom Loss BL (dB)', color='#8EA4C1')
axs[1,1].legend(fontsize=7.5, facecolor='#020B18', edgecolor='#152840', loc='upper right')

plt.suptitle('AUTONOMOUS SDR SONAR — PHYSICS TGC & SEABED IMPEDANCE CLASSIFIER\n'
             'Francois-Garrison (1982) JASA + Acoustic Impedance Z=rho*c',
             color='#FFFFFF', fontsize=13, fontweight='bold', y=0.99)
out_fig = os.path.join(os.path.dirname(__file__), '../docs/seabed_classification_analysis.png')
os.makedirs(os.path.dirname(out_fig), exist_ok=True)
plt.savefig(out_fig, dpi=200, bbox_inches='tight', facecolor='#020B18')
print(f"  EXPORTED: {out_fig}")
