import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from matplotlib.lines import Line2D

# Set font styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# Load the source images from docs/assets
img_clean_arch = mpimg.imread('docs/assets/clean_simulation_architecture.jpg')
img_proteus    = mpimg.imread('docs/assets/proteus_cosimulation.jpg')

# ==============================================================================
# 1. LIGHT THEMED SLIDE (Matches the PyroSat Presentation Theme)
# ==============================================================================
fig = plt.figure(figsize=(16, 9), dpi=300)
fig.patch.set_facecolor('#FCFBF7')

# Master rounded white card
ax_card = fig.add_axes([0.015, 0.02, 0.97, 0.96])
ax_card.set_axis_off()
card_rect = patches.FancyBboxPatch(
    (0, 0), 1, 1,
    boxstyle="round,pad=0.01,rounding_size=0.02",
    facecolor="#FFFFFF",
    edgecolor="#EADDC7",
    linewidth=2.0,
    transform=ax_card.transAxes
)
ax_card.add_patch(card_rect)

# ------------------------------------------------------------------------------
# TOP HEADER BLOCK: TITLE & SIGNAL PIPELINE FLOW DIAGRAM
# ------------------------------------------------------------------------------
ax_top = fig.add_axes([0.04, 0.74, 0.92, 0.21])
ax_top.set_axis_off()
ax_top.set_xlim(0, 100)
ax_top.set_ylim(0, 100)

# Slide Title
ax_top.text(50, 85, "OCEAN-SDR TECHNICAL ARCHITECTURE", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#0A2540')

# Flow Diagram Blocks: Sensors -> STM32 -> Waveform -> DAC -> Filter -> PA -> Output
blocks = [
    ("Sensors", "Temp/Depth/Turb"),
    ("STM32", "Cortex-M4 Prior"),
    ("Waveform", "DDS Engine"),
    ("DAC", "12-Bit PA4"),
    ("Filter", "4th-Order LPF"),
    ("PA", "Half-Bridge"),
    ("Output", "Transducer")
]

x_positions = np.linspace(5, 95, len(blocks))
box_w = 10.5
box_h = 32

for i, (b_name, b_sub) in enumerate(blocks):
    xp = x_positions[i]
    is_core = (b_name in ["STM32", "DAC", "PA"])
    
    # Styled block box
    box = patches.FancyBboxPatch(
        (xp - box_w/2, 36), box_w, box_h,
        boxstyle="round,pad=0.5,rounding_size=2.0",
        facecolor="#EBF5FF" if is_core else "#F4F7FA",
        edgecolor="#1E75D8" if is_core else "#CFD8DC",
        linewidth=1.4 if is_core else 1.0
    )
    ax_top.add_patch(box)
    
    ax_top.text(xp, 58, b_name, ha='center', va='center', fontsize=11, fontweight='bold', 
                color='#0D47A1' if is_core else '#263238')
    ax_top.text(xp, 44, b_sub, ha='center', va='center', fontsize=7.2, color='#546E7A')
    
    # Forward arrows between blocks
    if i < len(blocks) - 1:
        next_xp = x_positions[i+1]
        arrow = patches.FancyArrowPatch(
            (xp + box_w/2 + 0.5, 52), (next_xp - box_w/2 - 0.5, 52),
            arrowstyle='->,head_width=3.5,head_length=5',
            color='#1E75D8', linewidth=1.8
        )
        ax_top.add_patch(arrow)

# V / I / T Feedback Loop (from PA back to STM32)
pa_x = x_positions[5]     # PA center
stm32_x = x_positions[1]  # STM32 center

# Drop down from PA
ax_top.plot([pa_x, pa_x], [36, 16], color='#D32F2F', lw=1.8, ls='-')
# Horizontal line back to STM32
ax_top.plot([pa_x, stm32_x], [16, 16], color='#D32F2F', lw=1.8, ls='-')
# Arrow up to STM32
arrow_fb = patches.FancyArrowPatch(
    (stm32_x, 16), (stm32_x, 34),
    arrowstyle='->,head_width=4,head_length=5.5',
    color='#D32F2F', linewidth=1.8
)
ax_top.add_patch(arrow_fb)

# Feedback badge label
ax_top.text((pa_x + stm32_x)/2, 16, "  V / I / T Electrical & Thermal Feedback (INA180 + TMP36)  ", 
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#B71C1C',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFEBEE', edgecolor='#EF9A9A', lw=1.0))

# Horizontal Divider Line separating Top and Bottom sections
fig.add_artist(Line2D([0.04, 0.96], [0.73, 0.73], color='#E0E6ED', linewidth=1.5))

# ------------------------------------------------------------------------------
# BOTTOM LEFT PANEL: SYSTEM ARCHITECTURE
# ------------------------------------------------------------------------------
ax_left_container = fig.add_axes([0.04, 0.05, 0.445, 0.66])
ax_left_container.set_axis_off()

# Panel frame card
left_box = patches.FancyBboxPatch(
    (0, 0), 1, 1,
    boxstyle="round,pad=0.01,rounding_size=0.02",
    facecolor="#F8FAFC",
    edgecolor="#CFD8DC",
    linewidth=1.2,
    transform=ax_left_container.transAxes
)
ax_left_container.add_patch(left_box)

# Panel Header
ax_left_container.text(0.04, 0.94, "SYSTEM ARCHITECTURE", 
                       fontsize=12.5, fontweight='bold', color='#0A2540',
                       transform=ax_left_container.transAxes)
ax_left_container.text(0.04, 0.88, "4-Module Co-Simulation Pipeline (DSP, Analog, Ocean Prior, Firmware)", 
                       fontsize=8.5, color='#546E7A',
                       transform=ax_left_container.transAxes)

# Embed image inside frame
ax_left_img = fig.add_axes([0.052, 0.075, 0.421, 0.495])
ax_left_img.imshow(img_clean_arch)
ax_left_img.set_axis_off()

# ------------------------------------------------------------------------------
# BOTTOM RIGHT PANEL: HARDWARE SIMULATION (PROTEUS SCHEMATIC)
# ------------------------------------------------------------------------------
ax_right_container = fig.add_axes([0.515, 0.05, 0.445, 0.66])
ax_right_container.set_axis_off()

# Panel frame card
right_box = patches.FancyBboxPatch(
    (0, 0), 1, 1,
    boxstyle="round,pad=0.01,rounding_size=0.02",
    facecolor="#F8FAFC",
    edgecolor="#CFD8DC",
    linewidth=1.2,
    transform=ax_right_container.transAxes
)
ax_right_container.add_patch(right_box)

# Panel Header & Subtitle
ax_right_container.text(0.04, 0.94, "HARDWARE SIMULATION", 
                        fontsize=12.5, fontweight='bold', color='#0D47A1',
                        transform=ax_right_container.transAxes)
ax_right_container.text(0.04, 0.88, "STM32 + 4th-Order Sallen-Key Filter + Closed-Loop Power Control", 
                        fontsize=8.5, fontweight='bold', color='#1E75D8',
                        transform=ax_right_container.transAxes)

# Embed Proteus schematic image
ax_right_img = fig.add_axes([0.527, 0.075, 0.421, 0.495])
ax_right_img.imshow(img_proteus)
ax_right_img.set_axis_off()

# Save light version
out_light = "docs/technical_architecture_slide.png"
plt.savefig(out_light, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
print(f"✅ Generated light-themed architecture slide at: {out_light}")

# ==============================================================================
# 2. DARK TERMINAL THEMED SLIDE (Matches the Exact Attached Wireframe Style)
# ==============================================================================
plt.style.use('dark_background')
fig_dark = plt.figure(figsize=(16, 9), dpi=300)
fig_dark.patch.set_facecolor('#0B0F19')

# Card frame
ax_dcard = fig_dark.add_axes([0.015, 0.02, 0.97, 0.96])
ax_dcard.set_axis_off()
dcard_rect = patches.FancyBboxPatch(
    (0, 0), 1, 1,
    boxstyle="round,pad=0.01,rounding_size=0.02",
    facecolor="#101726",
    edgecolor="#2A3B53",
    linewidth=1.8,
    transform=ax_dcard.transAxes
)
ax_dcard.add_patch(dcard_rect)

# Top Block
ax_dtop = fig_dark.add_axes([0.04, 0.74, 0.92, 0.21])
ax_dtop.set_axis_off()
ax_dtop.set_xlim(0, 100)
ax_dtop.set_ylim(0, 100)

ax_dtop.text(50, 85, "OCEAN-SDR TECHNICAL ARCHITECTURE", 
             ha='center', va='center', fontsize=18, fontweight='bold', color='#00F0FF',
             family='monospace')

for i, (b_name, b_sub) in enumerate(blocks):
    xp = x_positions[i]
    box_d = patches.FancyBboxPatch(
        (xp - box_w/2, 36), box_w, box_h,
        boxstyle="round,pad=0.5,rounding_size=2.0",
        facecolor="#162235",
        edgecolor="#00F0FF" if b_name in ["STM32", "DAC", "PA"] else "#2A3B53",
        linewidth=1.4 if b_name in ["STM32", "DAC", "PA"] else 1.0
    )
    ax_dtop.add_patch(box_d)
    ax_dtop.text(xp, 58, b_name, ha='center', va='center', fontsize=11, fontweight='bold', 
                 color='#FFFFFF', family='monospace')
    ax_dtop.text(xp, 44, b_sub, ha='center', va='center', fontsize=7.2, color='#8EA4C1')
    
    if i < len(blocks) - 1:
        next_xp = x_positions[i+1]
        arrow_d = patches.FancyArrowPatch(
            (xp + box_w/2 + 0.5, 52), (next_xp - box_w/2 - 0.5, 52),
            arrowstyle='->,head_width=3.5,head_length=5',
            color='#00F0FF', linewidth=1.6
        )
        ax_dtop.add_patch(arrow_d)

ax_dtop.plot([pa_x, pa_x], [36, 16], color='#FF2E63', lw=1.8, ls='-')
ax_dtop.plot([pa_x, stm32_x], [16, 16], color='#FF2E63', lw=1.8, ls='-')
arrow_dfb = patches.FancyArrowPatch(
    (stm32_x, 16), (stm32_x, 34),
    arrowstyle='->,head_width=4,head_length=5.5',
    color='#FF2E63', linewidth=1.8
)
ax_dtop.add_patch(arrow_dfb)

ax_dtop.text((pa_x + stm32_x)/2, 16, "  V / I / T Feedback (Voltage / Current / Thermal)  ", 
             ha='center', va='center', fontsize=9.0, fontweight='bold', color='#FF2E63',
             family='monospace',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#26131F', edgecolor='#FF2E63', lw=1.0))

fig_dark.add_artist(Line2D([0.04, 0.96], [0.73, 0.73], color='#2A3B53', linewidth=1.5))

# Bottom Left Panel
ax_dl_container = fig_dark.add_axes([0.04, 0.05, 0.445, 0.66])
ax_dl_container.set_axis_off()
dl_box = patches.FancyBboxPatch(
    (0, 0), 1, 1,
    boxstyle="round,pad=0.01,rounding_size=0.02",
    facecolor="#131B2B",
    edgecolor="#2A3B53",
    linewidth=1.2,
    transform=ax_dl_container.transAxes
)
ax_dl_container.add_patch(dl_box)

ax_dl_container.text(0.04, 0.94, "SYSTEM ARCHITECTURE", 
                     fontsize=12.5, fontweight='bold', color='#00F0FF',
                     family='monospace', transform=ax_dl_container.transAxes)
ax_dl_container.text(0.04, 0.88, "Multi-Layer System Simulation Pipeline", 
                     fontsize=8.5, color='#8EA4C1', transform=ax_dl_container.transAxes)

ax_dl_img = fig_dark.add_axes([0.052, 0.075, 0.421, 0.495])
ax_dl_img.imshow(img_clean_arch)
ax_dl_img.set_axis_off()

# Bottom Right Panel
ax_dr_container = fig_dark.add_axes([0.515, 0.05, 0.445, 0.66])
ax_dr_container.set_axis_off()
dr_box = patches.FancyBboxPatch(
    (0, 0), 1, 1,
    boxstyle="round,pad=0.01,rounding_size=0.02",
    facecolor="#131B2B",
    edgecolor="#2A3B53",
    linewidth=1.2,
    transform=ax_dr_container.transAxes
)
ax_dr_container.add_patch(dr_box)

ax_dr_container.text(0.04, 0.94, "HARDWARE SIMULATION", 
                     fontsize=12.5, fontweight='bold', color='#00FFA3',
                     family='monospace', transform=ax_dr_container.transAxes)
ax_dr_container.text(0.04, 0.88, "STM32 + filter + control (Proteus VSM Co-Simulation)", 
                     fontsize=8.5, fontweight='bold', color='#00FFA3',
                     family='monospace', transform=ax_dr_container.transAxes)

ax_dr_img = fig_dark.add_axes([0.527, 0.075, 0.421, 0.495])
ax_dr_img.imshow(img_proteus)
ax_dr_img.set_axis_off()

out_dark = "docs/technical_architecture_dark.png"
plt.savefig(out_dark, dpi=300, facecolor=fig_dark.get_facecolor(), bbox_inches='tight')
print(f"✅ Generated dark-themed architecture slide at: {out_dark}")
