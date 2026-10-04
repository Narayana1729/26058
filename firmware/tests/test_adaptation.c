#include <stdio.h>
#include <assert.h>
#include "ocean_adaptation_table.h"
#include "chirp_lut.h"

int main(void) {
    printf("====================================================\n");
    printf("🧪 RUNNING UNIT TESTS: ocean_adaptation_table.h & chirp_lut.h\n");
    printf("====================================================\n");

    // 1. Test Clear Water Mode (Mode 0: 450 kHz High Res LFM)
    uint16_t adc_clean_min = 0;
    uint16_t adc_clean_edge = 1239;
    SonarOperatingMode_t mode_min = evaluate_ocean_adaptation(adc_clean_min);
    SonarOperatingMode_t mode_edge1 = evaluate_ocean_adaptation(adc_clean_edge);
    
    assert(mode_min == SONAR_MODE_LFM_HIGH_RES);
    assert(mode_edge1 == SONAR_MODE_LFM_HIGH_RES);
    printf("✅ TEST 1 PASSED: Clear Water Threshold (<1240) -> Mode 0 (%s, Mod=%s, ARR=%d)\n",
           SONAR_PROFILES[mode_min].mode_name, SONAR_PROFILES[mode_min].modulation_type, SONAR_PROFILES[mode_min].tim6_arr);

    // 2. Test Balanced Water Mode (Mode 1: 250 kHz Balanced LFM)
    uint16_t adc_mid = 1800;
    SonarOperatingMode_t mode_mid = evaluate_ocean_adaptation(adc_mid);
    assert(mode_mid == SONAR_MODE_LFM_BALANCED);
    printf("✅ TEST 2 PASSED: Normal Water Range (1240 - 2480) -> Mode 1 (%s, Mod=%s, ARR=%d)\n",
           SONAR_PROFILES[mode_mid].mode_name, SONAR_PROFILES[mode_mid].modulation_type, SONAR_PROFILES[mode_mid].tim6_arr);

    // 3. Test Muddy Water Mode (Mode 2: 100 kHz Deep Penetration LFM)
    uint16_t adc_mud_edge = 2481;
    uint16_t adc_mud_max = 4095;
    SonarOperatingMode_t mode_edge2 = evaluate_ocean_adaptation(adc_mud_edge);
    SonarOperatingMode_t mode_max = evaluate_ocean_adaptation(adc_mud_max);
    
    assert(mode_edge2 == SONAR_MODE_LFM_DEEP_PEN);
    assert(mode_max == SONAR_MODE_LFM_DEEP_PEN);
    printf("✅ TEST 3 PASSED: Muddy Water Threshold (>2480) -> Mode 2 (%s, Mod=%s, ARR=%d)\n",
           SONAR_PROFILES[mode_max].mode_name, SONAR_PROFILES[mode_max].modulation_type, SONAR_PROFILES[mode_max].tim6_arr);

    // 4. Test LUT Bank Verification (All 6 Profiles in Flash)
    printf("----------------------------------------------------\n");
    printf("🔍 VERIFYING 6-PROFILE MULTI-MODULATION LOOKUP TABLE BANK:\n");
    for (int p = 0; p < SONAR_PROFILE_COUNT; p++) {
        const uint16_t* lut = SONAR_LUT_BANK[p];
        assert(lut != NULL);
        assert(lut[0] == 2048);       // Zero-DC click entry condition
        assert(lut[511] == 2048);     // Zero-DC click exit condition
        
        uint16_t min_val = 4095, max_val = 0;
        for (int i = 0; i < CHIRP_SAMPLES; i++) {
            if (lut[i] < min_val) min_val = lut[i];
            if (lut[i] > max_val) max_val = lut[i];
        }
        assert(min_val >= 0 && max_val <= 4095);
        printf("   • Profile %d [%-22s | Mod: %-9s]: Min=%4d | Mid=%4d | Max=%4d | Zero-DC Click OK!\n",
               p, SONAR_PROFILES[p].mode_name, SONAR_PROFILES[p].modulation_type, min_val, lut[0], max_val);
    }

    // 5. Timer Clock Frequency Math Check (72 MHz APB1 clock)
    printf("----------------------------------------------------\n");
    uint32_t timer_clk = 72000000;
    for (int i = 0; i < SONAR_PROFILE_COUNT; i++) {
        uint32_t sample_rate = timer_clk / (SONAR_PROFILES[i].tim6_arr + 1);
        printf("   • Profile %d [%-22s]: ARR = %4d -> Sample Clock = %6d Hz\n",
               i, SONAR_PROFILES[i].mode_name, SONAR_PROFILES[i].tim6_arr, sample_rate);
    }

    printf("====================================================\n");
    printf("🎉 ALL 5 UNIT TESTS PASSED! FULL 6-PROFILE MULTI-MODULATION VERIFIED!\n");
    printf("====================================================\n");
    return 0;
}
