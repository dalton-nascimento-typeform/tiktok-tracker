
import streamlit as st
from utils import process_files

st.set_page_config(page_title="TikTok Tracker Updater", layout="wide")

st.title("📊 TikTok Ad Tracker Automation")

st.markdown(
    "Upload your **TikTok Export** file and one or more **DCM Tag Sheets** "
    "to automatically update tracking URLs and export a clean file."
)

tiktok_file = st.file_uploader("Upload TikTok Export File (.xlsx)", type=["xlsx"], key="tiktok")
dcm_files = st.file_uploader("Upload One or More DCM Tag Files (.xlsx)", type=["xlsx"], accept_multiple_files=True, key="dcm")

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ Processing complete! Download the updated file below.")
        st.download_button("📥 Download Updated File", data=output_file, file_name="Updated_TikTok_Ads.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files.\n\n{e}")
