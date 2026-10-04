# 💻 Embedded Firmware Architecture
### Autonomous Software-Defined Sonar Transmitter (STM32 ARM Cortex-M)

This directory houses the embedded software stack, hardware peripheral configurations, mathematical lookup tables, and host unit testbenches for the real-time sonar transmitter payload.

---

## 📁 Directory Architecture

```
firmware/
├── stm32_cubeide/                 # Standalone bare-metal CubeIDE project (Target MCU)
│   ├── main.c                     # Primary firmware loop (DMA DAC, 6-Ch ADC, Governor, HUD)
│   ├── main.h                     # Pin definitions & peripheral handles
│   ├── chirp_lut.h                # 12-bit unsigned DAC lookup table (512 samples)
│   ├── chirp_lut_8bit.h           # 8-bit DAC fallback lookup table
│   └── DEPLOYMENT_GUIDE.md        # Flashing & pin wiring guide (adheres to MASTER_PIN_MAP.md)
│
├── modular_stack/                 # Portable C drivers & algorithm layer
│   ├── sonar_system.h             # Master umbrella include
│   ├── main.c                     # Modular non-blocking executive loop
│   ├── control/                   # Adaptation controller & dwell guards
│   ├── dsp/                       # Waveform definitions & echo feature structs
│   └── generated/                 # Pre-computed acoustic profiles & substrate tables
│
├── include/                       # Authoritative waveform banks & ocean adaptation tables
│   ├── chirp_lut.h                # 6-Profile multi-modulation waveform bank
│   ├── chirp_lut_8bit.h           # 8-bit waveform bank
│   └── ocean_adaptation_table.h   # Turbidity thresholds & operating profiles
│
└── tests/                         # Host-compiled C verification harnesses
    ├── test_two_stage_power_governor.c # Power budget governor & thermal cutoff testbench
    ├── test_adaptation.c              # Ocean mode transition & lookup bank testbench
    └── test_sonar_stack.c             # Modular stack compilation & memory testbench
```

---

## 🧪 Running Embedded Unit Tests Locally

The firmware algorithms are written in clean ANSI C99 and compile cleanly on any host machine under `-Wall -Wextra -Werror`:

```bash
# 1. Test Power Budget Governor & Thermal State Machine
gcc -Wall -Wextra -Werror firmware/tests/test_two_stage_power_governor.c -o /tmp/test_gov
/tmp/test_gov

# 2. Test Ocean Mode Selection & 6-Profile Waveform Bank
gcc -Wall -Wextra -Werror -I firmware/include firmware/tests/test_adaptation.c -o /tmp/test_adapt
/tmp/test_adapt

# 3. Test Modular Sonar C-Stack
gcc -Wall -Wextra -Werror -I firmware/modular_stack -I firmware firmware/tests/test_sonar_stack.c -o /tmp/test_stack
/tmp/test_stack
```

---

## ⚡ Flashing the Nucleo-64 Target Board

Follow [`stm32_cubeide/DEPLOYMENT_GUIDE.md`](file:///Users/srimannarayanadeevi/SIH%202026/SIH%20Hardware/firmware/stm32_cubeide/DEPLOYMENT_GUIDE.md) to deploy the binary via ST-LINK V2/V3.
