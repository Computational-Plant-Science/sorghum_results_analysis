# Trait Analysis & Visualization Documentation

This document describes the end‑to‑end process for cleaning, analyzing, and visualizing plant trait data. 

---

## 1. Introduction

Modern phenotyping experiments generate large spreadsheets of trait measurements across many plots, treatments, and genotypes. Our goal is to build a reusable, transparent pipeline that:

1. **Aggregates** raw Excel files and merges them with experimental metadata.  
2. **Scales** trait values using domain‑specific factors or normalization.  
3. **Handles** outliers systematically (IQR clipping or removal).  
4. **Produces** cleaned outputs and a suite of visualizations.  

All scripts are written in Python (3.8+), relying on `pandas` for data handling, `numpy` for numeric operations, and `plotly` (plus `matplotlib`/`seaborn` where needed) for interactive and static plots.

---

## 2. Data & Metadata

- **Raw data** lives in `data/raw/`: one `.xlsx` file per experimental run.  
- **Metadata** in `data/meta.xlsx` contains plot‑to‑genotype mappings under two possible layouts:
  - **Wide format**: one column per condition (e.g. “well‑watered”, “water‑limited”) with plot IDs.
  - **Replicate format**: multiple “Rep” columns plus explicit `Condition` and `Genotype` columns.

Our `process_metadata()` function automatically detects the format, melts it into a tidy table with columns:
plot_number | Genotype | Condition

---

## 3. Environment Setup

1. **Clone the repo**  
  ```bash
   git clone https://github.com/Computational-Plant-Science/sorghum_results_analysis.git
  ```
2. **Install packages**
  ```bash
   pip install pandas numpy plotly openpyxl matplotlib seaborn
  ```

---
## 4. The Data Cleaning Pipeline

### 4.1 combine_and_clean_data.py
**Purpose**
- Read all .xlsx files matching --input-dir/*.xlsx.
- Tag each row with plot_number (parsed from filename).
- Merge numeric columns by averaging replicates per plot.
- Join with metadata (via process_metadata).
- Group by Genotype and Condition, averaging trait values.

**Key functions**
- process_metadata(metadata_df)
- combine_excels(file_pattern, metadata_path)
- scale_factor(df) applies string‑based scaling constants.
- replace_outliers_iqr(df, k, winsorise) performs IQR clipping.

**Run**
```bash
python combine_and_clean_data.py \
  --input-dir data/raw \
  --metadata data/meta.xlsx \
  --output results/cleaned.xlsx
```

After this step, results/cleaned.xlsx contains one row per genotype‑condition pair, with scaled, outlier‑handled trait values.

---

## 5. Visualization Modules
Each script reads results/cleaned.xlsx (or intermediate CSVs) and produces publication‑quality figures.

### 5.1 Trait Comparison (plot_comparisons.py)
- Grid of grouped bar charts, one subplot per trait.
- Compares mean trait values for HI vs LI across all genotypes.
- Customizable:
  - --traits to select a subset.
  - --cols to change grid width.
- Color map fixed: blue = HI, red = LI.
```bash
python plot_comparisons.py \
  --input results/cleaned.xlsx \
  --traits root_length root_volume \
  --cols 3 \
  --out results/trait_comparison.png
  ```

### 5.2 Mean/Median Summaries (plot_mean_median.py)
- Bar plot of overall mean or median per trait.
- Optionally includes standard error bars when plotting mean.
- Flags:
  - --type {Mean,Median}
  - --hide-error to omit error bars.
```bash
python plot_mean_median.py \
  --input results/cleaned.xlsx \
  --type Mean \
  --out results/mean_summary.png
  ```

### 5.3 Heritability Estimation (plot_heritability.py)
- Computes per‑trait variance components and H²:
  - Ve (error variance) ≅ std / √n
  - Vg (genetic variance) from difference of mean and Ve
  - H² = Vg / Vp
- Plots H² as bars, optionally split by HI vs LI (side‑by‑side) and with error bars.
```bash
python plot_heritability.py \
  --input results/cleaned.xlsx \
  --separate-by-treat \
  --show-error \
  --max-error 5.0 \
  --out results/heritiability.png
  ```

### 5.4 Plasticity Boxplots (plot_plasticity.py)
- Reads two Excel files (one per region) via --file1 and --file2.
- Filters data for the specified genotype (`--genotype`).
- Saves trait_plasticity_plot.png per trait.
```bash
python plot_plasticity.py \
  --genotype SC56 \
  --file1 results/arizona_cleaned.xlsx \
  --file2 results/texas_cleaned.xlsx \
  --trait root_system_length \
```

### 5.5 Regional Trend Lines (plot_line.py)
- Line plots of trait values across conditions, colored by region (e.g. Arizona vs Texas).
- Two modes:
  - Single-trait: --trait ROOT_LENGTH
  - All traits: omit --trait flag.
```bash
python plot_line.py \
  --genotype SC56 \
  --trait root_length \
  --file1 data/az_clean.xlsx\
  --file2 data/tx_clean.xlsx
  ```


## 6. Process Reflection & Challenges

### Combining Raw Files  
My first challenge was simply aggregating dozens of Excel files into a single DataFrame. I learned to use Python’s glob module to list *.xlsx files, and then iteratively read and concatenate them with pandas.concat(). This taught me how to build an efficient pipeline that scales to hundreds of files without manual editing.

### Mapping Metadata  
Once the raw data were loaded, I needed to join each plot to its genotype and treatment. Learning about pd.melt() and groupby().mean() was key: I wrote a process_metadata() function that automatically detects wide vs. replicate‐style metadata and “melts” it into a tidy table, then averages replicate measurements per plot.

### Early Plotting Mistakes  
I initially dove into visualization by writing custom matplotlib code, but I misunderstood the assignment and produced my own plot styles rather than replicating Suxing’s example figures. This taught me the importance of fully understanding requirements before coding.

### Switching to Plotly  
Because Suxing’s figures used interactive plotly charts, I refactored all of my plotting scripts from matplotlib to plotly.express. Adapting to Plotly’s API (facets, subplots, and consistent theming) was a steep but valuable learning curve.

### Recreating Suxing’s Plots  
After switching libraries, I matched every line and bar chart to Suxing’s originals—titles, axes, colors, and facet layouts all aligned. This validation step confirmed that my data transformations were correct.

### Scaling & Cleaning  
Parallel to plotting, I figured out Suxing’s scaling system (hard‑coded trait multipliers) and an outlier handler (IQR clipping). I iterated until the pipeline gracefully handled missing values and extreme points without breaking summaries or figures.

### Code Consolidation & Reusability
Earlier in the project, I had redundant cleanup and scaling logic scattered across multiple scripts. Some functions handled missing values and scaling, others didn’t. This led to inconsistent behavior and duplicated code.

I refactored the pipeline to standardize all data cleaning and scaling in one centralized script (combine_and_clean_data.py).

### Adapting to Texas Data  
When I received a second batch from Texas—whose Excel and metadata formats differed slightly. I extended my scripts to accept both formats seamlessly, adding defensive checks and more flexible column‐matching so the same code works on any location.

### Creative “Top‑N” Line Plot  
Inspired by Suxing’s spaghetti plots, I implemented a highlight function that automatically picks the top N most variable genotypes (by standard deviation) and greys out the rest. This shows the key trends without overwhelming the viewer.

### Bug Fixes & Input Flexibility  
Along the way I tackled numerous edge cases:
- Accepting ww vs. well-watered or HI vs. High in metadata  
- Ensuring x‑axes render on every subplot in facet grids  
- Preventing axis labels from overlapping when many traits are plotted 
- Stripped trailing whitespace, dots (.), or casing issues in genotype names (e.g., "SC56." vs. "SC56").
- Applied .str.lower() and robust matching logic to tolerate these variations.
- Added the option to include standard error bars for trait plots, which improved interpretability and aligned with common scientific reporting practices.

### Docker Containerization  

