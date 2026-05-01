#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figure 3: Precipitation-Recharge Dynamics (V6 - Pitfalls Fixed)

V6 ADAPTATIONS:
1. Uses V6 dataset (single SM_5cm column, no A/B)
2. TIME-BASED lookback/forward (not row-based) to handle gaps
3. Baseline at rain START (not END) to capture during-event rise
4. Dynamic threshold validation for V6 data distribution
5. Empty dataframe protection

LOGIC:
- Panel A: Rainfall magnitude vs percolation probability
- Panel B: Antecedent SURFACE moisture vs percolation (fixes saturation blindness)
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ================= CONFIGURATION =================
DATA_DIR = './V6'
OUT_DIR = './OUT'

# THRESHOLDS
MIN_EVENT_PRECIP = 0.5
EVENT_GAP_HOURS = 6
ANTECEDENT_WINDOW_HOURS = 24   # Look back 24 hours
RESPONSE_WINDOW_HOURS = 72     # Look forward 72 hours
RECHARGE_THRESH = 0.5          # 0.5% increase at 50cm

# SURFACE MOISTURE CLASSES (Will be validated against V6 data)
SM_DRY_5 = 15.0
SM_WET_5 = 20.0

def validate_thresholds(all_sm5_data):
    """
    FIX PITFALL #3: Validate thresholds against actual V6 data distribution.
    """
    q25, q75 = np.nanpercentile(all_sm5_data, [25, 75])
    print(f"\n=== V6 Surface Moisture Distribution ===")
    print(f"  25th percentile: {q25:.1f}%")
    print(f"  75th percentile: {q75:.1f}%")
    print(f"  Current thresholds: Dry<{SM_DRY_5}, Wet>{SM_WET_5}")
    
    if q25 > SM_DRY_5:
        print(f"  ⚠ WARNING: 'Dry' threshold ({SM_DRY_5}) is too low!")
        print(f"  → Only {(all_sm5_data < SM_DRY_5).sum()} points below threshold")
    if q75 < SM_WET_5:
        print(f"  ⚠ WARNING: 'Wet' threshold ({SM_WET_5}) is too high!")
        print(f"  → Only {(all_sm5_data > SM_WET_5).sum()} points above threshold")
    print()

def analyze_events(filepath):
    """
    Analyze rainfall-recharge events using V6 dataset.
    
    FIX PITFALL #1: Use TIME-BASED windows, not row counts
    FIX PITFALL #2: Baseline at rain START, not END
    """
    try:
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # V6: Clean column selection (no A/B hunting)
        if 'SM_5cm' not in df.columns or 'SM_50cm' not in df.columns:
            return None, None
            
        sm5 = pd.to_numeric(df['SM_5cm'], errors='coerce')
        sm50 = pd.to_numeric(df['SM_50cm'], errors='coerce')
        precip = pd.to_numeric(df['Precipitation'], errors='coerce').fillna(0)
        
        # FIX PITFALL #1: Ensure complete time index (handle gaps)
        df = df.set_index('timestamp')
        full_index = pd.date_range(df.index.min(), df.index.max(), freq='15min')
        df = df.reindex(full_index)
        
        sm5 = df['SM_5cm']
        sm50 = df['SM_50cm']
        precip = df['Precipitation'].fillna(0)
        
        # Identify rainfall events
        is_rain = precip > 0
        rain_times = df.index[is_rain]
        
        if len(rain_times) == 0:
            return None, sm5.dropna().values
        
        # Cluster rainfall into events (6-hour gap)
        gap_threshold = pd.Timedelta(hours=EVENT_GAP_HOURS)
        event_groups = np.split(rain_times, 
                               np.where(np.diff(rain_times) > gap_threshold)[0] + 1)
        
        results = []
        for grp in event_groups:
            if len(grp) == 0:
                continue
            
            event_start = grp[0]
            event_end = grp[-1]
            
            # Total rainfall during event
            total_mm = precip.loc[event_start:event_end].sum()
            
            if total_mm < MIN_EVENT_PRECIP:
                continue
            
            # FIX PITFALL #1: TIME-BASED antecedent window
            ant_start = event_start - pd.Timedelta(hours=ANTECEDENT_WINDOW_HOURS)
            ant_window = sm5.loc[ant_start:event_start]
            ant_sm5 = ant_window.mean()
            
            # FIX PITFALL #2: Baseline at START of rain (not END)
            # This captures the FULL event response, including during-rain rise
            base_val_50 = sm50.loc[event_start]
            
            # FIX PITFALL #1: TIME-BASED response window
            resp_end = event_end + pd.Timedelta(hours=RESPONSE_WINDOW_HOURS)
            resp_window = sm50.loc[event_end:resp_end]
            peak_val_50 = resp_window.max()
            
            increase = peak_val_50 - base_val_50
            success = (increase >= RECHARGE_THRESH)
            
            # Classify antecedent surface state
            if pd.isna(ant_sm5):
                ant_class = 'Unknown'
            elif ant_sm5 < SM_DRY_5:
                ant_class = 'Dry'
            elif ant_sm5 < SM_WET_5:
                ant_class = 'Medium'
            else:
                ant_class = 'Wet'
            
            if ant_class != 'Unknown':
                results.append({
                    'total_mm': total_mm,
                    'ant_sm5': ant_sm5,
                    'ant_class': ant_class,
                    'success': success,
                    'increase': increase
                })
        
        return pd.DataFrame(results), sm5.dropna().values
        
    except Exception as e:
        print(f"⚠ Skipping {os.path.basename(filepath)}: {e}")
        return None, None

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*_V6.csv')))
    
    if len(files) == 0:
        print(f"ERROR: No V6 files found in {DATA_DIR}")
        return
    
    print("="*70)
    print("ANALYZING V6 DATASET FOR FIGURE 3")
    print("="*70)
    
    all_events = []
    all_sm5_values = []
    
    for f in files:
        year = os.path.basename(f).split('_')[0]
        res, sm5_vals = analyze_events(f)
        
        if res is not None and len(res) > 0:
            all_events.append(res)
            print(f"  {year}: {len(res)} events")
        else:
            print(f"  {year}: No events")
            
        if sm5_vals is not None:
            all_sm5_values.extend(sm5_vals)
    
    # FIX PITFALL #4: Check for empty results
    if len(all_events) == 0:
        print("\n✗ No events found across all years!")
        return
    
    df = pd.concat(all_events, ignore_index=True)
    
    # FIX PITFALL #4: Additional empty check
    if df.empty:
        print("\n✗ Concatenated dataframe is empty!")
        return
    
    print(f"\nTotal Events: {len(df)}")
    print(f"  Percolation events: {df['success'].sum()} ({df['success'].mean()*100:.1f}%)")
    
    # FIX PITFALL #3: Validate thresholds
    validate_thresholds(np.array(all_sm5_values))
    
    # ==================== FIGURE GENERATION ====================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    
    # ========== PANEL A: Event Size ==========
    bins = [0, 5, 10, 25, 50, 999]
    labels = ['0-5', '5-10', '10-25', '25-50', '>50']
    df['bin'] = pd.cut(df['total_mm'], bins=bins, labels=labels)
    
    stats_size = df.groupby('bin', observed=True)['success'].agg(['mean', 'count'])
    stats_size['pct'] = stats_size['mean'] * 100
    
    colors_size = ['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850']
    bars1 = ax1.bar(labels, stats_size['pct'], color=colors_size, 
                    edgecolor='k', linewidth=1.5, alpha=0.9)
    
    # Add sample size labels
    for bar, count in zip(bars1, stats_size['count']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()+2, 
                f'n={count}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax1.set_ylabel('Percolation Probability (%)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Cumulative Event Rainfall (mm)', fontsize=12, fontweight='bold')
    ax1.set_title('(a) Rainfall Magnitude Control', loc='left', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, 110)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.axhline(y=50, color='gray', linestyle=':', alpha=0.5, linewidth=1)
    
    # ========== PANEL B: Antecedent Surface Moisture ==========
    order = ['Dry', 'Medium', 'Wet']
    stats_ant = df.groupby('ant_class', observed=True)['success'].agg(['mean', 'count'])
    stats_ant['pct'] = stats_ant['mean'] * 100
    
    # Reindex to ensure all categories present (even if empty)
    stats_ant = stats_ant.reindex(order, fill_value=0)
    
    # Color logic: Dry (Orange) -> Wet (Blue)
    colors_ant = ['#fdae61', '#fee08b', '#4575b4']
    bars2 = ax2.bar(order, stats_ant['pct'], color=colors_ant, 
                    edgecolor='k', linewidth=1.5, alpha=0.9)
    
    # Add sample size labels
    for bar, count in zip(bars2, stats_ant['count']):
        if count > 0:  # Only show label if category has data
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height()+2, 
                    f'n={int(count)}', ha='center', va='bottom', 
                    fontsize=10, fontweight='bold')
    
    # Add difference annotation (only if both Dry and Wet have data)
    if stats_ant.loc['Dry', 'count'] > 0 and stats_ant.loc['Wet', 'count'] > 0:
        diff = stats_ant.loc['Wet', 'pct'] - stats_ant.loc['Dry', 'pct']
        direction = "increases" if diff > 0 else "decreases"
        ax2.text(0.5, 0.88, f"Wet surface {direction}\nresponse by {abs(diff):.1f}%", 
                transform=ax2.transAxes, ha='center', fontsize=10,
                bbox=dict(facecolor='white', alpha=0.9, boxstyle='round', 
                         edgecolor='black', linewidth=1.5))
    
    ax2.set_ylabel('Percolation Probability (%)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Antecedent Surface Moisture (5 cm)', fontsize=12, fontweight='bold')
    ax2.set_title('(b) Surface State Control', loc='left', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 110)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5, linewidth=1)
    
    # Legend for moisture classes
    ax2.text(0.05, 0.95, f"Dry: <{SM_DRY_5}%\nWet: >{SM_WET_5}%", 
            transform=ax2.transAxes, fontsize=9, va='top',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    
    # Save figure
    output_path = os.path.join(OUT_DIR, 'Figure3_V6.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Figure saved: {output_path}")
    print("="*70)

if __name__ == "__main__":
    main()
