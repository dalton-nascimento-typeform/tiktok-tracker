import streamlit as st
from utils import process_files

st.set_page_config(page_title="TikTok Tag Updater", layout="centered")
st.title("📦 TikTok Bulk Tag Updater")

tiktok_file = st.file_uploader("Upload TikTok Export File", type=["xlsx"])
tag_files = st.file_uploader("Upload One or More Tag Files", type=["xlsx"], accept_multiple_files=True)

if tiktok_file and tag_files:
    if st.button("Run Tag Updater"):
        try:
            output = process_files(tiktok_file, tag_files)
            st.success("✅ Processing complete. Download the updated file below:")
            st.download_button("⬇️ Download Updated File", output, file_name="Updated_TikTok_Export.xlsx")
        except Exception as e:
            st.error(f"❌ An error occurred while processing the files: {e}")