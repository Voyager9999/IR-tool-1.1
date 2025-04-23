
import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.title("🔬 Structure Identifier")

try:
    df = pd.read_csv("data/uploaded.csv")
    x, y = df["x"].values, df["y"].values
except:
    st.error("Please upload spectrum from Page 1 first.")
    st.stop()

with open("data/memory.json") as f:
    memory = json.load(f)
with open("data/rules.json") as f:
    rules = json.load(f)

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

if memory:
    st.dataframe(pd.DataFrame(memory))
    peaks_x = [m["peak"] for m in memory]
    fig = px.line(x=x, y=y)
    fig.add_scatter(x=peaks_x, y=[y[x.tolist().index(int(p))] if int(p) in x else 1 for p in peaks_x],
                    mode="markers+text", text=[str(int(p)) for p in peaks_x], marker=dict(color="red"))
    fig.update_layout(xaxis_title="Wavenumber", yaxis_title="Absorbance")
    fig.update_layout(xaxis=dict(autorange="reversed"))
    st.plotly_chart(fig)

idx = st.number_input("Delete index", 0, len(memory)-1) if memory else 0
if st.button("❌ Delete") and memory:
    memory.pop(idx)
    with open("data/memory.json", "w") as f:
        json.dump(memory, f)
    st.experimental_rerun()

if st.button("🧹 Clear All"):
    with open("data/memory.json", "w") as f:
        json.dump([], f)
    st.experimental_rerun()
