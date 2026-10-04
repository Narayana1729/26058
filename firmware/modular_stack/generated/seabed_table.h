/*
 * seabed_table.h — Acoustic Impedance Reference Table
 * Generated: 2026-08-29 13:24 UTC
 *
 * Model: Normal-incidence, homogeneous half-space (idealised)
 *        Z = rho * c  [Rayl]
 *        Rp = (Z2-Z1)/(Z2+Z1)
 *        BL = -20*log10(|Rp|)  [dB]
 *
 * DISCLAIMER: Coarse reference classification under controlled experimental conditions. Real seabed classification also depends on grazing angle, roughness, sediment layering, frequency, grain size, porosity, density, sound speed gradient, volume scattering, and transducer directivity.
 *
 * Classification: argmin_i |BL_measured - BL_ref_i|
 * Report as: coarse reference classification.
 */

#ifndef SEABED_TABLE_H
#define SEABED_TABLE_H

#include <stdint.h>
#include <math.h>

typedef enum {
    SEABED_UNKNOWN    = 0,
    SEABED_SOFT_MUD   = 1,
    SEABED_SANDY_MUD  = 2,
    SEABED_SAND       = 3,
    SEABED_GRAVEL     = 4,
    SEABED_ROCK       = 5
} SeabedType_t;

typedef struct {
    const char   *name;
    float         Z_Mrayl;    /* Acoustic impedance [MRayl] */
    float         Rp;         /* Normal-incidence reflection coefficient */
    float         BL_dB;      /* Bottom loss [dB] */
    SeabedType_t  stype;
} SeabedReference_t;

/* Water reference: rho=1025 kg/m3, c=1500 m/s, Z=1.5375 MRayl */
#define WATER_Z_MRAYL  1.5375f

static const SeabedReference_t SEABED_REF_TABLE[] = {
    /* name              Z[MRayl]    Rp        BL[dB]  type */
    { "Soft Mud", 1.7020f, 0.05078f, 25.886f, SEABED_SOFT_MUD },
    { "Sandy Mud", 2.5600f, 0.24954f, 12.057f, SEABED_SANDY_MUD },
    { "Sand", 3.2300f, 0.35501f, 8.995f, SEABED_SAND },
    { "Gravel", 3.6000f, 0.40146f, 7.927f, SEABED_GRAVEL },
    { "Limestone/Rock", 9.4500f, 0.72014f, 2.852f, SEABED_ROCK },
};
#define SEABED_N_MATERIALS 5U

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
{
    if (!isfinite(bl_measured_dB)) return SEABED_UNKNOWN;

    int    best_idx = -1;
    float  best_err = 1.0e9f;

    for (unsigned i = 0; i < SEABED_N_MATERIALS; i++) {
        float err = fabsf(bl_measured_dB - SEABED_REF_TABLE[i].BL_dB);
        if (err < best_err) {
            best_err = err;
            best_idx = (int)i;
        }
    }

    if (best_idx < 0 || best_err > max_error_dB) return SEABED_UNKNOWN;
    return SEABED_REF_TABLE[best_idx].stype;
}

#endif /* SEABED_TABLE_H */
