import matplotlib.pyplot as plt
import textwrap
import matplotlib.patches as patches

# High-resolution card replicating the exact layout of the user's reference image
# Expanded slightly in height to comfortably fit DAC module & Digital Oscilloscope
fig, ax = plt.subplots(figsize=(6.5, 11.2), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Header
ax.text(0.06, 0.955, "Hardware & Software", 
        fontsize=17, fontweight='bold', color='#000000', ha='left', va='center', fontfamily='serif')

items = [
    ("Microcontroller (STM32F4 / Cortex-M4)", "Primary MCU engine for bare-metal zero-CPU circular DMA arbitration and synchronous 6-ch ADC sampling."),
    ("High-Speed Precision DAC (DAC8562 / On-Chip)", "16-bit / 12-bit dual-channel DAC streaming analog baseband chirps at up to 2.0 MSPS with ultra-low phase noise."),
    ("Digital Storage Oscilloscope (DSO Bench)", "100 MHz 1 GSa/s real-time oscilloscope for hardware verification of chirp bandwidth, envelope taper & THD."),
    ("Transducer (PZT-4 / PZT-8 Ceramic)", "Submersible acoustic projector delivering > 175 dB re 1 µPa @ 1 m source level across 10–100 kHz band."),
    ("Reconstruction Filter (OPA1612)", "Dual 4th-order Sallen-Key low-pass filter (fc = 100 kHz) providing > 48 dB/oct DAC anti-aliasing roll-off."),
    ("Power Stage & Toroidal Match", "Class-AB linear driver delivering 20–100 Vpp matched to the reactive BVD piezo resonance load."),
    ("Sensing Hardware (INA169 & NTC)", "High-side current shunt, precision voltage divider, and thermistor providing < 100 µs fault protection."),
    ("Python / NumPy / SciPy", "Discrete Tukey window synthesis, pulse compression matched filtering, and acoustic propagation modeling."),
    ("LTspice XVII & Proteus VSM", "Full-circuit AC frequency analysis, BVD transducer impedance verification, and MCU firmware co-simulation."),
    ("Ground Station (React 19 / Vite)", "Real-time Web Serial API dashboard parsing $SONAR NMEA sentences for live pulse energy & FFT display."),
    ("Power Subsystem (Li-Ion Pack)", "Dual isolated DC-DC supplies providing clean analog rails for high-power underwater acoustic bursts.")
]

y = 0.92
for title, desc in items:
    # Bullet
    ax.text(0.06, y, "•", fontsize=13, color='#000000', ha='left', va='top', fontfamily='serif')
    
    # Title
    ax.text(0.10, y, title + ":", fontsize=9.2, fontweight='bold', color='#000000', ha='left', va='top', fontfamily='serif')
    
    # Description lines wrapped
    wrapped = textwrap.wrap(desc, width=42)
    line_y = y - 0.021
    for wline in wrapped:
        ax.text(0.10, line_y, wline, fontsize=8.8, color='#1F2937', ha='left', va='top', fontfamily='serif')
        line_y -= 0.019
        
    y = line_y - 0.014

# Bottom blue bar accent like the reference image
blue_bar = patches.Rectangle((0, 0), 1, 0.02, facecolor='#0284C7', edgecolor='none')
ax.add_patch(blue_bar)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('docs/hardware_and_software_card.png', dpi=300, facecolor='#FFFFFF', bbox_inches='tight')
plt.savefig('additional_docs/simulation_images/presentation_slides/hardware_and_software_card.png', dpi=300, facecolor='#FFFFFF', bbox_inches='tight')
print("Successfully regenerated hardware_and_software_card.png with DAC and Oscilloscope!")
