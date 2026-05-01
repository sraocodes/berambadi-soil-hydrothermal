#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figure S1: Technical Validation (V6 - ESSD Publication Quality)
Thermal-Hydraulic Diagnostics (2016-2025)

CHANGES:
- Nature/ESSD style formatting (clean spines, Helvetica/Arial fonts).
- Robust percolation metric (normalized by valid days).
- Explicit 'Data Quality' annotation boxes.
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ================= CONFIGURATION =================
DATA_DIR = '/home/sathya-iisc/Documents/TIMESERIES/Aarya/V6'
OUT_DIR = '/home/sathya-iisc/Documents/TIMESERIES/AaryaOUT'
os.makedirs(OUT_DIR, exist_ok=True)

# PLOT STYLE
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.alpha'] = 0.3

# ================= LOGIC FUNCTIONS =================
def analyze_year_diagnostics(filepath):
    """
    Calculate validation metrics for one year.
    """
    year_str = Path(filepath).stem.split('_')[0]
    if not year_str.isdigit(): return None
    year = int(year_str)
    
    try:
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        required = ['SM_5cm', 'SM_50cm', 'Temp_5cm', 'Temp_50cm']
        if not all(col in df.columns for col in required):
            return None
        
        # Filter for valid complete rows only
        df = df.dropna(subset=['timestamp'] + required)
        if len(df) < 100: return None
        
        # Convert
        sm5 = pd.to_numeric(df['SM_5cm'], errors='coerce')
        sm50 = pd.to_numeric(df['SM_50cm'], errors='coerce')
        t5 = pd.to_numeric(df['Temp_5cm'], errors='coerce')
        t50 = pd.to_numeric(df['Temp_50cm'], errors='coerce')
        
        n_valid = len(df)
        
        # --- DIAGNOSTIC 1: Thermal Response ---
        # Surface (5cm) should fluctuate more than Deep (50cm).
        # Inversion (Deep > Surface) happens naturally at night.
        # If this is 0% or 100%, sensor is broken. 40-70% is healthy.
        temp_inversion_pct = (t50 > t5).mean() * 100
        
        # --- DIAGNOSTIC 2: Vertical Connectivity ---
        # Does 50cm respond? (Difference > 0.5% in 15 mins is a wetting pulse)
        # We normalize by "valid days" to handle partial years fairly.
        sm50_jumps = (sm50.diff() > 0.5).sum()
        valid_days = n_valid / 96.0
        events_per_week = (sm50_jumps / valid_days) * 7
        
        # --- DIAGNOSTIC 3: Hydraulic Physics ---
        # "Bottom Wetter" (50cm > 5cm) should be RARE in semi-arid (evap dominated).
        # If this is >90%, it implies a swamp or broken sensor.
        bottom_wetter_pct = (sm50 > sm5).mean() * 100
        
        # "Downward Potential" (5cm >> 50cm) happens during rain.
        downward_potential_pct = (sm5 > (sm50 + 5.0)).mean() * 100
        
        # Coverage
        full_year_days = 366 if (year % 4 == 0) else 365
        if year == 2025: full_year_days = 181 # Jan-Jun
        coverage_pct = (valid_days / full_year_days) * 100
        
        return {
            'year': year,
            'temp_inversion_pct': temp_inversion_pct,
            'percolation_metric': events_per_week, # Events per week
            'bottom_wetter_pct': bottom_wetter_pct,
            'head_down_pct': downward_potential_pct,
            'coverage_pct': coverage_pct
        }
        
    except Exception as e:
        print(f"Error {year}: {e}")
        return None

# ================= VISUALIZATION =================
def format_panel(ax, title, ylabel):
    ax.set_ylabel(ylabel, fontweight='bold', fontsize=11)
    ax.set_title(title, loc='left', fontweight='bold', fontsize=12, pad=10)
    ax.grid(axis='y', linestyle='--', zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def plot_figure_s1(df, outpath):
    years = df['year'].values
    n_years = len(years)
    x = np.arange(n_years)
    
    # Color mapping for data quality
    colors = []
    for c in df['coverage_pct']:
        if c > 95: colors.append('#2ca02c') # Green (Good)
        elif c > 80: colors.append('#ff7f0e') # Orange (OK)
        else: colors.append('#9467bd') # Purple (Partial)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # --- PANEL A: Thermal Inversion ---
    ax1.bar(x, df['temp_inversion_pct'], color=colors, edgecolor='k', alpha=0.8, zorder=3)
    format_panel(ax1, '(a) Thermal Response Validation', 'Inversion Frequency\n(% of time)')
    ax1.set_ylim(0, 100)
    
    # Annotation
    ax1.text(1.02, 0.5, "Validates sensor\nresponse times", transform=ax1.transAxes, 
             va='center', style='italic', fontsize=10, 
             bbox=dict(facecolor='#f0f0f0', edgecolor='none', pad=5))

    # --- PANEL B: Percolation ---
    ax2.bar(x, df['percolation_metric'], color=colors, edgecolor='k', alpha=0.8, zorder=3)
    format_panel(ax2, '(b) Vertical Connectivity Check', 'Deep Wetting Events\n(per week)')
    ax2.set_ylim(0, max(df['percolation_metric'])*1.2)
    
    ax2.text(1.02, 0.5, "Validates 50cm\nsensor physics", transform=ax2.transAxes, 
             va='center', style='italic', fontsize=10,
             bbox=dict(facecolor='#f0f0f0', edgecolor='none', pad=5))

    # --- PANEL C: Hydraulic State ---
    width = 0.35
    ax3.bar(x - width/2, df['head_down_pct'], width, label='Downward Gradient (Rain)', 
            color='#1f77b4', edgecolor='k', alpha=0.9, zorder=3)
    ax3.bar(x + width/2, df['bottom_wetter_pct'], width, label='Inverted Gradient (Bottom Wet)', 
            color='#d62728', edgecolor='k', alpha=0.9, zorder=3)
    
    format_panel(ax3, '(c) Hydraulic Regime Consistency', 'Occurrence Frequency\n(% of time)')
    ax3.legend(loc='upper left', frameon=True, framealpha=0.9)
    ax3.set_ylim(0, 40) # Zoom in to show the rarity
    
    ax3.text(1.02, 0.5, "Validates semi-arid\nevaporative regime", transform=ax3.transAxes, 
             va='center', style='italic', fontsize=10,
             bbox=dict(facecolor='#f0f0f0', edgecolor='none', pad=5))

    # X-Axis
    ax3.set_xticks(x)
    ax3.set_xticklabels(years, fontweight='bold', fontsize=11)
    
    # Partial Year Markers
    for i, cov in enumerate(df['coverage_pct']):
        if cov < 80:
            ax3.text(i, -5, '*', ha='center', va='top', fontsize=20, color='#d62728', fontweight='bold')

    # Global Legend for Colors
    patches = [
        mpatches.Patch(color='#2ca02c', label='Complete Year (>95%)'),
        mpatches.Patch(color='#ff7f0e', label='Near-Complete (>80%)'),
        mpatches.Patch(color='#9467bd', label='Partial Year (<80%)'),
        mpatches.Patch(color='none', label='* Data Gap Present')
    ]
    fig.legend(handles=patches, loc='upper center', bbox_to_anchor=(0.5, 0.05), 
               ncol=4, frameon=False, fontsize=10)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.08, right=0.85) # Make room for side notes
    plt.savefig(outpath, dpi=300)
    print(f"✓ Figure saved to: {outpath}")

# ================= MAIN =================
def main():
    print("Processing V6 Diagnostics...")
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*_V6.csv')))
    
    results = []
    for f in files:
        r = analyze_year_diagnostics(f)
        if r: results.append(r)
        
    if not results:
        print("No data found.")
        return
        
    df = pd.DataFrame(results)
    print(df[['year', 'coverage_pct', 'percolation_metric']])
    
    plot_figure_s1(df, os.path.join(OUT_DIR, 'FigureS1_V6_ESSD.png'))

if __name__ == "__main__":
    main()