import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Clean, minimalist high-impact white theme (matches official SIH winner slide decks)
fig, ax = plt.subplots(figsize=(16, 7.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Slide Title & Subtitle
ax.text(0.5, 0.93, "OCEAN-SDR : Simplified System Architecture", 
        fontsize=22, fontweight='bold', color='#0F172A', ha='center', va='center')
ax.text(0.5, 0.86, "High-Level Hardware Pipeline & Closed-Loop Telemetry Path", 
        fontsize=12, color='#475569', ha='center', va='center')

# 4 Main pipeline blocks
blocks = [
    {
        "title": "01. MCU SYNTHESIS",
        "sub": "STM32 ARM Cortex-M4",
        "points": [
            "• LFM Chirp (10–100 kHz)",
            "• Tukey Window (α = 0.25)",
            "• Zero-CPU Circular DMA"
        ],
        "bg": "#EFF6FF",
        "border": "#3B82F6",
        "title_color": "#1D4ED8"
    },
    {
        "title": "02. ACTIVE FILTER",
        "sub": "Reconstruction & DAC",
        "points": [
            "• 12-Bit DAC @ 2 MSPS",
            "• 4th-Order Butterworth",
            "• Cutoff fc = 100 kHz LPF"
        ],
        "bg": "#EFF6FF",
        "border": "#3B82F6",
        "title_color": "#1D4ED8"
    },
    {
        "title": "03. POWER AMPLIFIER",
        "sub": "High-Voltage Driver",
        "points": [
            "• Class-AB Linear Driver",
            "• 20Vpp – 100Vpp Output",
            "• Toroidal Transformer"
        ],
        "bg": "#EFF6FF",
        "border": "#3B82F6",
        "title_color": "#1D4ED8"
    },
    {
        "title": "04. TRANSDUCER",
        "sub": "Piezoelectric Projector",
        "points": [
            "• PZT Ceramic Resonator",
            "• Source Level: > 175 dB",
            "• Submersible to 100 m"
        ],
        "bg": "#F8FAFC",
        "border": "#64748B",
        "title_color": "#0F172A"
    }
]

bw = 0.205
bh = 0.32
by = 0.42
gap = 0.045
start_x = 0.035

for i, b in enumerate(blocks):
    bx = start_x + i * (bw + gap)
    
    # Outer box
    rect = patches.FancyBboxPatch((bx, by), bw, bh,
                                  boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor=b["bg"], edgecolor=b["border"],
                                  linewidth=2, zorder=2)
    ax.add_patch(rect)
    
    # Title & Sub
    ax.text(bx + bw/2, by + bh - 0.045, b["title"],
            fontsize=12, fontweight='bold', color=b["title_color"], ha='center', va='center')
    ax.text(bx + bw/2, by + bh - 0.08, b["sub"],
            fontsize=9.5, fontweight='bold', color='#64748B', ha='center', va='center')
    
    # Divider
    ax.plot([bx + 0.02, bx + bw - 0.02], [by + bh - 0.105, by + bh - 0.105],
            color=b["border"], linewidth=1, alpha=0.5, zorder=3)
    
    # Bullet points
    for p_i, pt in enumerate(b["points"]):
        ax.text(bx + 0.015, by + bh - 0.155 - (p_i * 0.05), pt,
                fontsize=9, color='#1E293B', ha='left', va='center')
        
    # Flow arrow between forward blocks
    if i < len(blocks) - 1:
        ax.annotate('', xy=(bx + bw + gap - 0.008, by + bh * 0.55), 
                    xytext=(bx + bw + 0.005, by + bh * 0.55),
                    arrowprops=dict(facecolor='#2563EB', edgecolor='none', width=3, headwidth=10, headlength=8),
                    zorder=4)

# ==================== BOTTOM FEEDBACK BLOCK ====================
bot_w = 4 * bw + 3 * gap
bot_h = 0.22
bot_y = 0.08
bot_x = start_x

bot_rect = patches.FancyBboxPatch((bot_x, bot_y), bot_w, bot_h,
                                  boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor='#ECFDF5', edgecolor='#10B981',
                                  linewidth=2, zorder=2)
ax.add_patch(bot_rect)

# Bottom Title
ax.text(bot_x + 0.03, bot_y + bot_h - 0.035, "05. CLOSED-LOOP HEALTH MONITORING & TELEMETRY",
        fontsize=12, fontweight='bold', color='#065F46', ha='left', va='center')

# 3 Feedback pillars
f_w = (bot_w - 0.06) / 3
feed_items = [
    ("Synchronous Sensing", [
        "• INA169 High-Side Current Sensing (Isense)",
        "• Precision Resistor Divider (Vpeak)",
        "• NTC Thermistor Heatsink Monitoring"
    ]),
    ("Embedded Health Engine", [
        "• In-Situ Pulse Energy: E = ∫ V·I dt",
        "• Real-time complex load impedance check",
        "• Hardware fault emergency cutoff (<100 µs)"
    ]),
    ("AUV Ground Station Stream", [
        "• Standardized NMEA 0183 ($SONAR sentence)",
        "• USB-UART Stream @ 115200 baud",
        "• React 19 live telemetry dashboard"
    ])
]

for idx, (head, pts) in enumerate(feed_items):
    fx = bot_x + 0.02 + idx * (f_w + 0.01)
    fy = bot_y + 0.02
    
    fbox = patches.FancyBboxPatch((fx, fy), f_w, 0.13,
                                  boxstyle="round,pad=0.01,rounding_size=0.015",
                                  facecolor='#FFFFFF', edgecolor='#A7F3D0',
                                  linewidth=1.2, zorder=3)
    ax.add_patch(fbox)
    
    ax.text(fx + f_w/2, fy + 0.105, head,
            fontsize=10, fontweight='bold', color='#047857', ha='center', va='center')
    
    for p_idx, pt in enumerate(pts):
        ax.text(fx + 0.012, fy + 0.072 - (p_idx * 0.03), pt,
                fontsize=8, color='#1E293B', ha='left', va='center')

# Feedback loop arrow coming back from Transducer & PA down to Sensing
ax.annotate('', xy=(start_x + 0.12, bot_y + bot_h + 0.005), 
            xytext=(start_x + 3 * (bw + gap) + bw / 2, by - 0.005),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=2.2, linestyle="--",
                            connectionstyle="arc3,rad=0.14"),
            zorder=5)

ax.text(0.72, 0.36, "Closed-Loop Feedback: V / I / Temp Sensors",
        fontsize=8.5, fontweight='bold', color='#065F46', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='#D1FAE5', edgecolor='#6EE7B7', lw=1))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('docs/simple_architecture_clean_white.png', dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
print("Saved docs/simple_architecture_clean_white.png successfully!")
