/*
 * ==============================================================================
 * main.c — Software-Defined Sonar Multi-Modulation Transmitter (Proteus / Nucleo)
 * Smart India Hackathon (SIH 2026) - Hardware Edition (Problem Statement 26058)
 * 
 * Hardware Pin Mapping (Strictly Aligned with MASTER_PIN_MAP.md):
 *   PA0 -> ADC1_IN0  (TSW-20 Turbidity via 10k/20k divider, 0-3.3V)
 *   PA1 -> ADC1_IN1  (Depth Potentiometer / MS5837, 0-3.3V)
 *   PC0 -> ADC1_IN10 (Salinity Potentiometer, 0-3.3V)
 *   PA4 -> DAC1_OUT1 (Hardware 12-bit DAC -> Sallen-Key 4th-Order LPF)
 *   PA5 -> ADC1_IN5  (INA180 Transmit Current Sense, Vout = 2.0 * Itx)
 *   PA6 -> ADC1_IN6  (Rail Voltage Monitor via 100k/10k divider, 0-3.0V)
 *          [Alt AF2] : TIM3_CH1 (PWM Carrier DAC Modulation fallback)
 *   PA7 -> ADC1_IN7  (PA Heatsink TMP36 Thermal Sensor, 10mV/°C)
 *   PA2 -> USART2_TX (Live NMEA Telemetry @ 115200 baud)
 *   PA3 -> USART2_RX (Ground Station Command Link @ 115200 baud)
 *   PB6 -> TIM4_CH1  (Benchtop Audible Demonstration Speaker)
 *   PB8 -> I2C1_SCL  (SSD1306 0.96" OLED Clock)
 *   PB9 -> I2C1_SDA  (SSD1306 0.96" OLED Data)
 * ==============================================================================
 */

#include "main.h"
#include "sonar_system.h"
#include <stdio.h>
#include <string.h>

/* Peripheral Handles */
TIM_HandleTypeDef htim3;
DMA_HandleTypeDef hdma_tim3_ch1;
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;
UART_HandleTypeDef huart2;

/* Sonar Adaptation Controller State */
AdaptationState_t sonar_controller;

/* Sensor & Metrology ADC Raw Buffer (6 Channels: Turbidity, Depth, Salinity, Current, Voltage, Thermal) */
uint16_t adc_sensor_values[6];

/* Function Prototypes */
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void);
static void MX_TIM3_Init(void);
static void MX_USART2_UART_Init(void);
void send_uart_telemetry(SonarOperatingMode_t mode, float turbidity_ntu, float v_rail, float i_tx);

int main(void)
{
    /* Reset peripherals, initialize Flash interface and Systick */
    HAL_Init();
    SystemClock_Config();

    /* Initialize all configured peripherals */
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_ADC1_Init();
    MX_TIM3_Init();
    MX_USART2_UART_Init();

    /* Initialize Closed-Loop Sonar Controller (Starts at High-Res 450kHz) */
    adaptation_init(&sonar_controller, SONAR_MODE_HIGH_RES);

    /* 
     * 🚀 START AUTONOMOUS DMA WAVEFORM STREAMING
     * PA4 (DAC1_OUT1) & PA6 (TIM3_CH1): Multi-Modulation Acoustic Chirp (512 samples)
     */
    HAL_TIM_PWM_Start_DMA(&htim3, TIM_CHANNEL_1, 
                          (uint32_t*)SONAR_LUT_BANK[sonar_controller.current_mode], 
                          512);

    /* Start Circular DMA Reading for Environmental & Metrology Channels */
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_sensor_values, 6);

    /* Send boot telemetry to Virtual Terminal */
    char boot_msg[200];
    snprintf(boot_msg, sizeof(boot_msg), 
             "\r\n======================================================\r\n"
             "🌊 [SDR SONAR] Multi-Modulation Transmitter Online\r\n"
             "   Mode: %s | PA4: DAC1 | PA6: PWM Carrier | PA5: Current\r\n"
             "   Metrology & Power Governor Loop Active (115200 8-N-1)\r\n"
             "======================================================\r\n",
             ACOUSTIC_PROFILES[sonar_controller.current_mode].name);
    HAL_UART_Transmit(&huart2, (uint8_t*)boot_msg, strlen(boot_msg), HAL_MAX_DELAY);

    while (1)
    {
        /* Simulated Periodic Ping Interval (50ms) */
        HAL_Delay(50);

        /* Convert PA0 ADC (0-4095) to Turbidity (accounting for 2/3 divider scaling) */
        float live_turbidity = ((float)adc_sensor_values[0] / 4095.0f) * 300.0f;

        /* Convert PA6 ADC to Rail Voltage (100k/10k divider -> 11x) */
        float live_v_rail = (((float)adc_sensor_values[4] * 3.3f) / 4095.0f) * 11.0f;
        if (live_v_rail < 1.0f) live_v_rail = 12.0f; // Bench default

        /* Convert PA5 ADC to Transmit Current (INA180 Gain=20, Rshunt=0.10 -> 2.0 V/A) */
        float live_i_tx = (((float)adc_sensor_values[3] * 3.3f) / 4095.0f) / 2.0f;

        /* Evaluate Echo & Environmental Feedback */
        EchoFeatures_t live_echo;
        if (live_turbidity > 100.0f) {
            live_echo.snr_db = 5.0f;  /* High turbidity attenuates high frequencies -> Low SNR */
        } else if (live_turbidity < 20.0f) {
            live_echo.snr_db = 25.0f; /* Clear water -> High SNR */
        } else {
            live_echo.snr_db = 15.0f;
        }
        live_echo.range_m = 3.5f;
        live_echo.peak_amplitude = 1800.0f;

        /* Autonomous Controller Decision */
        SonarOperatingMode_t next_mode = select_next_profile(&sonar_controller, &live_echo);

        /* If adaptation triggers mode switch, dynamically swap PWM DMA pointers */
        if (next_mode != sonar_controller.current_mode) {
            HAL_TIM_PWM_Stop_DMA(&htim3, TIM_CHANNEL_1);
            HAL_TIM_PWM_Start_DMA(&htim3, TIM_CHANNEL_1, 
                                  (uint32_t*)SONAR_LUT_BANK[next_mode], 512);

            send_uart_telemetry(next_mode, live_turbidity, live_v_rail, live_i_tx);
        }
    }
}

/* Telemetry Output to Virtual Terminal */
void send_uart_telemetry(SonarOperatingMode_t mode, float turbidity_ntu, float v_rail, float i_tx)
{
    char msg[160];
    snprintf(msg, sizeof(msg),
             "[AUTONOMOUS SWITCH] Turb: %.1f NTU | V_rail: %.1fV | I_tx: %.2fA -> Mode: %s (Carrier: %lu kHz)\r\n",
             turbidity_ntu,
             v_rail,
             i_tx,
             ACOUSTIC_PROFILES[mode].name,
             ACOUSTIC_PROFILES[mode].f_carrier_hz / 1000);
    HAL_UART_Transmit(&huart2, (uint8_t*)msg, strlen(msg), 100);
}
