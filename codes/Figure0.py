#!/usr/bin/env python3
"""
Figure 1: Study Site Location Map (ESSD / Nature Style)
Features:
- Regional Context (India -> Karnataka)
- Zoom Lines (connecting Regional Box -> Catchment Map)
- Consistent Sensor Star
- North Arrow & Scale Bar
"""

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, ConnectionPatch
import matplotlib.patheffects as pe

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
BASE = "."
FILES = {
    "india": f"{BASE}/india_India_Country_Boundary/india_India_Country_Boundary.shp",
    "states": f"{BASE}/india_India_Country_Boundary/State.shp",
    "bera": f"{BASE}/Berambadi.shp"
}
OUTPUT = "./Figure1_StudyLocation_Zoom.png"

# Sensor Coordinates
SENSOR_XY = (76.587991, 11.761146)

# Visual Settings
STAR_STYLE = dict(marker="*", color="#d62728", markeredgecolor="black", markeredgewidth=1.0, zorder=20)
BOX_STYLE = dict(fill=False, edgecolor="black", linewidth=1.5, linestyle="-", zorder=10)

# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------
def add_north_arrow(ax, xy=(0.95, 0.95), size=0.1):
    """Draw a simple North arrow in axes coordinates."""
    ax.annotate('N', xy=xy, xytext=(xy[0], xy[1]-size),
                arrowprops=dict(facecolor='black', width=4, headwidth=10, headlength=12),
                ha='center', va='top', fontsize=12, fontweight='bold', xycoords='axes fraction')

def add_scale_bar(ax, length_km, location=(0.1, 0.05)):
    """Approximation scale bar (for Lat/Lon plots)."""
    # 1 deg lat ~ 111 km. This is a visual estimation helper.
    # length_deg approx length_km / 111
    length_deg = length_km / 111.0
    x, y = location
    ax.plot([x, x + length_deg], [y, y], transform=ax.transData, color='black', linewidth=3)
    ax.plot([x, x + length_deg], [y, y], transform=ax.transData, color='white', linewidth=1) # stripe
    ax.text(x + length_deg/2, y + 0.01, f"{length_km} km", transform=ax.transData, 
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# ---------------------------------------------------------------------
# MAIN PLOT
# ---------------------------------------------------------------------
def main():
    # 1. Load Data
    india = gpd.read_file(FILES["india"]).to_crs(epsg=4326)
    states = gpd.read_file(FILES["states"]).to_crs(epsg=4326)
    bera = gpd.read_file(FILES["bera"]).to_crs(epsg=4326)
    karnataka = states[states["KGISStateN"].str.contains("Karnataka", case=False)]

    # 2. Setup Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw={'width_ratios': [1, 1.2]})
    plt.subplots_adjust(wspace=0.1) # Bring panels closer for zoom lines

    # ================= PANEL A: REGIONAL (INDIA + KARNATAKA) =================
    india.plot(ax=ax1, color="#f0f0f0", edgecolor="#bdbdbd", linewidth=0.5)
    karnataka.plot(ax=ax1, color="#deb887", edgecolor="black", linewidth=0.8, alpha=0.5)
    
    # Define Zoom Box (Area of Interest)
    # We make it larger than Berambadi so it's visible on the India map
    # Berambadi bounds: ~76.5 to 76.7 Lon, ~11.7 to 11.8 Lat
    # We'll create a box from 75.5 to 78.0 Lon, 11.0 to 13.0 Lat (Visual Context)
    minx, miny, maxx, maxy = bera.total_bounds
    pad = 1.0 # Large padding for visibility
    box_x = [minx-pad, maxx+pad, maxx+pad, minx-pad, minx-pad]
    box_y = [miny-pad, miny-pad, maxy+pad, maxy+pad, miny-pad]
    
    # Draw the box in Panel A
    rect = Rectangle((minx-pad, miny-pad), (maxx-minx)+2*pad, (maxy-miny)+2*pad, **BOX_STYLE)
    ax1.add_patch(rect)
    
    # Plot Sensor (Small star in A)
    ax1.plot(*SENSOR_XY, **STAR_STYLE, markersize=10) # Smaller star for regional map

    ax1.set_title("(a) Regional Context", loc='left', fontweight="bold", fontsize=12)
    ax1.set_aspect("equal")
    ax1.axis("off")
    
    # Add North Arrow to A
    add_north_arrow(ax1, xy=(0.92, 0.95))

    # ================= PANEL B: CATCHMENT (BERAMBADI) =================
    bera.plot(ax=ax2, color="#e5f5e0", edgecolor="#31a354", linewidth=2, alpha=0.6)
    
    # Plot Sensor (Big star in B)
    ax2.plot(*SENSOR_XY, **STAR_STYLE, markersize=22, label="Observation Station")
    
    # Add context text
    ax2.text(SENSOR_XY[0], SENSOR_XY[1]+0.015, "Soil Moisture\nStation", 
             ha='center', fontsize=10, fontweight='bold',
             path_effects=[pe.withStroke(linewidth=3, foreground="white")])

    ax2.set_title("(b) Berambadi Catchment", loc='left', fontweight="bold", fontsize=12)
    ax2.set_aspect("equal")
    
    # Clean grid for B (Optional: Add Lat/Lon ticks if desired, usually maps are cleaner without)
    ax2.set_xticks([])
    ax2.set_yticks([])
    for spine in ax2.spines.values(): spine.set_visible(False) # Remove box border

    # Add Scale Bar (Approx 5km)
    # We place it manually based on data bounds
    sb_x = minx + 0.02
    sb_y = miny + 0.01
    add_scale_bar(ax2, 5, location=(sb_x, sb_y))
    
    # Add Legend for Star
    ax2.legend(loc='upper right', frameon=True, fancybox=True, framealpha=0.9)

    # ================= ZOOM LINES (CONNECTING PATCHES) =================
    # Connect right corners of Box (A) to left corners of Axes (B)
    
    # Top Line
    con1 = ConnectionPatch(
        xyA=(maxx+pad, maxy+pad), coordsA=ax1.transData,
        xyB=(0, 1), coordsB=ax2.transAxes,
        color="black", linestyle="--", linewidth=1.0
    )
    # Bottom Line
    con2 = ConnectionPatch(
        xyA=(maxx+pad, miny-pad), coordsA=ax1.transData,
        xyB=(0, 0), coordsB=ax2.transAxes,
        color="black", linestyle="--", linewidth=1.0
    )
    
    fig.add_artist(con1)
    fig.add_artist(con2)

    # ---------------------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------------------
    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=300, bbox_inches="tight")
    print(f"\n✓ Figure saved: {OUTPUT}")
    plt.show()

if __name__ == "__main__":
    main()
