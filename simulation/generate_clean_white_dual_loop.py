import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 16:9 Presentation Aspect Ratio, Clean Modern White Theme
fig, ax = plt.subplots(figsize=(16, 8.8), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Header
ax.text(0.5, 0.95, "OCEAN-SDR : Dual-Loop Adaptive Architecture", 
        fontsize=22, fontweight='bold', color='#0F172A', ha='center', va='center', fontfamily='sans-serif')
ax.text(0.5, 0.90, "How the Transmitter Adapts: Environmental Acoustic Prior + Real-Time Electrical Health Governance", 
        fontsize=12, color='#475569', ha='center', va='center', fontfamily='sans-serif')

# ==================== LOOP 1 (TOP): ENVIRONMENTAL PRIOR ====================
l1_box = patches.FancyBboxPatch((0.04, 0.52), 0.92, 0.34,
                                boxstyle="round,pad=0.015,rounding_size=0.02",
                                facecolor='#F0F9FF', edgecolor='#0284C7',
                                linewidth=1.8, zorder=2)
ax.add_patch(l1_box)

l1_pill = patches.FancyBboxPatch((0.06, 0.815), 0.24, 0.032,
                                 boxstyle="round,pad=0.005,rounding_size=0.01",
                                 facecolor='#0284C7', edgecolor='none', zorder=3)
ax.add_patch(l1_pill)
ax.text(0.18, 0.831, "LOOP 1 : ENVIRONMENTAL ACOUSTIC PRIOR",
        fontsize=9, fontweight='bold', color='#FFFFFF', ha='center', va='center')

l1_steps = [
    {
        "num": "01",
        "title": "SENSE ENVIRONMENT",
        "sub": "Ocean Multi-Sensor Hub",
        "color": "#0369A1",
        "pts": ["• Temperature (DS18B20)", "• Depth (MS5837 Hydrostatic)", "• Salinity (Conductivity / Pot)", "• Turbidity (TSW-20 Optical)"]
    },
    {
        "num": "02",
        "title": "PHYSICS PREDICTION",
        "sub": "Theoretical Ocean Prior",
        "color": "#0369A1",
        "pts": ["• Mackenzie c(T,S,D) Sound Speed", "• François-Garrison Absorption α(f)", "• 3 Chemical Relaxation Modes", "• Spreading Loss: 20 log R"]
    },
    {
        "num": "03",
        "title": "WAVEFORM SELECTION",
        "sub": "Candidate Prior Bank",
        "color": "#0369A1",
        "pts": ["• LFM Chirp: High range resolution", "• HFM Chirp: Doppler invariant", "• CW Mode: Narrowband tracking", "• Barker-13: Stealth phase code"]
    },
    {
        "num": "04",
        "title": "SPECTRUM CONDITIONING",
        "sub": "Tukey Taper & DMA Stream",
        "color": "#0369A1",
        "pts": ["• Tukey Window (α = 0.25)", "• -32 dB Sidelobe Suppression", "• Zero-CPU Timer TRGO DMA", "• 12-Bit DAC @ 2.0 MSPS"]
    }
]

step_w = 0.20
step_gap = 0.024
step_x = 0.065
step_y = 0.55

for s_i, st in enumerate(l1_steps):
    sx = step_x + s_i * (step_w + step_gap)
    
    s_card = patches.FancyBboxPatch((sx, step_y), step_w, 0.24,
                                   boxstyle="round,pad=0.008,rounding_size=0.015",
                                   facecolor='#FFFFFF', edgecolor='#BAE6FD',
                                   linewidth=1.2, zorder=3)
    ax.add_patch(s_card)
    
    ax.text(sx + 0.015, step_y + 0.21, f"[{st['num']}] {st['title']}", 
            fontsize=9.5, fontweight='bold', color=st["color"], ha='left', va='center')
    ax.text(sx + 0.015, step_y + 0.18, st["sub"], 
            fontsize=8.2, fontweight='bold', color='#64748B', ha='left', va='center')
    
    ax.plot([sx + 0.015, sx + step_w - 0.015], [step_y + 0.16, step_y + 0.16],
            color='#E2E8F0', linewidth=1, zorder=4)
    
    for p_idx, pt in enumerate(st["pts"]):
        ax.text(sx + 0.012, step_y + 0.13 - (p_idx * 0.035), pt,
                fontsize=8, color='#334155', ha='left', va='center')
        
    if s_i < len(l1_steps) - 1:
        ax.annotate('', xy=(sx + step_w + step_gap - 0.005, step_y + 0.12), 
                    xytext=(sx + step_w + 0.003, step_y + 0.12),
                    arrowprops=dict(facecolor='#0284C7', edgecolor='none', width=2, headwidth=6, headlength=6),
                    zorder=5)

# Downward Transmission Arrow
ax.annotate('', xy=(0.85, 0.44), xytext=(0.85, 0.52),
            arrowprops=dict(facecolor='#059669', edgecolor='none', width=3, headwidth=9, headlength=8),
            zorder=6)
ax.text(0.85, 0.48, "TRANSMIT PING\n(4th-Order LPF + Class-AB PA)", 
        fontsize=8.5, fontweight='bold', color='#065F46', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='#D1FAE5', edgecolor='#10B981', lw=1))

# ==================== LOOP 2 (BOTTOM): HARDWARE & ENERGY ADAPTATION ====================
l2_box = patches.FancyBboxPatch((0.04, 0.07), 0.92, 0.35,
                                boxstyle="round,pad=0.015,rounding_size=0.02",
                                facecolor='#ECFDF5', edgecolor='#10B981',
                                linewidth=1.8, zorder=2)
ax.add_patch(l2_box)

l2_pill = patches.FancyBboxPatch((0.06, 0.375), 0.28, 0.032,
                                 boxstyle="round,pad=0.005,rounding_size=0.01",
                                 facecolor='#059669', edgecolor='none', zorder=3)
ax.add_patch(l2_pill)
ax.text(0.20, 0.391, "LOOP 2 : TRANSMITTER HEALTH & ENERGY GOVERNOR",
        fontsize=9, fontweight='bold', color='#FFFFFF', ha='center', va='center')

l2_steps = [
    {
        "num": "05",
        "title": "SYNCHRONOUS SENSING",
        "sub": "Live Metrology @ PA",
        "color": "#047857",
        "pts": ["• INA169 Shunt: Transmit Current I(t)", "• Precision Divider: Rail Voltage V(t)", "• NTC Thermistor: PA Heatsink Temp", "• Emergency Cutoff: < 100 µs fault"]
    },
    {
        "num": "06",
        "title": "ENERGY ACCOUNTING",
        "sub": "In-Situ Integration on MCU",
        "color": "#047857",
        "pts": ["• E_pulse = ∫ V(t)·I(t) dt", "• E_remaining = E_budget - Σ E_pulse", "• Dynamic Battery Sag Tracking", "• Real-Time Impedance Verification"]
    },
    {
        "num": "07",
        "title": "ENERGY GOVERNOR",
        "sub": "Multi-Tier State Machine",
        "color": "#047857",
        "pts": ["• >60% Budget: 100% Full Power", "• 20–60% Budget: -25% Pulse Duration", "• <20% Budget: 60% Amp, -50% Duration", "• Prevents Mission Blackout"]
    },
    {
        "num": "08",
        "title": "THERMAL STATE GUARD",
        "sub": "Active PA Heatsink Protection",
        "color": "#047857",
        "pts": ["• <50°C: Normal Transmission", "• 50–70°C: Warning (PRI +50%)", "• 70–85°C: Throttling (Amp -40%)", "• >85°C: Safe Thermal Shutdown"]
    }
]

step_y2 = 0.10
for s_i, st in enumerate(l2_steps):
    sx = step_x + s_i * (step_w + step_gap)
    
    s_card = patches.FancyBboxPatch((sx, step_y2), step_w, 0.24,
                                   boxstyle="round,pad=0.008,rounding_size=0.015",
                                   facecolor='#FFFFFF', edgecolor='#A7F3D0',
                                   linewidth=1.2, zorder=3)
    ax.add_patch(s_card)
    
    ax.text(sx + 0.015, step_y2 + 0.21, f"[{st['num']}] {st['title']}", 
            fontsize=9.5, fontweight='bold', color=st["color"], ha='left', va='center')
    ax.text(sx + 0.015, step_y2 + 0.18, st["sub"], 
            fontsize=8.2, fontweight='bold', color='#64748B', ha='left', va='center')
    
    ax.plot([sx + 0.015, sx + step_w - 0.015], [step_y2 + 0.16, step_y2 + 0.16],
            color='#E2E8F0', linewidth=1, zorder=4)
    
    for p_idx, pt in enumerate(st["pts"]):
        ax.text(sx + 0.012, step_y2 + 0.13 - (p_idx * 0.035), pt,
                fontsize=8, color='#334155', ha='left', va='center')
        
    if s_i < len(l2_steps) - 1:
        ax.annotate('', xy=(sx + step_w + step_gap - 0.005, step_y2 + 0.12), 
                    xytext=(sx + step_w + 0.003, step_y2 + 0.12),
                    arrowprops=dict(facecolor='#059669', edgecolor='none', width=2, headwidth=6, headlength=6),
                    zorder=5)

# Feedback Arrow from Step 08 back to Loop 1 Step 03
ax.annotate('', xy=(step_x + 2 * (step_w + step_gap) + step_w / 2, step_y - 0.01), 
            xytext=(step_x + 3 * (step_w + step_gap) + step_w / 2, step_y2 + 0.245),
            arrowprops=dict(arrowstyle="->", color="#D97706", lw=2.5, linestyle="--",
                            connectionstyle="arc3,rad=0.3"),
            zorder=6)

ax.text(0.68, 0.44, "ADAPT NEXT PULSE PARAMETERS\n(Energy-Aware Modulation & Duration Throttling)",
        fontsize=8.5, fontweight='bold', color='#92400E', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='#FEF3C7', edgecolor='#F59E0B', lw=1))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('docs/dual_loop_adaptation_clean_white.png', dpi=300, facecolor='#FFFFFF', bbox_inches='tight')
plt.savefig('additional_docs/simulation_images/presentation_slides/dual_loop_adaptation_clean_white.png', dpi=300, facecolor='#FFFFFF', bbox_inches='tight')
print("Saved docs/dual_loop_adaptation_clean_white.png successfully!")
