
import streamlit as st
import os

st.set_page_config(page_title="IR Spectrum Tool", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Spectrum Viewer", "Structure Identifier", "Literature Extractor"])

if page == "Spectrum Viewer":
    exec(open("pages/1_Spectrum_Viewer.py").read())
elif page == "Structure Identifier":
    exec(open("pages/2_Structure_Identifier.py").read())
elif page == "Literature Extractor":
    exec(open("pages/3_Literature_Peak_Extractor.py").read())
