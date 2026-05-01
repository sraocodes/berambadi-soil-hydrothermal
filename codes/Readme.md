# Soil Moisture & Climate Dataset (2016–2025)
**Version 6 (V6) - Curated & Quality Controlled**

## Overview
This dataset provides **15-minute interval environmental measurements** collected between **January 2016 and June 2025** at the Berambadi/Bechanahalli field station in southern India.

It contains:
- Soil moisture (SM)
- Electrical conductivity (EC) / Relative dielectric permittivity (RDP)
- Soil temperature (Temp) at multiple depths (5 cm, 15 cm, 50 cm)
- Precipitation

The dataset is distributed as **yearly CSV files** (`2016_V6.csv`, `2017_V6.csv`, …, `2025_V6.csv`).

---

## Data Curation Notes

**Surface (5 cm) Sensor Selection:**
- The original raw data contained redundant sensors (A and B) at 5 cm depth for quality assurance.
- A **physics-based selection algorithm** was applied to each year:
  1. **Anti-noise filter**: Removed physically impossible values (T < 0°C or T > 60°C)
  2. **Flatline detection**: Rejected sensors stuck at constant values
  3. **Variance check**: Selected sensor with realistic diurnal variation (Jan–Mar dry season)
  4. **Completeness check**: Preferred sensor with fewer data gaps
  5. **Depth consistency**: Verified surface shows higher variance than deep soil
- The 5 cm columns in this dataset represent the **best unified sensor** for each year.
- No sensor swapping was performed; depth labels are preserved as recorded.

**Result:** A single, high-quality time series for surface measurements.

---

## Variables & Units

| Column        | Description                                           | Unit                     | Notes |
|---------------|-------------------------------------------------------|--------------------------|-------|
| timestamp     | Date & time of measurement (local)                    | YYYY-MM-DD HH:MM:SS      | 15 min intervals |
| Temp_5cm      | Soil temperature at 5 cm depth                        | °C                       | Unified best sensor |
| SM_5cm        | Soil moisture at 5 cm depth                           | % (vol. water content)   | Unified best sensor |
| EC_5cm        | Electrical conductivity at 5 cm depth                 | dS/m (deciSiemens/m)     | Available 2016–2021 |
| RDP_5cm       | Relative dielectric permittivity at 5 cm              | dimensionless            | Available 2021–2025 |
| Temp_15cm     | Soil temperature at 15 cm depth                       | °C                       | Available 2021–2025 |
| SM_15cm       | Soil moisture at 15 cm depth                          | %                        | Available 2021–2025 |
| EC_15cm       | Electrical conductivity at 15 cm depth                | dS/m                     | Available 2021 only |
| RDP_15cm      | Relative dielectric permittivity at 15 cm depth       | dimensionless            | Available 2021–2025 |
| Temp_50cm     | Soil temperature at 50 cm depth                       | °C                       | Available 2016–2025 |
| SM_50cm       | Soil moisture at 50 cm depth                          | %                        | Available 2016–2025 |
| EC_50cm       | Electrical conductivity at 50 cm depth                | dS/m                     | Available 2016–2021 |
| RDP_50cm      | Relative dielectric permittivity at 50 cm depth       | dimensionless            | Available 2021–2025 |
| Precipitation | Rainfall                                              | mm per 15 min            | Available 2016–2025 |

---

## Yearly Data Summary

| Year | Rows   | Coverage   | Columns Present | Notes |
|------|--------|------------|-----------------|-------|
| 2016 | 35,137 | Jan–Dec | SM, EC, Temp, Precipitation | Full year |
| 2017 | 35,027 | Jan–Dec | SM, EC, Temp, Precipitation | Full year |
| 2018 | 33,309 | Jan–Dec | SM, EC, Temp, Precipitation | Full year |
| 2019 | 22,620 | Jan–Dec | SM, EC, Temp, Precipitation | Full year |
| 2020 | 7,733 | Oct–Dec | SM, EC, Temp, Precipitation | Only 3 months |
| 2021 | 32,392 | Jan–Dec | SM, EC, Temp, Precipitation | Full year |
| 2022 | 33,064 | Jan–Dec | SM, RDP, Temp, Precipitation | Full year |
| 2023 | 34,480 | Jan–Dec | SM, RDP, Temp, Precipitation | Full year |
| 2024 | 35,080 | Jan–Dec | SM, RDP, Temp, Precipitation | Full year |
| 2025 | 17,316 | Jan–Jun | SM, RDP, Temp, Precipitation | Partial year |

---

## Data Completeness (% Non-Missing Values)

| Year | SM_5cm | EC_5cm | RDP_5cm | Temp_5cm | SM_15cm | EC_15cm | RDP_15cm | Temp_15cm | SM_50cm | EC_50cm | RDP_50cm | Temp_50cm | Precipitation |
|------|------|------|------|------|------|------|------|------|------|------|------|------|------|
| 2016 | 100.0 | 100.0 | — | 100.0 | — | — | — | — | 100.0 | 100.0 | — | 100.0 | 100.0 |
| 2017 | 100.0 | 100.0 | — | 100.0 | — | — | — | — | 100.0 | 100.0 | — | 100.0 | 100.0 |
| 2018 | 76.1 | 76.1 | — | 76.1 | — | — | — | — | 99.8 | 99.8 | — | 99.8 | 100.0 |
| 2019 | 99.6 | 99.6 | — | 99.6 | — | — | — | — | 98.2 | 78.6 | — | 78.6 | 100.0 |
| 2020 | 100.0 | 100.0 | — | 100.0 | — | — | — | — | 100.0 | 100.0 | — | 100.0 | 100.0 |
| 2021 | 32.9 | 32.3 | — | 54.8 | 44.9 | — | 44.9 | 44.9 | 100.0 | 50.9 | 44.9 | 100.0 | 100.0 |
| 2022 | 100.0 | — | 100.0 | 100.0 | 100.0 | — | 100.0 | 100.0 | 100.0 | — | 100.0 | 100.0 | 100.0 |
| 2023 | 100.0 | — | 100.0 | 100.0 | 100.0 | — | 100.0 | 100.0 | 100.0 | — | 100.0 | 100.0 | 91.6 |
| 2024 | 100.0 | — | 100.0 | 100.0 | 100.0 | — | 100.0 | 100.0 | 100.0 | — | 100.0 | 100.0 | 99.7 |
| 2025 | 100.0 | — | 100.0 | 100.0 | 100.0 | — | 100.0 | 100.0 | 100.0 | — | 100.0 | 100.0 | 99.7 |

---

## Column Availability Across Years

| Column | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|---|---|---|---|---|---|---|---|---|---|
| Temp_5cm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SM_5cm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| EC_5cm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — | — |
| RDP_5cm | — | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Temp_15cm | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| SM_15cm | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| EC_15cm | — | — | — | — | — | ✓ | — | — | — | — |
| RDP_15cm | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Temp_50cm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SM_50cm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| EC_50cm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — | — |
| RDP_50cm | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Precipitation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Schema Changes

**2016–2020:** EC-based sensors
- Columns: `Temp_5cm`, `SM_5cm`, `EC_5cm`, `Temp_50cm`, `SM_50cm`, `EC_50cm`, `Precipitation`

**2021:** Transition year (contains both EC and RDP)
- Columns: All EC columns + `RDP_5cm`, `RDP_15cm`, `RDP_50cm`, `Temp_15cm`, `SM_15cm`

**2022–2025:** RDP-based sensors with 15 cm depth added
- Columns: `Temp_5cm`, `SM_5cm`, `RDP_5cm`, `Temp_15cm`, `SM_15cm`, `RDP_15cm`, `Temp_50cm`, `SM_50cm`, `RDP_50cm`, `Precipitation`

---

## Usage Recommendations

### Loading Data
```python
import pandas as pd
import numpy as np

# Load a year
df = pd.read_csv('2017_V6.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Handle any remaining string NaNs
df = df.replace("NaN", np.nan)
```

### Handling Schema Changes
For analyses spanning 2016–2025:
- Use **EC columns** for 2016–2021
- Use **RDP columns** for 2021–2025
- Note: 2021 contains both (transition year)

### Time Series Analysis
```python
# Resample to daily
daily = df.set_index('timestamp').resample('D').mean()

# Plot
import matplotlib.pyplot as plt
plt.plot(df['timestamp'], df['Temp_5cm'])
plt.ylabel('Temperature (°C)')
plt.xlabel('Date')
plt.show()
```

---

## Quality Assurance

This V6 dataset has undergone:
1. ✅ Sensor redundancy resolution (A/B selection)
2. ✅ Outlier removal (physically impossible values)
3. ✅ Flatline detection (stuck sensors rejected)
4. ✅ Depth consistency verification
5. ✅ String error codes replaced with NaN

**Data gaps remain as NaN** (no interpolation or gap-filling performed).

---

## Citation

*[Add your citation information here]*

---

## Contact

*[Add contact information here]*

---

**README Generated:** 2026-01-26 12:33:37  
**Script:** `verify_V6_dataset.py`
