
import streamlit as st
from utils import process_files

st.title("TikTok Tracker Tool")

tiktok_file = st.file_uploader("Upload TikTok Export Ads file", type=["xlsx"])
dcm_files = st.file_uploader("Upload Tag files", type=["xlsx"], accept_multiple_files=True)

if st.button("Process Files") and tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ File processed successfully!")
        st.download_button(
            label="Download Updated File",
            data=output_file.getvalue(),
            file_name="Updated_ExportAds.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files: {e}")
