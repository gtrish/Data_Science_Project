# Project Report: How Input Settings Affect FEM Simulation Results

## 1. What this project is about
This dataset comes from FEM simulations (computer simulations of how a
structure behaves under load). In each run, 9 input settings are changed
and 4 results (bending moments) are recorded. Our goal is to understand
which settings change the results, and by how much.

(Note: the inputs look like a concrete foundation on soil. To be
confirmed with the mentor.)

## 2. The data
- 5,184 rows: each row is one simulation run.
- 9 inputs: ecc, N, gammaG, Esoil, Econc, Dbot, H1, H2, H3.
- 4 results: Mr_t, Mt_t, Mr_c, Mt_c.
- No missing values and no duplicate rows.
- Every combination of input values appears exactly once.
- Cleaning steps (done by A):
  1. Loaded the dataset and found its structure: a full factorial grid
     of 5,184 runs.
  2. Checked for missing values: none found.
  3. Checked for duplicate rows: none found.
  4. Checked data types: all columns are numeric.
  5. Dropped the `Sample` column, because it is only a row number and
     carries no information.
  6. Calculated summary statistics (mean, median, standard deviation,
     quartiles) with `describe()`.
  7. Plotted histograms and boxplots for all 13 columns.
  8. Saved the result as `fem_cleaned.csv`: 5,184 rows and 13 columns
     (9 inputs and 4 results). No values were changed.
- Files used in the analysis:
  - `fem_cleaned.csv` (A): the cleaned data, 13 columns.
  - `data_with_flags.csv` (B): the same rows with 5 extra columns: the
    outlier flags (`outlier_global`, `outlier_group`, `outlier_mad`,
    `suspect_row`) and `M_ov`, which equals N × ecc. 18 columns in total.
  - `outliers_only.csv` (C): the 77 rows flagged by at least one method,
    with a `flagged_by` column, made for separate outlier tests.

## 3. Findings

### 3.1 Load position (ecc) matters most
As the load moves further from the center, the compression-side moments
(Mr_c, Mt_c) go up and the tension-side moments (Mr_t, Mt_t) go down, in
a nearly straight-line pattern. (Figure: figures/C_ecc_effect.png)

### 3.2 Load size (N) is second
Raising N from 2000 to 5000 makes the moments larger on both sides.
(Figure: figures/C_other_inputs.png)

### 3.3 Weak or no effect
- Foundation diameter (Dbot) has only a small effect.
- Concrete stiffness (Econc) has almost no effect.
- gammaG and Esoil are also close to zero (from B's analysis).

### 3.4 Multivariate view
The pairplot shows that ecc separates the results into distinct groups.
Centered loads (ecc = 0) give results near zero, and the results spread
further apart as ecc increases. (Figure: figures/C_pairplot.png)

PCA shows that the first component explains 96.7% of the variation in the
four results, and the first two explain 99.1%. So the four moments move
together, and the data is mostly one-dimensional. Colouring the points by
ecc shows that the load position is the main driver of this pattern.
(Figure: figures/C_pca.png)

## 4. Checks and outliers

### 4.1 Physics checks (done by B)
- When the load is centered (ecc = 0), tension and compression results
  match to within rounding, as expected.
- As ecc rises, the results follow the expected trend in all but one
  input group (Mr_c, N = 2000, Dbot = 23). That group contains one of
  the suspect rows below.

### 4.2 Outlier detection
Outliers are values that look very different from the rest. B used three
methods, and each one flags rows with a True/False column:

| Method | Rows flagged | Where they are |
|---|---|---|
| Global IQR (outlier_global) | 39 | All at ecc = 26 and N = 5000 |
| Per-group IQR (outlier_group) | 36 | All at ecc = 0 and Dbot = 23 |
| Per-group MAD (outlier_mad) | 4 | Same cells as the per-group IQR rows |
| Suspect rows (suspect_row) | 2 | Rows 4377 and 4381 |

In total 77 different rows are flagged by at least one method. Some rows
are flagged more than once, so the counts above add up to more than 77.
(Figure: figures/C_flag_counts.png)

### 4.3 What we decided
- **Global flags (39 rows):** these sit at the most extreme load setting,
  so they are real extreme results. Kept.
- **Per-group flags (36 and 4 rows):** at ecc = 0 all results are tiny, so
  small differences look big. This looks like a scale effect, not an
  error. Kept.
- **Suspect rows (4377 and 4381):** their Mr_c is about 0.1, while similar
  rows are around 1.0 to 1.4. They might be simulation errors, so they
  are kept but flagged for the mentor to review.
- **No rows were deleted.** To test whether the two suspect rows matter,
  we removed them and recomputed the average of each result at every ecc
  level. The largest change in any average was 0.0028 (for Mr_c), and the
  other three results changed by less than 0.001. The averages range from
  about -3 to +5, so the change is tiny and our findings do not depend on
  these rows. The dashboard has a checkbox to exclude them. If the mentor
  confirms they are errors, they will be removed.

## 5. Interactive dashboard
A Streamlit dashboard (`dashboard.py`) lets the reader explore the data:
- pick any input and see how it changes the four results
- see how many rows each outlier method flags, and look at those rows
- view the pairplot and the PCA chart, coloured by ecc, N or Dbot
- tick a checkbox to exclude the two suspect rows and watch the charts
  update

To run it: `streamlit run dashboard.py`

## 6. Questions for the mentor
1. What is this object? (We think it is a concrete foundation on soil.)
2. At ecc = 0 the tension and compression results are equal. Is that expected?
3. As ecc rises, the compression side goes up and the tension side goes
   down in a straight line. Is that physically reasonable?
4. Concrete stiffness (Econc) has almost no effect. Does that make sense?
5. Rows 4377 and 4381 have Mr_c near 0.1, while similar rows are near
   1.0 to 1.4. Are they errors?
6. What does gammaG mean?
7. M_ov equals N × ecc exactly (we checked every row). Is this the
   overturning moment? It is not an independent input, so it should be
   left out of the correlation heatmap.

## 7. Conclusion
The off-center load (ecc) and the load size (N) drive the results. The
other settings matter much less. The four results move together, so the
data is mostly one pattern. Outliers were flagged and checked, not
removed, and the two suspect rows do not change the findings.

## 8. Next steps
- Get the mentor's answers and correct anything they flag.
- If the mentor confirms rows 4377 and 4381 are errors, remove them and
  re-run the charts.
- Possible future work: predict the results from the inputs using a model.

## 9. Core data science concepts used (CO1)
- **Dataset:** a table where each row is one observation and each column
  is one variable. Here, each row is one simulation run.
- **Inputs and outputs:** inputs are the settings we change (ecc, N, Dbot
  and others). Outputs are the results we measure (the four moments).
- **Full factorial design:** every combination of the input values is run
  exactly once. This is why the 5,184 rows form a complete grid.
- **Data cleaning:** checking for missing values, duplicates and wrong data
  types before analysis, so that later results can be trusted.
- **Exploratory data analysis (EDA):** looking at the data with summary
  numbers and charts to find patterns before building any model.
- **Descriptive statistics:** mean, median, standard deviation and
  quartiles, which summarise each column.
- **Outliers:** values that look very different from the rest. We flagged
  them with three methods (global IQR, per-group IQR and MAD) and kept
  them, because most are real extreme cases.
- **Correlation and sensitivity:** measures of how strongly an input is
  linked to an output.
- **PCA (principal component analysis):** a way to squeeze many related
  columns into fewer axes, to see the overall structure.

## 10. Tools and industrial context (CO5)
**Tools (all open-source):**
- Python, with pandas and numpy for data handling
- matplotlib and seaborn for charts
- scikit-learn for PCA and scaling
- Jupyter notebooks in VS Code for the analysis
- Streamlit for the interactive dashboard
- Git and GitHub for teamwork and version control

**Industrial context:** The data comes from FEM (finite element) simulations.
Engineers use these simulations to check how a structure behaves under load
before building it. The inputs suggest a concrete foundation on soil carrying
an off-centre load, which is a common situation in structural design. (To be
confirmed with the mentor.) Running a simulation can be slow, so knowing which
settings matter most helps engineers focus on the ones that change the result.

## 11. Where each course outcome is covered
| Outcome | Where in this report |
|---|---|
| CO1: core data science concepts | Section 9 |
| CO2: statistical analysis | Summary statistics (section 2), PCA numbers (3.4), outlier methods and the suspect-row test (4) |
| CO3: explore, summarise, visualise | Sections 2, 3 and 4, with the figures and the dashboard |
| CO4: data types and visualisation in code | True/False flag columns shown as a bar chart (4.2), numeric charts (3), pairplot and PCA (3.4) |
| CO5: open-source tools on a real case | Section 10, plus the dashboard (section 5) |