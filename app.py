
import streamlit as st
from utils import process_files

st.title("📦 TikTok Tracker Auto-Updater")

tiktok_file = st.file_uploader("Upload TikTok ExportAds File", type=["xlsx"], key="tiktok")
dcm_files = st.file_uploader("Upload One or More Tag Files", type=["xlsx"], accept_multiple_files=True, key="dcm")

if st.button("Process Files"):
    if not tiktok_file or not dcm_files:
        st.error("Please upload both TikTok and Tag files.")
    else:
        try:
            output_file = process_files(tiktok_file, dcm_files)
            st.success("✅ Processing complete!")
            st.download_button("Download Updated File", data=output_file.getvalue(), file_name="Updated_TikTok_Export.xlsx")
        except Exception as e:
            st.error(f"❌ An error occurred while processing the files.\n\n{e}")
