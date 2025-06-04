import pandas as pd
import zipfile
import io
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def clean_url(url):
    if pd.isna(url):
        return ''
    return str(url).strip()


def extract_impression_url(cell):
    if pd.isna(cell):
        return ''
    match = re.search(r'"(https?://[^"]+)"', str(cell))
    return match.group(1) if match else str(cell).strip()


def ensure_tracking_params(url, source='tiktok', medium='paid_social'):
    if not url:
        return url

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Append if not present
    if 'tf_source' not in query:
        query['tf_source'] = [source]
    if 'tf_medium' not in query:
        query['tf_medium'] = [medium]

    # Keep other existing params
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def match_rows(tiktok_row, tag_df):
    campaign = str(tiktok_row['Campaign Name']).strip()
    placement = str(tiktok_row['Placement Name']).strip()
    ad = str(tiktok_row['Ad Name']).strip()

    for _, tag_row in tag_df.iterrows():
        if (
            str(tag_row['Campaign Name']).strip() == campaign and
            str(tag_row['Ad Group Name']).strip() == placement and
            str(tag_row['Ad Name']).strip() == ad
        ):
            return tag_row
    return None


def process_files(tiktok_file, tag_files):
    # --- Load TikTok Ads file ---
    df_ads = pd.read_excel(tiktok_file, sheet_name='Ads')

    # Ensure required columns
    required_cols = ['Campaign Name', 'Placement Name', 'Ad Name']
    for col in required_cols:
        if col not in df_ads.columns:
            raise ValueError(f"Missing required column '{col}' in TikTok Ads sheet")

    # Create 'Click URL' if missing
    if 'Click URL' not in df_ads.columns:
        df_ads['Click URL'] = ''

    # Clean
    df_ads['Click URL'] = df_ads['Click URL'].astype(str).apply(clean_url)

    # Load and combine tag files
    tag_data = []
    for f in tag_files:
        xls = pd.ExcelFile(f)
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet, header=10)
            if 'Campaign Name' in df.columns:
                tag_data.append(df)

    if not tag_data:
        raise ValueError("No valid tag data found. Make sure the sheets include 'Campaign Name'.")

    tag_df = pd.concat(tag_data, ignore_index=True)

    # Match & Update rows
    updated_rows = []
    for idx, row in df_ads.iterrows():
        tag_row = match_rows(row, tag_df)

        if tag_row is not None:
            # Update Click URL
            click = tag_row.get('Click Tracker', '')
            click = clean_url(click)
            click = ensure_tracking_params(click)
            df_ads.at[idx, 'Click URL'] = click

            # Update Impression tracking
            impression = tag_row.get('Impression Tracker', '')
            impression = extract_impression_url(impression)
            df_ads.at[idx, 'Impression Tracking URL'] = impression

            # Set UTM and TF campaign fields
            campaign = str(tag_row['Campaign Name']).strip()
            df_ads.at[idx, 'utm_campaign'] = campaign
            df_ads.at[idx, 'tf_campaign'] = campaign

        else:
            # If no match, still make sure tf_ and utm_ params are applied
            click_url = ensure_tracking_params(row['Click URL'])
            df_ads.at[idx, 'Click URL'] = click_url

    # Save output
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ads.to_excel(writer, index=False, sheet_name='Ads')

    output.seek(0)

    # Zip it up
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("Updated_ExportAds.xlsx", output.read())

    zip_buffer.seek(0)
    return zip_buffer
