import streamlit as st
import json
import os

st.set_page_config(page_title="JSON Cleaner", page_icon="🧹")

st.title("🧹 JSON Cleaner")

# --- Mode configuration -----------------------------------------------------
# Each mode defines which root component to look for in the story.
# All _uid values nested inside that component are collected recursively.
MODES = {
    "SEO": ["seo_config"],
    "Summary": ["summary"],
}

# Metadata keys that are always kept as-is (they carry no uuid)
keep_exact = ["page", "language", "url", "text_nodes"]


def find_components(node, target):
    """Return every dict in the tree whose 'component' field == target."""
    results = []
    if isinstance(node, dict):
        if node.get("component") == target:
            results.append(node)
        for value in node.values():
            results.extend(find_components(value, target))
    elif isinstance(node, list):
        for item in node:
            results.extend(find_components(item, target))
    return results


def collect_uuids(node):
    """Recursively collect all '_uid' values within a subtree."""
    uuids = set()
    if isinstance(node, dict):
        uid = node.get("_uid")
        if isinstance(uid, str):
            uuids.add(uid)
        for value in node.values():
            uuids |= collect_uuids(value)
    elif isinstance(node, list):
        for item in node:
            uuids |= collect_uuids(item)
    return uuids


def uuids_for_modes(story_data, target_components):
    """For each target component, gather the uuids of all its instances."""
    keep = set()
    for target in target_components:
        for comp in find_components(story_data, target):
            keep |= collect_uuids(comp)
    return keep


def key_uuid(key):
    """The uuid is the prefix before the first ':' -> '<uuid>:<component>:<field>'."""
    return key.split(":", 1)[0]


mode = st.radio("Select keys to keep:", options=list(MODES.keys()), index=0)

col1, col2 = st.columns(2)
with col1:
    translations_file = st.file_uploader("1. Translations JSON", type="json", key="translations")
with col2:
    story_file = st.file_uploader("2. Story Draft JSON (Storyblok)", type="json", key="story")

if translations_file is not None and story_file is not None:
    original_name = os.path.splitext(translations_file.name)[0]
    new_filename = f"{original_name}_to_translate.json"

    try:
        translations = json.load(translations_file)
        story = json.load(story_file)

        target_components = MODES[mode]
        keep_uuids = uuids_for_modes(story, target_components)

        if not keep_uuids:
            st.warning(
                f"No {target_components} component found in the story. "
                "Make sure you uploaded the correct JSON."
            )

        cleaned_data = {}
        for key, value in translations.items():
            if key in keep_exact:
                cleaned_data[key] = value
            elif key_uuid(key) in keep_uuids:
                cleaned_data[key] = value

        final_json = json.dumps(cleaned_data, indent=4, ensure_ascii=False)

        st.success(
            f"Filtered! Kept {len(cleaned_data)} keys "
            f"using {len(keep_uuids)} uuid(s) from component(s) {target_components}."
        )

        st.download_button(
            label="📥 Download Cleaned JSON",
            data=final_json.encode("utf-8"),
            file_name=new_filename,
            mime="application/json",
        )

        with st.expander(f"UUIDs to keep ({len(keep_uuids)})"):
            st.code("\n".join(sorted(keep_uuids)) or "(none)", language="text")

        with st.expander("Preview Cleaned Data", expanded=True):
            st.code(final_json, language="json")

    except Exception as e:
        st.error(f"Error parsing JSON: {e}")
