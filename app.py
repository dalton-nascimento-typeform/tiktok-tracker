
import streamlit as st
import pandas as pd
from utils import process_files

st.set_page_config(page_title="TikTok Tracker Updater")

st.title("📊 TikTok Tracking Tag Updater")
st.markdown("Upload your **Export Ads** file and one or more **Tag files**.")

tiktok_file = st.file_uploader("Upload Export Ads file", type=["xlsx"], key="export_ads")
dcm_files = st.file_uploader("Upload one or more Tag files", type=["xlsx"], accept_multiple_files=True, key="tag_files")

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ File processed successfully!")
        st.download_button("📥 Download Updated Export Ads File", output_file, file_name="Updated_ExportAds.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files: {e}")
