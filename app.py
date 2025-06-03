import streamlit as st
from utils import process_files

st.title("📦 TikTok UTM & Tracking Tag Updater")

tiktok_file = st.file_uploader("Upload TikTok ExportAds file", type=["xlsx"], key="tiktok")
dcm_files = st.file_uploader("Upload one or more DCM Tag files", type=["xlsx"], accept_multiple_files=True, key="dcm")

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ File processed successfully. Click below to download.")
        st.download_button("📥 Download Updated File", output_file.getvalue(), file_name="Updated_TikTok_Ads.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files.\n\n{e}")