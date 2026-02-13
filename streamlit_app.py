import streamlit as st
import json
import os

st.set_page_config(page_title="JSON SEO Cleaner", page_icon="🧹")

st.title("🧹 JSON Metadata Cleaner")

uploaded_file = st.file_uploader("Choose a JSON file", type="json")

if uploaded_file is not None:
    original_name = os.path.splitext(uploaded_file.name)[0]
    new_filename = f"{original_name}_seo.json"

    # 1. Load the actual JSON data
    try:
        data = json.load(uploaded_file)
        
        # 2. Define our "Keep" rules
        keep_keywords = ["seo_config", "thing_schema_type"]
        keep_exact = ["page", "language", "url", "text_nodes"]

        # 3. Create a new dictionary with only the keys we want
        cleaned_data = {}
        for key, value in data.items():
            # Check if key is one of the exact metadata keys
            if key in keep_exact:
                cleaned_data[key] = value
            # OR check if one of the partial keywords is inside the key string
            elif any(word in key for word in keep_keywords):
                cleaned_data[key] = value

        final_json = json.dumps(cleaned_data, indent=4)
        
        # 4. Success UI
        st.success(f"Successfully filtered! Kept {len(cleaned_data)} keys.")

        # Download Button
        st.download_button(
            label="📥 Download Cleaned JSON",
            data=final_json,
            file_name=new_filename,
            mime="application/json"
        )

        with st.expander("Preview Cleaned Data", expanded=True):
            st.code(final_json, language="json")

    except Exception as e:
        st.error(f"Error parsing JSON: {e}")