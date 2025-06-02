import streamlit as st
import pandas as pd
from utils import process_files

st.set_page_config(page_title="TikTok Auto Tracker", layout="centered")
st.title("📊 TikTok Tracking URL & DCM Tag Updater")

st.markdown("Upload your TikTok export file and one or more DCM tag files.")

tiktok_file = st.file_uploader("Upload TikTok Export File", type=["xlsx"], key="tiktok")
dcm_files = st.file_uploader("Upload One or More DCM Tag Files", type=["xls", "xlsx"], accept_multiple_files=True, key="dcm")

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ Processing complete. Download your updated file below:")
        st.download_button("⬇️ Download Updated Excel", output_file.getvalue(), file_name="Updated_TikTok_File.xlsx")
    except Exception as e:
        st.error("❌ An error occurred while processing the files.")
        st.exception(e)