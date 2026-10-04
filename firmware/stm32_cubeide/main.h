/*
 * ==============================================================================
 * OCEAN-SDR(TM) Autonomous Software-Defined Acoustic Sonar Transmitter
 * Smart India Hackathon (SIH 2026) - Problem Statement 26058
 * File: main.h
 * Target: STM32 Nucleo-64 (STM32G474RE / STM32F446RE / STM32F401RE)
 * Hardware Contract: Aligned 100% with MASTER_PIN_MAP.md
 * ==============================================================================
 */

#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* ==============================================================================
 * AUTHORITATIVE HARDWARE PIN ASSIGNMENTS (MASTER_PIN_MAP.md)
 * ==============================================================================
 */

/* --- 1. Environmental Sensory Stage (Stage 1 Prior Generation) --- */
#define TURBIDITY_ADC_PIN           GPIO_PIN_0      /* PA0 (A0): TSW-20 Turbidity via 10k/20k divider (0-3.3V) */
#define TURBIDITY_ADC_GPIO_PORT     GPIOA
#define DEPTH_POT_PIN               GPIO_PIN_1      /* PA1 (A1): Hydrostatic Depth (MS5837 / Potentiometer) */
#define DEPTH_POT_GPIO_PORT         GPIOA
#define SALINITY_POT_PIN            GPIO_PIN_0      /* PC0 (A5): Salinity / Ambient Calibration Potentiometer */
#define SALINITY_POT_GPIO_PORT      GPIOC
#define DS18B20_ONEWIRE_PIN         GPIO_PIN_10     /* PA10 (D2): Dallas 1-Wire Water Temp Probe (4.7k pullup) */
#define DS18B20_ONEWIRE_GPIO_PORT   GPIOA

/* --- 2. Acoustic Sonar Transmitter Stage --- */
#define SONAR_DAC_PIN               GPIO_PIN_4      /* PA4 (A2): Hardware 12-bit DAC1_OUT1 -> Sallen-Key LPF */
#define SONAR_DAC_GPIO_PORT         GPIOA
#define SONAR_PWM_PIN               GPIO_PIN_4      /* PA4 Alternate: Timer PWM fallback on boards without DAC */
#define SONAR_PWM_GPIO_PORT         GPIOA

/* --- 3. Electrical Metrology & Hardware Health Sensing (Stage 2 Feedback) --- */
#define CURRENT_SENSE_ADC_PIN       GPIO_PIN_5      /* PA5 (D13): INA180 Shunt Current Sense (0-1.65A -> 0-3.3V) */
#define CURRENT_SENSE_GPIO_PORT     GPIOA
#define RAIL_VOLTAGE_ADC_PIN        GPIO_PIN_6      /* PA6 (D12): Supply Rail 100k/10k Divider (0-33V -> 0-3.0V) */
#define RAIL_VOLTAGE_GPIO_PORT      GPIOA
#define PA_THERMAL_ADC_PIN          GPIO_PIN_7      /* PA7 (D11): PA Heatsink TMP36 Sensor (10mV/°C, 750mV@25°C) */
#define PA_THERMAL_GPIO_PORT        GPIOA

/* --- 4. Bench Audio Demo & Telemetry HUD --- */
#define SPEAKER_PWM_PIN             GPIO_PIN_6      /* PB6 (D10): TIM4_CH1 -> Benchtop Audio Speaker / Transducer */
#define SPEAKER_PWM_GPIO_PORT       GPIOB
#define OLED_SCL_PIN                GPIO_PIN_8      /* PB8 (D15): I2C1 SCL (Clock) */
#define OLED_SCL_GPIO_PORT          GPIOB
#define OLED_SDA_PIN                GPIO_PIN_9      /* PB9 (D14): I2C1 SDA (Data) */
#define OLED_SDA_GPIO_PORT          GPIOB

/* --- 5. Virtual COM Port Telemetry & UI Button --- */
#define USART_TX_PIN                GPIO_PIN_2      /* PA2 (D1): ST-Link Virtual COM TX (115200 8-N-1) */
#define USART_TX_GPIO_PORT          GPIOA
#define USART_RX_PIN                GPIO_PIN_3      /* PA3 (D0): ST-Link Virtual COM RX (Ground Station commands) */
#define USART_RX_GPIO_PORT          GPIOA
#define B1_USER_BUTTON_PIN          GPIO_PIN_13     /* PC13: Blue User Button (Mission Plume & Demo toggle) */
#define B1_USER_BUTTON_GPIO_PORT    GPIOC

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
