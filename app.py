
import streamlit as st
import pandas as pd
from utils import process_files

st.set_page_config(page_title="TikTok Tracker", layout="centered")
st.title("📊 TikTok Ad Tracker Tagger")

tiktok_file = st.file_uploader("Upload TikTok Export File (.xls or .xlsx)", type=["xls", "xlsx"])
dcm_files = st.file_uploader("Upload One or More DCM Tag Files", type=["xls", "xlsx"], accept_multiple_files=True)

if tiktok_file and dcm_files:
    output_file = process_files(tiktok_file, dcm_files)
    st.success("✅ File processed successfully!")
    st.download_button("⬇️ Download Updated File", output_file.read(), file_name="updated_tiktok_ads.xlsx")
