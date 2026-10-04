"""
Software-Defined Sonar Transmitter - Hydroacoustic Propagation & Absorption Engine
Autonomous SDR Sonar Payload (SIH 2026 — Problem Statement 26058)
Description:
  Harmonized Dual-Layer Sonar Architecture:
  - Layer 1 (Baseband DAC): 1 kHz to 20 kHz Tukey-windowed LFM Chirp at Fs = 100 kHz (matches 15.9 kHz LTspice filter)
  - Layer 2 (Carrier Band): Francois-Garrison Seawater Absorption from 1 kHz up to 500 kHz (100 kHz deep pen vs 450 kHz high res)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==============================================================================
# 1. FRANCOIS-GARRISON (1982) OCEAN SOUND ABSORPTION MODEL
# ==============================================================================

def sound_speed(T, S, D):
    """
    Mackenzie (1981) sound speed equation in seawater [m/s].
    """
    c = (1448.96 + 4.591 * T - 5.304e-2 * (T**2) + 2.374e-4 * (T**3)
         + 1.340 * (S - 35.0) + 1.630e-2 * D + 1.675e-7 * (D**2)
         - 1.025e-2 * T * (S - 35.0) - 7.139e-13 * T * (D**3))
    return c

def francois_garrison_absorption(f_khz, T=15.0, S=35.0, D=10.0, pH=8.0):
    """
    Calculates total sound absorption coefficient alpha (dB/km) using Francois-Garrison (1982).
    """
    f = np.asarray(f_khz, dtype=float)
    c = sound_speed(T, S, D)
    
    # 1. Boric Acid Contribution (B(OH)3) - Dominates 0.1 to 10 kHz (Baseband Region)
    A1 = (8.86 / c) * 10**(0.78 * pH - 5.0)
    P1 = 1.0
    f1 = 2.8 * np.sqrt(S / 35.0) * 10**(4.0 - 1245.0 / (T + 273.0))
    alpha_boric = A1 * P1 * (f1 * (f**2)) / (f1**2 + f**2)
    
    # 2. Magnesium Sulfate Contribution (MgSO4) - Dominates 10 kHz to 300 kHz (Sonar Carrier Region)
    A2 = 21.44 * (S / c) * (1.0 + 0.025 * T)
    P2 = 1.0 - 1.37e-4 * D + 6.2e-9 * (D**2)
    f2 = (8.17 * 10**(8.0 - 1990.0 / (T + 273.0))) / (1.0 + 0.0018 * (S - 35.0))
    alpha_mgso4 = A2 * P2 * (f2 * (f**2)) / (f2**2 + f**2)
    
    # 3. Pure Water Viscous Contribution - Dominates above 300 kHz
    if T <= 20.0:
        A3 = 4.937e-4 - 2.59e-5 * T + 9.11e-7 * (T**2) - 1.5e-8 * (T**3)
    else:
        A3 = 3.964e-4 - 1.146e-5 * T + 1.45e-7 * (T**2) - 6.5e-10 * (T**3)
    P3 = 1.0 - 3.83e-5 * D + 4.9e-10 * (D**2)
    alpha_pure_water = A3 * P3 * (f**2)
    
    alpha_total = alpha_boric + alpha_mgso4 + alpha_pure_water
    return alpha_total, alpha_boric, alpha_mgso4, alpha_pure_water

def turbidity_scattering_loss(f_khz, NTU):
    """
    Acoustic scattering attenuation due to suspended sediment/particulates [dB/km].
    """
    return 0.0015 * NTU * (f_khz ** 1.3)

# ==============================================================================
# 2. FULL-SPECTRUM EVALUATION (1 kHz to 500 kHz)
# ==============================================================================

freqs_broad = np.linspace(1, 500, 1000)  # 1 kHz to 500 kHz broad sweep
alpha_clean, a_b, a_mg, a_w = francois_garrison_absorption(freqs_broad, T=15.0, S=35.0, D=20.0, pH=8.0)
alpha_turb_50 = alpha_clean + turbidity_scattering_loss(freqs_broad, NTU=50)
alpha_turb_150 = alpha_clean + turbidity_scattering_loss(freqs_broad, NTU=150)

# Transmission Loss calculations
ranges_m = np.linspace(10, 500, 300)

def transmission_loss(R_m, alpha_db_km):
    R_km = R_m / 1000.0
    return 20.0 * np.log10(R_m) + alpha_db_km * R_km

alpha_baseband_20k = francois_garrison_absorption(20.0, T=15.0, S=35.0, D=20.0)[0]
alpha_100k_mud = francois_garrison_absorption(100.0, T=15.0, S=35.0, D=20.0)[0] + turbidity_scattering_loss(100.0, 150)
alpha_450k_mud = francois_garrison_absorption(450.0, T=15.0, S=35.0, D=20.0)[0] + turbidity_scattering_loss(450.0, 150)

tl_baseband = transmission_loss(ranges_m, alpha_baseband_20k)
tl_100k_mud = transmission_loss(ranges_m, alpha_100k_mud)
tl_450k_mud = transmission_loss(ranges_m, alpha_450k_mud)

# Create Master Harmonized 3-Panel Verification Figure
fig, axs = plt.subplots(3, 1, figsize=(10, 10))
plt.subplots_adjust(hspace=0.45)

# Panel 1: Full-Spectrum Francois-Garrison Chemical Components
axs[0].plot(freqs_broad, alpha_clean, 'w-', lw=2.5, label='Total Seawater Absorption α(f)')
axs[0].plot(freqs_broad, a_mg, '#00D4FF', lw=1.5, ls='--', label='MgSO4 Relaxation (10-300 kHz)')
axs[0].plot(freqs_broad, a_w, '#FF8C38', lw=1.5, ls=':', label='Water Viscosity (>300 kHz)')
axs[0].plot(freqs_broad, a_b, '#00E676', lw=1.2, ls='-.', label='Boric Acid B(OH)3 (<10 kHz)')
axs[0].axvspan(1, 20, color='#00D4FF', alpha=0.15, label='STM32 Baseband DAC Band (1-20 kHz)')
axs[0].set_title("1. Ocean Sound Absorption Breakdown (Full Spectrum 1 kHz to 500 kHz)", fontsize=11, fontweight='bold')
axs[0].set_xlabel("Frequency (kHz)")
axs[0].set_ylabel("Absorption α (dB/km)")
axs[0].set_xlim([1, 500])
axs[0].set_ylim([0.05, 200])
axs[0].set_xscale('log')
axs[0].set_yscale('log')
axs[0].grid(True, which="both", ls="--", alpha=0.4)
axs[0].legend(loc='upper left', fontsize=8.5)

# Panel 2: Turbidity Impact & Adaptive Operating Bands
axs[1].plot(freqs_broad, alpha_clean, '#00E676', lw=2.0, label='Clean Seawater (0 NTU)')
axs[1].plot(freqs_broad, alpha_turb_50, '#FFC107', lw=2.0, label='Moderate Turbidity (50 NTU)')
axs[1].plot(freqs_broad, alpha_turb_150, '#FF5252', lw=2.2, label='Heavy Murky Water (150 NTU)')
axs[1].axvline(20, color='#00E676', ls='--', lw=1.5, label='Baseband Top: 20 kHz (Low Absorption)')
axs[1].axvline(100, color='#00D4FF', ls='--', lw=1.5, label='Mode 2 Carrier: 100 kHz (Mud Penetration)')
axs[1].axvline(450, color='#E040FB', ls='--', lw=1.5, label='Mode 0 Carrier: 450 kHz (High Resolution)')
axs[1].set_title("2. Acoustic Loss vs Turbidity Across Sonar Operating Bands", fontsize=11, fontweight='bold')
axs[1].set_xlabel("Frequency (kHz)")
axs[1].set_ylabel("Total Loss α (dB/km)")
axs[1].set_xlim([1, 500])
axs[1].set_xscale('log')
axs[1].set_yscale('log')
axs[1].grid(True, which="both", ls="--", alpha=0.4)
axs[1].legend(loc='upper left', fontsize=8.5)

# Panel 3: Transmission Loss vs Range in Murky Water
axs[2].plot(ranges_m, tl_baseband, '#00E676', lw=2.2, label='20 kHz Baseband (Long Range: >500m penetration)')
axs[2].plot(ranges_m, tl_100k_mud, '#00D4FF', lw=2.2, label='100 kHz Ultrasonic Carrier in Mud (Penetrates ~300m)')
axs[2].plot(ranges_m, tl_450k_mud, '#FF5252', lw=2.2, ls='--', label='450 kHz Ultrasonic Carrier in Mud (Fails at >80m)')
axs[2].axhline(80.0, color='#8A99AD', ls=':', label='Receiver Detection Limit (80 dB TL)')
axs[2].set_title("3. Transmission Loss vs Range: Baseband & Carrier Performance in Murky Water", fontsize=11, fontweight='bold')
axs[2].set_xlabel("Sonar Range (meters)")
axs[2].set_ylabel("Transmission Loss (dB)")
axs[2].set_xlim([10, 500])
axs[2].set_ylim([20, 140])
axs[2].grid(True, ls="--", alpha=0.5)
axs[2].legend(loc='lower right', fontsize=8.5)

import os
simul_dir = os.path.dirname(__file__)
plt.savefig(os.path.join(simul_dir, "ocean_absorption_verification.png"), dpi=300)
print(f"🖼️ '{os.path.join(simul_dir, 'ocean_absorption_verification.png')}' updated and harmonized with baseband/carrier bands!")

# ==============================================================================
# 3. HARMONIZED C-HEADER (ocean_adaptation_table.h)
# ==============================================================================

header_code = """/*
 * Software-Defined Sonar Transmitter - Ocean Adaptation Lookup Table
 * Generated by Person 1 (DSP Math & Acoustic Physics Lead) - Day 2
 * 
 * Harmonized Dual-Layer Architecture:
 * - Baseband Generation: 1 kHz to 20 kHz LFM Chirp at Fs = 100 kHz (Nyquist = 50 kHz)
 * - Analog Reconstruction Filter Cutoff: 15.9 kHz (4th-order Sallen-Key)
 * - Acoustic Carrier Bands: 100 kHz (Deep Penetration) vs 450 kHz (High Resolution)
 */

#ifndef OCEAN_ADAPTATION_TABLE_H
#define OCEAN_ADAPTATION_TABLE_H

#include <stdint.h>

#define TURBIDITY_CLEAR_THRESHOLD     1240  // < 15 NTU   (~1.0V ADC) -> Mode 0: 450 kHz High Res
#define TURBIDITY_MUDDY_THRESHOLD     2480  // > 100 NTU  (~2.0V ADC) -> Mode 2: 100 kHz Deep Penetration

#ifndef SONAR_PROFILE_COUNT
#define SONAR_PROFILE_COUNT 6
#endif

// Operating Modes Definition
typedef enum {
    SONAR_MODE_HIGH_RES     = 0,   // High-Resolution Imaging Mode (Clear Water)
    SONAR_MODE_BALANCED     = 1,   // Standard Balanced Mode (Moderate Water)
    SONAR_MODE_DEEP_PEN     = 2,   // Deep Penetration Mode (Murky / Muddy Water)
    SONAR_MODE_EFM_GEOMETRIC= 3,   // Geometric / Exponential Sweep
    SONAR_MODE_HFM_DOPPLER  = 4,   // Doppler-Invariant Hyperbolic Chirp
    SONAR_MODE_BARKER_BPSK  = 5    // Phase-Coded Barker 13-bit Pulse
} SonarOperatingMode_t;

// Backward-compatibility and semantic aliases
#define SONAR_MODE_LFM_HIGH_RES  SONAR_MODE_HIGH_RES
#define SONAR_MODE_LFM_BALANCED  SONAR_MODE_BALANCED
#define SONAR_MODE_LFM_DEEP_PEN  SONAR_MODE_DEEP_PEN

// Structure for Adaptive Parameters
typedef struct {
    uint32_t carrier_freq_hz;  // Acoustic Carrier Frequency (Hz)
    uint32_t baseband_f0_hz;   // Baseband Start Frequency (Hz)
    uint32_t baseband_f1_hz;   // Baseband End Frequency (Hz)
    uint16_t tim6_arr;         // STM32 TIM6 Auto-Reload Register for Sample Clock
    uint16_t pulse_duration_ms;// Pulse length in milliseconds
    const char* mode_name;     // Name string for debug UART / LCD
    const char* modulation_type; // Modulation family (LFM, EFM, HFM, BPSK)
} SonarAdaptationProfile_t;

// Profiles mapped to 72 MHz STM32 Timer Clock
static const SonarAdaptationProfile_t SONAR_PROFILES[SONAR_PROFILE_COUNT] = {
    // Mode 0: High Resolution (Clear Water) -> fs = 200 kHz (ARR = 359), Baseband = 2k-30kHz
    { 450000, 2000, 30000,  359,  2, "HIGH_RES_450KHZ", "LFM" },
    
    // Mode 1: Balanced (Normal Water) -> fs = 100 kHz (ARR = 719), Baseband = 1k-20kHz
    { 250000, 1000, 20000,  719,  5, "BALANCED_250KHZ", "LFM" },
    
    // Mode 2: Deep Penetration (Muddy Water) -> fs = 50 kHz (ARR = 1439), Baseband = 500-8kHz
    { 100000,  500,  8000, 1439, 10, "DEEP_PEN_100KHZ", "LFM" },

    // Mode 3: Geometric / Exponential Sweep
    { 250000, 1000, 20000,  719,  5, "GEOMETRIC_SWEEP", "EFM" },

    // Mode 4: Doppler-Invariant Hyperbolic Chirp
    { 200000, 1000, 15000,  719,  6, "HFM_DOPPLER_INV", "HFM" },

    // Mode 5: Phase-Coded 13-bit Barker
    { 150000, 5000,  5000,  719,  4, "BARKER_BPSK_13", "BPSK" }
};

/**
 * @brief Evaluates raw 12-bit ADC Turbidity voltage and returns optimal Sonar Profile
 * @param adc_raw: Value from PA0 (0 to 4095)
 * @return SonarOperatingMode_t (0, 1, or 2)
 */
static inline SonarOperatingMode_t evaluate_ocean_adaptation(uint16_t adc_raw) {
    if (adc_raw < TURBIDITY_CLEAR_THRESHOLD) {
        return SONAR_MODE_HIGH_RES;
    } else if (adc_raw > TURBIDITY_MUDDY_THRESHOLD) {
        return SONAR_MODE_DEEP_PEN;
    } else {
        return SONAR_MODE_BALANCED;
    }
}

#endif // OCEAN_ADAPTATION_TABLE_H
"""

target_lut = os.path.join(os.path.dirname(simul_dir), "firmware", "include", "ocean_adaptation_table.h")
with open(target_lut, "w") as f:
    f.write(header_code)

print(f"📁 '{target_lut}' updated and harmonized successfully!")
