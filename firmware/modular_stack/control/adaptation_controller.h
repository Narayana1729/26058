/*
 * adaptation_controller.h — Closed-Loop Waveform Adaptation Controller
 * ======================================================================
 *
 * Controller architecture:
 *
 *   EchoFeatures (from previous ping)
 *          ↓
 *   SNR threshold evaluation
 *          ↓  (with dwell guard — MIN_MODE_DWELL_PINGS)
 *   select_next_profile()
 *          ↓
 *   SonarOperatingMode_t (for next ping)
 *
 * Mode ordering is EXPLICIT (do not infer from arithmetic):
 *
 *   Mode 0 — highest frequency (best resolution, most absorption)
 *   Mode 1 — balanced
 *   Mode 2 — deep penetration
 *   Mode 3 — HFM Doppler-tolerant
 *
 * Hysteresis: MIN_MODE_DWELL_PINGS prevents rapid oscillation near threshold.
 *
 * See also: firmware/generated/acoustic_profiles.h
 *           LOWER_FREQ_MODE[], HIGHER_FREQ_MODE[]
 */

#ifndef ADAPTATION_CONTROLLER_H
#define ADAPTATION_CONTROLLER_H

#include <stdint.h>
#include "../dsp/echo_features.h"
#include "../generated/acoustic_profiles.h"

/* -------------------------------------------------------------------------
 * Controller thresholds
 * -------------------------------------------------------------------------
 */
#define SNR_LOW_DB     8.0f   /* Switch to lower frequency if SNR < this */
#define SNR_HIGH_DB   22.0f   /* Switch to higher frequency if SNR > this */

/* Minimum pings at same mode before re-evaluating
 * Prevents mode oscillation near threshold.
 * Increase if rapid mode changes occur during hardware test.
 */
#define MIN_MODE_DWELL_PINGS  3U

/* -------------------------------------------------------------------------
 * Controller state — one instance per sonar channel
 * -------------------------------------------------------------------------
 */
typedef struct
{
    SonarOperatingMode_t current_mode;   /* Active mode for current ping */
    uint32_t             dwell_count;    /* Pings elapsed at current_mode */
    float                last_snr_db;    /* SNR from most recent ping     */
} AdaptationState_t;

/* Initialise controller to a known state */
static inline void adaptation_init(AdaptationState_t *s,
                                   SonarOperatingMode_t initial_mode)
{
    s->current_mode = initial_mode;
    s->dwell_count  = 0U;
    s->last_snr_db  = 0.0f;
}

/* -------------------------------------------------------------------------
 * select_next_profile()
 *
 * Call after each ping's echo has been processed into EchoFeatures.
 * Updates state and returns the mode to use for the NEXT ping.
 *
 * @param s      Adaptation state (updated in place)
 * @param echo   Echo features from the most recent ping
 * @return       Mode for next ping
 * -------------------------------------------------------------------------
 */
static inline SonarOperatingMode_t
select_next_profile(AdaptationState_t *s, const EchoFeatures_t *echo)
{
    if (!echo_features_valid(echo))
    {
        /* No valid echo — stay at current mode, don't count as dwell */
        return s->current_mode;
    }

    s->last_snr_db = echo->snr_db;

    /* --- Hysteresis guard: dwell at current mode --- */
    if (s->dwell_count < MIN_MODE_DWELL_PINGS)
    {
        s->dwell_count++;
        return s->current_mode;
    }

    /* --- SNR evaluation --- */
    SonarOperatingMode_t next = s->current_mode;

    if (echo->snr_db < SNR_LOW_DB)
    {
        /* SNR too low → go to lower frequency via safe lookup table */
        next = (SonarOperatingMode_t)LOWER_FREQ_MODE[s->current_mode];
    }
    else if (echo->snr_db > SNR_HIGH_DB)
    {
        /* SNR has margin → try higher frequency via safe lookup table */
        next = (SonarOperatingMode_t)HIGHER_FREQ_MODE[s->current_mode];
    }
    /* else: SNR within acceptable band → hold current mode */

    /* --- Update state --- */
    if (next != s->current_mode)
    {
        s->current_mode = next;
        s->dwell_count  = 0U;   /* Reset dwell on mode change */
    }
    else
    {
        s->dwell_count++;
    }

    return s->current_mode;
}

#endif /* ADAPTATION_CONTROLLER_H */
