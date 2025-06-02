
import streamlit as st
from utils import process_files
import tempfile

st.title("TikTok Tracking & Tagging Tool")

tiktok_file = st.file_uploader("Upload TikTok Ads Export File", type=["xlsx"])
dcm_files = st.file_uploader("Upload one or more DCM Tag Files", type=["xls", "xlsx"], accept_multiple_files=True)

if tiktok_file and dcm_files:
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(tiktok_file.read())
            tiktok_file_path = tmp_file.name
        output_file = process_files(tiktok_file_path, dcm_files)
        with open(output_file, "rb") as f:
            st.download_button("📥 Download Updated TikTok File", f, file_name="Updated_TikTok_File.xlsx")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the files.\n\n{e}")
