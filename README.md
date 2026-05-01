# Berambadi Soil Hydrothermal Dataset (2016–2025) — Code

Processing and figure-generation code accompanying the dataset:

> **A decade of high-frequency soil hydrothermal observations in a semi-arid monsoon catchment (2016–2025)**
> Rao, S., Upadhya, A., Goswami, S., Shaju, A. P., Kandala, R., Upadhyaya, D., Gupta, V., Ruiz, L., and Muddu, S. (2026)
> Zenodo. https://doi.org/10.5281/zenodo.18409640

The dataset contains continuous 15-minute measurements of soil moisture, temperature, and electrical conductivity or relative dielectric permittivity at 5 cm and 50 cm depths (with an additional 15 cm depth from 2021 onward), together with co-located precipitation, recorded at the Berambadi agricultural catchment in Karnataka, southern India.

This repository contains the Python code used to curate the released annual CSV files and generate the figures and tables presented in the accompanying Data Descriptor.

---

## Repository contents

| File | Description |
|---|---|
| `getting_started.py` | Quickstart script. Loads one year of data, prints a completeness summary, and plots the four core variables. **Start here.** |
| `curate_Data.py` | Sensor-selection algorithm used to convert raw multi-sensor records into the unified, quality-controlled annual CSV files described in Section 2.3 of the paper. |
| `Figure1.py` | Generates Figure 1 (study site location and temporal data availability). Requires shapefiles — see "Notes" below. |
| `Figure2.py` | Generates Figure 2 (high-frequency soil hydrothermal dynamics during the 2017 monsoon-to-dry transition). |
| `Figure3.py` | Generates Figure 3 (precipitation–percolation coupling dynamics). |
| `FigureS1.py` | Generates Figure A1 (technical validation of soil hydrothermal consistency). |
| `FigureS2.py` | Generates Figure A2 (electrical conductivity–soil moisture coupling at 50 cm). |

---

## Quick start

1. Download the data files from the Zenodo repository:
   https://doi.org/10.5281/zenodo.18409640

2. Place the annual CSV files (`2016_V1.csv` … `2025_V1.csv`) in a folder.

3. Install dependencies:
   ```bash
   pip install pandas matplotlib numpy scipy seaborn geopandas
   ```

4. Run the quickstart script:
   ```bash
   python getting_started.py
   ```

   By default this loads `2017_V1.csv` from the current folder. Edit `DATA_DIR` and `YEAR` at the top of the script to load a different year or point to a different folder.

---

## Variable conventions

All timestamps are in Indian Standard Time (IST, UTC+05:30). Missing values are represented as `NaN`.

| Variable | Description | Units | Years available |
|---|---|---|---|
| `SM_5cm`, `SM_15cm`, `SM_50cm` | Volumetric soil moisture | % | 5/50 cm: 2016–2025; 15 cm: 2021–2025 |
| `Temp_5cm`, `Temp_15cm`, `Temp_50cm` | Soil temperature | °C | 5/50 cm: 2016–2025; 15 cm: 2021–2025 |
| `EC_5cm`, `EC_50cm` | Electrical conductivity | dS m⁻¹ | 2016–2020 (sensor transition in 2021) |
| `RDP_5cm`, `RDP_15cm`, `RDP_50cm` | Relative dielectric permittivity | – | 2021–2025 |
| `Precipitation` | Rainfall per 15-min interval | mm | 2016–2025 |

A full description of variables, sensor history, and known limitations is included in the README within the Zenodo dataset.

---

## Notes

- **Figure 1 shapefiles.** `Figure1.py` requires shapefiles for the India boundary, state boundaries, and the Berambadi catchment. These are not included here. Country and state boundaries can be obtained from Survey of India open data portals; the Berambadi catchment boundary can be requested from the corresponding author.

- **Hardcoded paths.** Some scripts contain absolute paths from the local development environment at the top of the file (e.g., `/home/sathya-iisc/Documents/...`). Edit these to match your local setup before running.

- **Curation.** `curate_Data.py` was used to process the raw V4 multi-sensor records into the released V1 (formerly V6 internally) annual CSV files. Most users will not need to run this — the released CSV files are already curated. The script is provided for transparency and reproducibility.

---

## Citation

If you use this code or the associated dataset, please cite:

> Rao, S., Upadhya, A., Goswami, S., Shaju, A. P., Kandala, R., Upadhyaya, D., Gupta, V., Ruiz, L., and Muddu, S. (2026). A decade of high-frequency soil hydrothermal observations in a semi-arid monsoon catchment (2016–2025) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18409640

---

## License

Code in this repository is released under the **MIT License** (see `LICENSE`).

The associated dataset on Zenodo is released under **Creative Commons Attribution 4.0 International (CC-BY 4.0)**.

---

## Contact

For questions about the code or dataset, please contact the corresponding author:

**Sekhar Muddu** — sekhar.muddu@gmail.com
Department of Civil Engineering, Indian Institute of Science, Bengaluru, India

For technical issues with the code, please open an issue on this repository.
