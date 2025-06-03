import streamlit as st
from utils import process_files

st.set_page_config(page_title="TikTok Tracker Tool", layout="wide")
st.title("📊 TikTok Tracking Updater")

tiktok_file = st.file_uploader("Upload TikTok ExportAds file", type=["xlsx"])
dcm_files = st.file_uploader("Upload one or more DCM Tag files", type=["xlsx"], accept_multiple_files=True)

if st.button("Process Files") and tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ Processing complete! Download your updated file below.")
        st.download_button(
            label="📥 Download Updated TikTok File",
            data=output_file.getvalue(),
            file_name="Updated_TikTok_ExportAds.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files.

{e}")
