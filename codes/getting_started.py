#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Getting Started: Berambadi Soil Hydrothermal Dataset (2016-2025)
=================================================================

This script loads one year of data, prints a quick summary, and plots
the four core variables (precipitation, soil moisture, temperature, and
electrical conductivity / relative dielectric permittivity) at 5 cm and
50 cm depths.

Run this first to verify your setup and see what the data looks like.

Dataset: 15-minute soil moisture, temperature, EC/RDP, and precipitation
         from the Berambadi catchment, Karnataka, India.

Usage:
    1. Place this script in the same folder as the annual CSV files
       (e.g., 2017_V1.csv) OR edit DATA_DIR below to point to them.
    2. Run: python getting_started.py
    3. Change YEAR below to load a different year (2016 through 2025).

Requirements: pandas, matplotlib
    pip install pandas matplotlib

Citation: Rao, S. et al. (2026). A decade of high-frequency soil
          hydrothermal observations in a semi-arid monsoon catchment
          (2016-2025) [Data set]. Zenodo.
          https://doi.org/10.5281/zenodo.18409640
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# ============================================================================
# CONFIGURATION (edit these if needed)
# ============================================================================

# Folder containing the annual CSV files. "." means the current folder.
DATA_DIR = "."

# Which year to load. Pick any year from 2016 through 2025.
YEAR = 2017


# ============================================================================
# LOAD DATA
# ============================================================================

filename = f"{YEAR}_V1.csv"
filepath = os.path.join(DATA_DIR, filename)

if not os.path.isfile(filepath):
    raise FileNotFoundError(
        f"Could not find {filepath}. "
        f"Edit DATA_DIR at the top of this script to point to the folder "
        f"containing the annual CSV files."
    )

print(f"Loading {filename} ...")
df = pd.read_csv(filepath)
df["timestamp"] = pd.to_datetime(df["timestamp"])

print(f"  Loaded {len(df):,} rows ({df['timestamp'].min()} to {df['timestamp'].max()})")
print(f"  Columns: {list(df.columns)}")
print()


# ============================================================================
# QUICK SUMMARY
# ============================================================================

print("Data completeness (% non-missing):")
for col in df.columns:
    if col == "timestamp":
        continue
    pct = df[col].notna().mean() * 100
    print(f"  {col:<20s} {pct:6.1f}%")
print()

# Note on EC vs RDP: the dataset reports electrical conductivity (EC) for
# 2016-2020 and relative dielectric permittivity (RDP) for 2021-2025.
# 2021 contains both during the sensor transition. Pick whichever is
# available for the year you loaded.
if "EC_5cm" in df.columns and df["EC_5cm"].notna().any():
    cond_col_5cm, cond_col_50cm = "EC_5cm", "EC_50cm"
    cond_label = "Electrical conductivity (dS m$^{-1}$)"
else:
    cond_col_5cm, cond_col_50cm = "RDP_5cm", "RDP_50cm"
    cond_label = "Relative dielectric permittivity (-)"


# ============================================================================
# PLOT
# ============================================================================

fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)

# (a) Precipitation
axes[0].vlines(df["timestamp"], 0, df["Precipitation"], color="#08519c", lw=1)
axes[0].set_ylabel("Rainfall\n(mm / 15 min)", fontweight="bold")
axes[0].set_title(f"Berambadi soil hydrothermal observations, {YEAR}",
                  loc="left", fontweight="bold")

# (b) Soil moisture
axes[1].plot(df["timestamp"], df["SM_5cm"],  color="#d95f02", lw=1, label="5 cm")
axes[1].plot(df["timestamp"], df["SM_50cm"], color="#1b9e77", lw=1, label="50 cm")
axes[1].set_ylabel("Soil moisture\n(% VWC)", fontweight="bold")
axes[1].legend(loc="upper right", frameon=False)

# (c) Soil temperature
axes[2].plot(df["timestamp"], df["Temp_5cm"],  color="#d95f02", lw=1, label="5 cm")
axes[2].plot(df["timestamp"], df["Temp_50cm"], color="#1b9e77", lw=1, label="50 cm")
axes[2].set_ylabel("Soil temperature\n($^{\\circ}$C)", fontweight="bold")
axes[2].legend(loc="upper right", frameon=False)

# (d) Electrical conductivity OR relative dielectric permittivity
axes[3].plot(df["timestamp"], df[cond_col_5cm],  color="#d95f02", lw=1, label="5 cm")
axes[3].plot(df["timestamp"], df[cond_col_50cm], color="#1b9e77", lw=1, label="50 cm")
axes[3].set_ylabel(cond_label, fontweight="bold")
axes[3].legend(loc="upper right", frameon=False)
axes[3].set_xlabel("Date (timestamps in Indian Standard Time, UTC+05:30)",
                   fontweight="bold")
axes[3].xaxis.set_major_formatter(mdates.DateFormatter("%b"))

for ax in axes:
    ax.grid(True, linestyle=":", alpha=0.4)

plt.tight_layout()

output_path = f"getting_started_{YEAR}.png"
plt.savefig(output_path, dpi=150)
print(f"Plot saved to: {output_path}")
plt.show()
