
import streamlit as st
import pandas as pd
import io
from utils import process_files

st.set_page_config(page_title="TikTok Tracking Tag Updater", layout="wide")
st.title("📊 TikTok Tracking Automation")

st.markdown("Upload your TikTok export file and one or more DCM tag sheets to automatically update tracking parameters.")

tiktok_file = st.file_uploader("Upload TikTok Export File (Excel)", type=["xls", "xlsx"])
dcm_files = st.file_uploader("Upload DCM Tag Files (Excel)", type=["xls", "xlsx"], accept_multiple_files=True)

if st.button("Process Files"):
    if not tiktok_file or not dcm_files:
        st.warning("Please upload both the TikTok export file and at least one DCM tag file.")
    else:
        try:
            output_file = process_files(tiktok_file, dcm_files)
            st.success("✅ File processed successfully!")
            st.download_button(
                label="📥 Download Updated File",
                data=output_file,
                file_name="Updated_TikTok_Tracking.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error("❌ An error occurred while processing the files.")
            st.exception(e)
