
import streamlit as st
from utils import process_files

st.title("TikTok Tracking Auto-Updater")

st.markdown("Upload your TikTok export file and one or more DCM tag sheets to update tracking info automatically.")

tiktok_file = st.file_uploader("Upload TikTok export file", type=["xlsx"])
dcm_files = st.file_uploader("Upload one or more DCM tag files", type=["xlsx"], accept_multiple_files=True)

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ Files processed successfully. Download the updated file below:")
        st.download_button(
            label="📥 Download Updated Excel File",
            data=output_file,
            file_name="Updated_TikTok_Export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files.\n\n{e}")
