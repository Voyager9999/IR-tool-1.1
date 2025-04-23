
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from core.spectrum_analyzer import SmartPeakDetector

st.title("📈 Spectrum Viewer")

uploaded_file = st.file_uploader("Upload IR Spectrum CSV", type="csv")
show_peaks = st.checkbox("Show detected peaks", value=True)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if "x" in df.columns and "y" in df.columns:
        df.to_csv("data/uploaded.csv", index=False)
        x, y = df["x"].values, df["y"].values
        detector = SmartPeakDetector(sensitivity=0.7)
        peaks = detector.find_peaks(x, y)
        fig, ax = plt.subplots()
        ax.plot(x, y, label="IR Spectrum")
        if show_peaks:
            for p in peaks:
                ax.axvline(x=p["position"], color="r", linestyle="--", alpha=0.6)
                ax.text(p["position"], p["intensity"], f'{int(p["position"])}', color="blue", fontsize=8)
        ax.invert_xaxis()
        ax.set_xlabel("Wavenumber (cm⁻¹)")
        ax.set_ylabel("Absorbance")
        st.pyplot(fig)
    else:
        st.error("CSV must contain 'x' and 'y' columns.")
