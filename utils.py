import pandas as pd
import io
import zipfile
import re

def clean_url(url):
    return url.strip().replace('\u200b', '')

def extract_impression_url(cell_value):
    if pd.isna(cell_value):
        return None
    match = re.search(r'"(https?://[^"]+)"', str(cell_value))
    return match.group(1).strip() if match else None

def process_files(tiktok_file, tag_files):
    # Load TikTok Ads file
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    ads_sheet = df_main.get("Ads")
    if ads_sheet is None:
        raise ValueError("The TikTok file must contain a sheet named 'Ads'.")

    df_ads = ads_sheet.copy()

    # Check required columns
    required_tiktok_cols = ['Campaign Name', 'Ad Group Name', 'Ad Name', 'Click URL']
    for col in required_tiktok_cols:
        if col not in df_ads.columns:
            raise ValueError(f"Missing required column '{col}' in TikTok Ads sheet")

    # Load all tag files
    df_tags_list = []
    for tag_file in tag_files:
        df_tag_sheets = pd.read_excel(tag_file, sheet_name=None, header=10)  # Read from row 11
        for sheet_name, df in df_tag_sheets.items():
            if 'Campaign Name' in df.columns:
                df_tags_list.append(df)

    if not df_tags_list:
        raise ValueError("No valid tag data found. Make sure the sheets include 'Campaign Name'.")

    df_tags_all = pd.concat(df_tags_list, ignore_index=True)

    # Clean columns and data
    df_ads['Click URL'] = df_ads['Click URL'].astype(str).apply(clean_url)
    df_tags_all['Click Tracker'] = df_tags_all.get('Click Tracker', '').astype(str).apply(clean_url)
    df_tags_all['Impression Tracker'] = df_tags_all.get('Impression Tracker', '').astype(str)

    # Prepare a list to collect impression trackers
    impression_trackers = []

    # Update URLs and add click/impression tags
    updated_urls = []
    for idx, row in df_ads.iterrows():
        campaign = row['Campaign Name']
        adgroup = row['Ad Group Name']
        adname = row['Ad Name']
        click_url = row['Click URL']

        # Find matching tag row
        matched_tag = df_tags_all[
            (df_tags_all['Campaign Name'] == campaign) &
            (df_tags_all['Placement Name'] == adgroup) &
            (df_tags_all['Ad Name'] == adname)
        ]

        if not matched_tag.empty:
            tag_row = matched_tag.iloc[0]
            click_tracker = tag_row.get('Click Tracker', '').strip()
            imp_tracker = extract_impression_url(tag_row.get('Impression Tracker', ''))

            # Update URL
            updated_url = click_url
            if click_tracker:
                updated_url = f"{click_tracker}{click_url}"

            if '?utm_source=' not in updated_url:
                updated_url += f"?utm_source=tiktok&utm_medium=paid&utm_campaign={campaign}&tf_campaign={campaign}"
            if '&tf_source=' not in updated_url:
                updated_url += '&tf_source=tiktok'
            if '&tf_medium=' not in updated_url:
                updated_url += '&tf_medium=paid_social'

            df_ads.at[idx, 'Click URL'] = updated_url

            # Store impression tracker
            impression_trackers.append(imp_tracker or "")
        else:
            # No match found: still check for missing UTM/TF
            updated_url = click_url
            if '?utm_source=' not in updated_url:
                updated_url += f"?utm_source=tiktok&utm_medium=paid&utm_campaign={campaign}&tf_campaign={campaign}"
            if '&tf_source=' not in updated_url:
                updated_url += '&tf_source=tiktok'
            if '&tf_medium=' not in updated_url:
                updated_url += '&tf_medium=paid_social'
            df_ads.at[idx, 'Click URL'] = updated_url
            impression_trackers.append("")

    df_ads['Impression Tracker'] = impression_trackers

    # Save to Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ads.to_excel(writer, sheet_name="Ads", index=False)

    output.seek(0)
    return output
