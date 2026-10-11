# How input settings affect FEM simulation results

A data science project on a finite element method (FEM) simulation dataset.
Each row is one simulation run. We change 9 input settings and record 4 results (moments).
We use exploratory data analysis (EDA), outlier checks and visualisation to find which inputs matter most.
No predictive model is built in this phase.

## Dataset

- Source: the Kaggle dataset "FEM simulations" (author: daalgi).
- Main file: `data/raw/5184doe.csv`. It has 5,184 runs: every combination of the input values appears exactly once (a full factorial design).
- Inputs (9): `ecc`, `N`, `gammaG`, `Esoil`, `Econc`, `Dbot`, `H1`, `H2`, `H3`.
- Results (4): `Mr_t`, `Mt_t`, `Mr_c`, `Mt_c`.
- Two smaller files, `1000randoms.csv` and `40semi-randoms.csv`, are used to check the findings on independent data.
- What the inputs and results physically mean is still to be confirmed with our mentor. See the questions in `reports/C_report.md`.

## Folder layout

```
data/raw/          original CSV files
data/processed/    cleaned data (fem_cleaned.csv), data with outlier flags (data_with_flags.csv), flagged rows (outliers_only.csv)
notebooks/         01 data quality (A), 02 outliers and checks (B), 03 multivariate analysis (C), 04 validation
figures/           charts saved by the notebooks
reports/           B_findings.md and C_report.md (the full report)
dashboard.py       interactive Streamlit dashboard
requirements.txt   Python packages
```

## How to run

1. Create and activate a virtual environment.
   Windows PowerShell:
```
   python -m venv venv
   venv\Scripts\Activate.ps1
```
   macOS or Linux:
```
   python3 -m venv venv
   source venv/bin/activate
```
2. Install the packages:
```
   pip install -r requirements.txt
```
3. Start the dashboard from the repo root:
```
   streamlit run dashboard.py
```
4. To rerun the analysis, open the notebooks in `notebooks/` in order (01, 02, 03, 04) and use Restart and Run All.

## Main findings

- The load position `ecc` has the largest effect on all four results (effect size 2.04 to 2.26).
- The load size `N` is second (0.75 to 1.04).
- `Dbot`, `H1` and `H2` have small effects that depend on the result. `Econc`, `gammaG` and `Esoil` have almost none.
- `M_ov = N x ecc` correlates with the results more strongly than either input alone.
- The four results move together: the first principal component explains 96.7% of the variation.
- At `ecc = 0`, tension and compression results match to within rounding, as expected.
- A check on the independent 1,000-run sample gives the same ranking: `ecc` first, `N` second, the rest weak.

## Outliers

Three methods flag unusual rows (global IQR: 39 rows, per-`ecc` IQR: 36, per-`ecc` MAD: 4).
Two further rows (4377 and 4381) break the expected trend and are marked `suspect_row`.
In total, 77 distinct rows are flagged. No rows were deleted.
Removing the two suspect rows changes the group averages by at most 0.003, so the findings do not depend on them.
The mentor will confirm whether those two rows are simulation errors.

## Course outcomes

`reports/C_report.md` maps this work to course outcomes CO1 to CO5 (section 11).

## Team

- A: data quality and univariate analysis
- B: outliers, physics checks, correlation and sensitivity
- C: multivariate analysis, dashboard and report

Guide: <name>. Mentor: <name>.

## Future work

Compare a hand-calculation formula with the FEM results for all 5,184 runs, and study where and why they differ.