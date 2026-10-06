# B Findings: EDA and Outliers

## Data quality
- Rows: 5184 | Columns in the cleaned file: 13 (18 after adding my 5 flags)
- Missing values: 0 in every column | Duplicate rows: 0 | Duplicate input combinations: 0
- Complete grid: yes (5184 rows = 4 x 2 x 2 x 2 x 2 x 3 x 3 x 3 x 3 input combinations, each appearing once)

## Physics checks
- Symmetry at ecc = 0: max |Mr_t - Mr_c| = 1.0e-9, max |Mt_t - Mt_c| = 7.0e-10.
  The tension and compression sides match to within rounding (the file
  stores 10 decimals), so the symmetry check passes.
- Trend breaks as ecc rises (number of input groups that break the expected trend):
  Mr_t 0, Mt_t 0, Mr_c 1, Mt_c 0.
  The one Mr_c break is the group N = 2000, gammaG = 1.1, Esoil = 75,
  Econc = 37000, Dbot = 23, H1 = 1.2, H2 = 1.5, H3 = 1.6.
  Its Mr_c goes 0.0973 (ecc = 0), 0.0797 (ecc = 10), 0.961 (ecc = 18),
  1.832 (ecc = 26). The drop from ecc = 0 to 10 breaks the rising trend.
  The ecc = 10 row is one of the suspect rows 4377 and 4381, so the
  trend check and the suspect-row check point to the same data.

## Outliers
- Global IQR flags (outlier_global): Mr_t 6, Mr_c 33, Mt_t 0, Mt_c 0.
  All 39 flagged rows are at ecc = 26 and N = 5000: 33 at Dbot = 17 and 6 at Dbot = 23.
  They sit at the most extreme load condition, so they are real extremes and are kept.
- Per-ecc IQR flags (outlier_group): Mr_t 28, Mt_t 30, Mr_c 28, Mt_c 30.
  The flagged rows are all at ecc = 0 and Dbot = 23: 18 at N = 2000 and 18 at
  N = 5000 (36 rows). They spread over 7 of the 27 H1/H2/H3 combinations
  (4 or 8 rows each). H1 is always 1.2 or 1.6, never 0.8, and H3 = 1.6 in 24 of the
  36 rows. Output values at ecc = 0 are tiny, so this looks like a scale
  artifact, and the rows are kept.
- Per-ecc MAD flags (outlier_mad): Mt_t 4, Mt_c 4, Mr_t 0, Mr_c 0.
  The flagged rows are all at ecc = 0 and Dbot = 23: 2 at N = 2000 and 2 at
  N = 5000 (4 rows). They are in the same ecc/N/Dbot cells as the per-ecc IQR
  flags, so the same scale-artifact explanation applies and the rows are kept.

## Suspect rows
- Rows 4377 and 4381 (ecc = 10, N = 2000, gammaG = 1.1, Esoil = 75, Dbot = 23,
  H1 = 1.2, H2 = 1.5, H3 = 1.6, Econc = 30000 and 37000).
- Mr_c is about 0.105 and 0.080, while sibling rows sit around 1.03 to 1.39.
- The Econc = 37000 row (Mr_c = 0.0797) is the Mr_c trend break in the physics
  check above: it falls below its own ecc = 0 value of 0.0973.
- Flagged with suspect_row, not deleted. For mentor review on Day 6.

## Which inputs matter most
- Strongest: ecc (effect size 2.04 to 2.26 across all four outputs).
- Second: N (0.75 to 1.04).
- Smaller but notable: Dbot on Mr_t (0.40), H2 on Mt_c (0.20) and Mr_t (0.15),
  Dbot on Mt_c (0.12), H1 on Mr_t and Mt_c (0.11 and 0.10).
- Weakest: Econc (0.00 on all outputs). gammaG and Esoil are also near 0
  (0.05 or less).

## Clustering
- Silhouette scores: k=2: 0.361, k=3: 0.290, k=4: 0.315, k=5: 0.314, k=6: 0.267.
- Best is k = 2 at 0.361, which is moderate structure. The other values are
  around 0.27 to 0.32, so there is no clear natural number of groups.

## Files handed to C
- data/processed/data_with_flags.csv
- figures/dist_outputs.png, box_by_ecc.png, corr_heatmap.png, sensitivity_heatmap.png