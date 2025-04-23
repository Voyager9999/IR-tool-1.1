
import streamlit as st
import fitz
import pandas as pd
import re
import json

st.title("📄 Literature Peak Extractor")

with open("data/rules.json") as f:
    rules = json.load(f)

upload = st.file_uploader("Upload PDF", type="pdf")
if upload:
    doc = fitz.open(stream=upload.read(), filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    peaks = re.findall(r"\b(\d{3,4})\b", text)
    result = []
    for p in peaks:
        num = int(p)
        match = []
        for name, info in rules.items():
            for lo, hi in info["ranges"]:
                if lo <= num <= hi:
                    match.append(f"{name} ({info['description']})")
        result.append({"peak": num, "match": match or ["Unassigned"]})
    st.dataframe(pd.DataFrame(result))

name = st.text_input("Group Name")
low = st.number_input("From", 400, 4000)
high = st.number_input("To", 400, 4100)
desc = st.text_input("Description")

if st.button("Add Rule"):
    if name and high > low:
        if name not in rules:
            rules[name] = {"ranges": [], "description": desc}
        rules[name]["ranges"].append([low, high])
        with open("data/rules.json", "w") as f:
            json.dump(rules, f)
        st.success("Added.")
        st.experimental_rerun()

if st.button("🧹 Clear All Rules"):
    with open("data/rules.json", "w") as f:
        json.dump({}, f)
    st.experimental_rerun()
