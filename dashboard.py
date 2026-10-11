import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import plotly.express as px
BASE = Path(__file__).parent

@st.cache_data
def load():
    return pd.read_csv(BASE / "data" / "processed" / "data_with_flags.csv")

df = load()

# Sidebar switch: exclude the 2 suspect rows
st.sidebar.header("Options")
exclude = st.sidebar.checkbox("Exclude the 2 suspect rows", value=False)
if exclude:
    df = df[~df["suspect_row"].astype(bool)]
st.sidebar.write(f"Rows in use: {len(df)}")

inputs = ["ecc", "N", "gammaG", "Esoil", "Econc", "Dbot", "H1", "H2", "H3"]
outputs = ["Mr_t", "Mt_t", "Mr_c", "Mt_c"]
flag_cols = [c for c in df.columns if c.startswith("outlier") or c == "suspect_row"]
full = load()  # unfiltered copy; used for the option lists and the run lookup
 
 
def reset_filters():
    for c in inputs:
        st.session_state[f"filter_{c}"] = sorted(full[c].unique().tolist())
 
 
with st.sidebar.expander("Filter by input value"):
    for c in inputs:
        opts = sorted(full[c].unique().tolist())
        st.session_state.setdefault(f"filter_{c}", opts)
        chosen = st.multiselect(c, opts, key=f"filter_{c}")
        df = df[df[c].isin(chosen)]
    st.button("Reset filters", on_click=reset_filters)
 
st.sidebar.write(f"Rows after filters: {len(df)}")
if len(df) < 3:
    st.warning("Fewer than 3 runs match the filters. Widen the filters in the sidebar.")
    st.stop()
st.title("How input settings affect FEM simulation results")
st.write("Each row is one simulation run. We change 9 input settings "
         "and record 4 results (moments).")

# 1. Data
st.header("1. The data")
c1, c2, c3 = st.columns(3)
c1.metric("Rows", df.shape[0])
c2.metric("Inputs", len(inputs))
c3.metric("Results", len(outputs))
st.dataframe(df[inputs + outputs].head(10))

# 2. Effect explorer
st.header("2. Effect of each input")
choice = st.selectbox("Pick an input to explore:", inputs)
avg = df.groupby(choice)[outputs].mean().reset_index()
fig = px.line(avg, x=choice, y=outputs, markers=True,
              labels={"value": "Average moment", "variable": "Result"},
              title=f"Average result vs {choice}")
st.plotly_chart(fig, use_container_width=True)
st.header("2b. Try the settings")
st.write("Pick a value for every input. The data is a full grid, so each "
         "combination is exactly one simulation run. This ignores the sidebar filters.")
 
cols = st.columns(3)
pick = {}
for i, c in enumerate(inputs):
    opts = sorted(full[c].unique().tolist())
    pick[c] = cols[i % 3].selectbox(c, opts, key=f"pick_{c}")
 
mask = pd.Series(True, index=full.index)
for c, v in pick.items():
    mask &= full[c] == v
run = full[mask]
 
if run.empty:
    st.info("No run with this combination.")
else:
    r = run.iloc[0]
    if "suspect_row" in full.columns and bool(r["suspect_row"]):
        st.warning("This run is one of the 2 suspect rows.")
    mcols = st.columns(4)
    for col, o in zip(mcols, outputs):
        col.metric(o, f"{r[o]:.3f}",
                   delta=f"{r[o] - full[o].mean():+.3f} vs average",
                   delta_color="off")
    st.caption(f"Row index {run.index[0]}. N × ecc = {r['N'] * r['ecc']:.0f}. "
               "The delta compares with the average of all runs.")
 
st.header("2c. Compare two inputs")
c1, c2, c3 = st.columns(3)
x_in = c1.selectbox("X axis (input)", inputs, key="sl_x")
by_in = c2.selectbox("One line per value of", [c for c in inputs if c != x_in],
                     key="sl_by")
out_in = c3.selectbox("Result", outputs, key="sl_out")
show_runs = st.checkbox("Show every run instead of averages", key="sl_runs")
 
if show_runs:
    pdat = df.assign(**{by_in: df[by_in].astype(str)})
    fig_s = px.scatter(pdat, x=x_in, y=out_in, color=by_in, opacity=0.4,
                       hover_data=inputs)
    st.caption("Each dot is one run (filtered rows). Dots overlap because the inputs are a grid.")
else:
    g = df.groupby([x_in, by_in])[out_in].mean().reset_index()
    g[by_in] = g[by_in].astype(str)
    fig_s = px.line(g, x=x_in, y=out_in, color=by_in, markers=True)
    st.caption("Each point averages the other 7 inputs, over the filtered rows.")
fig_s.update_layout(legend_title_text=by_in)
st.plotly_chart(fig_s, use_container_width=True)
 
# 3. Findings
st.header("3. Main findings")
rows = {}
for i in inputs:
    m = df.groupby(i)[outputs].mean()
    rows[i] = (m.max() - m.min()) / df[outputs].std()
eff = pd.DataFrame(rows).T.round(2)
eff = eff.loc[eff.sum(axis=1).sort_values(ascending=False).index]
st.dataframe(eff)
st.write("Effect size = spread of group averages ÷ output std. Bigger = stronger. "
         "`ecc` is first and `N` is second. The effect of Dbot, H1 and H2 depends on the output.")
# 4. Outliers
st.header("4. Outliers")
st.write("Outliers were flagged, not removed. Pick a method to see its rows.")
counts = df[flag_cols].astype(bool).sum()
fig2 = px.bar(x=counts.index, y=counts.values,
              labels={"x": "Method", "y": "Rows flagged"},
              title="Rows flagged by each method")
st.plotly_chart(fig2, use_container_width=True)

flag = st.selectbox("Show the rows flagged by:", flag_cols)
flagged = df[df[flag].astype(bool)]
st.write(f"{len(flagged)} rows flagged by **{flag}**.")
if len(flagged) > 0:
    st.write("Where they sit (ecc, N, Dbot):")
    st.dataframe(flagged[["ecc", "N", "Dbot"]].value_counts().reset_index(name="rows"))
    st.dataframe(flagged[inputs + outputs])

# 5. Multivariate
st.header("5. Multivariate view")
pair = BASE / "figures" / "C_pairplot.png"
if pair.exists():
    st.image(str(pair), caption="Pairplot, coloured by ecc")

@st.cache_data
def run_pca(frame):
    X = StandardScaler().fit_transform(frame)
    model = PCA(n_components=2)
    return model.fit_transform(X), model.explained_variance_ratio_
 
 
pcs, ratio = run_pca(df[outputs])
st.write(f"PCA: the first component explains {ratio[0]:.1%} "
         f"of the variation, and the first two explain {ratio.sum():.1%}.")
colour_by = st.selectbox("Colour the PCA chart by:", ["ecc", "N", "Dbot"])
 
pc_df = pd.DataFrame({"PC1": pcs[:, 0], "PC2": pcs[:, 1]})
for c in inputs:
    pc_df[c] = df[c].values
fig3 = px.scatter(pc_df, x="PC1", y="PC2", color=colour_by,
                  hover_data=inputs, opacity=0.7,
                  color_continuous_scale="Viridis")
st.plotly_chart(fig3, use_container_width=True)
# 6. B's charts
st.header("6. Charts from the analysis")
for name in ["dist_outputs.png", "box_by_ecc.png",
             "corr_heatmap.png", "sensitivity_heatmap.png"]:
    path = BASE / "figures" / name
    if path.exists():
        st.image(str(path), caption=name)
#checks
st.header("Checks")
z = df[df.ecc == 0]
st.write(f"At ecc = 0, tension and compression match: max difference "
         f"{(z.Mr_t - z.Mr_c).abs().max():.1e}.")
st.write("`M_ov = N × ecc` correlates with the outputs better than `ecc` or `N` alone:")
st.dataframe(df[["ecc","N","M_ov"] + outputs]
             .corr(method="spearman").loc[["ecc","N","M_ov"], outputs].round(2))
st.write("Clustering found no clear groups (silhouette 0.27–0.36).")
# 7. Mentor
st.header("7. Rows for the mentor to check")
st.write("Rows 4377 and 4381 may be simulation errors. They are kept in "
         "the data, flagged, until the mentor confirms.")
suspects = load()
st.dataframe(suspects[suspects["suspect_row"].astype(bool)])
st.header("8. Hand calc vs FEM")
st.write("Can a simple formula predict the FEM moments? Two hand-calc models are "
         "fitted on the rows with ecc > 0.")
st.markdown(
    "- **A:** `moment = k × N × ecc` (one constant k per result)\n"
    "- **B:** `moment = c × N^a × ecc^b × Dbot^d` (fitted in log space)"
)
 
z = df[df["ecc"] > 0]
h = z["N"] * z["ecc"]
 
 
def fit_models(o):
    """Return FEM values and the predictions of models A and B for result o."""
    y = z[o]
    sign = np.sign(y.median())
    k = (y * h).sum() / (h * h).sum()
    pred_a = k * h
    ok = (y * sign) > 0  # model B needs a consistent sign (log of magnitude)
    X = np.column_stack([np.ones(ok.sum()), np.log(z.loc[ok, "N"]),
                         np.log(z.loc[ok, "ecc"]), np.log(z.loc[ok, "Dbot"])])
    coef = np.linalg.lstsq(X, np.log((y * sign)[ok]), rcond=None)[0]
    pred_b = pd.Series(sign * np.exp(X @ coef), index=y.index[ok])
    return y, pred_a, pred_b, k, coef
 
 
def metrics(y, p):
    y = y.loc[p.index]
    err = (y - p).abs() / y.abs()
    r2 = 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return {"R²": round(r2, 3), "Median error": round(err.median(), 3),
            "Within 10%": round((err < 0.10).mean(), 3),
            "Within 20%": round((err < 0.20).mean(), 3)}
 
 
fits = {o: fit_models(o) for o in outputs}
table = []
for o in outputs:
    y, pa, pb, k, coef = fits[o]
    table.append({"Result": o, "Model": "A", **metrics(y, pa)})
    table.append({"Result": o, "Model": "B", **metrics(y, pb)})
st.dataframe(pd.DataFrame(table))
 
st.write("Fitted constants:")
st.dataframe(pd.DataFrame(
    {o: {"k (model A)": fits[o][3], "c (B)": np.exp(fits[o][4][0]),
         "a, power of N": fits[o][4][1], "b, power of ecc": fits[o][4][2],
         "d, power of Dbot": fits[o][4][3]} for o in outputs}
).T)
 
res = st.selectbox("Result to inspect:", outputs, key="hc_result")
model = st.radio("Model:", ["A", "B"], horizontal=True, key="hc_model")
y, pa, pb, _, _ = fits[res]
pred = pa if model == "A" else pb
yy = y.loc[pred.index]
 
fig4, ax4 = plt.subplots(figsize=(5.5, 5.5))
ax4.scatter(yy.abs(), pred.abs(), s=6, alpha=0.4)
lim = max(yy.abs().max(), pred.abs().max()) * 1.05
ax4.plot([0, lim], [0, lim], "--", color="tab:orange", label="perfect match")
ax4.set_xlabel("FEM moment (magnitude)")
ax4.set_ylabel("Hand-calc moment (magnitude)")
ax4.set_title(f"{res}, model {model}")
ax4.legend()
st.pyplot(fig4)
plt.close(fig4)
 
err = ((yy - pred).abs() / yy.abs()).rename("error")
by_ecc = err.groupby(z.loc[pred.index, "ecc"]).median()
fig5, ax5 = plt.subplots(figsize=(7, 3.5))
by_ecc.plot(kind="bar", ax=ax5)
ax5.set_ylabel("Median error")
ax5.set_xlabel("ecc")
ax5.set_title(f"Hand-calc error by ecc: {res}, model {model}")
st.pyplot(fig5)
plt.close(fig5)
 
st.subheader("Conclusion")
st.markdown(
    "- Model B is the better hand calc. It reaches about 6–8% median error on all four results.\n"
    "- Model A is good for compression (Mr_c, Mt_c) but weaker for tension, "
    "especially Mr_t.\n"
    "- Mt_t and Mt_c have larger error at ecc = 10 than at ecc 18 and 26, "
    "so one constant k does not hold across ecc.\n"
    "- Contact-stress formulas do not fit. They scale as 1/D³ but FEM moments "
    "barely change with Dbot. They also need a vertical load that the data does not have.\n"
    "- Units of N, ecc and the moments are unknown (Kaggle data, no model files). "
    
)
 