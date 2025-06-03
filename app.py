
import streamlit as st
import pandas as pd
from utils import process_files

st.set_page_config(page_title="TikTok Tracker Updater", layout="centered")

st.title("📊 TikTok Export Ads Tracker Updater")

tiktok_file = st.file_uploader("Upload TikTok Export Ads File", type=["xlsx"])
tag_files = st.file_uploader("Upload One or More Tag Files", type=["xlsx"], accept_multiple_files=True)

if tiktok_file and tag_files:
    try:
        output_file = process_files(tiktok_file, tag_files)
        st.success("✅ Processing complete. Download your updated file below.")
        st.download_button("⬇️ Download Updated File", data=output_file.read(), file_name="Updated_ExportAds.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files: {e}")
