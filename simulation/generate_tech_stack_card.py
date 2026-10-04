import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

fig = plt.figure(figsize=(10.5, 12), dpi=300)
fig.patch.set_facecolor('#FCFBF7')

# Outer Card Frame
ax_card = fig.add_axes([0.03, 0.02, 0.94, 0.96])
ax_card.set_axis_off()
card_rect = patches.FancyBboxPatch(
    (0, 0), 1, 1,
    boxstyle="round,pad=0.015,rounding_size=0.02",
    facecolor="#FFFFFF",
    edgecolor="#D0D7DE",
    linewidth=1.5,
    transform=ax_card.transAxes
)
ax_card.add_patch(card_rect)

# ------------------------------------------------------------------------------
# TOP SECTION: TECHNOLOGIES & TOOLS
# ------------------------------------------------------------------------------
ax_top = fig.add_axes([0.06, 0.49, 0.88, 0.47])
ax_top.set_axis_off()
ax_top.set_xlim(0, 100)
ax_top.set_ylim(0, 100)

# Section Header
ax_top.text(2, 95, "Technologies, Tools & Test Instruments:", fontsize=15, fontweight='bold', color='#1565C0')
# Blue underline bar matching reference
ax_top.plot([2, 58], [91, 91], color='#1565C0', lw=2.2)

tech_tools = [
    ("Precision DAC (DAC8562 / On-Chip 12-Bit)", "for continuous circular DMA waveform reconstruction at up to 2.0 MSPS with sub-mV DC offset."),
    ("Digital Storage Oscilloscope (DSO 100MHz)", "for bench validation of LFM chirp instantaneous bandwidth, Tukey envelope taper, and THD (<0.05%)."),
    ("Bare-Metal C (C99 / CMSIS)", "for zero-CPU circular DMA DAC streaming and synchronous 6-ch ADC sampling on STM32 ARM Cortex-M."),
    ("STM32CubeIDE & GCC Toolchain", "for embedded firmware compilation, HAL/LL register drivers, and ST-LINK hardware flashing."),
    ("Python 3.11 & NumPy / SciPy", "for discrete Tukey window synthesis, matched filter pulse compression, and numerical FFT verification."),
    ("LTspice XVII / 24", "for 4th-order Sallen-Key reconstruction filter AC sweeps and BVD piezo transducer load simulation."),
    ("Proteus VSM 8.16", "for virtual hardware-in-the-loop co-simulation of the STM32 MCU, active filter, and real-time virtual DSO telemetry."),
    ("React 19 / Vite & Web Serial API", "for real-time USB-UART telemetry streaming (115200 baud) and interactive hydroacoustic ground station display.")
]

y_pos = 83
for name, desc in tech_tools:
    ax_top.text(3, y_pos, "•", fontsize=12, fontweight='bold', color='#263238')
    ax_top.text(6, y_pos, f"{name}:", fontsize=9.8, fontweight='bold', color='#111111')
    ax_top.text(6, y_pos - 3.4, f"  {desc}", fontsize=8.8, color='#37474F')
    y_pos -= 10.0

# Horizontal Divider Line separating Top and Bottom
fig.add_artist(plt.Line2D([0.05, 0.95], [0.48, 0.48], color='#CFD8DC', linewidth=1.5))

# ------------------------------------------------------------------------------
# BOTTOM SECTION: ACOUSTIC MODELS, STANDARDS & DATA SOURCES
# ------------------------------------------------------------------------------
ax_bot = fig.add_axes([0.06, 0.04, 0.88, 0.43])
ax_bot.set_axis_off()
ax_bot.set_xlim(0, 100)
ax_bot.set_ylim(0, 100)

ax_bot.text(2, 94, "Acoustic Models, Standards & Data Sources:", fontsize=15, fontweight='bold', color='#1565C0')
ax_bot.plot([2, 60], [90, 90], color='#1565C0', lw=2.2)

sources = [
    ("Francois-Garrison (1982) JASA Model", "multi-mechanism 3-relaxation chemical absorption (Boric Acid, MgSO4, Pure Water) across 10–500 kHz."),
    ("Mackenzie (1981) Nine-Term Formulation", "seawater sound speed c(T, S, D) calculation from temperature, salinity, and depth sensors."),
    ("Urick (1983) Principles of Underwater Sound", "sonar range equations, geometric transmission loss (20 log R), and ambient noise spectral levels."),
    ("Butterworth-Van Dyke (BVD) Model", "lumped equivalent circuit (C0, Cm, Lm, Rm) modeling reactive piezo transducer resonance & loading."),
    ("NMEA 0183 Telemetry Standard ($SONAR)", "custom 24-field telemetry sentence formatting for live V, I, Epulse, and heatsink thermal reporting."),
    ("UNESCO TEOS-10 Seawater Reference", "empirical oceanographic bounds for temperature (-2°C to 35°C), salinity (0–42 ppt), and hydrostatic depth.")
]

y_pos = 80
for name, desc in sources:
    ax_bot.text(3, y_pos, "•", fontsize=12, fontweight='bold', color='#263238')
    ax_bot.text(6, y_pos, f"{name}:", fontsize=9.8, fontweight='bold', color='#111111')
    ax_bot.text(6, y_pos - 3.4, f"  {desc}", fontsize=8.8, color='#37474F')
    y_pos -= 12.0

plt.savefig('docs/technologies_and_sources_slide.png', dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
plt.savefig('additional_docs/simulation_images/presentation_slides/technologies_and_sources_slide.png', dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
print("Successfully regenerated technologies_and_sources_slide.png with DAC and DSO!")
