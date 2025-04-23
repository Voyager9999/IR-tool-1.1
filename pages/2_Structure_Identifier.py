
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import os

st.title("🔬 Structure Identifier")

# 初始化 memory 数据
if "peaks" not in st.session_state:
    if os.path.exists("data/memory.json"):
        with open("data/memory.json") as f:
            st.session_state["peaks"] = json.load(f)
    else:
        st.session_state["peaks"] = []

try:
    df = pd.read_csv("data/uploaded.csv")
    x, y = df["x"].values, df["y"].values
except:
    st.error("Please upload spectrum from Page 1 first.")
    st.stop()

with open("data/rules.json") as f:
    rules = json.load(f)

picked = st.slider("Select Peak (cm⁻¹)", 400, 4100, int(x[len(x)//2]))

if st.button("➕ Confirm Peak"):
    if not any(abs(m["peak"] - picked) < 1 for m in st.session_state["peaks"]):
        matches = []
        for name, info in rules.items():
            for lo, hi in info["ranges"]:
                if lo <= picked <= hi:
                    matches.append(f"{name} ({info['description']})")
        st.session_state["peaks"].append({"peak": picked, "match": matches or ["Unassigned"]})
        st.session_state["peaks"] = sorted(st.session_state["peaks"], key=lambda p: p["peak"])
        with open("data/memory.json", "w") as f:
            json.dump(st.session_state["peaks"], f)

st.subheader("📊 Spectrum + Confirmed Peaks")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="IR Spectrum"))
if st.session_state["peaks"]:
    pxs = [m["peak"] for m in st.session_state["peaks"]]
    pys = [y[(abs(x - p)).argmin()] for p in pxs]
    fig.add_trace(go.Scatter(x=pxs, y=pys, mode="markers+text",
                             marker=dict(color="red", size=8),
                             text=[str(int(p)) for p in pxs],
                             name="Confirmed Peaks"))

# 实时垂直线提示
fig.add_vline(x=picked, line_color="green", line_dash="dash", annotation_text="Selected", annotation_position="top")

fig.update_layout(xaxis_title="Wavenumber (cm⁻¹)", yaxis_title="Absorbance", xaxis=dict(autorange="reversed"))
st.plotly_chart(fig)

if st.session_state["peaks"]:
    st.dataframe(pd.DataFrame(st.session_state["peaks"]))
    idx = st.number_input("Delete index", 0, len(st.session_state["peaks"])-1)
    if st.button("❌ Delete"):
        st.session_state["peaks"].pop(idx)
        with open("data/memory.json", "w") as f:
            json.dump(st.session_state["peaks"], f)
    if st.button("🧹 Clear All"):
        st.session_state["peaks"] = []
        with open("data/memory.json", "w") as f:
            json.dump([], f)
