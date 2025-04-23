
import streamlit as st
import fitz
import pandas as pd
import re
import json

st.title("📄 Literature Peak Extractor")

with open("data/rules.json") as f:
    rules = json.load(f)

upload = st.file_uploader("Upload PDF (with peaks)", type="pdf")
if upload:
    doc = fitz.open(stream=upload.read(), filetype="pdf")
    full_text = "".join(page.get_text() for page in doc)
    peak_nums = re.findall(r"\b(\d{3,4})\b", full_text)
    peak_nums = [int(p) for p in peak_nums]
    
    result = []
    for p in peak_nums:
        matched = []
        for name, info in rules.items():
            for lo, hi in info["ranges"]:
                if lo <= p <= hi:
                    matched.append(f"{name} ({info['description']})")
        result.append({"peak": p, "match": matched or ["Unassigned"]})

    if result:
        st.success(f"Found {len(result)} peaks in PDF.")
        st.dataframe(pd.DataFrame(result))
    else:
        st.warning("No peaks detected in the uploaded PDF.")

st.markdown("---")
st.subheader("🛠 Manage Peak Assignment Rules")

with open("data/rules.json") as f:
    rules = json.load(f)

st.markdown("### ➕ Add New Rule")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Group Name")
    desc = st.text_input("Description")
with col2:
    low = st.number_input("Start (cm⁻¹)", 400, 4100, step=1)
    high = st.number_input("End (cm⁻¹)", 400, 4100, step=1)

if st.button("Add Rule"):
    if name and high > low:
        if name not in rules:
            rules[name] = {"ranges": [], "description": desc}
        rules[name]["ranges"].append([low, high])
        with open("data/rules.json", "w") as f:
            json.dump(rules, f, indent=2)
        st.success(f"Rule '{name}' added.")
        st.experimental_rerun()

if st.button("🧹 Clear All Rules"):
    with open("data/rules.json", "w") as f:
        json.dump({}, f)
    st.success("All rules cleared.")
    st.experimental_rerun()

if rules:
    st.markdown("### 📋 Existing Rules")
    all_rules = []
    for name, info in rules.items():
        for rng in info["ranges"]:
            all_rules.append({"Group": name, "From": rng[0], "To": rng[1], "Description": info["description"]})
    st.dataframe(pd.DataFrame(all_rules))
