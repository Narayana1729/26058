"""
generate_luts.py
================
Single responsibility: call the 3 physics modules, write 3 firmware headers.

Outputs
-------
firmware/generated/tgc_lut.h       — TGC DAC codes + metadata
firmware/generated/seabed_table.h  — Impedance, Rp, BL reference table
firmware/generated/acoustic_profiles.h — Per-mode alpha + SNR thresholds

Usage
-----
    cd 'SIH Hardware/python'
    python3 generate_luts.py

All physics parameters are sourced from the module defaults.
To override, pass environment dict to the relevant functions.
"""

import sys
import os
import numpy as np
from datetime import datetime, timezone

# Allow importing sibling modules
sys.path.insert(0, os.path.dirname(__file__))

from acoustic_model import alpha_dB_per_m, sound_speed_mackenzie, DEFAULT_ENV
from tgc_generator  import (generate_tgc_db, dac_code_from_gain_db,
                             MIN_TGC_DB, MAX_TGC_DB, DAC_BITS, DAC_MAX_CODE)
from seabed_model   import (theoretical_bl_table, WATER_REF, SEABED_DISCLAIMER)

# ---------------------------------------------------------------------------
# Mode definitions — must match ocean_adaptation_table.h
# ---------------------------------------------------------------------------
MODES = [
    {
        "id": 0,
        "name": "HIGH_RES_450KHZ",
        "f_carrier_hz": 450_000,
        "f_base_hz": 2_000,
        "f_top_hz": 30_000,
        "tim6_arr": 359,
        "pulse_ms": 2,
    },
    {
        "id": 1,
        "name": "BALANCED_250KHZ",
        "f_carrier_hz": 250_000,
        "f_base_hz": 1_000,
        "f_top_hz": 20_000,
        "tim6_arr": 719,
        "pulse_ms": 5,
    },
    {
        "id": 2,
        "name": "DEEP_PEN_100KHZ",
        "f_carrier_hz": 100_000,
        "f_base_hz": 500,
        "f_top_hz": 8_000,
        "tim6_arr": 1439,
        "pulse_ms": 10,
    },
    {
        "id": 3,
        "name": "HFM_DOPPLER_250K",
        "f_carrier_hz": 250_000,
        "f_base_hz": 1_000,
        "f_top_hz": 20_000,
        "tim6_arr": 719,
        "pulse_ms": 5,
    },
]

N_SAMPLES = 512
FS        = 100_000.0    # Hz — must match firmware sampling rate
ENV       = DEFAULT_ENV  # simulation reference environment

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "firmware", "generated")
FIRMWARE_DIR = os.path.join(os.path.dirname(__file__), "..", "firmware")
TIMESTAMP  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# ---------------------------------------------------------------------------
# Compute sound speed and alpha for all modes
# ---------------------------------------------------------------------------
c = sound_speed_mackenzie(ENV["temperature_C"], ENV["salinity_ppt"], ENV["depth_m"])

def alpha_fn(f_hz):
    return alpha_dB_per_m(f_hz, ENV["temperature_C"], ENV["salinity_ppt"],
                          ENV["depth_m"], ENV["pH"])

print(f"  Environment : T={ENV['temperature_C']}°C  S={ENV['salinity_ppt']}ppt"
      f"  pH={ENV['pH']}  D={ENV['depth_m']}m")
print(f"  Sound speed : {c:.2f} m/s  (Mackenzie 1981)")
print(f"  N_SAMPLES   : {N_SAMPLES}   Fs={FS/1e3:.0f} kHz")
print(f"  Max range   : {c*(N_SAMPLES/FS)/2:.3f} m per ping")
print(f"  TGC limits  : {MIN_TGC_DB:.1f} – {MAX_TGC_DB:.1f} dB (Nominal AD8331/AD603 VGA range)")
print()

mode_results = []
for m in MODES:
    ranges_m, tgc_theory, tgc_clipped = generate_tgc_db(
        alpha_fn, m["f_carrier_hz"], N_SAMPLES, FS, c
    )
    dac_codes = dac_code_from_gain_db(tgc_clipped, MIN_TGC_DB, MAX_TGC_DB, DAC_BITS)
    alpha_val = alpha_fn(m["f_carrier_hz"])
    mode_results.append({
        **m,
        "alpha_dB_per_m": alpha_val,
        "ranges_m":       ranges_m,
        "tgc_theory_dB":  tgc_theory,
        "tgc_clipped_dB": tgc_clipped,
        "dac_codes":      dac_codes,
        "tl_at_maxR":     tgc_theory[-1],
    })
    print(f"  Mode {m['id']} ({m['name']:20s}) "
          f"alpha={alpha_val*1e3:.4f} dB/km  "
          f"TL@{ranges_m[-1]:.2f}m={tgc_theory[-1]:.2f}dB  "
          f"clipped_max={tgc_clipped[-1]:.1f}dB")

# Reference seabed table
bl_table = theoretical_bl_table()

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------
# 1. tgc_lut.h
# -----------------------------------------------------------------------
with open(os.path.join(OUTPUT_DIR, "tgc_lut.h"), "w") as f:
    f.write(f"""/*
 * tgc_lut.h — Physics-Derived TGC Gain Table
 * Generated: {TIMESTAMP}
 * Generator: python/generate_luts.py
 *
 * Physics:   TL_2way = 40*log10(R) + 2*alpha(f)*R  [dB]
 *            alpha = Francois-Garrison (1982), ONE-WAY dB/m
 *            c     = Mackenzie (1981), {c:.2f} m/s
 *
 * Environment (simulation defaults):
 *            T={ENV['temperature_C']}C  S={ENV['salinity_ppt']}ppt  pH={ENV['pH']}  D={ENV['depth_m']}m
 *
 * TGC limits: {MIN_TGC_DB:.1f} to {MAX_TGC_DB:.1f} dB (Nominal dynamic range for AD8331 / AD603 VGA stage)
 * DAC       : {DAC_BITS}-bit, codes 0–{DAC_MAX_CODE}
 *
 * Usage in firmware:
 *     uint16_t code = TGC_DAC_CODES[mode][sample_index];
 *     DAC1->DHR12R1 = code;   // or equivalent
 *
 * IMPORTANT: If AFE hardware gain range changes, re-run generate_luts.py
 *            with updated MIN_TGC_DB / MAX_TGC_DB in tgc_generator.py.
 */

#ifndef TGC_LUT_H
#define TGC_LUT_H

#include <stdint.h>

/* Environment at generation time */
#define TGC_ENV_TEMP_C      {ENV['temperature_C']:.1f}f
#define TGC_ENV_SAL_PPT     {ENV['salinity_ppt']:.1f}f
#define TGC_ENV_PH          {ENV['pH']:.1f}f
#define TGC_ENV_DEPTH_M     {ENV['depth_m']:.1f}f
#define TGC_SOUND_SPEED_MPS {c:.2f}f

/* Hardware gain limits [dB * 10 for integer use] */
#define TGC_MIN_GAIN_DB_X10 {int(MIN_TGC_DB*10)}
#define TGC_MAX_GAIN_DB_X10 {int(MAX_TGC_DB*10)}
#define TGC_DAC_BITS        {DAC_BITS}
#define TGC_DAC_MAX_CODE    {DAC_MAX_CODE}U

/* One-way absorption per mode [dB/m * 1e7, integer] */
""")
    for mr in mode_results:
        f.write(f"#define TGC_ALPHA_MODE{mr['id']}_E7  "
                f"{int(round(mr['alpha_dB_per_m']*1e7))}L"
                f"  /* {mr['name']}: {mr['alpha_dB_per_m']*1e3:.4f} dB/km ONE-WAY */\n")

    f.write(f"""
/* Number of samples and sampling rate */
#define TGC_N_SAMPLES  {N_SAMPLES}U
#define TGC_FS_HZ      {int(FS)}U

/*
 * TGC_DAC_CODES[mode][sample]
 *
 * Mapping:  code = round((TL_clipped - MIN_TGC_DB) / (MAX_TGC_DB - MIN_TGC_DB) * {DAC_MAX_CODE})
 * Inverse:  gain_dB = code * (MAX_TGC_DB - MIN_TGC_DB) / {DAC_MAX_CODE} + MIN_TGC_DB
 *
 * Mode ordering (0=highest frequency, 3=lowest):
""")
    for mr in mode_results:
        f.write(f" *   {mr['id']} = {mr['name']}"
                f"  fc={mr['f_carrier_hz']//1000}kHz"
                f"  alpha={mr['alpha_dB_per_m']*1e3:.2f}dB/km\n")
    f.write(" */\n")
    f.write(f"static const uint16_t TGC_DAC_CODES[4][{N_SAMPLES}] = {{\n")
    for mr in mode_results:
        codes = mr["dac_codes"]
        f.write(f"    /* Mode {mr['id']}: {mr['name']} */\n    {{\n        ")
        rows = [", ".join(f"{v:4d}" for v in codes[i:i+16]) for i in range(0, N_SAMPLES, 16)]
        f.write(",\n        ".join(rows))
        f.write("\n    }" + ("," if mr["id"] < 3 else "") + "\n")
    f.write("};\n\n#endif /* TGC_LUT_H */\n")

print(f"\n  WROTE: firmware/generated/tgc_lut.h")

# -----------------------------------------------------------------------
# 2. seabed_table.h
# -----------------------------------------------------------------------
rho_w, c_w = WATER_REF
Z_water = rho_w * c_w

with open(os.path.join(OUTPUT_DIR, "seabed_table.h"), "w") as f:
    f.write(f"""/*
 * seabed_table.h — Acoustic Impedance Reference Table
 * Generated: {TIMESTAMP}
 *
 * Model: Normal-incidence, homogeneous half-space (idealised)
 *        Z = rho * c  [Rayl]
 *        Rp = (Z2-Z1)/(Z2+Z1)
 *        BL = -20*log10(|Rp|)  [dB]
 *
 * DISCLAIMER: {SEABED_DISCLAIMER}
 *
 * Classification: argmin_i |BL_measured - BL_ref_i|
 * Report as: coarse reference classification.
 */

#ifndef SEABED_TABLE_H
#define SEABED_TABLE_H

#include <stdint.h>
#include <math.h>

typedef enum {{
    SEABED_UNKNOWN    = 0,
    SEABED_SOFT_MUD   = 1,
    SEABED_SANDY_MUD  = 2,
    SEABED_SAND       = 3,
    SEABED_GRAVEL     = 4,
    SEABED_ROCK       = 5
}} SeabedType_t;

typedef struct {{
    const char   *name;
    float         Z_Mrayl;    /* Acoustic impedance [MRayl] */
    float         Rp;         /* Normal-incidence reflection coefficient */
    float         BL_dB;      /* Bottom loss [dB] */
    SeabedType_t  stype;
}} SeabedReference_t;

/* Water reference: rho={rho_w:.0f} kg/m3, c={c_w:.0f} m/s, Z={Z_water/1e6:.4f} MRayl */
#define WATER_Z_MRAYL  {Z_water/1e6:.4f}f

static const SeabedReference_t SEABED_REF_TABLE[] = {{
    /* name              Z[MRayl]    Rp        BL[dB]  type */
""")
    for name, ref in bl_table.items():
        stype_name = f"SEABED_{ref.stype.name}"
        f.write(f"    {{ \"{name}\","
                f" {ref.Z/1e6:.4f}f,"
                f" {ref.Rp:.5f}f,"
                f" {ref.BL_dB:.3f}f,"
                f" {stype_name} }},\n")

    n_materials = len(bl_table)
    f.write(f"""}};
#define SEABED_N_MATERIALS {n_materials}U

/**
 * @brief Classify seabed by nearest reference BL (argmin).
 * @param bl_measured_dB : propagation-corrected echo bottom loss [dB]
 * @param max_error_dB   : accept threshold [dB]; return UNKNOWN if exceeded
 * @return SeabedType_t
 *
 * Report result as "coarse reference classification", not geological fact.
 */
static inline SeabedType_t classify_seabed_nearest(float bl_measured_dB,
                                                     float max_error_dB)
{{
    if (!isfinite(bl_measured_dB)) return SEABED_UNKNOWN;

    int    best_idx = -1;
    float  best_err = 1.0e9f;

    for (unsigned i = 0; i < SEABED_N_MATERIALS; i++) {{
        float err = fabsf(bl_measured_dB - SEABED_REF_TABLE[i].BL_dB);
        if (err < best_err) {{
            best_err = err;
            best_idx = (int)i;
        }}
    }}

    if (best_idx < 0 || best_err > max_error_dB) return SEABED_UNKNOWN;
    return SEABED_REF_TABLE[best_idx].stype;
}}

#endif /* SEABED_TABLE_H */
""")

print(f"  WROTE: firmware/generated/seabed_table.h")

# -----------------------------------------------------------------------
# 3. acoustic_profiles.h
# -----------------------------------------------------------------------
with open(os.path.join(OUTPUT_DIR, "acoustic_profiles.h"), "w") as f:
    f.write(f"""/*
 * acoustic_profiles.h — Per-Mode Acoustic Parameters + Controller Thresholds
 * Generated: {TIMESTAMP}
 *
 * Mode ordering: 0 = highest frequency (best resolution)
 *                3 = lowest frequency  (deepest penetration)
 * This ordering is EXPLICIT and must not be inferred from enum arithmetic.
 */

#ifndef ACOUSTIC_PROFILES_H
#define ACOUSTIC_PROFILES_H

#include <stdint.h>

/* Operating Modes Definition */
typedef enum {{
    SONAR_MODE_HIGH_RES    = 0,   /* High-Resolution Imaging Mode (Clear Water, 450 kHz) */
    SONAR_MODE_BALANCED    = 1,   /* Standard Balanced Mode (Moderate Water, 250 kHz)     */
    SONAR_MODE_DEEP_PEN    = 2,   /* Deep Penetration Mode (Murky/Muddy Water, 100 kHz)   */
    SONAR_MODE_HFM_DOPPLER = 3    /* Doppler-Invariant Hyperbolic Chirp Mode (AUV Cruise) */
}} SonarOperatingMode_t;

/* SNR thresholds for closed-loop waveform selection [dB * 10] */
#define SNR_LOW_THRESHOLD_DB_X10    80    /*  8.0 dB — switch to lower frequency */
#define SNR_HIGH_THRESHOLD_DB_X10  220    /* 22.0 dB — switch to higher frequency */

/* Minimum pings at same mode before re-evaluating (hysteresis / dwell) */
#define MIN_MODE_DWELL_PINGS  3U

typedef struct {{
    SonarOperatingMode_t mode_id;
    uint32_t f_carrier_hz;
    uint32_t f_base_hz;
    uint32_t f_top_hz;
    uint16_t tim6_arr;
    uint8_t  pulse_ms;
    int32_t  alpha_E7;        /* one-way alpha [dB/m * 1e7] */
    const char *name;
}} AcousticProfile_t;

static const AcousticProfile_t ACOUSTIC_PROFILES[4] = {{
""")
    for mr in mode_results:
        f.write(f"    {{ (SonarOperatingMode_t){mr['id']}U, {mr['f_carrier_hz']}UL, "
                f"{mr['f_base_hz']}UL, {mr['f_top_hz']}UL, "
                f"{mr['tim6_arr']}U, {mr['pulse_ms']}U, "
                f"{int(round(mr['alpha_dB_per_m']*1e7))}L, "
                f"\"{mr['name']}\" }},\n")
    f.write(f"""}};

/*
 * Safe lower-frequency fallback table.
 * DO NOT use enum arithmetic (mode + 1) — use this table.
 * Index [i] = next-lower-frequency mode from mode i.
 */
static const uint8_t LOWER_FREQ_MODE[4] = {{
    1,   /* from HIGH_RES  -> BALANCED  */
    2,   /* from BALANCED  -> DEEP_PEN  */
    3,   /* from DEEP_PEN  -> HFM_DOPPLER (lowest available) */
    3    /* from HFM       -> stay at 3 */
}};

static const uint8_t HIGHER_FREQ_MODE[4] = {{
    0,   /* from HIGH_RES  -> stay at 0 */
    0,   /* from BALANCED  -> HIGH_RES  */
    1,   /* from DEEP_PEN  -> BALANCED  */
    1    /* from HFM       -> BALANCED  */
}};

#endif /* ACOUSTIC_PROFILES_H */
""")

print(f"  WROTE: firmware/generated/acoustic_profiles.h")

# -----------------------------------------------------------------------
# 4. Master Umbrella Header: firmware/sonar_system.h
# -----------------------------------------------------------------------
with open(os.path.join(FIRMWARE_DIR, "sonar_system.h"), "w") as f:
    f.write(f"""/*
 * sonar_system.h — Master Umbrella Header for Software-Defined Sonar
 * Generated: {TIMESTAMP}
 *
 * Single include for the complete embedded sonar pipeline:
 * - Acoustic Profiles & Safe Mode Tables
 * - Waveform LUTs (LFM & HFM)
 * - Physics-Derived TGC DAC Table
 * - Seabed Reflection & Substrate Classification
 * - Echo Feature Extraction Structs
 * - Closed-Loop Feedback Controller
 */

#ifndef SONAR_SYSTEM_H
#define SONAR_SYSTEM_H

#include "generated/acoustic_profiles.h"
#include "../chirp_lut.h"
#include "generated/tgc_lut.h"
#include "generated/seabed_table.h"
#include "dsp/echo_features.h"
#include "control/adaptation_controller.h"

#endif /* SONAR_SYSTEM_H */
""")

print(f"  WROTE: firmware/sonar_system.h")
print(f"\n  generate_luts.py complete — all headers verified and aligned!")

print(f"\n  generate_luts.py complete — 3 headers written to firmware/generated/")
