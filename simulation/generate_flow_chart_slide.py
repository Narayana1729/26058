import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 16:9 widescreen presentation layout
fig, ax = plt.subplots(figsize=(16, 8.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Slide Border (light dotted border like the user image)
border_rect = patches.FancyBboxPatch((0.01, 0.01), 0.98, 0.98,
                                    boxstyle="round,pad=0.01,rounding_size=0.01",
                                    facecolor='none', edgecolor='#FCA5A5',
                                    linestyle='--', linewidth=1.2, zorder=1)
ax.add_patch(border_rect)

# Heading: "FLOW CHART" with blue underline
ax.text(0.04, 0.93, "FLOW CHART", 
        fontsize=20, fontweight='bold', color='#1E3A8A', ha='left', va='center')
ax.plot([0.04, 0.16], [0.905, 0.905], color='#1E3A8A', linewidth=2.2)

# ==================== LEFT PILLAR: ADAPTIVE TRANSMISSION ENGINE ====================
# Salmon Box: "Mission Parameters" (like GNSS in ref)
p_box = patches.FancyBboxPatch((0.15, 0.68), 0.13, 0.12,
                               boxstyle="round,pad=0.01,rounding_size=0.015",
                               facecolor='#FECACA', edgecolor='#EF4444',
                               linewidth=1.8, zorder=3)
ax.add_patch(p_box)
ax.text(0.215, 0.75, "Mission\nProfile", 
        fontsize=13, fontweight='bold', color='#7F1D1D', ha='center', va='center', multialignment='center')

# Small Cyan Pill: "Waveform Specs"
pill1 = patches.FancyBboxPatch((0.31, 0.78), 0.09, 0.045,
                               boxstyle="round,pad=0.005,rounding_size=0.01",
                               facecolor='#A7F3D0', edgecolor='#10B981',
                               linewidth=1.2, zorder=3)
ax.add_patch(pill1)
ax.text(0.355, 0.802, "Target Specs", 
        fontsize=9, fontweight='bold', color='#065F46', ha='center', va='center')

# Connect Mission Profile to Target Specs
ax.annotate('', xy=(0.31, 0.802), xytext=(0.28, 0.75),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5,
                            connectionstyle="arc3,rad=-0.2"), zorder=4)
ax.text(0.30, 0.84, "Target Range & Bathymetry", fontsize=7.5, color='#475569', ha='center')

# Down arrow from Mission Profile: "Standard Ping" -> Adaptive LFM Chirp
ax.annotate('', xy=(0.215, 0.58), xytext=(0.215, 0.68),
            arrowprops=dict(arrowstyle="->", color="#EF4444", lw=1.8), zorder=4)
ax.text(0.245, 0.63, "Chirp Select", fontsize=8.5, color='#B91C1C', fontweight='bold', ha='left')

# Cyan Box: "Adaptive LFM Chirp" (like LEO SoO in ref)
leo_box = patches.FancyBboxPatch((0.15, 0.46), 0.13, 0.12,
                                 boxstyle="round,pad=0.01,rounding_size=0.015",
                                 facecolor='#A7F3D0', edgecolor='#10B981',
                                 linewidth=1.8, zorder=3)
ax.add_patch(leo_box)
ax.text(0.215, 0.52, "Adaptive\nLFM Chirp", 
        fontsize=13, fontweight='bold', color='#065F46', ha='center', va='center', multialignment='center')

# Down arrow from LFM Chirp: "CW Fallback"
ax.annotate('', xy=(0.215, 0.36), xytext=(0.215, 0.46),
            arrowprops=dict(arrowstyle="->", color="#EF4444", lw=1.8), zorder=4)
ax.text(0.245, 0.41, "Thermal Alert", fontsize=8.5, color='#B91C1C', fontweight='bold', ha='left')

# Light Teal Box: "Safe CW / Low Duty Cycle" (like INS IMU in ref)
ins_box = patches.FancyBboxPatch((0.15, 0.24), 0.13, 0.12,
                                 boxstyle="round,pad=0.01,rounding_size=0.015",
                                 facecolor='#CCFBF1', edgecolor='#14B8A6',
                                 linewidth=1.8, zorder=3)
ax.add_patch(ins_box)
ax.text(0.215, 0.30, "Power Safe\nCW Mode", 
        fontsize=12, fontweight='bold', color='#0F766E', ha='center', va='center', multialignment='center')

# Left Output Box: "Acoustic Ping" (like PNT on left of ref)
pnt_left = patches.FancyBboxPatch((0.035, 0.49), 0.075, 0.08,
                                  boxstyle="round,pad=0.008,rounding_size=0.01",
                                  facecolor='#FFFFFF', edgecolor='#64748B',
                                  linewidth=1.5, zorder=3)
ax.add_patch(pnt_left)
ax.text(0.0725, 0.53, "Acoustic\nPing Out", 
        fontsize=10, fontweight='bold', color='#0F172A', ha='center', va='center', multialignment='center')

# Green signal arrows converging to Acoustic Ping Out
ax.annotate('', xy=(0.11, 0.53), xytext=(0.15, 0.52),
            arrowprops=dict(arrowstyle="->", color="#10B981", lw=2), zorder=4)
ax.text(0.125, 0.55, "Pulse", fontsize=8, color='#047857', fontweight='bold')

ax.annotate('', xy=(0.11, 0.55), xytext=(0.15, 0.74),
            arrowprops=dict(arrowstyle="->", color="#10B981", lw=1.5,
                            connectionstyle="arc3,rad=0.2"), zorder=4)

ax.annotate('', xy=(0.11, 0.51), xytext=(0.15, 0.30),
            arrowprops=dict(arrowstyle="->", color="#10B981", lw=1.5,
                            connectionstyle="arc3,rad=-0.2"), zorder=4)

# ==================== TOP-RIGHT BLUE CONTAINER ====================
# "Ocean Acoustic Channel Simulation" (matches Stimulation of LEO Satellite signal)
big_blue = patches.FancyBboxPatch((0.53, 0.44), 0.43, 0.46,
                                  boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor='#E0F2FE', edgecolor='#0284C7',
                                  linewidth=1.5, zorder=2)
ax.add_patch(big_blue)
ax.text(0.745, 0.88, "Ocean Acoustic Channel Simulation & Absorption", 
        fontsize=10.5, fontweight='bold', color='#0369A1', ha='center', va='center')

# Inner Cyan Boxes inside Blue Container
# Box 1: Hydrophone / Bathymetry Model
b1 = patches.FancyBboxPatch((0.55, 0.75), 0.14, 0.075,
                            boxstyle="round,pad=0.005,rounding_size=0.01",
                            facecolor='#A7F3D0', edgecolor='#059669', linewidth=1.2, zorder=3)
ax.add_patch(b1)
ax.text(0.62, 0.787, "Ocean CTD Profile\n(T, S, Depth)", fontsize=8.5, fontweight='bold', color='#065F46', ha='center', va='center')

# Box 2: Sound Speed & Ray Tracing
b2 = patches.FancyBboxPatch((0.74, 0.75), 0.10, 0.075,
                            boxstyle="round,pad=0.005,rounding_size=0.01",
                            facecolor='#A7F3D0', edgecolor='#059669', linewidth=1.2, zorder=3)
ax.add_patch(b2)
ax.text(0.79, 0.787, "Mackenzie c(T,S,D)\n& Spreading Loss", fontsize=8.2, fontweight='bold', color='#065F46', ha='center', va='center')

# Box 3: Francois-Garrison Attenuation
b3 = patches.FancyBboxPatch((0.87, 0.75), 0.075, 0.075,
                            boxstyle="round,pad=0.005,rounding_size=0.01",
                            facecolor='#A7F3D0', edgecolor='#059669', linewidth=1.2, zorder=3)
ax.add_patch(b3)
ax.text(0.907, 0.787, "Francois-\nGarrison α(f)", fontsize=8, fontweight='bold', color='#065F46', ha='center', va='center')

# Box 4: Ambient Noise & Multipath Reverberation
b4 = patches.FancyBboxPatch((0.74, 0.52), 0.16, 0.075,
                            boxstyle="round,pad=0.005,rounding_size=0.01",
                            facecolor='#A7F3D0', edgecolor='#059669', linewidth=1.2, zorder=3)
ax.add_patch(b4)
ax.text(0.82, 0.557, "Ambient Noise (Wenz)\n& Doppler Distortion", fontsize=8.2, fontweight='bold', color='#065F46', ha='center', va='center')

# Box 5: SNR Verification & Window Check
b5 = patches.FancyBboxPatch((0.55, 0.52), 0.14, 0.075,
                            boxstyle="round,pad=0.005,rounding_size=0.01",
                            facecolor='#A7F3D0', edgecolor='#059669', linewidth=1.2, zorder=3)
ax.add_patch(b5)
ax.text(0.62, 0.557, "Compare SNR &\nPulse Compression", fontsize=8.5, fontweight='bold', color='#065F46', ha='center', va='center')

# Connecting Arrows inside blue box
ax.annotate('', xy=(0.74, 0.787), xytext=(0.69, 0.787),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5), zorder=4)
ax.annotate('', xy=(0.87, 0.787), xytext=(0.84, 0.787),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5), zorder=4)
ax.annotate('', xy=(0.907, 0.557), xytext=(0.907, 0.75),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5,
                            connectionstyle="arc3,rad=-0.3"), zorder=4)
ax.annotate('', xy=(0.74, 0.557), xytext=(0.69, 0.557),
            arrowprops=dict(arrowstyle="<-", color="#334155", lw=1.5), zorder=4)

# Loop back arrow from Compare SNR back to CTD: "< 12 dB SNR: Re-adapt Pulse"
ax.annotate('', xy=(0.62, 0.75), xytext=(0.62, 0.595),
            arrowprops=dict(arrowstyle="->", color="#B91C1C", lw=1.5), zorder=4)
ax.text(0.57, 0.67, "< 12 dB SNR\n(Re-adapt)", fontsize=7.5, color='#B91C1C', fontweight='bold', ha='right')

# Path from Target Specs to Ocean Sim
ax.annotate('', xy=(0.55, 0.787), xytext=(0.40, 0.802),
            arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.8,
                            connectionstyle="arc3,rad=-0.15"), zorder=4)
ax.text(0.47, 0.835, "Environmental Sounding", fontsize=7.5, color='#0369A1', fontweight='bold', ha='center')

# ==================== BOTTOM-MIDDLE PURPLE CONTAINER ====================
# "Closed-Loop Sonar Signal Processing" (matches Adaptive signal processing in ref)
purp_box = patches.FancyBboxPatch((0.31, 0.05), 0.20, 0.64,
                                 boxstyle="round,pad=0.015,rounding_size=0.018",
                                 facecolor='#F3E8FF', edgecolor='#A855F7',
                                 linewidth=1.8, zorder=2)
ax.add_patch(purp_box)
ax.text(0.41, 0.665, "Embedded Signal Chain", 
        fontsize=10.5, fontweight='bold', color='#6B21A8', ha='center', va='center')

# 5 Pink Vertical Action Boxes inside Purple Container
pink_steps = [
    "Tukey Taper Windowing",
    "DMA DAC 2 MSPS Streaming",
    "4th-Order LPF (OPA1612)",
    "Class-AB Linear Amplification",
    "Continuous Pulse Energy Calc"
]

for s_i, step in enumerate(pink_steps):
    s_y = 0.56 - s_i * 0.105
    s_b = patches.FancyBboxPatch((0.325, s_y), 0.17, 0.065,
                                boxstyle="round,pad=0.005,rounding_size=0.008",
                                facecolor='#FCE7F3', edgecolor='#EC4899',
                                linewidth=1.2, zorder=3)
    ax.add_patch(s_b)
    ax.text(0.41, s_y + 0.0325, step, 
            fontsize=8.2, fontweight='bold', color='#9D174D', ha='center', va='center')
    
    if s_i < len(pink_steps) - 1:
        ax.annotate('', xy=(0.41, s_y - 0.04), xytext=(0.41, s_y),
                    arrowprops=dict(arrowstyle="->", color="#BE185D", lw=1.5), zorder=4)

# Connection from Blue Box (>12dB match) to Purple Container
ax.annotate('', xy=(0.51, 0.56), xytext=(0.55, 0.557),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=2), zorder=4)
ax.text(0.53, 0.585, "> 12 dB SNR (Optimal)", fontsize=8, color='#047857', fontweight='bold', ha='center')

# Connection from Purple Container back to Adaptive LFM Chirp
ax.annotate('', xy=(0.28, 0.52), xytext=(0.325, 0.52),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=2), zorder=4)

# Pink Side-Badge: "Closed-Loop Health Interlock" (matches AI Avoids Spoofed signals in ref)
side_pink = patches.FancyBboxPatch((0.55, 0.28), 0.18, 0.075,
                                  boxstyle="round,pad=0.005,rounding_size=0.01",
                                  facecolor='#FCE7F3', edgecolor='#EC4899',
                                  linewidth=1.5, zorder=3)
ax.add_patch(side_pink)
ax.text(0.64, 0.317, "Closed-Loop Thermal &\nOver-Current Guard (<100 µs)", 
        fontsize=8.5, fontweight='bold', color='#9D174D', ha='center', va='center', multialignment='center')

# Arrow from Side-Badge into Purple Processing Box
ax.annotate('', xy=(0.495, 0.32), xytext=(0.55, 0.32),
            arrowprops=dict(arrowstyle="->", color="#DB2777", lw=1.8), zorder=4)

# Telemetry NMEA Out box bottom right
tele_box = patches.FancyBboxPatch((0.76, 0.15), 0.19, 0.12,
                                  boxstyle="round,pad=0.01,rounding_size=0.015",
                                  facecolor='#ECFDF5', edgecolor='#10B981',
                                  linewidth=1.8, zorder=3)
ax.add_patch(tele_box)
ax.text(0.855, 0.21, "AUV Telemetry\n$SONAR Stream\n(115200 Baud)", 
        fontsize=9.5, fontweight='bold', color='#065F46', ha='center', va='center', multialignment='center')

# Arrow from Step 5 to Telemetry Out
ax.annotate('', xy=(0.76, 0.21), xytext=(0.495, 0.14),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=1.8,
                            connectionstyle="arc3,rad=-0.15"), zorder=4)
ax.text(0.62, 0.12, "Synchronous V/I/Temp Sensing", fontsize=8, color='#047857', fontweight='bold', ha='center')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('docs/ocean_sdr_flow_chart.png', dpi=300, facecolor='#FFFFFF', bbox_inches='tight')
print("Successfully generated docs/ocean_sdr_flow_chart.png")
