#!/usr/bin/env python3
"""
Figure 2 (V6 - Minimal Adaptation)
- Adapted for V6 dataset (single sensor at 5cm, no _A suffix)
- No changes to figure appearance or colors
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

# ==========================================
# 1. SETUP
# ==========================================
DATA_PATH = '../2017_V6.csv'  # V6 path
OUT_DIR = './section2_output'
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 10,
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'sans-serif'],
    'figure.dpi': 300,
    'axes.linewidth': 1.0,
    'xtick.direction': 'out',
    'ytick.direction': 'out'
})

# STRICT COLOR CONSISTENCY
C_RAIN  = '#08519c'  # Blue
C_5CM   = '#d95f02'  # Orange (Always 5cm)
C_50CM  = '#1b9e77'  # Green  (Always 50cm)
C_DAILY = '#525252'  # Gray (Daily Mean)
C_RATE  = '#d62728'  # Red (Wetting Rate)

def generate_figure():
    try:
        df = pd.read_csv(DATA_PATH)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except FileNotFoundError:
        print(f"Error: {DATA_PATH} not found.")
        return

    # Window Selection
    start_main, end_main = '2017-08-25', '2017-10-15'
    df_m = df[(df['timestamp'] >= start_main) & (df['timestamp'] <= end_main)].copy()
    
    # Zoom Window
    start_zoom, end_zoom = '2017-09-01 06:00', '2017-09-04 06:00'
    df_z = df[(df['timestamp'] >= start_zoom) & (df['timestamp'] <= end_zoom)].copy()

    # --- CALCULATIONS (V6: changed SM_5cm_A → SM_5cm) ---
    df_daily = df_m.set_index('timestamp').resample('D').mean().reset_index()
    df_daily['timestamp'] += pd.Timedelta(hours=12)
    df_m['wetting_rate'] = df_m['SM_5cm'].diff().clip(lower=0)  # V6: no _A
    df_m['deep_pulse'] = df_m['SM_50cm'].diff().rolling(4).mean().clip(lower=0)

    # --- PLOTTING ---
    fig = plt.figure(figsize=(8, 11), constrained_layout=True)
    gs = fig.add_gridspec(5, 1, height_ratios=[0.6, 2.0, 1.1, 1.1, 0.7])

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax4 = fig.add_subplot(gs[3], sharex=ax1)
    ax5 = fig.add_subplot(gs[4], sharex=ax1)

    # (a) RAINFALL
    ax1.vlines(df_m['timestamp'], 0, df_m['Precipitation'], colors=C_RAIN, lw=2)
    ax1.set_ylabel('Precip.\n(mm)', fontweight='bold')
    ax1.set_ylim(0, df_m['Precipitation'].max()*1.15)
    ax1.text(0.01, 0.85, '(a) Rainfall Forcing', transform=ax1.transAxes, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    ax1.text(0.99, 0.85, '15-min intervals', transform=ax1.transAxes, ha='right', fontsize=9, color='gray', style='italic')

    # (b) MOISTURE DYNAMICS (V6: SM_5cm_A → SM_5cm)
    ax2.plot(df_m['timestamp'], df_m['SM_5cm'], color=C_5CM, lw=1.5, label='5 cm')  # V6
    ax2.plot(df_m['timestamp'], df_m['SM_50cm'], color=C_50CM, lw=1.5, label='50 cm')
    ax2.plot(df_daily['timestamp'], df_daily['SM_5cm'], color=C_DAILY, ls='--', lw=1.5, alpha=0.8, label='Daily Mean')  # V6
    
    # Background shading
    ax2b = ax2.twinx()
    ax2b.fill_between(df_m['timestamp'], 0, df_m['deep_pulse'], color='gray', alpha=0.15)
    ax2b.set_yticks([])

    ax2.set_ylabel('Soil Moisture\n(% VWC)', fontweight='bold')
    ax2.legend(loc='upper right', frameon=False, ncol=3, fontsize=9)
    ax2.text(0.01, 0.95, '(b) Moisture Dynamics', transform=ax2.transAxes, fontweight='bold')

    # (c) BULK EC (V6: EC_5cm_A → EC_5cm)
    ax3.plot(df_m['timestamp'], df_m['EC_5cm'], color=C_5CM, lw=1.2, alpha=0.9, label='5 cm')  # V6
    ax3.plot(df_m['timestamp'], df_m['EC_50cm'], color=C_50CM, lw=1.2, alpha=0.8, label='50 cm')
    ax3.set_ylabel('Bulk EC\n(dS m$^{-1}$)', fontweight='bold')
    ax3.text(0.01, 0.9, '(c) Bulk EC Dynamics', transform=ax3.transAxes, fontweight='bold')

    # (d) TEMPERATURE (V6: Temp_5cm_A → Temp_5cm)
    ax4.plot(df_m['timestamp'], df_m['Temp_5cm'], color=C_5CM, lw=1.2, label='5 cm')  # V6
    ax4.plot(df_m['timestamp'], df_m['Temp_50cm'], color=C_50CM, lw=1.2, label='50 cm')
    ax4.set_ylabel('Temp.\n($^{\circ}$C)', fontweight='bold')
    ax4.text(0.01, 0.9, '(d) Thermal Damping', transform=ax4.transAxes, fontweight='bold')

    # (e) WETTING RATE
    ax5.fill_between(df_m['timestamp'], 0, df_m['wetting_rate'], color=C_RATE, alpha=0.7)
    ax5.set_ylabel('ΔSM / 15 min\n(%)', fontweight='bold', fontsize=9, color=C_RATE)
    ax5.text(0.01, 0.82, '(e) Rapid Wetting Rate', transform=ax5.transAxes, fontweight='bold', color=C_RATE)
    ax5.text(0.99, 0.82, 'Invisible in daily data', transform=ax5.transAxes, ha='right', fontsize=9, color=C_RATE, style='italic')
    max_rate = df_m['wetting_rate'].max()
    ax5.set_ylim(0, max_rate * 1.1 if max_rate > 0 else 1.0)

    # --- INSET (V6: SM_5cm_A → SM_5cm) ---
    axins = inset_axes(ax2, width="35%", height="45%", loc='center right', borderpad=1)
    axins.plot(df_z['timestamp'], df_z['SM_5cm'], color=C_5CM, lw=2)  # V6
    axins.plot(df_z['timestamp'], df_z['SM_50cm'], color=C_50CM, lw=2)
    axins.set_xlim(pd.to_datetime(start_zoom), pd.to_datetime(end_zoom))
    axins.set_title("Wetting Front", fontsize=9)
    
    # FIX: Use 'Day-Month' format and rotate labels
    axins.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    axins.tick_params(axis='x', labelsize=8, rotation=45) 
    axins.tick_params(axis='y', labelsize=8)
    
    mark_inset(ax2, axins, loc1=3, loc2=4, fc="none", ec="0.4", ls='--', lw=0.8)

    # Final Formatting
    ax5.set_xlabel('Date (2017)', fontweight='bold')
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    
    for ax in [ax1, ax2, ax3, ax4]:
        plt.setp(ax.get_xticklabels(), visible=False)
        ax.grid(axis='x', color='gray', alpha=0.1)
        ax.grid(axis='y', linestyle=':', alpha=0.3)
    ax5.grid(True, linestyle=':', alpha=0.3)

    plt.savefig(os.path.join(OUT_DIR, 'Figure2_ESSD_V6.png'))
    print("Figure saved: V6 dataset (Figure appearance unchanged)")

if __name__ == "__main__":
    generate_figure()
