
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go

st.title("🔬 Structure Identifier")

try:
    df = pd.read_csv("data/uploaded.csv")
    x, y = df["x"].values, df["y"].values
except:
    st.error("Please upload spectrum from Page 1 first.")
    st.stop()

with open("data/rules.json") as f:
    rules = json.load(f)
with open("data/memory.json") as f:
    memory = json.load(f)

picked = st.slider("Select Peak (cm⁻¹)", 400, 4100, int(x[len(x)//2]))

if st.button("➕ Confirm Peak"):
    if not any(abs(m["peak"] - picked) < 1 for m in memory):
        matches = []
        for name, info in rules.items():
            for lo, hi in info["ranges"]:
                if lo <= picked <= hi:
                    matches.append(f"{name} ({info['description']})")
        memory.append({"peak": picked, "match": matches or ["Unassigned"]})
        memory = sorted(memory, key=lambda p: p["peak"])
        with open("data/memory.json", "w") as f:
            json.dump(memory, f)
        st.experimental_rerun()

st.subheader("📊 Spectrum + Confirmed Peaks")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="IR Spectrum"))
if memory:
    peaks_x = [m["peak"] for m in memory]
    peaks_y = [y[(abs(x - p)).argmin()] for p in peaks_x]
    fig.add_trace(go.Scatter(x=peaks_x, y=peaks_y, mode="markers+text",
                             marker=dict(color="red", size=8),
                             text=[str(int(p)) for p in peaks_x],
                             name="Confirmed Peaks"))
fig.update_layout(xaxis_title="Wavenumber (cm⁻¹)", yaxis_title="Absorbance", xaxis=dict(autorange="reversed"))
st.plotly_chart(fig)

if memory:
    st.dataframe(pd.DataFrame(memory))
    idx = st.number_input("Delete index", 0, len(memory)-1)
    if st.button("❌ Delete"):
        memory.pop(idx)
        with open("data/memory.json", "w") as f:
            json.dump(memory, f)
        st.experimental_rerun()

if st.button("🧹 Clear All"):
    with open("data/memory.json", "w") as f:
        json.dump([], f)
    st.experimental_rerun()
