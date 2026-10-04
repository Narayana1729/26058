import matplotlib.pyplot as plt
import matplotlib.patches as patches

# High-DPI professional slide graphic: Simple 5-Stage Architecture
fig, ax = plt.subplots(figsize=(16, 8.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Title & Subtitle
ax.text(0.5, 0.93, "OCEAN-SDR : System Architecture", 
        fontsize=24, fontweight='bold', color='#0F172A', ha='center', va='center', fontfamily='sans-serif')
ax.text(0.5, 0.87, "End-to-End Signal Chain: From Mission Parameters to Acoustic Emission & Telemetry", 
        fontsize=13, color='#475569', ha='center', va='center', fontfamily='sans-serif')

# Define the 5 main pipeline stages
stages = [
    {
        "num": "01",
        "title": "MISSION CONTROL",
        "subtitle": "Waveform Synthesis",
        "tech": "STM32 ARM Cortex-M\nBare-Metal C99 / CMSIS",
        "points": [
            "• Programmable Chirp (LFM)",
            "• Tukey Tapering (α = 0.25)",
            "• Zero spectral splatter",
            "• Frequency: 10 – 100 kHz"
        ],
        "color": "#0284C7",
        "light_color": "#F0F9FF",
        "border": "#BAE6FD"
    },
    {
        "num": "02",
        "title": "SIGNAL RECONSTRUCTION",
        "subtitle": "DAC & Active Filtering",
        "tech": "Circular DMA + Dual Sallen-Key\nOp-Amp: OPA1612 (Low Noise)",
        "points": [
            "• 12-Bit DAC @ 1–2 MSPS",
            "• 4th-Order Butterworth LPF",
            "• Cutoff fc = 100 kHz",
            "• > 48 dB/oct anti-aliasing"
        ],
        "color": "#0284C7",
        "light_color": "#F0F9FF",
        "border": "#BAE6FD"
    },
    {
        "num": "03",
        "title": "POWER AMPLIFIER",
        "subtitle": "High-Voltage Driver",
        "tech": "Class-AB Linear Booster\n+ Toroidal Impedance Match",
        "points": [
            "• Dual-rail high-V drive",
            "• Output: 20 – 100 Vpp",
            "• Low harmonic distortion",
            "• Thermal heatsink coupled"
        ],
        "color": "#0369A1",
        "light_color": "#F0F9FF",
        "border": "#BAE6FD"
    },
    {
        "num": "04",
        "title": "ACOUSTIC TRANSDUCER",
        "subtitle": "Piezo Projector",
        "tech": "PZT Ceramic Resonator\nSubmersible (100 m Depth)",
        "points": [
            "• Electromechanical emission",
            "• Source Level: > 175 dB",
            "• Resonant match (BVD model)",
            "• Directional acoustic ping"
        ],
        "color": "#0F172A",
        "light_color": "#F8FAFC",
        "border": "#CBD5E1"
    }
]

# Layout parameters
box_w = 0.21
box_h = 0.44
start_x = 0.04
gap_x = 0.035
box_y = 0.36

# Draw 4 sequential stages
for i, stage in enumerate(stages):
    bx = start_x + i * (box_w + gap_x)
    
    # Outer card
    rect = patches.FancyBboxPatch((bx, box_y), box_w, box_h,
                                  boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor=stage["light_color"], edgecolor=stage["border"],
                                  linewidth=1.8, zorder=2)
    ax.add_patch(rect)
    
    # Top banner pill for stage number
    pill = patches.FancyBboxPatch((bx + 0.015, box_y + box_h - 0.04), 0.04, 0.025,
                                  boxstyle="round,pad=0.005,rounding_size=0.01",
                                  facecolor=stage["color"], edgecolor='none', zorder=3)
    ax.add_patch(pill)
    ax.text(bx + 0.035, box_y + box_h - 0.0275, stage["num"],
            fontsize=10, fontweight='bold', color='#FFFFFF', ha='center', va='center')
    
    # Stage Title & Subtitle
    ax.text(bx + 0.065, box_y + box_h - 0.0275, stage["title"],
            fontsize=11, fontweight='bold', color=stage["color"], ha='left', va='center')
    ax.text(bx + 0.015, box_y + box_h - 0.07, stage["subtitle"],
            fontsize=10, fontweight='bold', color='#1E293B', ha='left', va='center')
    
    # Tech tag box
    tech_box = patches.FancyBboxPatch((bx + 0.015, box_y + box_h - 0.155), box_w - 0.03, 0.065,
                                      boxstyle="round,pad=0.005,rounding_size=0.01",
                                      facecolor='#FFFFFF', edgecolor='#E2E8F0',
                                      linewidth=1.2, zorder=3)
    ax.add_patch(tech_box)
    ax.text(bx + (box_w)/2, box_y + box_h - 0.122, stage["tech"],
            fontsize=8.5, color='#0284C7' if i < 3 else '#334155', fontweight='bold', ha='center', va='center', multialignment='center')

    # Bullet points
    for p_idx, pt in enumerate(stage["points"]):
        ax.text(bx + 0.015, box_y + box_h - 0.19 - (p_idx * 0.048), pt,
                fontsize=8.5, color='#334155', ha='left', va='center')

    # Arrow between cards
    if i < len(stages) - 1:
        arr_x = bx + box_w + 0.005
        arr_y = box_y + box_h * 0.58
        ax.annotate('', xy=(arr_x + gap_x - 0.01, arr_y), xytext=(arr_x, arr_y),
                    arrowprops=dict(facecolor='#0284C7', edgecolor='none', width=2.5, headwidth=8, headlength=7),
                    zorder=4)

# Bottom Full-Width Card: Closed-Loop Monitoring & Ground Station Telemetry
bot_w = 4 * box_w + 3 * gap_x
bot_h = 0.22
bot_y = 0.07
bot_x = start_x

bot_rect = patches.FancyBboxPatch((bot_x, bot_y), bot_w, bot_h,
                                  boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor='#F8FAFC', edgecolor='#CBD5E1',
                                  linewidth=1.8, zorder=2)
ax.add_patch(bot_rect)

# Bottom Badge
bot_pill = patches.FancyBboxPatch((bot_x + 0.02, bot_y + bot_h - 0.035), 0.14, 0.025,
                                  boxstyle="round,pad=0.005,rounding_size=0.01",
                                  facecolor='#059669', edgecolor='none', zorder=3)
ax.add_patch(bot_pill)
ax.text(bot_x + 0.09, bot_y + bot_h - 0.0225, "FEEDBACK & TELEMETRY",
        fontsize=9, fontweight='bold', color='#FFFFFF', ha='center', va='center')

ax.text(bot_x + 0.175, bot_y + bot_h - 0.0225, "Closed-Loop Health Monitoring & Real-Time Telemetry Stream",
        fontsize=11, fontweight='bold', color='#0F172A', ha='left', va='center')

# 3 columns inside the bottom feedback card
col_w = (bot_w - 0.08) / 3

col_data = [
    {
        "title": "Synchronous ADC Sensing",
        "points": [
            "• Current sense (INA169) & Peak V monitor",
            "• Heatsink thermistor thermal guard",
            "• Hardware interrupt fault cutoff (< 100 µs)"
        ]
    },
    {
        "title": "On-Board Pulse Energy & Health",
        "points": [
            "• In-situ pulse energy calculation: E = ∫ V·I dt",
            "• Dynamic duty cycle & thermal power throttling",
            "• Transducer impedance drift detection"
        ]
    },
    {
        "title": "AUV Ground Station Telemetry",
        "points": [
            "• High-speed USB-UART (115200 baud)",
            "• Standardized $SONAR NMEA 0183 sentences",
            "• Live Web Serial API React 19 dashboard"
        ]
    }
]

for c_idx, col in enumerate(col_data):
    cx = bot_x + 0.02 + c_idx * (col_w + 0.02)
    cy = bot_y + 0.03
    
    # Inner column box
    c_box = patches.FancyBboxPatch((cx, cy), col_w, 0.125,
                                   boxstyle="round,pad=0.005,rounding_size=0.01",
                                   facecolor='#FFFFFF', edgecolor='#E2E8F0',
                                   linewidth=1.2, zorder=3)
    ax.add_patch(c_box)
    
    ax.text(cx + col_w / 2, cy + 0.105, col["title"],
            fontsize=9.5, fontweight='bold', color='#0284C7', ha='center', va='center')
    
    for p_i, pt in enumerate(col["points"]):
        ax.text(cx + 0.01, cy + 0.075 - (p_i * 0.032), pt,
                fontsize=8, color='#334155', ha='left', va='center')

# Feedback loop arrows from Transducer & PA down to Sensing
ax.annotate('', xy=(start_x + 0.15, bot_y + bot_h + 0.005), 
            xytext=(start_x + 3 * (box_w + gap_x) + box_w / 2, box_y - 0.005),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=2, linestyle="--",
                            connectionstyle="arc3,rad=0.15"),
            zorder=4)

ax.text(0.72, 0.31, "Closed-Loop V / I / Temp Feedback",
        fontsize=8.5, fontweight='bold', color='#059669', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='#ECFDF5', edgecolor='#A7F3D0', lw=1))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('docs/simple_architecture_slide.png', dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
print("Successfully generated docs/simple_architecture_slide.png")
