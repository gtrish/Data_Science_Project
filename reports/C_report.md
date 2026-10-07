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
- Cleaning steps: [ask A and write them here].

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

## 4. Checks and problems
- When the load is centered (ecc = 0), tension and compression results
  match, as expected.
- 39 rows are extreme values, but they come from the most extreme load
  settings, so they were kept.
- Two rows (4377 and 4381) look suspect and need the mentor's review.

## 5. Conclusion
The off-center load (ecc) and the load size (N) drive the results. The
other settings matter much less.

## 6. Next steps
[Fill in after the group agrees on what comes next.]
