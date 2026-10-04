import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure with high DPI and 16:9 presentation aspect ratio
fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
fig.patch.set_facecolor('#0B0F19') # Deep professional navy/slate
ax.set_facecolor('#0B0F19')

# Header
ax.text(0.5, 0.94, "OCEAN-SDR : SYSTEM ARCHITECTURE", 
        fontsize=22, fontweight='bold', color='#F8FAFC', ha='center', va='center', fontfamily='sans-serif')
ax.text(0.5, 0.89, "Hardware-Software Signal Pipeline & Closed-Loop Telemetry Chain", 
        fontsize=12, color='#94A3B8', ha='center', va='center', fontfamily='sans-serif')

# Pipeline cards definition
cards = [
    {
        "step": "STAGE 01",
        "title": "WAVEFORM SYNTHESIS",
        "sub": "STM32 ARM Cortex-M",
        "icon_color": "#0284C7",
        "card_bg": "#111827",
        "card_border": "#1E293B",
        "accent": "#38BDF8",
        "bullets": [
            ("Base Hardware", "STM32F4 / ARM Cortex-M4 @ 168MHz"),
            ("Chirp Synthesis", "LFM 10 kHz -> 100 kHz (B=90kHz)"),
            ("Windowing", "Tukey (alpha = 0.25) spectral tapering"),
            ("Suppression", "-32 dB side-lobe suppression"),
            ("Output Mode", "Zero-CPU Continuous Circular DMA")
        ]
    },
    {
        "step": "STAGE 02",
        "title": "SIGNAL CONDITIONING",
        "sub": "DAC & Active Reconstruction",
        "icon_color": "#0EA5E9",
        "card_bg": "#111827",
        "card_border": "#1E293B",
        "accent": "#38BDF8",
        "bullets": [
            ("Converter", "12-Bit DAC @ 1.0 - 2.0 MSPS"),
            ("Filter Topology", "4th-Order Sallen-Key Butterworth"),
            ("Cutoff Freq", "fc = 100 kHz (-3 dB corner)"),
            ("Roll-off Rate", "> 48 dB / octave stopband"),
            ("THD Level", "< 0.05% Total Harmonic Distortion")
        ]
    },
    {
        "step": "STAGE 03",
        "title": "POWER AMPLIFIER",
        "sub": "High-Voltage Linear Driver",
        "icon_color": "#2563EB",
        "card_bg": "#111827",
        "card_border": "#1E293B",
        "accent": "#60A5FA",
        "bullets": [
            ("Topology", "Class-AB Linear Driver Stage"),
            ("Drive Swing", "20 Vpp - 100 Vpp Output"),
            ("Matching Net", "Toroidal Ferrite Core Transformer"),
            ("Impedance", "Matched to Piezo Resonance"),
            ("Safety Feature", "Thermal heatsink clamp (<85 deg C)")
        ]
    },
    {
        "step": "STAGE 04",
        "title": "ACOUSTIC TRANSDUCER",
        "sub": "Underwater Projector",
        "icon_color": "#4F46E5",
        "card_bg": "#111827",
        "card_border": "#1E293B",
        "accent": "#818CF8",
        "bullets": [
            ("Element Type", "PZT-4 / PZT-8 Piezoelectric Disk"),
            ("Source Level", "> 175 dB re 1 uPa @ 1 m"),
            ("Submersion", "IP68 Submersible to 100 m Depth"),
            ("Beam Pattern", "Omni-directional / Targeted cone"),
            ("Acoustic Model", "Butterworth-Van Dyke (BVD)")
        ]
    }
]

# Geometry
card_w = 0.218
card_h = 0.44
start_x = 0.035
gap_x = 0.026
top_y = 0.38

for i, c in enumerate(cards):
    cx = start_x + i * (card_w + gap_x)
    
    # Background Card Box
    bg_box = patches.FancyBboxPatch((cx, top_y), card_w, card_h,
                                    boxstyle="round,pad=0.012,rounding_size=0.02",
                                    facecolor=c["card_bg"], edgecolor=c["card_border"],
                                    linewidth=1.8, zorder=2)
    ax.add_patch(bg_box)
    
    # Top Pill Badge
    pill = patches.FancyBboxPatch((cx + 0.015, top_y + card_h - 0.042), 0.075, 0.026,
                                  boxstyle="round,pad=0.004,rounding_size=0.01",
                                  facecolor=c["icon_color"], edgecolor='none', zorder=3)
    ax.add_patch(pill)
    ax.text(cx + 0.0525, top_y + card_h - 0.029, c["step"],
            fontsize=8.5, fontweight='bold', color='#FFFFFF', ha='center', va='center')
    
    # Card Header Titles
    ax.text(cx + 0.015, top_y + card_h - 0.075, c["title"],
            fontsize=10.5, fontweight='bold', color='#F1F5F9', ha='left', va='center')
    ax.text(cx + 0.015, top_y + card_h - 0.105, c["sub"],
            fontsize=8.5, fontweight='bold', color=c["accent"], ha='left', va='center')
    
    # Divider line
    ax.plot([cx + 0.015, cx + card_w - 0.015], [top_y + card_h - 0.125, top_y + card_h - 0.125],
            color='#334155', linewidth=1, zorder=3)
    
    # Bullets
    for b_idx, (label, val) in enumerate(c["bullets"]):
        by = top_y + card_h - 0.165 - (b_idx * 0.055)
        
        # Small glowing dot
        dot = patches.Circle((cx + 0.022, by), 0.0035, facecolor=c["accent"], edgecolor='none', zorder=3)
        ax.add_patch(dot)
        
        ax.text(cx + 0.035, by + 0.012, label,
                fontsize=7.5, color='#94A3B8', fontweight='bold', ha='left', va='center')
        ax.text(cx + 0.035, by - 0.01, val,
                fontsize=8, color='#E2E8F0', ha='left', va='center')

    # Arrow connecting forward stages
    if i < len(cards) - 1:
        ax.annotate('', xy=(cx + card_w + gap_x - 0.005, top_y + card_h * 0.65), 
                    xytext=(cx + card_w + 0.003, top_y + card_h * 0.65),
                    arrowprops=dict(facecolor='#38BDF8', edgecolor='none', width=2.5, headwidth=8, headlength=7),
                    zorder=4)

# ==================== BOTTOM FEEDBACK & TELEMETRY SECTION ====================
bot_w = 4 * card_w + 3 * gap_x
bot_h = 0.24
bot_x = start_x
bot_y = 0.07

bot_box = patches.FancyBboxPatch((bot_x, bot_y), bot_w, bot_h,
                                 boxstyle="round,pad=0.012,rounding_size=0.02",
                                 facecolor='#0F172A', edgecolor='#059669',
                                 linewidth=1.8, zorder=2)
ax.add_patch(bot_box)

# Top Bar Badge on Bottom Card
f_pill = patches.FancyBboxPatch((bot_x + 0.02, bot_y + bot_h - 0.038), 0.13, 0.024,
                                boxstyle="round,pad=0.004,rounding_size=0.01",
                                facecolor='#059669', edgecolor='none', zorder=3)
ax.add_patch(f_pill)
ax.text(bot_x + 0.085, bot_y + bot_h - 0.026, "STAGE 05 : FEEDBACK",
        fontsize=8.5, fontweight='bold', color='#FFFFFF', ha='center', va='center')

ax.text(bot_x + 0.165, bot_y + bot_h - 0.026, "CLOSED-LOOP HEALTH MONITORING & REAL-TIME TELEMETRY ENGINE",
        fontsize=10.5, fontweight='bold', color='#34D399', ha='left', va='center')

# 3 Inner panels for the feedback loop
col_w = (bot_w - 0.06) / 3
feed_cols = [
    {
        "title": "1. SENSING HARDWARE",
        "color": "#10B981",
        "items": [
            "• INA169 High-Side Shunt: Live current (Isense)",
            "• Precision Resistor Divider: Peak swing (Vpeak)",
            "• NTC 10k Thermistor: Heatsink thermal monitoring",
            "• Hardware Comparator: < 100 us instant cutoff"
        ]
    },
    {
        "title": "2. EMBEDDED COMPUTATION",
        "color": "#34D399",
        "items": [
            "• In-Situ Energy: E_pulse = integral(V * I dt)",
            "• Impedance Estimation: Z_load = V_rms / I_rms",
            "• Dynamic Thermal Guard: Duty cycle power backoff",
            "• Fault Protection: Over-V / Over-I / Over-Temp"
        ]
    },
    {
        "title": "3. AUV GROUND STATION STREAM",
        "color": "#6EE7B7",
        "items": [
            "• Telemetry Format: NMEA 0183 ($SONAR sentence)",
            "• Data Link: High-speed USB-UART @ 115200 baud",
            "• Ground Station: React 19 + Web Serial API dashboard",
            "• Visuals: Live energy gauge, thermal map & spectrum"
        ]
    }
]

for c_idx, fc in enumerate(feed_cols):
    col_x = bot_x + 0.015 + c_idx * (col_w + 0.015)
    col_y = bot_y + 0.02
    
    col_bg = patches.FancyBboxPatch((col_x, col_y), col_w, 0.155,
                                    boxstyle="round,pad=0.008,rounding_size=0.012",
                                    facecolor='#1E293B', edgecolor='#334155',
                                    linewidth=1.2, zorder=3)
    ax.add_patch(col_bg)
    
    ax.text(col_x + 0.015, col_y + 0.132, fc["title"],
            fontsize=9, fontweight='bold', color=fc["color"], ha='left', va='center')
    
    for it_idx, item in enumerate(fc["items"]):
        ax.text(col_x + 0.015, col_y + 0.098 - (it_idx * 0.028), item,
                fontsize=7.8, color='#CBD5E1', ha='left', va='center')

# Green feedback loop arrows from Stage 03/04 down into Stage 05
ax.annotate('', xy=(bot_x + bot_w * 0.5, bot_y + bot_h + 0.005), 
            xytext=(start_x + 3 * (card_w + gap_x) + card_w * 0.5, top_y - 0.005),
            arrowprops=dict(arrowstyle="->", color="#10B981", lw=2.2, linestyle="--",
                            connectionstyle="arc3,rad=-0.18"),
            zorder=5)

# Pill label on feedback arrow
arrow_pill = patches.FancyBboxPatch((0.68, 0.33), 0.22, 0.028,
                                    boxstyle="round,pad=0.004,rounding_size=0.01",
                                    facecolor='#064E3B', edgecolor='#10B981',
                                    linewidth=1, zorder=6)
ax.add_patch(arrow_pill)
ax.text(0.79, 0.344, "Closed-Loop V / I / Temp Sensor Feedback",
        fontsize=7.5, fontweight='bold', color='#6EE7B7', ha='center', va='center')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('docs/ocean_sdr_simple_architecture.png', dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
print("Saved docs/ocean_sdr_simple_architecture.png successfully!")
