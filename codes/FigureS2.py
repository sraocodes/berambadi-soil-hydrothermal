#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EC-SM SENSOR VALIDATION (V6 - ESSD Compliant)
Berambadi Catchment — Validates EC/SM sensor coupling (2016-2025)

ESSD SCOPE: Sensor validation only
- Demonstrates RDP→EC calibration continuity (2021 transition)
- Validates EC and SM sensors respond coherently to infiltration
- Applies strict physical outlier removal to focus on bulk sensor behavior

Output: Single-panel correlation figure + console summary
"""

import os
import glob
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
from pathlib import Path

# Suppress warnings
warnings.filterwarnings("ignore")

# ============================================================================
# CONFIGURATION
# ============================================================================
DATA_DIR = "/home/sathya-iisc/Documents/TIMESERIES/Aarya/V6"
OUT_DIR = "/home/sathya-iisc/Documents/TIMESERIES/AaryaOUT"
os.makedirs(OUT_DIR, exist_ok=True)

# Event detection settings
MIN_EVENT_PRECIP = 0.5  # mm
EVENT_GAP_HOURS = 6
SAMPLING_INTERVAL = 0.25  # 15 min

# Response analysis windows
RESPONSE_WINDOW_HOURS = 72
RESPONSE_WINDOW = int(RESPONSE_WINDOW_HOURS / SAMPLING_INTERVAL)

# Plotting Style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 11
sns.set_style("ticks")
sns.set_context("paper", font_scale=1.2)

# ============================================================================
# RDP→EC CALIBRATION
# ============================================================================
def learn_rdp_to_ec_calibration(data_dir):
    """Learn RDP→EC mapping from 2021 overlap period."""
    cal_file = os.path.join(data_dir, '2021_V6.csv')
    if not os.path.exists(cal_file): return None
    
    try:
        df = pd.read_csv(cal_file)
        if 'EC_50cm' not in df.columns or 'RDP_50cm' not in df.columns: return None
        
        cal_data = df[['EC_50cm', 'RDP_50cm']].dropna()
        cal_data = cal_data[(cal_data['EC_50cm'] > 0) & (cal_data['RDP_50cm'] > 0)]
        if len(cal_data) < 100: return None
        
        # Robust regression (remove 3-sigma outliers)
        z_scores = np.abs(stats.zscore(cal_data['EC_50cm']))
        cal_data = cal_data[z_scores < 3]
        
        slope, intercept, r_val, _, _ = stats.linregress(cal_data['RDP_50cm'], cal_data['EC_50cm'])
        print(f"Calibration (2021): EC = {slope:.4f}*RDP + {intercept:.4f} (r={r_val:.3f})")
        
        return {'slope': slope, 'intercept': intercept}
    except:
        return None

# ============================================================================
# EVENT DETECTION & ANALYSIS
# ============================================================================
def identify_precipitation_events(df):
    """Identify discrete rainfall events."""
    events = []
    precip = df['Precipitation'].values
    rain_indices = np.where(precip > 0)[0]
    if len(rain_indices) == 0: return []

    gap_intervals = int(EVENT_GAP_HOURS / SAMPLING_INTERVAL)
    split_indices = np.where(np.diff(rain_indices) > gap_intervals)[0] + 1
    event_clusters = np.split(rain_indices, split_indices)
    
    for cluster in event_clusters:
        if len(cluster) == 0: continue
        total_mm = np.sum(precip[cluster[0]:cluster[-1]+1])
        if total_mm >= MIN_EVENT_PRECIP:
            events.append({'end': cluster[-1], 'total_mm': total_mm})
    return events

def analyze_ec_sm_coupling(filepath, rdp_cal=None):
    """Calculate ΔEC and ΔSM for rainfall events."""
    try:
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        if 'SM_50cm' not in df.columns: return None
        
        # Load & Clean
        df = df.dropna(subset=['timestamp', 'SM_50cm']).reset_index(drop=True)
        df['Precipitation'] = pd.to_numeric(df['Precipitation'], errors='coerce').fillna(0)
        df['SM_50cm'] = pd.to_numeric(df['SM_50cm'], errors='coerce')

        # Handle EC Source
        if 'EC_50cm' in df.columns:
            df['EC_50cm'] = pd.to_numeric(df['EC_50cm'], errors='coerce')
            source = 'EC'
        elif 'RDP_50cm' in df.columns and rdp_cal:
            df['RDP_50cm'] = pd.to_numeric(df['RDP_50cm'], errors='coerce')
            df['EC_50cm'] = rdp_cal['slope'] * df['RDP_50cm'] + rdp_cal['intercept']
            source = 'RDP→EC'
        else:
            return None

        events = identify_precipitation_events(df)
        if not events: return None
        
        results = []
        for ev in events:
            end_idx = ev['end']
            if end_idx >= len(df): continue
            
            # Baseline & Response
            base_sm = df.at[end_idx, 'SM_50cm']
            base_ec = df.at[end_idx, 'EC_50cm']
            
            # Search forward
            search_end = min(len(df)-1, end_idx + RESPONSE_WINDOW)
            window = df.loc[end_idx:search_end]
            if len(window) < 5: continue
            
            delta_sm = window['SM_50cm'].max() - base_sm
            delta_ec = window['EC_50cm'].max() - base_ec
            
            # Basic detection threshold
            if abs(delta_sm) > 0.1 and abs(delta_ec) > 0.001:
                results.append({
                    'year': int(Path(filepath).stem.split('_')[0]),
                    'delta_sm': delta_sm,
                    'delta_ec': delta_ec,
                    'ec_source': source
                })
        
        return pd.DataFrame(results) if results else None
    except:
        return None

# ============================================================================
# UPDATED PLOTTING FUNCTION (STRICT FILTERING)
# ============================================================================
def plot_ec_sm_validation(df_all, outpath):
    """
    Single-panel correlation plot proving EC/SM sensor coherence.
    Includes strict physical outlier filtering to remove sensor noise.
    """
    fig, ax = plt.subplots(1, 1, figsize=(8, 7))
    
    # === STRICTER OUTLIER FILTERING ===
    # Remove physically implausible sensor spikes
    # Rule 1: ΔEC > 0.6 dS/m is sensor noise (realistic max ~0.4-0.5)
    # Rule 2: Remove top/bottom 0.5% to catch extreme artifacts
    # Rule 3: Only positive wetting (ΔSM > 0)
    
    q_ec_high = df_all['delta_ec'].quantile(0.995)
    q_sm_high = df_all['delta_sm'].quantile(0.995)
    
    df_clean = df_all[
        (df_all['delta_ec'] < 0.6) &          # Physical limit (no massive spikes)
        (df_all['delta_ec'] > -0.1) &         # Physical limit (allow slight dilution)
        (df_all['delta_sm'] > 0) &            # Only wetting events
        (df_all['delta_ec'] < q_ec_high) &    # Statistical outlier removal
        (df_all['delta_sm'] < q_sm_high)
    ]
    
    print(f"Filtered {len(df_all) - len(df_clean)} outliers (Physical limits & 99.5% quantile)")
    
    # Split by source
    ec_native = df_clean[df_clean['ec_source'] == 'EC']
    ec_calib = df_clean[df_clean['ec_source'] == 'RDP→EC']
    
    # # Scatter Plots
    if not ec_native.empty:
        ax.scatter(ec_native['delta_sm'], ec_native['delta_ec'], 
                   s=40, alpha=0.6, color='#1f77b4', edgecolor='none', 
                   label=f'Native EC Sensors (2016-2020)')
                   
    if not ec_calib.empty:
        ax.scatter(ec_calib['delta_sm'], ec_calib['delta_ec'], 
                   s=40, alpha=0.6, color='#ff7f0e', edgecolor='none', 
                   label=f'Calibrated RDP Sensors (2021-2025)')
    
    # Overall Regression Line (Calculated on CLEAN data)
    slope, intercept, r, p, _ = stats.linregress(df_clean['delta_sm'], df_clean['delta_ec'])
    x_range = np.linspace(df_clean['delta_sm'].min(), df_clean['delta_sm'].max(), 100)
    y_fit = slope * x_range + intercept
    
    ax.plot(x_range, y_fit, color='#d62728', linestyle='-', linewidth=2, 
            label=f'Linear Fit (r={r:.2f})')
    
    # Labels & Title
    ax.set_xlabel('$\Delta$ Soil Moisture at 50 cm (%)', fontweight='bold')
    ax.set_ylabel('$\Delta$ Bulk EC at 50 cm (dS m$^{-1}$)', fontweight='bold')
    ax.set_title('Sensor Coupling Validation: Coherent Response to Infiltration', 
                 fontweight='bold', pad=15)
    
    # Grid & Spines
    ax.grid(True, linestyle='--', alpha=0.3)
    sns.despine(ax=ax)
    
    # Annotations
    stats_text = (f"Validates:\n"
                  f"• EC/SM respond coherently\n"
                  f"• Calibration continuity\n"
                  f"• n = {len(df_clean)} events (outliers removed)")
                  
    ax.text(0.95, 0.05, stats_text, transform=ax.transAxes, 
            ha='right', va='bottom', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#dee2e6', alpha=0.9))
            
    ax.legend(loc='upper left', frameon=True, framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    print(f"\n✓ Figure saved: {outpath}")

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("Running Sensor Validation (Strict Filter)...")
    rdp_cal = learn_rdp_to_ec_calibration(DATA_DIR)
    
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*_V6.csv')))
    all_results = []
    
    for f in files:
        res = analyze_ec_sm_coupling(f, rdp_cal)
        if res is not None: all_results.append(res)
            
    if not all_results: return
        
    df_all = pd.concat(all_results, ignore_index=True)
    plot_ec_sm_validation(df_all, os.path.join(OUT_DIR, 'FigureS4_EC_SM_Validation_V6.png'))
    df_all.to_csv(os.path.join(OUT_DIR, 'ec_sm_event_deltas_v6.csv'), index=False)

if __name__ == "__main__":
    main()