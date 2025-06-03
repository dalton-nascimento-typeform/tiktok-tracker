import streamlit as st
from utils import process_files

st.title("TikTok Tracker Automation")

tiktok_file = st.file_uploader("Upload TikTok Export Ads File", type=["xlsx"])
dcm_files = st.file_uploader("Upload One or More Tag Files", type=["xlsx"], accept_multiple_files=True)

if tiktok_file and dcm_files:
    try:
        output_file = process_files(tiktok_file, dcm_files)
        st.success("✅ File processed successfully!")
        st.download_button(label="📥 Download Updated File", data=output_file, file_name="Updated_TikTok_Ads.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files: {e}")
