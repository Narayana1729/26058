/*
 * test_sonar_stack.c — Comprehensive C Compilation & Functional Verification
 * Tests:
 * 1. Single umbrella header include (#include "sonar_system.h")
 * 2. 4-profile LUT access (SONAR_LUT_BANK)
 * 3. Physics TGC lookup (TGC_DAC_CODES)
 * 4. Seabed substrate classification (classify_seabed_nearest)
 * 5. Closed-loop adaptation controller (select_next_profile with dwell)
 */

#include <stdio.h>
#include <assert.h>
#include "sonar_system.h"

int main(void)
{
    printf("========================================================\n");
    printf("🌊 COMPREHENSIVE EMBEDDED SONAR C-STACK VERIFICATION\n");
    printf("========================================================\n\n");

    // 1. Verify Operating Profiles & ARR registers
    printf("1. Verifying Operating Profiles:\n");
    for (int i = 0; i < 4; i++) {
        const AcousticProfile_t *p = &ACOUSTIC_PROFILES[i];
        printf("   [Mode %d] %-18s | fc: %6u kHz | ARR: %4u | alpha: %.2f dB/km\n",
               (int)p->mode_id, p->name, (unsigned int)(p->f_carrier_hz / 1000), p->tim6_arr, (float)p->alpha_E7 / 10000.0f);
        assert((int)p->mode_id == i);
    }

    // 2. Verify Chirp LUT Bank
    printf("\n2. Verifying Chirp LUT Bank Boundaries:\n");
    for (int m = 0; m < SONAR_PROFILE_COUNT; m++) {
        const uint16_t *lut = SONAR_LUT_BANK[m];
        printf("   [Mode %d] Start Sample: %u | Mid Sample: %u | End Sample: %u\n",
               m, lut[0], lut[256], lut[511]);
        assert(lut[0] == 2048);   // Zero-DC click boundary
        assert(lut[511] == 2048); // Zero-DC click boundary
    }

    // 3. Verify Physics-Derived TGC Table
    printf("\n3. Verifying Physics-Derived TGC Table:\n");
    for (int m = 0; m < 4; m++) {
        uint16_t dac_min = TGC_DAC_CODES[m][0];
        uint16_t dac_max = TGC_DAC_CODES[m][511];
        printf("   [Mode %d] Sample 0 (Near-Field): DAC=%u | Sample 511 (Far-Field): DAC=%u\n",
               m, dac_min, dac_max);
        assert(dac_max > dac_min);
        assert(dac_max <= TGC_DAC_MAX_CODE);
    }

    // 4. Verify Seabed Substrate Classification
    printf("\n4. Verifying Seabed Substrate Classification (Nearest Ref):\n");
    // Test case A: Strong echo from rock (BL = 2.8 dB)
    SeabedType_t s_rock = classify_seabed_nearest(2.85f, 15.0f);
    printf("   Measured BL = 2.85 dB  --> Classified as: %s (Type: %d)\n",
           SEABED_REF_TABLE[s_rock - 1].name, s_rock);
    assert(s_rock == SEABED_ROCK);

    // Test case B: Moderate echo from sand (BL = 9.0 dB)
    SeabedType_t s_sand = classify_seabed_nearest(9.0f, 15.0f);
    printf("   Measured BL = 9.00 dB  --> Classified as: %s (Type: %d)\n",
           SEABED_REF_TABLE[s_sand - 1].name, s_sand);
    assert(s_sand == SEABED_SAND);

    // Test case C: Weak echo from soft mud (BL = 25.5 dB)
    SeabedType_t s_mud = classify_seabed_nearest(25.5f, 15.0f);
    printf("   Measured BL = 25.50 dB --> Classified as: %s (Type: %d)\n",
           SEABED_REF_TABLE[s_mud - 1].name, s_mud);
    assert(s_mud == SEABED_SOFT_MUD);

    // 5. Verify Closed-Loop Adaptation Controller
    printf("\n5. Verifying Closed-Loop Adaptation Controller (SNR + Dwell):\n");
    AdaptationState_t state;
    adaptation_init(&state, SONAR_MODE_HIGH_RES);
    assert(state.current_mode == SONAR_MODE_HIGH_RES);

    EchoFeatures_t echo = {
        .range_m = 2.5f,
        .peak_amplitude = 1200.0f,
        .noise_rms = 50.0f,
        .snr_db = 5.0f, // LOW SNR (< 8.0 dB) -> Should trigger lower frequency after dwell
        .predicted_tl_db = 22.0f,
        .measured_loss_db = 23.0f,
        .estimated_reflection_coeff = 0.35f
    };

    // Ping 1 (Dwell 0 -> 1)
    SonarOperatingMode_t next = select_next_profile(&state, &echo);
    printf("   Ping 1 (SNR=5.0dB): Mode=%d (Dwell=%u, Reason: Dwell Guard)\n", next, state.dwell_count);
    assert(next == SONAR_MODE_HIGH_RES);

    // Ping 2 (Dwell 1 -> 2)
    next = select_next_profile(&state, &echo);
    printf("   Ping 2 (SNR=5.0dB): Mode=%d (Dwell=%u, Reason: Dwell Guard)\n", next, state.dwell_count);
    assert(next == SONAR_MODE_HIGH_RES);

    // Ping 3 (Dwell 2 -> 3)
    next = select_next_profile(&state, &echo);
    printf("   Ping 3 (SNR=5.0dB): Mode=%d (Dwell=%u, Reason: Dwell Guard)\n", next, state.dwell_count);
    assert(next == SONAR_MODE_HIGH_RES);

    // Ping 4 (Dwell = 3 >= MIN_DWELL -> Switch to LOWER_FREQ_MODE[0] = BALANCED)
    next = select_next_profile(&state, &echo);
    printf("   Ping 4 (SNR=5.0dB): Mode=%d (Dwell=%u, TRIGGERED: Switched to BALANCED!)\n", next, state.dwell_count);
    assert(next == SONAR_MODE_BALANCED);

    printf("\n========================================================\n");
    printf("✅ ALL C-STACK HEADERS ARE 100%% VERIFIED & COMPILING CLEANLY!\n");
    printf("========================================================\n");
    return 0;
}
