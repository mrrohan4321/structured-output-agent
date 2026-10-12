import json

import streamlit as st

from agent import extract

st.set_page_config(page_title="Structured Output Agent", page_icon="🧾")
st.title("Structured Output Agent")
st.caption("Unstructured text theke validated JSON ber kore.")

SAMPLE = (
    "Hi, I'm Rahul Das. I'm 21 years old.\n"
    "I know Python, SQL, and machine learning.\n"
    "My email is rahul@example.com."
)

text = st.text_area("Text paste kor", value=SAMPLE, height=180)

if st.button("Extract Information", type="primary"):
    with st.spinner("Extracting..."):
        result = extract(text)

    if result.ok:
        st.success(f"Valid output (attempts: {result.attempts})")
        st.json(result.data)
        st.download_button(
            "Download JSON",
            json.dumps(result.data, indent=2),
            file_name="output.json",
            mime="application/json",
        )
    else:
        st.error("Extraction failed.")
        for e in result.errors:
            st.write(f"- {e}")