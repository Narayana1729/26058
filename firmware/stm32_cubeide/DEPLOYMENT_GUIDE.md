==============================================================================
OCEAN-SDR(TM) NUCLEO-F401RE / F446RE / G474RE HARDWARE PACKAGE (FOR STM32CUBEIDE)
Smart India Hackathon 2026 (SIH 2026) — Problem Statement 26058
Demonstration Level: Closed-Loop Software-Defined Sonar Transmitter & Power Governor
Contract Authority: STRICTLY ALIGNED WITH MASTER_PIN_MAP.md
==============================================================================

Files in this folder:
1. main.c                       -> Core Embedded Firmware (True 12-Bit DAC + PWM + Two-Stage Governor)
2. main.h                       -> Authoritative Pin Definitions & Register Configurations
3. chirp_lut_8bit.h             -> 8-bit Rescaled Waveform Bank (0-255 for PWM-DAC)
4. chirp_lut.h                  -> 12-bit Waveform Bank (0-4095 for Hardware DAC)
5. DEPLOYMENT_GUIDE.md         -> This Guide

------------------------------------------------------------------------------
AUTHORITATIVE HARDWARE PIN CONNECTIONS (NUCLEO-64):
------------------------------------------------------------------------------
1. ACOUSTIC TRANSMITTER SIGNAL CHAIN (DAC & AFE):
  • PA4  (Arduino A2)  : DAC1_OUT1 True 12-bit Hardware DAC Acoustic Signal Output
                         -> Feeds 4th-Order Active Sallen-Key Low-Pass Filter
                         -> Connect Filter Output to Oscilloscope Channel 1!
  • PA6  (Arduino D12) : ADC1_IN6 Supply Rail Voltage Monitor (100k/10k divider)
                         [Alt Mode: TIM3_CH1 328 kHz PWM Carrier for Dual DAC/PWM bench demo]

2. ELECTRICAL METROLOGY & HEALTH SENSING (CLOSED-LOOP STAGE 2 GOVERNOR):
  • PA5  (Arduino D13) : ADC1_IN5 Transmit Current Sense from INA180 (Vout = 2.0 * Itx)
  • PA6  (Arduino D12) : ADC1_IN6 Rail Voltage Monitor (100k/10k precision divider, 0-33V -> 0-3.0V)
  • PA7  (Arduino D11) : ADC1_IN7 PA Heatsink Thermal Sensor (TMP36, 10mV/°C, 750mV @ 25°C)

3. ENVIRONMENTAL SENSORY INGRESS (STAGE 1 PRIOR GENERATION):
  • PA0  (Arduino A0)  : ADC1_IN0 TSW-20 Turbidity via 10kΩ/20kΩ divider (0-5V -> 0-3.3V)
                         -> Adapts Waveform Modulation Family (LFM / CW), Carrier, and Bandwidth
  • PA1  (Arduino A1)  : ADC1_IN1 Hydrostatic Depth Sensor (MS5837 / Simulation Potentiometer)
                         -> Adapts Pulse Duration (0.39 ms to 1.56 ms, full bandwidth preserved)
  • PC0  (Arduino A5)  : ADC1_IN10 Salinity / Ambient Calibration Potentiometer (0 to 42 PSU)
  • PA10 (Arduino D2)  : DS18B20 1-Wire Digital Water Temperature Probe (4.7kΩ pullup to 3.3V)

4. AUDIBLE BENCH DEMONSTRATION & SUBSEA HUD:
  • PB6  (Arduino D10) : TIM4_CH1 Independent Audible Speaker Output
                         -> Connect directly to 8Ω Speaker / Piezo / TDA2030 Amplifier for Jury Audibility!
  • PB8  (Arduino D15) : SSD1306 0.96" OLED I2C SCL (Clock)
  • PB9  (Arduino D14) : SSD1306 0.96" OLED I2C SDA (Data)
  • PC13 (Blue B1 Btn) : User Pushbutton (Short: Autonomous Plume Mission | Long: Melodic Octave Demo)
  • PA2 / PA3 (ST-Link): USART2 TX/RX @ 115200 baud to Web Ground Station Dashboard

------------------------------------------------------------------------------
CRITICAL NOTE ON OP-AMP POWER SUPPLY:
------------------------------------------------------------------------------
  • Standard TL072 op-amps require a minimum supply of ±4.5V (or >7V single-supply).
  • DO NOT power TL072 from the Nucleo 3.3V pin! It will clip or latch up.
  • Power arrangement:
      Option A (Recommended): Dual ±9V supplies (two 9V batteries, ground to Nucleo GND).
      Option B: Single +9V/+12V external supply with a 100kΩ/100kΩ resistive divider
                virtual ground (buffered with a 10µF cap) biasing the input to Vcc/2.
      Option C (If strictly 3.3V single-supply): Use 3.3V rail-to-rail op-amps (OPA350 / MCP6002 / LMV358).

------------------------------------------------------------------------------
FAST 2-MINUTE FLASH INSTRUCTIONS (STM32CubeIDE):
------------------------------------------------------------------------------
Step 1: Open STM32CubeIDE.
Step 2: File -> New -> STM32 Project -> Select Board: "NUCLEO-F401RE" (or F446RE / G474RE).
Step 3: Keep Default Peripheral Initialization (Yes).
Step 4: In the project explorer on the left:
        - Copy 'main.c' into 'Core/Src/main.c' (replace existing).
        - Copy 'main.h' into 'Core/Inc/main.h' (replace existing).
        - Copy 'chirp_lut_8bit.h' into 'Core/Inc/chirp_lut_8bit.h'.
        - Copy 'chirp_lut.h' into 'Core/Inc/chirp_lut.h'.
Step 5: Plug the STM32 Nucleo board into USB.
Step 6: Click the GREEN PLAY / RUN Button (Ctrl + F11).
        STM32CubeIDE will compile and flash the board in 5 seconds!

------------------------------------------------------------------------------
VERIFYING ON THE BENCH (OSCILLOSCOPE & GROUND STATION):
------------------------------------------------------------------------------
1. Oscilloscope on PA4 (DAC Output):
   Observe the clean 12-bit analog chirp with discrete Tukey tapering and zero-DC clicks.
2. Oscilloscope after Sallen-Key Filter:
   Observe the smooth sinusoidal reconstruction with -80 dB/decade roll-off.
3. Turn Turbidity Pot (PA0):
   Watch the system transition across High-Res (450 kHz) -> Balanced (250 kHz) -> Deep Pen (100 kHz).
4. Monitor Web Ground Station:
   Connect ST-Link COM port @ 115200 baud to view real-time NMEA packet:
   $SONAR,MODE,TURB,TURB_OK,DEPTH,SNR,ALPHA,AUDIO_MODE,TEMP,SAL,TEMP_OK,DEPTH_OK,SAL_OK,PULSE_LEN,AMP_PCT,DMA_CNT,V_RAIL,I_PEAK,E_PULSE,E_REM,E_BUDGET,T_PA,THM_STATE,GOV_MODE
5. Deplete Energy Budget (Press 'R' to reset):
   Observe the Two-Stage Governor throttle duration by 25% (Balanced), throttle amplitude by 40% (Conservative),
   and shut down before battery exhaustion or thermal runaway (>85°C)!
==============================================================================
