#!/usr/bin/env python3
"""
BULLETPROOF Sensor Selection and Data Curation (V4 → V6)
=========================================================

Dataset: Soil Moisture & Climate (2016-2025)
Location: Berambadi/Bechanahalli, India
Interval: 15-minute measurements

Implements all safety checks to prevent selecting broken sensors:
1. Anti-Noise Filter (removes physically impossible values)
2. Stuck/Flatline Detection (rejects sensors with zero variation)
3. Jan-Mar Check (if missing → default to A)
4. Depth Inversion Warning (compares winner vs 50cm)
5. Least Inverted Logic (picks higher variance even if both bad)

Dataset-Specific Handling:
- 2016-2020: EC-based sensors, Sensor A & B at 5cm
- 2021: Transition year (EC → RDP, some gaps)
- 2022-2025: RDP-based sensors, only Sensor A at 5cm, 15cm depth added
- 2020: Only Oct-Dec data (no Jan-Mar) → defaults to A
- String "NaN", "E36", "E6" replaced with np.nan

Author: Sathya (IISc)
Date: 2026-01-26
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============= CONFIGURATION =============

DATA_DIR = '/home/sathya-iisc/Documents/TIMESERIES/Aarya/V4'
OUTPUT_DIR = '/home/sathya-iisc/Documents/TIMESERIES/Aarya/V6'

# Years available in dataset (per README: 2016-2025)
YEARS_TO_PROCESS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

# Physical limits (Anti-Noise Rule)
TEMP_MIN = 0.0      # °C (minimum realistic soil temperature)
TEMP_MAX = 60.0     # °C (maximum realistic soil temperature)

# Stuck sensor threshold (Flatline Rule)
STUCK_THRESHOLD = 0.05  # If std < 0.05, sensor is stuck/dead

# Variance comparison threshold
VARIANCE_RATIO = 0.5    # If Var(A) < 0.5*Var(B), A is significantly worse

# Completeness threshold
COMPLETENESS_THRESHOLD = 0.20  # 20% difference in data count

# ============= UTILITY FUNCTIONS =============

def apply_physical_limits(series, var_name='Temperature'):
    """
    Anti-Noise Rule: Remove physically impossible values.
    
    Converts values outside realistic range to NaN.
    This prevents broken sensors with electrical noise from being selected.
    """
    series_clean = series.copy()
    
    # Count outliers before filtering
    n_too_low = (series < TEMP_MIN).sum()
    n_too_high = (series > TEMP_MAX).sum()
    n_outliers = n_too_low + n_too_high
    
    # Apply limits
    series_clean.loc[series_clean < TEMP_MIN] = np.nan
    series_clean.loc[series_clean > TEMP_MAX] = np.nan
    
    if n_outliers > 0:
        print(f"    Removed {n_outliers} outliers ({n_too_low} < {TEMP_MIN}°C, {n_too_high} > {TEMP_MAX}°C)")
    
    return series_clean


def is_stuck(series, var_name='Sensor'):
    """
    Flatline Rule: Detect if sensor is stuck at a single value.
    
    A sensor can fail by outputting the same number repeatedly.
    This counts as "complete data" but is useless.
    """
    valid_data = series.dropna()
    
    if len(valid_data) < 10:
        return True, "Insufficient data"
    
    std = valid_data.std()
    
    if std < STUCK_THRESHOLD:
        return True, f"Flatline detected (std={std:.4f} < {STUCK_THRESHOLD})"
    
    return False, f"OK (std={std:.2f})"


# ============= SENSOR SELECTION RULES =============

def rule1_physical_check(df, check_months=[1, 2, 3]):
    """
    Rule 1: Jan-Mar Physical Reality Check
    
    If Jan-Mar data is insufficient (<100 points):
        → Skip variance check, return PASS (will default to A via tie-breaker)
    
    This handles years like 2020 (only Oct-Dec) cleanly.
    
    Returns: ('A', 'B', or 'PASS', reason, metrics_dict)
    """
    print(f"\n{'─'*70}")
    print(f"RULE 1: PHYSICAL REALITY CHECK (Variance Analysis)")
    print(f"{'─'*70}")
    
    # Try Jan-Mar window (dry season)
    df_window = df[df['timestamp'].dt.month.isin(check_months)].copy()
    window_name = "Jan-Mar"  # Add this line
    
    if len(df_window) < 100:
        print(f"  ⚠ Insufficient Jan-Mar data ({len(df_window)} points)")
        print(f"  → Skipping variance check, will default to Sensor A")
        return 'PASS', f'No Jan-Mar data → default to A', {}
    
    print(f"  Using {window_name} window: {len(df_window)} points")
    
    # Apply physical limits (Anti-Noise Rule)
    print(f"\n  Step 1: Apply physical limits ({TEMP_MIN}°C to {TEMP_MAX}°C)")
    temp_A_clean = apply_physical_limits(df_window['Temp_5cm_A'].copy())
    temp_B_clean = apply_physical_limits(df_window['Temp_5cm_B'].copy())
    
    # Check for stuck sensors (Flatline Rule)
    print(f"\n  Step 2: Check for stuck/flatlined sensors")
    stuck_A, reason_A = is_stuck(temp_A_clean, 'Sensor A')
    stuck_B, reason_B = is_stuck(temp_B_clean, 'Sensor B')
    
    print(f"    Sensor A: {reason_A}")
    print(f"    Sensor B: {reason_B}")
    
    # If both stuck, manual review needed
    if stuck_A and stuck_B:
        return 'MANUAL', 'Both sensors are stuck/flatlined', {}
    
    # If only one stuck, choose the other
    if stuck_A:
        return 'B', f'Sensor A stuck ({reason_A}), Sensor B OK', {}
    if stuck_B:
        return 'A', f'Sensor B stuck ({reason_B}), Sensor A OK', {}
    
    # Calculate variance (Least Inverted Logic)
    print(f"\n  Step 3: Calculate variance (higher is better for surface)")
    var_A = temp_A_clean.var()
    var_B = temp_B_clean.var()
    
    print(f"    Sensor A variance: {var_A:.2f}")
    print(f"    Sensor B variance: {var_B:.2f}")
    
    # Check for NaN
    if pd.isna(var_A) and pd.isna(var_B):
        return 'MANUAL', 'Both sensors have no valid data', {}
    elif pd.isna(var_A):
        return 'B', f'Sensor A has no valid data', {'var_B': var_B}
    elif pd.isna(var_B):
        return 'A', f'Sensor B has no valid data', {'var_A': var_A}
    
    metrics = {'var_A': var_A, 'var_B': var_B}
    
    # Least Inverted Logic: Select sensor with HIGHER variance
    # (Even if both are damped, pick the "least bad" one)
    if var_B > var_A * (1 + VARIANCE_RATIO):
        ratio = var_B / var_A
        return 'B', f'Sensor B has {ratio:.1f}x higher variance → better for surface', metrics
    elif var_A > var_B * (1 + VARIANCE_RATIO):
        ratio = var_A / var_B
        return 'A', f'Sensor A has {ratio:.1f}x higher variance → better for surface', metrics
    else:
        # Variances similar, proceed to next rule
        return 'PASS', f'Similar variance (A={var_A:.2f}, B={var_B:.2f})', metrics


def rule2_completeness_check(df):
    """
    Rule 2: Data Completeness Check
    
    BUT: Only counts "real" data (not stuck sensors)
    """
    print(f"\n{'─'*70}")
    print(f"RULE 2: DATA COMPLETENESS CHECK")
    print(f"{'─'*70}")
    
    # Apply physical limits first
    temp_A_clean = apply_physical_limits(df['Temp_5cm_A'].copy())
    temp_B_clean = apply_physical_limits(df['Temp_5cm_B'].copy())
    
    # Check if stuck (for full year)
    stuck_A, _ = is_stuck(temp_A_clean, 'Sensor A')
    stuck_B, _ = is_stuck(temp_B_clean, 'Sensor B')
    
    # Count valid data (treat stuck sensors as having 0 valid data)
    count_A = 0 if stuck_A else temp_A_clean.notna().sum()
    count_B = 0 if stuck_B else temp_B_clean.notna().sum()
    
    total_rows = len(df)
    
    print(f"  Sensor A: {count_A:,}/{total_rows:,} valid points")
    print(f"  Sensor B: {count_B:,}/{total_rows:,} valid points")
    
    if count_A == 0 and count_B == 0:
        return 'MANUAL', 'Both sensors have no valid data (or stuck)', {}
    elif count_A == 0:
        return 'B', f'Sensor A has no valid data', {'count_B': count_B}
    elif count_B == 0:
        return 'A', f'Sensor B has no valid data', {'count_A': count_A}
    
    # Check for significant difference
    if count_B > count_A * (1 + COMPLETENESS_THRESHOLD):
        pct_diff = (count_B - count_A) / count_A * 100
        return 'B', f'Sensor B has {pct_diff:.0f}% more data', {'count_A': count_A, 'count_B': count_B}
    elif count_A > count_B * (1 + COMPLETENESS_THRESHOLD):
        pct_diff = (count_A - count_B) / count_B * 100
        return 'A', f'Sensor A has {pct_diff:.0f}% more data', {'count_A': count_A, 'count_B': count_B}
    
    return 'PASS', f'Similar completeness', {'count_A': count_A, 'count_B': count_B}


def rule3_tiebreaker():
    """
    Rule 3: Tie-Breaker (Default to A)
    """
    print(f"\n{'─'*70}")
    print(f"RULE 3: TIE-BREAKER")
    print(f"{'─'*70}")
    print(f"  Both sensors passed all checks")
    print(f"  → Defaulting to Sensor A (consistency across years)")
    
    return 'A', 'Tie-breaker: both sensors good', {}


def check_depth_inversion(df, selected_sensor, metrics):
    """
    Final Safety Check: Depth Inversion Warning
    
    Compares selected 5cm sensor variance against 50cm variance.
    Surface must be MORE variable than deep soil.
    """
    print(f"\n{'─'*70}")
    print(f"FINAL CHECK: DEPTH INVERSION WARNING")
    print(f"{'─'*70}")
    
    # Get 50cm variance
    if 'Temp_50cm' not in df.columns:
        print(f"  ⚠ No 50cm data available for comparison")
        return 'UNKNOWN'
    
    df_janfeb = df[df['timestamp'].dt.month.isin([1, 2, 3])].copy()
    temp_50_clean = apply_physical_limits(df_janfeb['Temp_50cm'].copy())
    var_50 = temp_50_clean.var()
    
    if pd.isna(var_50):
        print(f"  ⚠ 50cm sensor has no valid data")
        return 'UNKNOWN'
    
    # Get selected 5cm variance
    var_5cm = metrics.get('var_A') if selected_sensor == 'A' else metrics.get('var_B')
    
    if var_5cm is None:
        print(f"  ⚠ Could not retrieve 5cm variance from metrics")
        return 'UNKNOWN'
    
    print(f"  Selected 5cm sensor variance: {var_5cm:.2f}")
    print(f"  50cm sensor variance:         {var_50:.2f}")
    print(f"  Ratio (5cm/50cm):             {var_5cm/var_50:.2f}")
    
    # Physical expectation: Surface should be MORE variable
    if var_5cm < var_50:
        print(f"\n  ⚠⚠⚠ WARNING: DEPTH INVERSION DETECTED ⚠⚠⚠")
        print(f"  Surface (5cm) has LOWER variance than deep (50cm)")
        print(f"  This suggests physical burial or sensor malfunction")
        print(f"  → Keeping data as-is (NO SWAPPING), but flagging year")
        return 'INVERTED'
    else:
        print(f"\n  ✓ Physical depth relationship is correct")
        print(f"  Surface is more variable than deep soil")
        return 'OK'


def select_sensor(df, year):
    """
    Master selection logic with all safety checks.
    
    Handles cases where Sensor B may not exist (e.g., 2022+)
    """
    print(f"\n{'='*70}")
    print(f"SENSOR SELECTION FOR {year}")
    print(f"{'='*70}")
    
    # Check if both sensors exist
    has_sensor_A = 'Temp_5cm_A' in df.columns
    has_sensor_B = 'Temp_5cm_B' in df.columns
    
    print(f"  Sensor A present: {has_sensor_A}")
    print(f"  Sensor B present: {has_sensor_B}")
    
    # If only one sensor exists, use it
    if has_sensor_A and not has_sensor_B:
        print(f"\n  → Only Sensor A available, using A by default")
        report = {
            'year': year,
            'final_choice': 'A',
            'decision_basis': 'Only Sensor A exists',
            'depth_check': 'SKIP',
            'metrics': {}
        }
        return 'A', report
    
    if has_sensor_B and not has_sensor_A:
        print(f"\n  → Only Sensor B available, using B by default")
        report = {
            'year': year,
            'final_choice': 'B',
            'decision_basis': 'Only Sensor B exists',
            'depth_check': 'SKIP',
            'metrics': {}
        }
        return 'B', report
    
    if not has_sensor_A and not has_sensor_B:
        print(f"\n  ✗ No 5cm temperature sensors found!")
        report = {
            'year': year,
            'final_choice': 'MANUAL',
            'decision_basis': 'No sensors available',
            'depth_check': 'N/A',
            'metrics': {}
        }
        return 'MANUAL', report
    
    # Both sensors exist - proceed with normal selection
    report = {
        'year': year,
        'rule1_result': None,
        'rule1_reason': None,
        'rule2_result': None,
        'rule2_reason': None,
        'final_choice': None,
        'decision_basis': None,
        'depth_check': None,
        'metrics': {}
    }
    
    # Rule 1: Physical Check
    choice1, reason1, metrics1 = rule1_physical_check(df)
    report['rule1_result'] = choice1
    report['rule1_reason'] = reason1
    report['metrics'].update(metrics1)
    
    if choice1 == 'MANUAL':
        print(f"\n{'='*70}")
        print(f"⚠ MANUAL REVIEW REQUIRED")
        print(f"{'='*70}")
        report['final_choice'] = 'MANUAL'
        report['decision_basis'] = reason1
        return 'MANUAL', report
    
    if choice1 != 'PASS':
        report['final_choice'] = choice1
        report['decision_basis'] = f'Rule 1: {reason1}'
        
        # Check depth inversion
        depth_status = check_depth_inversion(df, choice1, report['metrics'])
        report['depth_check'] = depth_status
        
        print(f"\n{'='*70}")
        print(f"✓ DECISION: Use Sensor {choice1}")
        print(f"  Basis: Rule 1 (Physical Reality Check)")
        print(f"{'='*70}")
        return choice1, report
    
    # Rule 2: Completeness Check
    choice2, reason2, metrics2 = rule2_completeness_check(df)
    report['rule2_result'] = choice2
    report['rule2_reason'] = reason2
    report['metrics'].update(metrics2)
    
    if choice2 == 'MANUAL':
        print(f"\n{'='*70}")
        print(f"⚠ MANUAL REVIEW REQUIRED")
        print(f"{'='*70}")
        report['final_choice'] = 'MANUAL'
        report['decision_basis'] = reason2
        return 'MANUAL', report
    
    if choice2 != 'PASS':
        report['final_choice'] = choice2
        report['decision_basis'] = f'Rule 2: {reason2}'
        
        # Check depth inversion
        depth_status = check_depth_inversion(df, choice2, report['metrics'])
        report['depth_check'] = depth_status
        
        print(f"\n{'='*70}")
        print(f"✓ DECISION: Use Sensor {choice2}")
        print(f"  Basis: Rule 2 (Data Completeness)")
        print(f"{'='*70}")
        return choice2, report
    
    # Rule 3: Tie-Breaker
    choice3, reason3, metrics3 = rule3_tiebreaker()
    report['final_choice'] = choice3
    report['decision_basis'] = reason3
    report['metrics'].update(metrics3)
    
    # Check depth inversion
    depth_status = check_depth_inversion(df, choice3, report['metrics'])
    report['depth_check'] = depth_status
    
    print(f"\n{'='*70}")
    print(f"✓ DECISION: Use Sensor {choice3}")
    print(f"  Basis: Rule 3 (Tie-Breaker)")
    print(f"{'='*70}")
    return choice3, report


# ============= DATA PROCESSING =============

def process_year(year):
    """Process a single year."""
    input_file = Path(DATA_DIR) / f"{year}.csv"
    output_file = Path(OUTPUT_DIR) / f"{year}_V6.csv"  # Add _V6 suffix
    
    print(f"\n{'='*70}")
    print(f"PROCESSING YEAR {year}")
    print(f"{'='*70}")
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    
    if not input_file.exists():
        print(f"✗ File not found")
        return None
    
    try:
        df = pd.read_csv(input_file)
        print(f"✓ Loaded {len(df):,} rows")
        
        # CRITICAL: Replace string "NaN" with actual NaN (per README)
        df = df.replace("NaN", np.nan)
        df = df.replace("E36", np.nan)  # Error codes from logger
        df = df.replace("E6", np.nan)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Select sensor
    selected_sensor, report = select_sensor(df, year)
    
    if selected_sensor == 'MANUAL':
        print(f"\n⚠ Skipping file creation - manual review required")
        return report
    
    # Create output
    print(f"\n{'='*70}")
    print(f"CREATING UNIFIED 5cm COLUMNS (Coupling Rule)")
    print(f"{'='*70}")
    
    df_out = df.copy()
    
    # Detect available conductivity columns (both EC and RDP may exist in 2021)
    has_EC_A = 'EC_5cm_A' in df.columns
    has_EC_B = 'EC_5cm_B' in df.columns
    has_RDP_A = 'RDP_5cm_A' in df.columns
    has_RDP_B = 'RDP_5cm_B' in df.columns
    
    print(f"  Available conductivity columns:")
    print(f"    EC_5cm_A: {has_EC_A}, EC_5cm_B: {has_EC_B}")
    print(f"    RDP_5cm_A: {has_RDP_A}, RDP_5cm_B: {has_RDP_B}")
    
    if selected_sensor == 'A':
        # Temperature
        if 'Temp_5cm_A' in df.columns:
            df_out['Temp_5cm'] = df['Temp_5cm_A']
            print(f"  Temp_5cm ← Temp_5cm_A")
        
        # Soil Moisture
        if 'SM_5cm_A' in df.columns:
            df_out['SM_5cm'] = df['SM_5cm_A']
            print(f"  SM_5cm   ← SM_5cm_A")
        
        # EC (process if exists)
        if has_EC_A:
            df_out['EC_5cm'] = df['EC_5cm_A']
            print(f"  EC_5cm   ← EC_5cm_A")
        
        # RDP (process if exists - independent of EC)
        if has_RDP_A:
            df_out['RDP_5cm'] = df['RDP_5cm_A']
            print(f"  RDP_5cm  ← RDP_5cm_A")
    
    else:  # Sensor B
        # Temperature
        if 'Temp_5cm_B' in df.columns:
            df_out['Temp_5cm'] = df['Temp_5cm_B']
            print(f"  Temp_5cm ← Temp_5cm_B")
        
        # Soil Moisture
        if 'SM_5cm_B' in df.columns:
            df_out['SM_5cm'] = df['SM_5cm_B']
            print(f"  SM_5cm   ← SM_5cm_B")
        
        # EC (process if exists)
        if has_EC_B:
            df_out['EC_5cm'] = df['EC_5cm_B']
            print(f"  EC_5cm   ← EC_5cm_B")
        
        # RDP (process if exists - independent of EC)
        if has_RDP_B:
            df_out['RDP_5cm'] = df['RDP_5cm_B']
            print(f"  RDP_5cm  ← RDP_5cm_B")
    
    # Drop _A and _B columns
    cols_to_drop = [col for col in df_out.columns 
                    if ('_5cm_A' in col or '_5cm_B' in col) and 
                       col not in ['SM_5cm', 'Temp_5cm', 'EC_5cm', 'RDP_5cm']]
    df_out = df_out.drop(columns=cols_to_drop)
    
    print(f"\n  Dropped {len(cols_to_drop)} redundant columns")
    
    # Reorder columns (flexible for EC and/or RDP presence)
    priority_cols = ['timestamp', 'Temp_5cm', 'SM_5cm']
    
    # Add EC and RDP if they exist
    if 'EC_5cm' in df_out.columns:
        priority_cols.append('EC_5cm')
    if 'RDP_5cm' in df_out.columns:
        priority_cols.append('RDP_5cm')
    
    # Add other depth measurements
    priority_cols.extend(['Temp_15cm', 'SM_15cm', 'EC_15cm', 'RDP_15cm',
                         'Temp_50cm', 'SM_50cm', 'EC_50cm', 'RDP_50cm', 
                         'Precipitation'])
    
    other_cols = [col for col in df_out.columns if col not in priority_cols]
    ordered_cols = [col for col in priority_cols if col in df_out.columns] + other_cols
    df_out = df_out[ordered_cols]
    
    # Save
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_file, index=False)
    
    print(f"\n✓ Saved: {output_file}")
    print(f"  Rows: {len(df_out):,}")
    
    return report


# ============= MAIN =============

def main():
    print("\n" + "="*70)
    print("BULLETPROOF SENSOR SELECTION AND DATA CURATION")
    print("="*70)
    print(f"Input:  {DATA_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Years:  {YEARS_TO_PROCESS}")
    print("="*70)
    
    reports = []
    for year in YEARS_TO_PROCESS:
        report = process_year(year)
        if report:
            reports.append(report)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    
    if reports:
        print(f"\n{'Year':<6} {'Sensor':<8} {'Depth':<10} {'Decision Basis':<45}")
        print("-" * 70)
        
        for r in reports:
            depth_str = r.get('depth_check', 'N/A')
            choice_str = r['final_choice'] if r['final_choice'] != 'MANUAL' else 'MANUAL'
            basis_str = r['decision_basis'][:45]
            
            # Highlight problems
            if r['final_choice'] == 'MANUAL':
                print(f"{r['year']:<6} {'⚠MANUAL':<8} {'-':<10} {basis_str:<45}")
            elif depth_str == 'INVERTED':
                print(f"{r['year']:<6} {choice_str:<8} {'⚠INVERT':<10} {basis_str:<45}")
            else:
                print(f"{r['year']:<6} {choice_str:<8} {'✓OK':<10} {basis_str:<45}")
        
        # Counts
        count_A = sum(1 for r in reports if r['final_choice'] == 'A')
        count_B = sum(1 for r in reports if r['final_choice'] == 'B')
        count_manual = sum(1 for r in reports if r['final_choice'] == 'MANUAL')
        count_inverted = sum(1 for r in reports if r.get('depth_check') == 'INVERTED')
        
        print("\n" + "-" * 70)
        print(f"Sensor A selected:     {count_A} year(s)")
        print(f"Sensor B selected:     {count_B} year(s)")
        print(f"Manual review needed:  {count_manual} year(s)")
        print(f"Depth inversion found: {count_inverted} year(s)")
    
    print("\n" + "="*70)
    print("CURATION COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()