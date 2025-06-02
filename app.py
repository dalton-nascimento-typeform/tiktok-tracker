import streamlit as st
import pandas as pd
from utils import process_files

st.title("TikTok Tracker Auto-Updater")

tiktok_file = st.file_uploader("Upload TikTok Export File", type=["xlsx", "xls"])
dcm_files = st.file_uploader("Upload One or More DCM Tag Files", type=["xlsx", "xls"], accept_multiple_files=True)

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ File processed successfully!")
        st.download_button(
            label="📥 Download Updated File",
            data=output_file,
            file_name="Updated_TikTok_Export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files.\n\n{e}")