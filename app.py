
import streamlit as st
from utils import process_files

st.title("TikTok Tracking Updater")

tiktok_file = st.file_uploader("Upload TikTok Export File", type=["xlsx"])
dcm_files = st.file_uploader("Upload Tag Files (one or more)", type=["xls", "xlsx"], accept_multiple_files=True)

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ Processing complete. Download your updated file below:")
        st.download_button(
            label="📥 Download Updated File",
            data=output_file.getvalue(),
            file_name="Updated_TikTok_File.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files.\n\n{e}")
