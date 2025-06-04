
import streamlit as st
from utils import process_files

st.set_page_config(page_title="TikTok Tracker", layout="wide")
st.title("📦 TikTok Tracker Uploader")

tiktok_file = st.file_uploader("Upload TikTok Export Ads file (Excel)", type=["xlsx"])
tag_files = st.file_uploader("Upload one or more Tags files (Excel)", type=["xlsx"], accept_multiple_files=True)

if st.button("Process Files") and tiktok_file and tag_files:
    try:
        output_file = process_files(tiktok_file, tag_files)
        st.success("✅ Processing complete. Download the updated file below.")
        st.download_button(label="📥 Download Updated Excel", data=output_file, file_name="Updated_ExportAds.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files: {e}")
