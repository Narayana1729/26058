/*
 * acoustic_profiles.h — Per-Mode Acoustic Parameters + Controller Thresholds
 * Generated: 2026-08-29 13:24 UTC
 *
 * Mode ordering: 0 = highest frequency (best resolution)
 *                3 = lowest frequency  (deepest penetration)
 * This ordering is EXPLICIT and must not be inferred from enum arithmetic.
 */

#ifndef ACOUSTIC_PROFILES_H
#define ACOUSTIC_PROFILES_H

#include <stdint.h>

/* Operating Modes Definition */
typedef enum {
    SONAR_MODE_HIGH_RES    = 0,   /* High-Resolution Imaging Mode (Clear Water, 450 kHz) */
    SONAR_MODE_BALANCED    = 1,   /* Standard Balanced Mode (Moderate Water, 250 kHz)     */
    SONAR_MODE_DEEP_PEN    = 2,   /* Deep Penetration Mode (Murky/Muddy Water, 100 kHz)   */
    SONAR_MODE_HFM_DOPPLER = 3    /* Doppler-Invariant Hyperbolic Chirp Mode (AUV Cruise) */
} SonarOperatingMode_t;

/* SNR thresholds for closed-loop waveform selection [dB * 10] */
#define SNR_LOW_THRESHOLD_DB_X10    80    /*  8.0 dB — switch to lower frequency */
#define SNR_HIGH_THRESHOLD_DB_X10  220    /* 22.0 dB — switch to higher frequency */

/* Minimum pings at same mode before re-evaluating (hysteresis / dwell) */
#define MIN_MODE_DWELL_PINGS  3U

typedef struct {
    SonarOperatingMode_t mode_id;
    uint32_t f_carrier_hz;
    uint32_t f_base_hz;
    uint32_t f_top_hz;
    uint16_t tim6_arr;
    uint8_t  pulse_ms;
    int32_t  alpha_E7;        /* one-way alpha [dB/m * 1e7] */
    const char *name;
} AcousticProfile_t;

static const AcousticProfile_t ACOUSTIC_PROFILES[4] = {
    { (SonarOperatingMode_t)0U, 450000UL, 2000UL, 30000UL, 359U, 2U, 1813739L, "HIGH_RES_450KHZ" },
    { (SonarOperatingMode_t)1U, 250000UL, 1000UL, 20000UL, 719U, 5U, 1299984L, "BALANCED_250KHZ" },
    { (SonarOperatingMode_t)2U, 100000UL, 500UL, 8000UL, 1439U, 10U, 565528L, "DEEP_PEN_100KHZ" },
    { (SonarOperatingMode_t)3U, 250000UL, 1000UL, 20000UL, 719U, 5U, 1299984L, "HFM_DOPPLER_250K" },
};

/*
 * Safe lower-frequency fallback table.
 * DO NOT use enum arithmetic (mode + 1) — use this table.
 * Index [i] = next-lower-frequency mode from mode i.
 */
static const uint8_t LOWER_FREQ_MODE[4] = {
    1,   /* from HIGH_RES  -> BALANCED  */
    2,   /* from BALANCED  -> DEEP_PEN  */
    3,   /* from DEEP_PEN  -> HFM_DOPPLER (lowest available) */
    3    /* from HFM       -> stay at 3 */
};

static const uint8_t HIGHER_FREQ_MODE[4] = {
    0,   /* from HIGH_RES  -> stay at 0 */
    0,   /* from BALANCED  -> HIGH_RES  */
    1,   /* from DEEP_PEN  -> BALANCED  */
    1    /* from HFM       -> BALANCED  */
};

#endif /* ACOUSTIC_PROFILES_H */
