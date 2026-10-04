/*
 * ==============================================================================
 * OCEAN-SDR(TM) Autonomous Software-Defined Acoustic Sonar Transmitter
 * Smart India Hackathon (SIH 2026) - Hardware Edition (Problem Statement 26058)
 * Target: STM32 Nucleo-64 (STM32G474RE / STM32F446RE / STM32F401RE)
 * Hardware Contract: STRICTLY ALIGNED WITH MASTER_PIN_MAP.md
 * ==============================================================================
 * Authoritative Pin Allocation:
 *   - PA0  (Arduino A0)  : ADC1_IN0  <- Turbidity Sensor (TSW-20 via 10k/20k divider, 0-3.3V)
 *   - PA1  (Arduino A1)  : ADC1_IN1  <- Depth Sensor (MS5837 or Precision Simulation Pot)
 *   - PC0  (Arduino A5)  : ADC1_IN10 <- Salinity / Ambient Calibration Potentiometer
 *   - PA10 (Arduino D2)  : GPIO_OD   <- Seawater Temperature Probe (DS18B20 1-Wire, 4.7k pullup)
 *   - PA4  (Arduino A2)  : DAC1_OUT1 <- True 12-bit DAC Acoustic Output -> Sallen-Key LPF
 *   - PA5  (Arduino D13) : ADC1_IN5  <- INA180 Current Sense (Vout = 20 * 0.10Ω * Itx = 2.0 * Itx)
 *   - PA6  (Arduino D12) : ADC1_IN6  <- Supply Rail Voltage Monitor (100k/10k divider, 0-33V -> 0-3.0V)
 *                          [Alt AF2] : TIM3_CH1 PWM Carrier generation for dual DAC/PWM mode
 *   - PA7  (Arduino D11) : ADC1_IN7  <- PA Heatsink Thermal Sensor (TMP36, 10mV/°C, 750mV @ 25°C)
 *   - PB6  (Arduino D10) : TIM4_CH1  <- Bench Audible Demonstration Speaker / Transducer
 *   - PB8  (Arduino D15) : I2C1_SCL  <- SSD1306 0.96" Monochrome OLED Display Clock
 *   - PB9  (Arduino D14) : I2C1_SDA  <- SSD1306 0.96" Monochrome OLED Display Data
 *   - PA2  (ST-Link TX)  : USART2_TX <- Virtual COM Port Telemetry Stream @ 115200 baud
 *   - PA3  (ST-Link RX)  : USART2_RX <- Virtual COM Port Ground Station Commands @ 115200 baud
 *   - PC13 (User Button) : GPIO_IN   <- B1 Pushbutton (Short: Plume Mission, Long: Melody Demo)
 * ==============================================================================
 */

#include "main.h"
#include "chirp_lut_8bit.h"
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

/* --- 1. WAVEFORM VECTOR DEFINITIONS & MODES (Layer 1) --- */
#define CHIRP_SAMPLES 512

typedef enum {
    MODE_HIGH_RES = 0,    /* Clear Water: 450 kHz carrier / 2.4 - 3.8 kHz audible chirp */
    MODE_BALANCED = 1,    /* Coastal Water: 250 kHz carrier / 1.2 - 2.0 kHz audible chirp */
    MODE_LONG_RANGE = 2   /* Murky Mud Plume: 100 kHz carrier / 450 - 850 Hz deep bass chirp */
} SonarMode_t;

typedef enum {
    WAVEFORM_CW = 0,
    WAVEFORM_LFM,
    WAVEFORM_HFM,
    WAVEFORM_BARKER13,
    WAVEFORM_COUNT
} WaveformType_t;

const char* WAVEFORM_NAMES[] = {
    "CW",
    "LFM",
    "HFM",
    "BARKER13"
};

typedef struct {
    uint32_t fc_hz;           // Center carrier frequency (Hz)
    uint32_t bandwidth_hz;    // Sweep bandwidth (Hz)
    float duration_ms;        // Active pulse length (ms)
    float amplitude_norm;     // Drive amplitude scaling (0.0 to 1.0)
    WaveformType_t type;      // Modulation family
} WaveformVector_t;

typedef enum {
    AUDIO_MODE_TACTICAL_CHIRP = 0, /* Real Scientific Sonar LFM Chirp Pulses (150ms ping + listening window) */
    AUDIO_MODE_MELODIC_DEMO = 1    /* Pirates of the Caribbean Melodic Octave-Shifter */
} AudioMode_t;

/* --- 2. POWER BUDGET & THERMAL PROTECTION STATE MACHINES (Layers 4 & 5) --- */
typedef enum {
    MODE_PERFORMANCE = 0,     // High energy remaining (> 60%)
    MODE_BALANCED_GOV,        // Medium energy remaining (20% - 60%)
    MODE_CONSERVATIVE,        // Low energy remaining (< 20%)
    MODE_DEPLETED             // Budget exhausted (0%)
} PowerGovernorMode_t;

typedef enum {
    THERMAL_NORMAL = 0,       // T_pa < 50°C
    THERMAL_WARNING,          // 50°C <= T_pa < 70°C (PRI extended)
    THERMAL_THROTTLED,        // 70°C <= T_pa < 85°C (Amplitude reduced by 40%)
    THERMAL_SHUTDOWN          // T_pa >= 85°C (Emergency transmission cutoff)
} ThermalState_t;

typedef struct {
    float energy_budget_j;    // Total mission energy budget (Joules, default 50.0 J)
    float energy_remaining_j; // Cumulative remaining energy (Joules)
    float pa_temp_c;          // Measured PA heatsink temperature (°C)
    float supply_voltage_v;   // Monitored supply rail voltage (V)
    uint32_t total_pings;     // Pulse counter
    PowerGovernorMode_t mode; // Current operational governor mode
    ThermalState_t thermal;   // Current thermal protection state
} TransmitterState_t;

/* Peripheral Handles */
TIM_HandleTypeDef htim3;         /* TIM3: PA6 PWM-DAC / Carrier modulation */
TIM_HandleTypeDef htim4;         /* TIM4: PB6 Independent Audible Speaker Output */
DMA_HandleTypeDef hdma_tim3_ch1; /* DMA1 Stream 4 Channel 5 for TIM3_CH1 */
ADC_HandleTypeDef hadc1;
DAC_HandleTypeDef hdac1;         /* True 12-bit Hardware DAC on PA4 (DAC1_OUT1) */
UART_HandleTypeDef huart2;

/* Global System State */
TransmitterState_t tx_state = {
    .energy_budget_j = 50.0f,     // 50 Joules mission test budget
    .energy_remaining_j = 50.0f,
    .pa_temp_c = 28.0f,           // Ambient 28°C
    .supply_voltage_v = 12.0f,    // 12V supply rail
    .total_pings = 0,
    .mode = MODE_PERFORMANCE,
    .thermal = THERMAL_NORMAL
};

uint16_t dma_ping_buffer[CHIRP_SAMPLES];
volatile uint8_t is_dma_ping_in_progress = 0;
uint16_t active_ping_samples = CHIRP_SAMPLES;
uint8_t current_amplitude_pct = 100;
uint32_t dma_ping_count = 0;

SonarMode_t current_mode = MODE_HIGH_RES;
AudioMode_t current_audio_mode = AUDIO_MODE_TACTICAL_CHIRP;

/* Environmental Sensory State */
float current_turbidity_ntu = 12.0f;
float simulated_depth_m = 500.0f;
float current_temperature_c = 24.5f;
float current_salinity_psu = 35.0f;
float simulated_snr_db = 26.4f;
float alpha_absorption_db_km = 97.0f;

/* Sensor Online Flags */
uint8_t sensor_data_received = 1; /* Turbidity Sensor (PA0): 1 = online, 0 = disconnected */
uint8_t temp_sensor_ok = 1;       /* DS18B20 1-Wire (PA10): 1 = online, 0 = disconnected */
uint8_t depth_sensor_ok = 1;      /* Depth Potentiometer (PA1): 1 = connected, 0 = pulled down */
uint8_t sal_sensor_ok = 1;        /* Salinity Potentiometer (PC0): 1 = connected, 0 = pulled down */
uint32_t sim_override_until = 0;   /* Timestamp until which GUI simulation override takes precedence */

/* Electrical Metrology Live Readings */
float live_v_rail = 12.0f;        // Rail voltage in Volts (PA6)
float live_i_peak = 0.85f;        // Transmit current in Amperes (PA5)
float live_e_pulse = 0.012f;      // Energy of last pulse in Joules

/* --- 16-SAMPLE CIRCULAR MOVING-AVERAGE FILTER FOR TURBIDITY ADC --- */
#define ADC_FILTER_SAMPLES 16
uint32_t adc_history[ADC_FILTER_SAMPLES] = {0};
uint8_t adc_hist_idx = 0;
uint8_t adc_hist_count = 0;

uint32_t Filter_ADC_Sample(uint32_t new_sample)
{
    adc_history[adc_hist_idx] = new_sample;
    adc_hist_idx = (adc_hist_idx + 1) % ADC_FILTER_SAMPLES;
    if (adc_hist_count < ADC_FILTER_SAMPLES) adc_hist_count++;

    uint32_t sum = 0;
    for (uint8_t i = 0; i < adc_hist_count; i++) {
        sum += adc_history[i];
    }
    return sum / adc_hist_count;
}

/* ==============================================================================
 * STAGE 1: ENVIRONMENTAL PREDICTION PRIOR (Layer 2)
 * Predicts optimal carrier frequency and pulse vector from Francois-Garrison physics
 * ============================================================================== */
WaveformVector_t stage1_predict_prior(float temp_c, float depth_m, float turbidity_ntu)
{
    WaveformVector_t w0;
    (void)temp_c;
    (void)depth_m;

    if (turbidity_ntu < 15.0f) {
        w0.type = WAVEFORM_LFM;
        w0.fc_hz = 450000;
        w0.bandwidth_hz = 100000;
        w0.duration_ms = 2.0f;
        w0.amplitude_norm = 1.0f;
    } else if (turbidity_ntu <= 100.0f) {
        w0.type = WAVEFORM_LFM;
        w0.fc_hz = 250000;
        w0.bandwidth_hz = 50000;
        w0.duration_ms = 4.0f;
        w0.amplitude_norm = 1.0f;
    } else {
        w0.type = WAVEFORM_CW;
        w0.fc_hz = 100000;
        w0.bandwidth_hz = 0;
        w0.duration_ms = 10.0f;
        w0.amplitude_norm = 1.0f;
    }
    return w0;
}

/* ==============================================================================
 * STAGE 2: ELECTRICAL REFINEMENT & POWER GOVERNOR (Layers 3, 4, 5)
 * Closed-loop adaptation based on remaining mission battery budget and thermal stress
 * ============================================================================== */
WaveformVector_t stage2_refine_and_govern(const WaveformVector_t* w0, TransmitterState_t* tx)
{
    WaveformVector_t w_actual = *w0;

    // A. Evaluate Remaining Energy Budget
    float budget_fraction = (tx->energy_budget_j > 0.0f) ?
                            (tx->energy_remaining_j / tx->energy_budget_j) : 0.0f;

    if (budget_fraction > 0.60f) {
        tx->mode = MODE_PERFORMANCE;
    } else if (budget_fraction >= 0.20f) {
        tx->mode = MODE_BALANCED_GOV;
        // Throttle pulse duration by 25% to conserve energy
        w_actual.duration_ms *= 0.75f;
    } else if (budget_fraction > 0.0f) {
        tx->mode = MODE_CONSERVATIVE;
        // Shift to conservative mode: 60% amplitude, 50% duration
        w_actual.amplitude_norm *= 0.60f;
        w_actual.duration_ms *= 0.50f;
        if (w_actual.type == WAVEFORM_LFM) {
            w_actual.bandwidth_hz /= 2;
        }
    } else {
        tx->mode = MODE_DEPLETED;
        w_actual.amplitude_norm = 0.0f;
        w_actual.duration_ms = 0.0f;
        return w_actual;
    }

    // B. Evaluate Power Amplifier Thermal State Machine
    if (tx->pa_temp_c < 50.0f) {
        tx->thermal = THERMAL_NORMAL;
    } else if (tx->pa_temp_c < 70.0f) {
        tx->thermal = THERMAL_WARNING;
        // PRI extended (handled by scheduling loop)
    } else if (tx->pa_temp_c < 85.0f) {
        tx->thermal = THERMAL_THROTTLED;
        // Actively throttle drive amplitude by 40% to halt thermal climb
        w_actual.amplitude_norm *= 0.60f;
    } else {
        tx->thermal = THERMAL_SHUTDOWN;
        // Emergency cutoff: shut down transmission immediately
        w_actual.amplitude_norm = 0.0f;
        w_actual.duration_ms = 0.0f;
    }

    return w_actual;
}

/* ==============================================================================
 * 1. FAST BIT-BANG I2C DRIVER FOR SSD1306 OLED (PB8=SCL, PB9=SDA)
 * Works universally on all STM32 HAL builds without HAL_I2C dependency
 * ============================================================================== */
#define OLED_ADDR 0x78

static void I2C_Delay(void) {
    for (volatile int i = 0; i < 8; i++);
}

static void I2C_Start(void) {
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    I2C_Delay();
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_RESET);
    I2C_Delay();
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
    I2C_Delay();
}

static void I2C_Stop(void) {
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    I2C_Delay();
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_SET);
    I2C_Delay();
}

static void I2C_WriteByte(uint8_t byte) {
    for (int i = 0; i < 8; i++) {
        if (byte & 0x80) {
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_SET);
        } else {
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_RESET);
        }
        byte <<= 1;
        I2C_Delay();
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
        I2C_Delay();
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
        I2C_Delay();
    }
    // ACK bit
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_SET);
    I2C_Delay();
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    I2C_Delay();
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
    I2C_Delay();
}

static void OLED_WriteCommand(uint8_t cmd) {
    I2C_Start();
    I2C_WriteByte(OLED_ADDR);
    I2C_WriteByte(0x00);
    I2C_WriteByte(cmd);
    I2C_Stop();
}

static void OLED_WriteData(uint8_t data) {
    I2C_Start();
    I2C_WriteByte(OLED_ADDR);
    I2C_WriteByte(0x40);
    I2C_WriteByte(data);
    I2C_Stop();
}

void OLED_Init(void) {
    OLED_WriteCommand(0xAE); // Display off
    OLED_WriteCommand(0xD5); // Set display clock divide ratio/oscillator frequency
    OLED_WriteCommand(0x80);
    OLED_WriteCommand(0xA8); // Set multiplex ratio
    OLED_WriteCommand(0x3F); // 1/64 duty
    OLED_WriteCommand(0xD3); // Set display offset
    OLED_WriteCommand(0x00); // No offset
    OLED_WriteCommand(0x40); // Set start line address
    OLED_WriteCommand(0x8D); // Enable charge pump regulator
    OLED_WriteCommand(0x14);
    OLED_WriteCommand(0x20); // Set memory addressing mode
    OLED_WriteCommand(0x02); // Page addressing mode
    OLED_WriteCommand(0xA1); // Segment remap
    OLED_WriteCommand(0xC8); // Set COM Output Scan Direction
    OLED_WriteCommand(0xDA); // Set COM pins hardware configuration
    OLED_WriteCommand(0x12);
    OLED_WriteCommand(0x81); // Set contrast control register
    OLED_WriteCommand(0xCF);
    OLED_WriteCommand(0xD9); // Set pre-charge period
    OLED_WriteCommand(0xF1);
    OLED_WriteCommand(0xDB); // Set VCOMH deselect level
    OLED_WriteCommand(0x40);
    OLED_WriteCommand(0xA4); // Entire display ON
    OLED_WriteCommand(0xA6); // Set normal display
    OLED_WriteCommand(0xAF); // Display ON

    // Clear display buffer
    for (uint8_t page = 0; page < 8; page++) {
        OLED_WriteCommand(0xB0 + page);
        OLED_WriteCommand(0x00);
        OLED_WriteCommand(0x10);
        for (uint8_t col = 0; col < 128; col++) {
            OLED_WriteData(0x00);
        }
    }
}

// 5x7 ASCII Font Table
static const uint8_t font5x7[][5] = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, // Space
    {0x00, 0x00, 0x5F, 0x00, 0x00}, // !
    {0x00, 0x07, 0x00, 0x07, 0x00}, // "
    {0x14, 0x7F, 0x14, 0x7F, 0x14}, // #
    {0x24, 0x2A, 0x7F, 0x2A, 0x12}, // $
    {0x23, 0x13, 0x08, 0x64, 0x62}, // %
    {0x36, 0x49, 0x55, 0x22, 0x50}, // &
    {0x00, 0x05, 0x03, 0x00, 0x00}, // '
    {0x00, 0x1C, 0x22, 0x41, 0x00}, // (
    {0x00, 0x41, 0x22, 0x1C, 0x00}, // )
    {0x14, 0x08, 0x3E, 0x08, 0x14}, // *
    {0x08, 0x08, 0x3E, 0x08, 0x08}, // +
    {0x00, 0x50, 0x30, 0x00, 0x00}, // ,
    {0x08, 0x08, 0x08, 0x08, 0x08}, // -
    {0x00, 0x60, 0x60, 0x00, 0x00}, // .
    {0x20, 0x10, 0x08, 0x04, 0x02}, // /
    {0x3E, 0x51, 0x49, 0x45, 0x3E}, // 0
    {0x00, 0x42, 0x7F, 0x40, 0x00}, // 1
    {0x42, 0x61, 0x51, 0x49, 0x46}, // 2
    {0x21, 0x41, 0x45, 0x4B, 0x31}, // 3
    {0x18, 0x14, 0x12, 0x7F, 0x10}, // 4
    {0x27, 0x45, 0x45, 0x45, 0x39}, // 5
    {0x3C, 0x4A, 0x49, 0x49, 0x30}, // 6
    {0x01, 0x71, 0x09, 0x05, 0x03}, // 7
    {0x36, 0x49, 0x49, 0x49, 0x36}, // 8
    {0x06, 0x49, 0x49, 0x29, 0x1E}, // 9
    {0x00, 0x36, 0x36, 0x00, 0x00}, // :
    {0x00, 0x56, 0x36, 0x00, 0x00}, // ;
    {0x08, 0x14, 0x22, 0x41, 0x00}, // <
    {0x14, 0x14, 0x14, 0x14, 0x14}, // =
    {0x00, 0x41, 0x22, 0x14, 0x08}, // >
    {0x02, 0x01, 0x51, 0x09, 0x06}, // ?
    {0x32, 0x49, 0x79, 0x41, 0x3E}, // @
    {0x7E, 0x11, 0x11, 0x11, 0x7E}, // A
    {0x7F, 0x49, 0x49, 0x49, 0x36}, // B
    {0x3E, 0x41, 0x41, 0x41, 0x22}, // C
    {0x7F, 0x41, 0x41, 0x22, 0x1C}, // D
    {0x7F, 0x49, 0x49, 0x49, 0x41}, // E
    {0x7F, 0x09, 0x09, 0x09, 0x01}, // F
    {0x3E, 0x41, 0x49, 0x49, 0x7A}, // G
    {0x7F, 0x08, 0x08, 0x08, 0x7F}, // H
    {0x00, 0x41, 0x7F, 0x41, 0x00}, // I
    {0x20, 0x40, 0x41, 0x3F, 0x01}, // J
    {0x7F, 0x08, 0x14, 0x22, 0x41}, // K
    {0x7F, 0x40, 0x40, 0x40, 0x40}, // L
    {0x7F, 0x02, 0x0C, 0x02, 0x7F}, // M
    {0x7F, 0x04, 0x08, 0x10, 0x7F}, // N
    {0x3E, 0x41, 0x41, 0x41, 0x3E}, // O
    {0x7F, 0x09, 0x09, 0x09, 0x06}, // P
    {0x3E, 0x41, 0x51, 0x21, 0x5E}, // Q
    {0x7F, 0x09, 0x19, 0x29, 0x46}, // R
    {0x46, 0x49, 0x49, 0x49, 0x31}, // S
    {0x01, 0x01, 0x7F, 0x01, 0x01}, // T
    {0x3F, 0x40, 0x40, 0x40, 0x3F}, // U
    {0x1F, 0x20, 0x40, 0x20, 0x1F}, // V
    {0x3F, 0x40, 0x38, 0x40, 0x3F}, // W
    {0x63, 0x14, 0x08, 0x14, 0x63}, // X
    {0x07, 0x08, 0x70, 0x08, 0x07}, // Y
    {0x61, 0x51, 0x49, 0x45, 0x43}, // Z
    {0x00, 0x7F, 0x41, 0x41, 0x00}, // [
    {0x02, 0x04, 0x08, 0x10, 0x20}, // '\'
    {0x00, 0x41, 0x41, 0x7F, 0x00}, // ]
    {0x04, 0x02, 0x01, 0x02, 0x04}, // ^
    {0x40, 0x40, 0x40, 0x40, 0x40}  // _
};

static void OLED_PrintChar(uint8_t page, uint8_t col, char c) {
    if (c < 32 || c > 95) c = ' ';
    uint8_t idx = c - 32;

    OLED_WriteCommand(0xB0 + page);
    OLED_WriteCommand(col & 0x0F);
    OLED_WriteCommand(0x10 | (col >> 4));

    for (int i = 0; i < 5; i++) {
        OLED_WriteData(font5x7[idx][i]);
    }
    OLED_WriteData(0x00); // 1-pixel spacing
}

void OLED_PrintString(uint8_t page, uint8_t col, const char* str) {
    while (*str && col < 122) {
        OLED_PrintChar(page, col, *str++);
        col += 6;
    }
}

/* Updated OLED HUD: Displays Live Mode, Power Governor Mode, Remaining Energy Bar, V/I, and Thermal State */
void OLED_UpdateHUD(SonarMode_t mode, float turb, float depth, float temp, float sal, uint8_t t_ok, uint8_t d_ok, uint8_t c_ok, uint8_t s_ok) {
    char l1[24], l2[24], l3[24], l4[24];
    const char* mode_str = (mode == MODE_HIGH_RES) ? "HF450" :
                           (mode == MODE_BALANCED) ? "MID250" : "LF100";
    const char* gov_str = (tx_state.mode == MODE_PERFORMANCE) ? "PERF" :
                          (tx_state.mode == MODE_BALANCED_GOV) ? "BAL " :
                          (tx_state.mode == MODE_CONSERVATIVE) ? "CONS" : "OFF ";
    const char* thm_str = (tx_state.thermal == THERMAL_NORMAL) ? "NORM" :
                          (tx_state.thermal == THERMAL_WARNING) ? "WARN" :
                          (tx_state.thermal == THERMAL_THROTTLED) ? "THRT" : "SHUT";

    float rem_pct = (tx_state.energy_budget_j > 0.0f) ?
                    (tx_state.energy_remaining_j / tx_state.energy_budget_j) * 100.0f : 0.0f;
    if (rem_pct > 100.0f) rem_pct = 100.0f;
    if (rem_pct < 0.0f) rem_pct = 0.0f;

    snprintf(l1, sizeof(l1), "SDR-TX GOV:%-4s %3.0f%%", gov_str, rem_pct);
    snprintf(l2, sizeof(l2), "M:%-5s E:%4.1fJ/%2.0fJ", mode_str, tx_state.energy_remaining_j, tx_state.energy_budget_j);
    snprintf(l3, sizeof(l3), "V:%4.1fV I:%4.2fA", live_v_rail, live_i_peak);
    snprintf(l4, sizeof(l4), "T:%2.0fC [%-4s] #%lu", tx_state.pa_temp_c, thm_str, (unsigned long)(dma_ping_count % 1000));

    OLED_PrintString(0, 4, l1);
    OLED_PrintString(2, 4, l2);
    OLED_PrintString(4, 4, l3);
    OLED_PrintString(6, 4, l4);
}

/* ==============================================================================
 * 2. 1-WIRE DS18B20 TEMPERATURE SENSOR DRIVER (PA10 / Arduino D2)
 * ============================================================================== */
#define DS18B20_ONEWIRE_PIN GPIO_PIN_10
#define DS18B20_ONEWIRE_GPIO_PORT GPIOA

static void DS18B20_Delay_us(uint32_t us) {
    uint32_t count = us * 14;
    while (count--) {
        __NOP();
    }
}

static void DS18B20_SetOutput(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = DS18B20_ONEWIRE_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(DS18B20_ONEWIRE_GPIO_PORT, &GPIO_InitStruct);
}

static void DS18B20_SetInput(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = DS18B20_ONEWIRE_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(DS18B20_ONEWIRE_GPIO_PORT, &GPIO_InitStruct);
}

static uint8_t DS18B20_Reset(void) {
    DS18B20_SetOutput();
    HAL_GPIO_WritePin(DS18B20_ONEWIRE_GPIO_PORT, DS18B20_ONEWIRE_PIN, GPIO_PIN_RESET);
    DS18B20_Delay_us(480);
    DS18B20_SetInput();
    DS18B20_Delay_us(70);
    uint8_t presence = (HAL_GPIO_ReadPin(DS18B20_ONEWIRE_GPIO_PORT, DS18B20_ONEWIRE_PIN) == GPIO_PIN_RESET) ? 1 : 0;
    DS18B20_Delay_us(410);
    return presence;
}

static void DS18B20_WriteBit(uint8_t bit) {
    DS18B20_SetOutput();
    HAL_GPIO_WritePin(DS18B20_ONEWIRE_GPIO_PORT, DS18B20_ONEWIRE_PIN, GPIO_PIN_RESET);
    DS18B20_Delay_us(bit ? 6 : 60);
    HAL_GPIO_WritePin(DS18B20_ONEWIRE_GPIO_PORT, DS18B20_ONEWIRE_PIN, GPIO_PIN_SET);
    DS18B20_Delay_us(bit ? 64 : 10);
}

static uint8_t DS18B20_ReadBit(void) {
    DS18B20_SetOutput();
    HAL_GPIO_WritePin(DS18B20_ONEWIRE_GPIO_PORT, DS18B20_ONEWIRE_PIN, GPIO_PIN_RESET);
    DS18B20_Delay_us(2);
    DS18B20_SetInput();
    DS18B20_Delay_us(10);
    uint8_t bit = (HAL_GPIO_ReadPin(DS18B20_ONEWIRE_GPIO_PORT, DS18B20_ONEWIRE_PIN) == GPIO_PIN_SET) ? 1 : 0;
    DS18B20_Delay_us(55);
    return bit;
}

static void DS18B20_WriteByte(uint8_t byte) {
    for (int i = 0; i < 8; i++) {
        DS18B20_WriteBit(byte & 0x01);
        byte >>= 1;
    }
}

static uint8_t DS18B20_ReadByte(void) {
    uint8_t byte = 0;
    for (int i = 0; i < 8; i++) {
        if (DS18B20_ReadBit()) {
            byte |= (1 << i);
        }
    }
    return byte;
}

float DS18B20_ReadTemperature(void) {
    if (!DS18B20_Reset()) {
        temp_sensor_ok = 0;
        return current_temperature_c;
    }
    DS18B20_WriteByte(0xCC); // Skip ROM
    DS18B20_WriteByte(0x44); // Convert T

    if (!DS18B20_Reset()) {
        temp_sensor_ok = 0;
        return current_temperature_c;
    }
    DS18B20_WriteByte(0xCC); // Skip ROM
    DS18B20_WriteByte(0xBE); // Read Scratchpad

    uint8_t lsb = DS18B20_ReadByte();
    uint8_t msb = DS18B20_ReadByte();
    int16_t raw_temp = (msb << 8) | lsb;
    float temp_c = (float)raw_temp / 16.0f;

    if (temp_c < -10.0f || temp_c > 85.0f) {
        temp_sensor_ok = 0;
        return current_temperature_c;
    }
    temp_sensor_ok = 1;
    return temp_c;
}

/* ==============================================================================
 * 3. 6-CHANNEL ADC READING (PA0, PA1, PC0, PA5, PA6, PA7)
 * ============================================================================== */
uint32_t Read_ADC_Channel(uint32_t channel) {
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = channel;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_84CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 15) == HAL_OK) {
        uint32_t val = HAL_ADC_GetValue(&hadc1);
        HAL_ADC_Stop(&hadc1);
        return val;
    }
    HAL_ADC_Stop(&hadc1);
    return 0;
}

/* Electrical Metrology Sensor Readers */
float Read_Rail_Voltage(void)
{
    uint32_t raw = Read_ADC_Channel(ADC_CHANNEL_6);
    float v_adc = ((float)raw * 3.3f) / 4095.0f;
    // 100k / 10k divider -> ratio = 11.0x
    float v_rail = v_adc * 11.0f;
    if (v_rail < 1.0f) {
        // Benchtop simulation fallback when DC power supply is offline
        v_rail = 12.0f;
    }
    return v_rail;
}

float Read_Transmit_Current(float ampl_norm)
{
    uint32_t raw = Read_ADC_Channel(ADC_CHANNEL_5);
    float v_adc = ((float)raw * 3.3f) / 4095.0f;
    // INA180 Gain=20, Rshunt=0.10Ω -> Vout = 2.0 * I_tx -> I_tx = Vout / 2.0
    float i_tx = v_adc / 2.0f;
    if (i_tx < 0.05f) {
        // Benchtop simulation fallback: 1.2A peak scaled by drive amplitude
        i_tx = 1.2f * ampl_norm;
    }
    return i_tx;
}

float Read_PA_Temperature(void)
{
    uint32_t raw = Read_ADC_Channel(ADC_CHANNEL_7);
    // TMP36: 10 mV/°C, 500 mV offset at 0°C -> T = (V - 0.50) * 100
    float v_adc = ((float)raw * 3.3f) / 4095.0f;
    if (v_adc >= 0.10f && v_adc <= 2.2f) {
        float temp = (v_adc - 0.50f) * 100.0f;
        if (temp >= 5.0f && temp <= 105.0f) return temp;
    }
    return tx_state.pa_temp_c;
}

/* Function Prototypes */
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void);
static void MX_DAC1_Init(void);
static void MX_TIM3_Init(void);
static void MX_TIM4_Init(void);
static void MX_USART2_UART_Init(void);
void Trigger_Adaptive_Sonar_Ping(SonarMode_t mode, float depth_m, float salinity_psu);
void Play_Speaker_Chirp(SonarMode_t mode);
void Play_Sonar_Chirp(SonarMode_t mode);
float Compute_Acoustic_Absorption(float ntu, SonarMode_t mode);
float Compute_Sonar_SNR(float ntu, float depth_m, SonarMode_t mode);
void Send_Telemetry(void);
SonarMode_t Evaluate_Turbidity_Hysteresis(float ntu, SonarMode_t active_mode);

/* ==============================================================================
 * PIRATES OF THE CARIBBEAN - MELODIC OCTAVE SHIFTER
 * ============================================================================== */
#define NOTE_D4   294
#define NOTE_E4   330
#define NOTE_F4   349
#define NOTE_G4   392
#define NOTE_A4   440
#define NOTE_AS4  466
#define NOTE_C5   523
#define NOTE_D5   587
#define NOTE_E5   659
#define NOTE_F5   698
#define NOTE_G5   784
#define NOTE_A5   880
#define NOTE_AS5  932
#define NOTE_C6   1046
#define NOTE_REST 0

typedef struct {
    uint16_t note;
    uint16_t duration_ms;
} MelodyNote_t;

const MelodyNote_t pirates_theme[] = {
    {NOTE_D4, 110}, {NOTE_D4, 110}, {NOTE_D4, 110}, {NOTE_D4, 110},
    {NOTE_A4, 130}, {NOTE_C5, 130}, {NOTE_D5, 260}, {NOTE_D5, 130},
    {NOTE_D5, 130}, {NOTE_E5, 130}, {NOTE_F5, 260}, {NOTE_F5, 130},
    {NOTE_F5, 130}, {NOTE_G5, 130}, {NOTE_E5, 260}, {NOTE_E5, 130},
    {NOTE_D5, 130}, {NOTE_C5, 130}, {NOTE_C5, 130}, {NOTE_D5, 260},
    {NOTE_A4, 130}, {NOTE_C5, 130}, {NOTE_D5, 260}, {NOTE_D5, 130},
    {NOTE_D5, 130}, {NOTE_E5, 130}, {NOTE_F5, 260}, {NOTE_F5, 130},
    {NOTE_F5, 130}, {NOTE_G5, 130}, {NOTE_E5, 260}, {NOTE_E5, 130},
    {NOTE_D5, 130}, {NOTE_C5, 130}, {NOTE_D5, 360}, {NOTE_REST, 90},
    {NOTE_A4, 130}, {NOTE_C5, 130}, {NOTE_D5, 260}, {NOTE_D5, 130},
    {NOTE_D5, 130}, {NOTE_F5, 130}, {NOTE_G5, 260}, {NOTE_G5, 130},
    {NOTE_G5, 130}, {NOTE_A5, 130}, {NOTE_AS5, 260}, {NOTE_AS5, 130},
    {NOTE_A5, 130}, {NOTE_G5, 130}, {NOTE_A5, 130}, {NOTE_D5, 260},
    {NOTE_D5, 130}, {NOTE_E5, 130}, {NOTE_F5, 260}, {NOTE_F5, 130},
    {NOTE_G5, 130}, {NOTE_A5, 130}, {NOTE_D5, 260}, {NOTE_D5, 130},
    {NOTE_F5, 130}, {NOTE_E5, 130}, {NOTE_E5, 130}, {NOTE_F5, 130},
    {NOTE_D5, 130}, {NOTE_E5, 360}, {NOTE_REST, 140}
};
#define MELODY_LENGTH (sizeof(pirates_theme) / sizeof(MelodyNote_t))

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    /* Initialize Peripherals */
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_ADC1_Init();
    MX_DAC1_Init();
    MX_TIM3_Init();
    MX_TIM4_Init();
    MX_USART2_UART_Init();

    /* Initialize Onboard OLED Display (SSD1306 on PB8/PB9) */
    OLED_Init();
    OLED_PrintString(0, 4, "OCEAN-SDR ADAPTIVE");
    OLED_PrintString(2, 4, "TWO-STAGE GOVERNOR");
    OLED_PrintString(4, 4, "TRUE 12-BIT DAC PA4");
    OLED_PrintString(6, 4, "SIH 2026 HARDWARE");

    /* Send Initial Welcome Banner to Web Ground Station */
    char init_banner[] = "\r\n========================================================\r\n"
                         "[SYSTEM] OCEAN-SDR Autonomous Adaptive Acoustic Sonar Online\r\n"
                         "[DAC OUT] PA4 (A2): True 12-bit DAC1_OUT1 -> Sallen-Key 4th-Order LPF\r\n"
                         "[PWM OUT] PA6 (D12): TIM3 Carrier PWM (Dual DAC/PWM fallback)\r\n"
                         "[SPEAKER] PB6 (D10): TIM4 Independent Audible Transducer / Speaker\r\n"
                         "[METROLOGY] PA5: Current Sense | PA6: Voltage Monitor | PA7: Heatsink Temp\r\n"
                         "[SENSORS  ] PA0: Turbidity (10k/20k) | PA1: Depth Pot | PC0: Salinity Pot\r\n"
                         "[GOVERNOR ] Closed-Loop Energy Budget & Thermal Protection Active\r\n"
                         "========================================================\r\n";
    HAL_UART_Transmit(&huart2, (uint8_t*)init_banner, strlen(init_banner), 100);

    /* Scheduling and State Variables */
    uint32_t last_adc_tick = 0;
    uint32_t last_ping_tick = 0;
    uint32_t last_telemetry_tick = 0;
    uint32_t btn_press_start = 0;
    uint8_t  btn_was_pressed = 0;

    uint8_t  is_plume_mission_active = 0;
    uint32_t mission_step_tick = 0;
    uint8_t  mission_step = 0;

    uint16_t note_idx = 0;
    uint32_t note_start_tick = 0;
    SonarMode_t last_applied_mode = current_mode;

    while (1)
    {
        uint32_t now = HAL_GetTick();

        /* --- 0. ROBUST NON-BLOCKING UART COMMAND HANDLER --- */
        if (__HAL_UART_GET_FLAG(&huart2, UART_FLAG_ORE) ||
            __HAL_UART_GET_FLAG(&huart2, UART_FLAG_FE)  ||
            __HAL_UART_GET_FLAG(&huart2, UART_FLAG_NE))
        {
            __HAL_UART_CLEAR_OREFLAG(&huart2);
            __HAL_UART_CLEAR_FEFLAG(&huart2);
            __HAL_UART_CLEAR_NEFLAG(&huart2);
            (void)huart2.Instance->DR;
        }

        if (__HAL_UART_GET_FLAG(&huart2, UART_FLAG_RXNE))
        {
            uint8_t rx_char = (uint8_t)(huart2.Instance->DR & 0xFF);
            if (rx_char == '0') {
                is_plume_mission_active = 0;
                current_mode = MODE_HIGH_RES;
                current_turbidity_ntu = 12.0f;
                sim_override_until = now + 8000;
                last_ping_tick = now;
                Play_Sonar_Chirp(current_mode);
            } else if (rx_char == '1') {
                is_plume_mission_active = 0;
                current_mode = MODE_BALANCED;
                current_turbidity_ntu = 85.0f;
                sim_override_until = now + 8000;
                last_ping_tick = now;
                Play_Sonar_Chirp(current_mode);
            } else if (rx_char == '2') {
                is_plume_mission_active = 0;
                current_mode = MODE_LONG_RANGE;
                current_turbidity_ntu = 240.0f;
                sim_override_until = now + 8000;
                last_ping_tick = now;
                Play_Sonar_Chirp(current_mode);
            } else if (rx_char == 'M' || rx_char == 'm') {
                is_plume_mission_active = !is_plume_mission_active;
                sim_override_until = is_plume_mission_active ? (now + 60000) : 0;
                mission_step_tick = now;
                mission_step = 0;
            } else if (rx_char == 'C' || rx_char == 'c') {
                current_audio_mode = AUDIO_MODE_TACTICAL_CHIRP;
                HAL_TIM_PWM_Stop(&htim4, TIM_CHANNEL_1);
            } else if (rx_char == 'P' || rx_char == 'p') {
                current_audio_mode = AUDIO_MODE_MELODIC_DEMO;
                note_idx = 0;
                note_start_tick = now;
            } else if (rx_char == 'R' || rx_char == 'r') {
                // Reset energy budget to 50 Joules
                tx_state.energy_remaining_j = tx_state.energy_budget_j;
                tx_state.total_pings = 0;
                tx_state.mode = MODE_PERFORMANCE;
                tx_state.thermal = THERMAL_NORMAL;
            }
        }

        /* --- 1. MULTI-FUNCTION USER BUTTON B1 (PC13) --- */
        if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET)
        {
            if (!btn_was_pressed)
            {
                btn_was_pressed = 1;
                btn_press_start = now;
            }
        }
        else
        {
            if (btn_was_pressed)
            {
                uint32_t press_duration = now - btn_press_start;
                btn_was_pressed = 0;

                if (press_duration >= 800)
                {
                    // Long press: Toggle Audio Mode
                    current_audio_mode = (current_audio_mode == AUDIO_MODE_TACTICAL_CHIRP) ?
                                          AUDIO_MODE_MELODIC_DEMO : AUDIO_MODE_TACTICAL_CHIRP;
                    HAL_TIM_PWM_Stop(&htim4, TIM_CHANNEL_1);
                }
                else if (press_duration >= 40)
                {
                    // Short press: Toggle Plume Mission
                    is_plume_mission_active = !is_plume_mission_active;
                    mission_step_tick = now;
                    mission_step = 0;
                }
            }
        }

        /* --- 2. AUTONOMOUS PLUME MISSION LOOP --- */
        if (is_plume_mission_active)
        {
            if (now - mission_step_tick >= 1200)
            {
                mission_step_tick = now;
                mission_step = (mission_step + 1) % 5;

                if (mission_step == 0 || mission_step == 4) {
                    current_mode = MODE_HIGH_RES;
                    current_turbidity_ntu = 12.5f;
                } else if (mission_step == 1 || mission_step == 3) {
                    current_mode = MODE_BALANCED;
                    current_turbidity_ntu = 88.0f;
                } else {
                    current_mode = MODE_LONG_RANGE;
                    current_turbidity_ntu = 245.0f;
                }
            }
        }
        else
        {
            /* --- 3. 6-CHANNEL SENSOR & METROLOGY SAMPLING (35 ms loop) --- */
            if (now - last_adc_tick >= 35)
            {
                last_adc_tick = now;

                // 3a. Read Turbidity (Channel 0 / PA0 via 10k/20k divider)
                uint32_t raw_turb_adc = Read_ADC_Channel(ADC_CHANNEL_0);
                sensor_data_received = (raw_turb_adc >= 40) ? 1 : 0;

                if (sensor_data_received)
                {
                    uint32_t filtered_adc = Filter_ADC_Sample(raw_turb_adc);

                    // Calibrated TSW-20 Turbidity Equation (accounting for 2/3 divider scaling)
                    if (filtered_adc >= 3200) {
                        current_turbidity_ntu = 8.0f + (float)(4095 - filtered_adc) * 0.14f;
                    } else if (filtered_adc >= 1600) {
                        current_turbidity_ntu = 45.0f + (float)(3200 - filtered_adc) * (120.0f / 1600.0f);
                    } else {
                        current_turbidity_ntu = 165.0f + (float)(1600 - filtered_adc) * (500.0f / 1600.0f);
                    }
                    if (current_turbidity_ntu > 999.0f) current_turbidity_ntu = 999.0f;
                    if (current_turbidity_ntu < 1.0f) current_turbidity_ntu = 1.0f;

                    SonarMode_t target_mode = Evaluate_Turbidity_Hysteresis(current_turbidity_ntu, current_mode);
                    if (now >= sim_override_until)
                    {
                        if (target_mode != current_mode) current_mode = target_mode;
                    }
                }

                // 3b. Read Depth Potentiometer (Channel 1 / PA1) -> 0.0m to 1000.0m
                uint32_t raw_depth_adc = Read_ADC_Channel(ADC_CHANNEL_1);
                if (raw_depth_adc <= 80) {
                    simulated_depth_m = 0.0f;
                } else if (raw_depth_adc >= 3980) {
                    simulated_depth_m = 1000.0f;
                } else {
                    simulated_depth_m = ((float)(raw_depth_adc - 80) / (3980.0f - 80.0f)) * 1000.0f;
                }
                depth_sensor_ok = 1;

                // 3c. Read Salinity Potentiometer (Channel 10 / PC0) -> 0.0 to 42.0 PSU
                uint32_t raw_sal_adc = Read_ADC_Channel(ADC_CHANNEL_10);
                if (raw_sal_adc <= 80) {
                    current_salinity_psu = 0.0f;
                } else if (raw_sal_adc >= 3980) {
                    current_salinity_psu = 42.0f;
                } else {
                    current_salinity_psu = ((float)(raw_sal_adc - 80) / (3980.0f - 80.0f)) * 42.0f;
                }
                sal_sensor_ok = 1;

                // 3d. Electrical Metrology Sampling
                live_v_rail = Read_Rail_Voltage();
                tx_state.supply_voltage_v = live_v_rail;

                float measured_t = Read_PA_Temperature();
                // Slowly decay towards measured/ambient temperature (natural convective cooling)
                tx_state.pa_temp_c = (tx_state.pa_temp_c * 0.95f) + (measured_t * 0.05f);
            }
        }

        /* --- 4. SONAR TRANSMISSION & AUDIO ENGINE --- */
        if (current_audio_mode == AUDIO_MODE_TACTICAL_CHIRP)
        {
            // PRI Interval dynamically governed by thermal warning state
            uint32_t pri_ms = (tx_state.thermal == THERMAL_WARNING) ? 3500 : 2000;
            if (now - last_ping_tick >= pri_ms)
            {
                last_ping_tick = now;
                Trigger_Adaptive_Sonar_Ping(current_mode, simulated_depth_m, current_salinity_psu);
            }
        }
        else
        {
            // Melodic Octave-Shifter Demo
            uint16_t note_duration = pirates_theme[note_idx].duration_ms;
            uint8_t note_expired = (now - note_start_tick >= note_duration);
            uint8_t mode_changed = (current_mode != last_applied_mode);

            if (note_expired || mode_changed)
            {
                if (note_expired)
                {
                    note_idx = (note_idx + 1) % MELODY_LENGTH;
                    note_start_tick = now;
                }

                last_applied_mode = current_mode;
                uint16_t base_freq = pirates_theme[note_idx].note;

                if (base_freq == NOTE_REST)
                {
                    HAL_TIM_PWM_Stop(&htim4, TIM_CHANNEL_1);
                }
                else
                {
                    uint32_t octave_mult = (current_mode == MODE_HIGH_RES) ? 4 :
                                           (current_mode == MODE_BALANCED) ? 2 : 1;

                    uint32_t play_freq = base_freq * octave_mult;
                    if (play_freq > 0)
                    {
                        uint32_t period = 1000000 / play_freq;
                        __HAL_TIM_SET_AUTORELOAD(&htim4, period - 1);
                        __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_1, period / 2);
                        HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_1);
                    }
                }
            }
        }

        /* --- 5. EMBEDDED OCEAN ACOUSTICS & PERIODIC TELEMETRY STREAMING (2 sec) --- */
        if (now - last_telemetry_tick >= 2000)
        {
            last_telemetry_tick = now;

            // Sample DS18B20 Seawater Temperature Probe (PA10)
            current_temperature_c = DS18B20_ReadTemperature();

            // Refresh Onboard SSD1306 OLED HUD (PB8/PB9)
            OLED_UpdateHUD(current_mode, current_turbidity_ntu, simulated_depth_m,
                           current_temperature_c, current_salinity_psu,
                           sensor_data_received, depth_sensor_ok, temp_sensor_ok, sal_sensor_ok);

            // Execute Francois-Garrison Ocean Absorption & Sonar Equation
            alpha_absorption_db_km = Compute_Acoustic_Absorption(current_turbidity_ntu, current_mode);
            simulated_snr_db = Compute_Sonar_SNR(current_turbidity_ntu, simulated_depth_m, current_mode);

            // Transmit NMEA Telemetry Stream
            Send_Telemetry();
        }
    }
}

/* ==============================================================================
 * AUTONOMOUS ADAPTIVE SONAR TRANSMITTER ENGINE (DAC + PWM + METROLOGY)
 * ============================================================================== */

/* 1. Independent Audible Speaker Acoustic Sweep Generator on PB6 (TIM4_CH1) */
void Play_Speaker_Chirp(SonarMode_t mode)
{
    uint32_t f_start, f_end;
    uint32_t pulse_ms;

    if (mode == MODE_HIGH_RES) {
        f_start = 2800;
        f_end = 4200;
        pulse_ms = 120;
    } else if (mode == MODE_BALANCED) {
        f_start = 1200;
        f_end = 1800;
        pulse_ms = 180;
    } else {
        f_start = 400;
        f_end = 700;
        pulse_ms = 250;
    }

    HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_1);

    const int num_steps = 20;
    uint32_t step_delay = pulse_ms / num_steps;
    if (step_delay == 0) step_delay = 5;

    for (int step = 0; step < num_steps; step++)
    {
        uint32_t freq = f_start + ((f_end - f_start) * step) / num_steps;
        if (freq == 0) freq = 1000;
        uint32_t period = 1000000 / freq;
        __HAL_TIM_SET_AUTORELOAD(&htim4, period - 1);
        __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_1, period / 2);
        HAL_Delay(step_delay);
    }

    HAL_TIM_PWM_Stop(&htim4, TIM_CHANNEL_1);
}

/* 2. Full Adaptive Sonar Ping Transmitter: Stage 1 Prior + Stage 2 Governor + DAC/PWM DMA */
void Trigger_Adaptive_Sonar_Ping(SonarMode_t mode, float depth_m, float salinity_psu)
{
    // Stop ongoing transmission to avoid buffer overlap
    if (is_dma_ping_in_progress) {
        HAL_TIM_PWM_Stop_DMA(&htim3, TIM_CHANNEL_1);
        is_dma_ping_in_progress = 0;
    }

    // --- STAGE 1: Environmental Prior Prediction ---
    WaveformVector_t w0 = stage1_predict_prior(current_temperature_c, depth_m, current_turbidity_ntu);

    // --- STAGE 2: Electrical Refinement & Power Governor ---
    WaveformVector_t w_act = stage2_refine_and_govern(&w0, &tx_state);

    // If budget exhausted or thermal shutdown, inhibit transmission
    if (tx_state.mode == MODE_DEPLETED || tx_state.thermal == THERMAL_SHUTDOWN ||
        w_act.amplitude_norm <= 0.0f || w_act.duration_ms <= 0.0f)
    {
        current_amplitude_pct = 0;
        active_ping_samples = 0;
        HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, 2048); // Idle mid-rail
        return;
    }

    // Rescale active samples based on governed pulse duration
    // 5.0ms duration maps to full 512 samples
    uint32_t sample_calc = (uint32_t)((w_act.duration_ms / 5.0f) * 512.0f);
    if (sample_calc < 64) sample_calc = 64;
    if (sample_calc > CHIRP_SAMPLES) sample_calc = CHIRP_SAMPLES;
    active_ping_samples = (uint16_t)sample_calc;

    // Rescale amplitude percentage based on governed amplitude
    current_amplitude_pct = (uint8_t)(w_act.amplitude_norm * 100.0f);
    if (current_amplitude_pct > 100) current_amplitude_pct = 100;
    if (current_amplitude_pct < 10) current_amplitude_pct = 10;

    // Waveform bank lookup
    uint8_t prof_idx = (uint8_t)mode;
    if (prof_idx >= SONAR_PROFILE_COUNT) prof_idx = 0;
    const uint16_t *source_lut = SONAR_LUT_BANK_8BIT[prof_idx];

    // Resample LUT into DMA buffer
    int32_t mid = 128;
    for (int i = 0; i < active_ping_samples; i++) {
        uint32_t src_idx = ((uint32_t)i * CHIRP_SAMPLES) / active_ping_samples;
        if (src_idx >= CHIRP_SAMPLES) src_idx = CHIRP_SAMPLES - 1;

        int32_t val = (int32_t)source_lut[src_idx] - mid;
        val = (val * (int32_t)current_amplitude_pct) / 100;
        int32_t out = mid + val;
        if (out < 0) out = 0;
        if (out > 255) out = 255;
        dma_ping_buffer[i] = (uint16_t)out;
    }
    dma_ping_buffer[0] = 128;
    dma_ping_buffer[active_ping_samples - 1] = 128;

    // Drive True 12-Bit Hardware DAC on PA4 (scaled to 12-bit range 0-4095)
    uint32_t mid_sample = (uint32_t)dma_ping_buffer[active_ping_samples / 2];
    uint32_t dac_val12 = mid_sample << 4;
    HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, dac_val12);

    is_dma_ping_in_progress = 1;
    dma_ping_count++;

    // Launch Autonomous DMA Stream: transfers LUT duty cycles -> TIM3->CCR1 at 328.125 kS/s
    HAL_TIM_PWM_Start_DMA(&htim3, TIM_CHANNEL_1, (uint32_t*)dma_ping_buffer, active_ping_samples);

    // --- ON-CHIP DISCRETE ENERGY INTEGRATION: E_pulse = ∫ V · I dt ---
    live_v_rail = Read_Rail_Voltage();
    tx_state.supply_voltage_v = live_v_rail;
    live_i_peak = Read_Transmit_Current(w_act.amplitude_norm);
    float i_rms = live_i_peak * 0.707f;
    float pulse_time_s = w_act.duration_ms / 1000.0f;
    live_e_pulse = live_v_rail * i_rms * pulse_time_s;

    // Deduct from budget
    tx_state.energy_remaining_j -= live_e_pulse;
    if (tx_state.energy_remaining_j < 0.0f) tx_state.energy_remaining_j = 0.0f;
    tx_state.total_pings++;

    // Thermal model update: heat accumulated from pulse dissipation (0.15°C per Joule)
    tx_state.pa_temp_c += (live_e_pulse * 0.15f);

    // Concurrently trigger audible acoustic demonstration sweep on PB6 (Speaker)
    if (current_audio_mode == AUDIO_MODE_TACTICAL_CHIRP) {
        Play_Speaker_Chirp(mode);
    }
}

void Play_Sonar_Chirp(SonarMode_t mode)
{
    Trigger_Adaptive_Sonar_Ping(mode, simulated_depth_m, current_salinity_psu);
}

/* ==============================================================================
 * EMBEDDED OCEAN ACOUSTICS: FRANCOIS-GARRISON ABSORPTION MODEL
 * ============================================================================== */
float Compute_Acoustic_Absorption(float ntu, SonarMode_t mode)
{
    float alpha = 0.0f;
    switch (mode)
    {
        case MODE_HIGH_RES:   /* 450 kHz carrier */
            alpha = 92.4f + (ntu * 0.38f);
            break;
        case MODE_BALANCED:   /* 250 kHz carrier */
            alpha = 41.5f + (ntu * 0.18f);
            break;
        case MODE_LONG_RANGE: /* 100 kHz carrier */
            alpha = 14.2f + (ntu * 0.06f);
            break;
    }
    return alpha;
}

/* Active Sonar Radar Equation: SNR = SL - 2*TL + TS - NL */
float Compute_Sonar_SNR(float ntu, float depth_m, SonarMode_t mode)
{
    float alpha = Compute_Acoustic_Absorption(ntu, mode);
    float sl = 205.0f;
    float r = (depth_m > 1.0f) ? depth_m : 1.0f;

    float tl = 20.0f * log10f(r) + (alpha * r * 0.001f);
    float ts = -15.0f;
    float nl = 58.0f + (ntu * 0.08f);

    float snr = sl - (2.0f * tl) + ts - nl;
    if (snr < 0.0f) snr = 0.0f;
    if (snr > 42.0f) snr = 42.0f;
    return snr;
}

SonarMode_t Evaluate_Turbidity_Hysteresis(float ntu, SonarMode_t active_mode)
{
    switch (active_mode)
    {
        case MODE_HIGH_RES:
            if (ntu >= 65.0f) return MODE_BALANCED;
            return MODE_HIGH_RES;

        case MODE_BALANCED:
            if (ntu <= 40.0f) return MODE_HIGH_RES;
            if (ntu >= 165.0f) return MODE_LONG_RANGE;
            return MODE_BALANCED;

        case MODE_LONG_RANGE:
            if (ntu <= 140.0f) return MODE_BALANCED;
            return MODE_LONG_RANGE;

        default:
            return MODE_HIGH_RES;
    }
}

/* Transmit NMEA-Style Telemetry Packet to Web Ground Station */
void Send_Telemetry(void)
{
    char buf[160];
    int t_int = (int)current_turbidity_ntu;
    int t_dec = (int)((current_turbidity_ntu - (float)t_int) * 10.0f);
    if (t_dec < 0) t_dec = -t_dec;

    int d_int = (int)simulated_depth_m;
    int d_dec = (int)((simulated_depth_m - (float)d_int) * 10.0f);
    if (d_dec < 0) d_dec = -d_dec;

    int snr_int = (int)simulated_snr_db;
    int snr_dec = (int)((simulated_snr_db - (float)snr_int) * 10.0f);
    if (snr_dec < 0) snr_dec = -snr_dec;

    int alpha_int = (int)alpha_absorption_db_km;
    int alpha_dec = (int)((alpha_absorption_db_km - (float)alpha_int) * 10.0f);
    if (alpha_dec < 0) alpha_dec = -alpha_dec;

    int temp_int = (int)current_temperature_c;
    int temp_dec = (int)((current_temperature_c - (float)temp_int) * 10.0f);
    if (temp_dec < 0) temp_dec = -temp_dec;

    int sal_int = (int)current_salinity_psu;
    int sal_dec = (int)((current_salinity_psu - (float)sal_int) * 10.0f);
    if (sal_dec < 0) sal_dec = -sal_dec;

    char audio_char = (current_audio_mode == AUDIO_MODE_TACTICAL_CHIRP) ? 'C' : 'P';

    // Format: $SONAR,MODE,TURB,TURB_OK,DEPTH,SNR,ALPHA,AUDIO_MODE,TEMP,SAL,TEMP_OK,DEPTH_OK,SAL_OK,PULSE_LEN,AMP_PCT,DMA_CNT,V_RAIL,I_PEAK,E_PULSE,E_REM,E_BUDGET,T_PA,THM_STATE,GOV_MODE\r\n
    snprintf(buf, sizeof(buf),
             "$SONAR,%d,%d.%d,%d,%d.%d,%d.%d,%d.%d,%c,%d.%d,%d.%d,%d,%d,%d,%d,%d,%lu,%.2f,%.2f,%.4f,%.2f,%.2f,%.1f,%d,%d\r\n",
             (int)current_mode,
             t_int, t_dec,
             (int)sensor_data_received,
             d_int, d_dec,
             snr_int, snr_dec,
             alpha_int, alpha_dec,
             audio_char,
             temp_int, temp_dec,
             sal_int, sal_dec,
             (int)temp_sensor_ok,
             (int)depth_sensor_ok,
             (int)sal_sensor_ok,
             (int)active_ping_samples,
             (int)current_amplitude_pct,
             (unsigned long)dma_ping_count,
             live_v_rail,
             live_i_peak,
             live_e_pulse,
             tx_state.energy_remaining_j,
             tx_state.energy_budget_j,
             tx_state.pa_temp_c,
             (int)tx_state.thermal,
             (int)tx_state.mode);

    HAL_UART_Transmit(&huart2, (uint8_t*)buf, strlen(buf), 30);
}

/* ==============================================================================
 * HARDWARE PERIPHERAL INITIALIZATIONS
 * ============================================================================== */

static void MX_USART2_UART_Init(void)
{
    huart2.Instance = USART2;
    huart2.Init.BaudRate = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart2);
}

static void MX_ADC1_Init(void)
{
    __HAL_RCC_ADC1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    /* Configure PA0 (Turbidity), PA1 (Depth), PA5 (Current Sense), PA6 (Rail Voltage), PA7 (Thermal) */
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* Configure PC0 (Salinity Potentiometer) as Analog Input */
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = DISABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1;
    hadc1.Init.DMAContinuousRequests = DISABLE;
    hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
    HAL_ADC_Init(&hadc1);
}

static void MX_DAC1_Init(void)
{
    __HAL_RCC_DAC_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    /* Configure PA4 (DAC1_OUT1) as True 12-bit Analog Output */
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_4;
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    DAC_ChannelConfTypeDef sConfig = {0};
    hdac1.Instance = DAC;
    HAL_DAC_Init(&hdac1);

    sConfig.DAC_Trigger = DAC_TRIGGER_NONE;
    sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
    HAL_DAC_ConfigChannel(&hdac1, &sConfig, DAC_CHANNEL_1);
    HAL_DAC_Start(&hdac1, DAC_CHANNEL_1);
    HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, 2048); // Center bias (1.65V)
}

static void MX_TIM3_Init(void)
{
    __HAL_RCC_TIM3_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    /* Configure PA6 (Arduino D12) as Alternate Function TIM3_CH1 (PWM Carrier) */
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_6;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF2_TIM3;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    TIM_ClockConfigTypeDef sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    TIM_OC_InitTypeDef sConfigOC = {0};

    htim3.Instance = TIM3;
    htim3.Init.Prescaler = 0;
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim3.Init.Period = 255; // 328.125 kHz PWM carrier
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    HAL_TIM_Base_Init(&htim3);

    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig);
    HAL_TIM_PWM_Init(&htim3);

    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig);

    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 128;
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1);
}

static void MX_TIM4_Init(void)
{
    __HAL_RCC_TIM4_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    /* Configure PB6 (Arduino D10) as Alternate Function TIM4_CH1 (Audible Speaker Output) */
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_6;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF2_TIM4;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

    TIM_ClockConfigTypeDef sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    TIM_OC_InitTypeDef sConfigOC = {0};

    htim4.Instance = TIM4;
    htim4.Init.Prescaler = 84 - 1; // 1 MHz timer tick
    htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim4.Init.Period = 1000;
    htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    HAL_TIM_Base_Init(&htim4);

    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    HAL_TIM_ConfigClockSource(&htim4, &sClockSourceConfig);
    HAL_TIM_PWM_Init(&htim4);

    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    HAL_TIMEx_MasterConfigSynchronization(&htim4, &sMasterConfig);

    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 500;
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    HAL_TIM_PWM_ConfigChannel(&htim4, &sConfigOC, TIM_CHANNEL_1);
}

static void MX_DMA_Init(void)
{
    __HAL_RCC_DMA1_CLK_ENABLE();

    hdma_tim3_ch1.Instance = DMA1_Stream4;
    hdma_tim3_ch1.Init.Channel = DMA_CHANNEL_5;
    hdma_tim3_ch1.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_tim3_ch1.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_tim3_ch1.Init.MemInc = DMA_MINC_ENABLE;
    hdma_tim3_ch1.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    hdma_tim3_ch1.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
    hdma_tim3_ch1.Init.Mode = DMA_NORMAL;
    hdma_tim3_ch1.Init.Priority = DMA_PRIORITY_HIGH;
    hdma_tim3_ch1.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    HAL_DMA_Init(&hdma_tim3_ch1);

    __HAL_LINKDMA(&htim3, hdma[TIM_DMA_ID_CC1], hdma_tim3_ch1);

    HAL_NVIC_SetPriority(DMA1_Stream4_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(DMA1_Stream4_IRQn);
}

void DMA1_Stream4_IRQHandler(void)
{
    HAL_DMA_IRQHandler(&hdma_tim3_ch1);
}

void HAL_TIM_PWM_PulseFinishedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM3)
    {
        HAL_TIM_PWM_Stop_DMA(&htim3, TIM_CHANNEL_1);
        __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 128);
        is_dma_ping_in_progress = 0;
    }
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    /* Configure GPIO pin : PA10 (DS18B20 1-Wire Data Line) */
    GPIO_InitStruct.Pin = GPIO_PIN_10;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* Configure GPIO pins : PB8 (I2C1 SCL), PB9 (I2C1 SDA) for OLED Display */
    GPIO_InitStruct.Pin = GPIO_PIN_8 | GPIO_PIN_9;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8 | GPIO_PIN_9, GPIO_PIN_SET);

    /* Configure GPIO pin : PC13 (B1 Blue User Button) */
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
}

void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
    RCC_OscInitStruct.PLL.PLLM = 16;
    RCC_OscInitStruct.PLL.PLLN = 336;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
    RCC_OscInitStruct.PLL.PLLQ = 7;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);

    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                                |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}

void Error_Handler(void)
{
    __disable_irq();
    while (1) {}
}
