import streamlit as st
import re
import json
import os

st.set_page_config(page_title="JSON SEO Cleaner", page_icon="🧹")

st.title("🧹 JSON Metadata Cleaner")
st.markdown("Filters for `seo_config`, `thing_schema_type`, and core metadata.")

# File Uploader
uploaded_file = st.file_uploader("Choose a JSON file", type="json")

if uploaded_file is not None:
    # 1. Determine the new filename
    original_name = os.path.splitext(uploaded_file.name)[0]
    new_filename = f"{original_name}_seo.json"

    # 2. Read and Process the file
    stringio = uploaded_file.getvalue().decode("utf-8")
    lines = stringio.splitlines()

    # The Regex pattern provided
    regex_pattern = r"^(?!\s*[{}\[\]])(?!.*(seo_config|thing_schema_type|page|language|url|text_nodes)).*"
    
    cleaned_lines = []
    for line in lines:
        if not re.match(regex_pattern, line):
            cleaned_lines.append(line)

    raw_cleaned_text = "\n".join(cleaned_lines)

    # 3. Clean up trailing commas and validate
    try:
        # Regex to fix trailing commas: finds a comma followed by whitespace and a closing brace/bracket
        fixed_text = re.sub(r',\s*([\]}])', r'\1', raw_cleaned_text)
        json_object = json.loads(fixed_text)
        final_json = json.dumps(json_object, indent=4)
        st.success(f"JSON processed successfully! New file: {new_filename}")
    except Exception:
        st.warning("Processed with regex, but standard JSON formatting couldn't be enforced. Check for trailing commas.")
        final_json = raw_cleaned_text

    # 4. Download Button (placed BEFORE the code output)
    st.download_button(
        label="📥 Download Cleaned JSON",
        data=final_json,
        file_name=new_filename,
        mime="application/json"
    )

    # 5. Preview
    with st.expander("Preview Cleaned Data", expanded=True):
        st.code(final_json, language="json")

else:
    st.info("Please upload a .json file to begin.")