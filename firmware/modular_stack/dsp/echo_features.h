/*
 * echo_features.h — Echo Feature Extraction and Signal Chain Structs
 * ===================================================================
 *
 * Signal chain:
 *
 *   RAW ADC BUFFER
 *       ↓
 *   MATCHED FILTER (cross-correlation with chirp reference)
 *       ↓
 *   PEAK DETECTION
 *       ↓
 *   EchoFeatures  ← populated by extract_echo_features()
 *       ↓
 *   ┌───────────────────┬───────────────────┐
 *   ↓                   ↓
 * classify_seabed()  select_next_profile()
 *   ↓                   ↓
 * SeabedType_t      SonarOperatingMode_t
 *
 * Key design rule:
 *   predicted_tl_db  = model output (40*log10(R) + 2*alpha*R)
 *   measured_loss_db = derived from echo amplitude (measurement)
 *   These are two different quantities and must NOT be mixed.
 */

#ifndef ECHO_FEATURES_H
#define ECHO_FEATURES_H

#include <stdint.h>
#include <math.h>
#include "../generated/tgc_lut.h"

/* -------------------------------------------------------------------------
 * EchoFeatures — populated after each matched-filter evaluation
 * -------------------------------------------------------------------------
 */
typedef struct
{
    /* Range estimation */
    float    range_m;               /* Estimated one-way range [m]; c*t/2            */

    /* Signal amplitude */
    float    peak_amplitude;        /* Matched-filter peak output [linear, normalised] */
    float    noise_rms;             /* RMS of noise region before echo [linear]       */

    /* SNR */
    float    snr_db;                /* 20*log10(peak/noise_rms) [dB]                  */

    /* Propagation model output (DO NOT confuse with measured_loss_db) */
    float    predicted_tl_db;       /* Model: 40*log10(R) + 2*alpha(f)*R  [dB]       */

    /* Measured propagation loss (from echo amplitude, after TGC) */
    float    measured_loss_db;      /* -20*log10(echo_amp / tx_amp) corrected [dB]    */

    /* Reflection estimate (model-corrected) */
    float    estimated_reflection_coeff; /* echo amp corrected for TL; compare to Rp table */

} EchoFeatures_t;

/* -------------------------------------------------------------------------
 * Validity check
 * -------------------------------------------------------------------------
 */
static inline int echo_features_valid(const EchoFeatures_t *e)
{
    return (e != 0)
        && isfinite(e->range_m)
        && (e->range_m > 0.0f)
        && isfinite(e->snr_db)
        && isfinite(e->peak_amplitude)
        && (e->noise_rms > 0.0f);
}

/* -------------------------------------------------------------------------
 * Forward Interface: Echo Feature Extractor (V2 Receiver Coupling Interface)
 * Reserved for Phase V2 hydrophone integration; interface signature defined for stack coupling.
 *
 * @param adc_buf      Raw 12-bit ADC samples (DMA buffer)
 * @param chirp_ref    Reference chirp LUT (from chirp_lut.h, current mode)
 * @param n_samples    Number of samples (512)
 * @param mode         Current operating mode (0-3)
 * @param out          Output EchoFeatures struct to populate
 * @return             0 on success, -1 if no valid echo found
 * -------------------------------------------------------------------------
 */
int extract_echo_features(const uint16_t    *adc_buf,
                          const uint16_t    *chirp_ref,
                          uint32_t           n_samples,
                          uint8_t            mode,
                          EchoFeatures_t    *out);

#endif /* ECHO_FEATURES_H */
