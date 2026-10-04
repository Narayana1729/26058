/*
 * sonar_system.h — Master Umbrella Header for Software-Defined Sonar
 * Generated: 2026-08-29 13:24 UTC
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
#include "../include/chirp_lut.h"
#include "generated/tgc_lut.h"
#include "generated/seabed_table.h"
#include "dsp/echo_features.h"
#include "control/adaptation_controller.h"

#endif /* SONAR_SYSTEM_H */
