import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).parent
df = pd.read_csv(BASE / "data" / "processed" / "data_with_flags.csv")

inputs = ["ecc", "N", "gammaG", "Esoil", "Econc", "Dbot", "H1", "H2", "H3"]
outputs = ["Mr_t", "Mt_t", "Mr_c", "Mt_c"]

st.title("How input settings affect FEM simulation results")
st.write(
    "Each row is one simulation run. We change 9 input settings "
    "and record 4 results (bending moments)."
)

# Data overview
st.header("1. The data")
col1, col2, col3 = st.columns(3)
col1.metric("Rows", df.shape[0])
col2.metric("Inputs", len(inputs))
col3.metric("Results", len(outputs))
st.dataframe(df[inputs + outputs].head(10))

# Interactive effect chart
st.header("2. Effect of each input")
choice = st.selectbox("Pick an input to explore:", inputs)
fig, ax = plt.subplots(figsize=(7, 4))
df.groupby(choice)[outputs].mean().plot(marker="o", ax=ax)
ax.set_ylabel("Average moment")
ax.set_title(f"Average result vs {choice}")
st.pyplot(fig)

# Key findings
st.header("3. Main findings")
st.write("- **ecc** (load off-center) has the biggest effect.")
st.write("- **N** (load size) is second.")
st.write("- **Dbot** has a small effect.")
st.write("- **Econc**, **gammaG** and **Esoil** have almost no effect.")

# B's charts
st.header("4. Charts from the analysis")
for name in ["dist_outputs.png", "box_by_ecc.png",
             "corr_heatmap.png", "sensitivity_heatmap.png"]:
    path = BASE / "figures" / name
    if path.exists():
        st.image(str(path), caption=name)

# Suspect rows
st.header("5. Rows for the mentor to check")
if "suspect_row" in df.columns:
    st.dataframe(df[df["suspect_row"] == True])
else:
    st.write("Column suspect_row not found.")