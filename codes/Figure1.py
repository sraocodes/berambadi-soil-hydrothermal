#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIGURE 1 GENERATOR: Space-Optimized (ESSD / Nature Style)
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, ConnectionPatch
import matplotlib.patheffects as pe
import seaborn as sns
import geopandas as gpd
import warnings

warnings.filterwarnings('ignore')

# ================= CONFIGURATION =================
DATA_DIR = '/home/sathya-iisc/Documents/TIMESERIES/Aarya/V6'
MAP_BASE = "/home/sathya-iisc/Documents/TIMESERIES/V6Analysis"
SHP_INDIA = f"{MAP_BASE}/india_India_Country_Boundary/india_India_Country_Boundary.shp"
SHP_STATES = f"{MAP_BASE}/india_India_Country_Boundary/State.shp"
SHP_BERA = f"{MAP_BASE}/Berambadi.shp"
OUT_DIR = '/home/sathya-iisc/Documents/TIMESERIES/AaryaOUT'
os.makedirs(OUT_DIR, exist_ok=True)

SENSOR_XY = (76.587991, 11.761146)

# Styles
STAR_STYLE = dict(marker="*", color="#d62728", markeredgecolor="black", markeredgewidth=0.8, zorder=20)
BOX_STYLE = dict(fill=False, edgecolor="black", linewidth=1.2, linestyle="-", zorder=10)

# ================= DATA LOGIC (Condensed) =================
def get_coverage_data():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*_V6.csv')))
    results = []
    for f in files:
        try:
            df = pd.read_csv(f)
            if 'timestamp' not in df.columns: continue
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp', 'SM_5cm', 'SM_50cm'])
            if len(df) < 1000: continue
            
            # Simple coverage calc
            year = int(os.path.basename(f).split('_')[0])
            days = df['timestamp'].dt.date.nunique()
            exp = 181 if year == 2025 else (366 if year%4==0 else 365)
            results.append({'year': year, 'coverage_pct': (days/exp)*100})
        except: continue
    return pd.DataFrame(results)

# ================= PLOTTING =================
def main():
    df_cov = get_coverage_data()
    
    # Load Maps
    india = gpd.read_file(SHP_INDIA).to_crs(epsg=4326)
    states = gpd.read_file(SHP_STATES).to_crs(epsg=4326)
    bera = gpd.read_file(SHP_BERA).to_crs(epsg=4326)
    karnataka = states[states["KGISStateN"].str.contains("Karnataka", case=False)]

    # === OPTIMIZED LAYOUT ===
    # figsize=(12, 10) fits standard A4/Letter page width nicely
    fig = plt.figure(figsize=(12, 10))
    
    # GridSpec: 
    # Row 1 (Maps): Height 1.3 relative to Row 2
    # Row 1 Cols: Width ratios [0.8, 1.2] -> Give Map B (Catchment) more space!
    gs = fig.add_gridspec(2, 2, height_ratios=[1.3, 0.8], width_ratios=[0.7, 1.3], 
                          hspace=0.15, wspace=0.1)

    ax1 = fig.add_subplot(gs[0, 0]) # India (Smaller)
    ax2 = fig.add_subplot(gs[0, 1]) # Berambadi (Hero)
    ax3 = fig.add_subplot(gs[1, :]) # Timeline (Bottom)

    # --- PANEL A: INDIA ---
    india.plot(ax=ax1, color="#f5f5f5", edgecolor="#bfbfbf", linewidth=0.5)
    karnataka.plot(ax=ax1, color="#e6d8ad", edgecolor="#505050", linewidth=0.6, alpha=0.8)
    
    # Zoom Box
    minx, miny, maxx, maxy = bera.total_bounds
    pad = 0.8
    rect = Rectangle((minx-pad, miny-pad), (maxx-minx)+2*pad, (maxy-miny)+2*pad, **BOX_STYLE)
    ax1.add_patch(rect)
    ax1.plot(*SENSOR_XY, **STAR_STYLE, markersize=8)

    ax1.set_title("(a) Regional Context", loc='left', fontweight="bold", fontsize=12)
    ax1.set_aspect("equal")
    ax1.axis("off")

    # --- PANEL B: BERAMBADI (HERO MAP) ---
    bera.plot(ax=ax2, color="#e5f5e0", edgecolor="#31a354", linewidth=1.5, alpha=0.7)
    ax2.plot(*SENSOR_XY, **STAR_STYLE, markersize=20, label="Station")
    
    # Label
    ax2.text(SENSOR_XY[0], SENSOR_XY[1]+0.012, "Soil Moisture\nStation", 
             ha='center', fontsize=10, fontweight='bold',
             path_effects=[pe.withStroke(linewidth=3, foreground="white")])

    ax2.set_title("(b) Berambadi Catchment", loc='left', fontweight="bold", fontsize=12)
    ax2.set_aspect("equal")
    ax2.axis("off")
    
    # Scale Bar (Approx 5km)
    sb_x, sb_y = minx + 0.015, miny + 0.01
    ax2.plot([sb_x, sb_x + 5/111], [sb_y, sb_y], color='black', lw=2)
    ax2.text(sb_x + 2.5/111, sb_y + 0.005, "5 km", ha='center', fontsize=9, fontweight='bold')

    # Zoom Lines
    con1 = ConnectionPatch(xyA=(maxx+pad, maxy+pad), coordsA=ax1.transData,
                           xyB=(0, 1), coordsB=ax2.transAxes, color="black", linestyle="--", lw=0.6)
    con2 = ConnectionPatch(xyA=(maxx+pad, miny-pad), coordsA=ax1.transData,
                           xyB=(0, 0), coordsB=ax2.transAxes, color="black", linestyle="--", lw=0.6)
    fig.add_artist(con1)
    fig.add_artist(con2)

    # --- PANEL C: TIMELINE ---
    years = df_cov['year'].values
    vals = df_cov['coverage_pct'].values
    colors = ['#1b9e77' if c > 95 else '#d95f02' if c > 80 else '#7570b3' for c in vals]
    
    bars = ax3.bar(years, vals, color=colors, edgecolor='black', linewidth=1, width=0.65)
    
    # Text inside/above bars
    for bar, v in zip(bars, vals):
        ax3.text(bar.get_x() + bar.get_width()/2, v + 2, f'{v:.0f}%', 
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax3.set_title("(c) Temporal Data Availability (2016–2025)", loc='left', fontweight="bold", fontsize=12)
    ax3.set_ylabel("Coverage (%)", fontweight='bold')
    ax3.set_ylim(0, 115)
    ax3.set_xticks(years)
    ax3.set_xticklabels(years, fontsize=11, fontweight='bold')
    ax3.grid(axis='y', linestyle=':', alpha=0.5)
    sns.despine(ax=ax3)

    # Smart Legend (Inside Plot to save margin space)
    patches = [
        mpatches.Patch(color='#1b9e77', label='Complete (>95%)'),
        mpatches.Patch(color='#d95f02', label='Near-complete (>80%)'),
        mpatches.Patch(color='#7570b3', label='Partial (<80%)')
    ]
    # Place legend in empty top-left or top-right space of bar chart
    ax3.legend(handles=patches, loc='upper center', bbox_to_anchor=(0.5, 1.05), 
               ncol=3, frameon=False, fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'Figure1_Optimized.png'), dpi=300)
    print(f"✓ Saved Optimized Figure 1")
    plt.show()

if __name__ == "__main__":
    main()