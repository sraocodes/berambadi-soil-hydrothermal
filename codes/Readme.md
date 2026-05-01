# Berambadi Soil Hydrothermal Dataset (2016–2025) — Code

Python code accompanying the dataset:

> Rao, S. et al. (2026). *A decade of high-frequency soil hydrothermal observations in a semi-arid monsoon catchment (2016–2025)*. Zenodo. https://doi.org/10.5281/zenodo.18409640

The dataset contains 15-minute soil moisture, temperature, electrical conductivity / relative dielectric permittivity, and precipitation from the Berambadi catchment, Karnataka, India.

---

## Files

### `getting_started.py`
Quickstart script. Loads one year of data, prints a completeness summary, and plots the four core variables (rainfall, soil moisture, temperature, EC/RDP) at 5 cm and 50 cm depths. **Run this first.**

### `curate_Data.py`
Sensor-selection algorithm. Converts the raw multi-sensor records (V4) into the unified, quality-controlled annual CSV files (V6) released with the dataset. Implements the physics-based selection logic described in Section 2.3 of the paper (anti-noise filter, flatline detection, variance check, depth consistency). Most users won't need to run this — the released CSV files are already curated. Provided for transparency and reproducibility.

### `Figure1.py`
Generates **Figure 1** of the paper: study site location and temporal data availability. Three panels — regional context (India / Karnataka), Berambadi catchment with sensor location, and annual data coverage bar chart. Requires shapefiles (see "Notes" below).

### `Figure2.py`
Generates **Figure 2** of the paper: high-frequency soil hydrothermal dynamics during the 2017 monsoon-to-dry transition (August–October). Five-panel time series of rainfall, soil moisture, electrical conductivity, soil temperature, and rapid wetting rate, with an inset showing a single storm event.

### `Figure3.py`
Generates **Figure 3** of the paper: precipitation–percolation coupling dynamics. Two panels — (a) percolation probability versus rainfall event magnitude, and (b) percolation probability versus antecedent surface moisture state. Iterates over all annual files and aggregates 916 rainfall events.

### `FigureS1.py`
Generates **Figure A1** of the appendix: technical validation of soil hydrothermal consistency across the decade. Three panels — thermal inversion frequency, vertical connectivity, and hydraulic regime.

### `FigureS2.py`
Generates **Figure A2** of the appendix: validation of EC–soil moisture coupling at 50 cm depth across the 2021 sensor transition (native EC sensors vs calibrated dielectric permittivity sensors).

---

## Quick start

1. Download the data from Zenodo: https://doi.org/10.5281/zenodo.18409640
2. Install dependencies:
   ```
   pip install pandas numpy matplotlib scipy seaborn geopandas
   ```
3. Open any script and edit the `DATA_DIR` variable at the top to point to the folder containing the annual CSV files.
4. Run `getting_started.py` first to confirm the data loads correctly.

---

## Notes

- **Filenames.** Internal working files use the suffix `_V6.csv` (e.g., `2017_V6.csv`). The Zenodo release uses `_V1.csv`. If you downloaded from Zenodo, either rename the files or update the filename pattern in the scripts.
- **Hardcoded paths.** All scripts contain absolute paths from the development environment (`/home/sathya-iisc/Documents/...`) at the top. Edit `DATA_DIR` and `OUT_DIR` to match your local setup.
- **Figure 1 shapefiles.** `Figure1.py` requires shapefiles for India, state boundaries, and the Berambadi catchment. These are not included in this repository. Country and state boundaries are available from open Survey of India sources; the Berambadi catchment boundary can be requested from the corresponding author.
- **Timestamps.** All timestamps in the dataset are in Indian Standard Time (IST, UTC+05:30).
- **EC vs RDP.** Electrical conductivity (EC) is reported for 2016–2020. Relative dielectric permittivity (RDP) is reported for 2021–2025. The year 2021 contains both during the sensor transition.

---

## Citation

If you use this code or the dataset, please cite:

> Rao, S., Upadhya, A., Goswami, S., Shaju, A. P., Kandala, R., Upadhyaya, D., Gupta, V., Ruiz, L., and Muddu, S. (2026). A decade of high-frequency soil hydrothermal observations in a semi-arid monsoon catchment (2016–2025) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18409640

---

## License

Code: MIT License. Dataset: CC-BY 4.0.

---

## Contact

**Sekhar Muddu** — sekhar.muddu@gmail.com
Department of Civil Engineering, Indian Institute of Science, Bengaluru, India

For code issues, please open a GitHub issue.
