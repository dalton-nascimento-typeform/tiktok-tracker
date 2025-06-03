
import streamlit as st
from utils import process_files
import io

st.set_page_config(page_title="TikTok Tracking Updater", layout="centered")
st.title("📊 TikTok Tracking Auto-Updater")

tiktok_file = st.file_uploader("Upload the TikTok ExportAds file", type=["xlsx"])
dcm_files = st.file_uploader("Upload one or more tag files (DCM)", type=["xlsx"], accept_multiple_files=True)

if tiktok_file and dcm_files:
    try:
        st.markdown("### ✅ Ready to process files")
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ Files processed successfully!")
        st.download_button("📥 Download updated file", data=output_file.getvalue(), file_name="Updated_ExportAds.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files: {e}")
