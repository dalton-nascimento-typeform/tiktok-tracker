
import streamlit as st
import pandas as pd
from utils import process_files

st.title("📊 TikTok Export Ads Tracker")

st.markdown("""
Upload the TikTok Export Ads file and one or more DCM Tag files.
The tool will merge and update tracking URLs, click tags, and impression tags automatically.
""")

# File uploaders
tiktok_file = st.file_uploader("Upload TikTok Export Ads file", type=["xlsx"])
dcm_files = st.file_uploader("Upload one or more DCM Tag files", type=["xlsx"], accept_multiple_files=True)

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ Processing complete. Download the updated file below.")
        st.download_button("📥 Download Updated File", data=output_file.getvalue(), file_name="Updated_ExportAds.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files: {e}")
