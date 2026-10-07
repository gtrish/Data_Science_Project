import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

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

st.title("How input settings affect FEM simulation results")
st.write("Each row is one simulation run. We change 9 input settings "
         "and record 4 results (bending moments).")

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
fig, ax = plt.subplots(figsize=(7, 4))
df.groupby(choice)[outputs].mean().plot(marker="o", ax=ax)
ax.set_ylabel("Average moment")
ax.set_title(f"Average result vs {choice}")
st.pyplot(fig)

# 3. Findings
st.header("3. Main findings")
st.write("- **ecc** (load off-center) has the biggest effect.")
st.write("- **N** (load size) is second.")
st.write("- **Dbot** has a small effect.")
st.write("- **Econc**, **gammaG** and **Esoil** have almost no effect.")

# 4. Outliers
st.header("4. Outliers")
st.write("Outliers were flagged, not removed. Pick a method to see its rows.")
counts = df[flag_cols].astype(bool).sum()
fig2, ax2 = plt.subplots(figsize=(7, 3.5))
counts.plot(kind="bar", ax=ax2)
ax2.set_ylabel("Rows flagged")
ax2.set_title("Rows flagged by each method")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
st.pyplot(fig2)

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

X = StandardScaler().fit_transform(df[outputs])
pca = PCA(n_components=2)
pcs = pca.fit_transform(X)
st.write(f"PCA: the first component explains {pca.explained_variance_ratio_[0]:.1%} "
         f"of the variation, and the first two explain "
         f"{pca.explained_variance_ratio_.sum():.1%}.")
colour_by = st.selectbox("Colour the PCA chart by:", ["ecc", "N", "Dbot"])
fig3, ax3 = plt.subplots(figsize=(7, 4))
sc = ax3.scatter(pcs[:, 0], pcs[:, 1], c=df[colour_by], cmap="viridis", s=8)
fig3.colorbar(sc, label=colour_by)
ax3.set_xlabel("PC1")
ax3.set_ylabel("PC2")
st.pyplot(fig3)

# 6. B's charts
st.header("6. Charts from the analysis")
for name in ["dist_outputs.png", "box_by_ecc.png",
             "corr_heatmap.png", "sensitivity_heatmap.png"]:
    path = BASE / "figures" / name
    if path.exists():
        st.image(str(path), caption=name)

# 7. Mentor
st.header("7. Rows for the mentor to check")
st.write("Rows 4377 and 4381 may be simulation errors. They are kept in "
         "the data, flagged, until the mentor confirms.")
suspects = load()
st.dataframe(suspects[suspects["suspect_row"].astype(bool)])