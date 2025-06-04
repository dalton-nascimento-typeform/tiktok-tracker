import pandas as pd
import io
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, parse_qsl

def clean_url(url):
    return url.strip().replace(' ', '%20').replace('"', '').replace("'", '')

def update_url_params(url, campaign_name):
    if not isinstance(url, str) or not url:
        return url

    url = clean_url(url)

    parsed_url = urlparse(url)
    query = dict(parse_qsl(parsed_url.query))

    # UTM defaults
    if 'utm_source' not in query:
        query['utm_source'] = 'tiktok'
    if 'utm_medium' not in query:
        query['utm_medium'] = 'paid'
    if 'utm_campaign' not in query:
        query['utm_campaign'] = campaign_name

    # TF defaults
    if 'tf_source' not in query:
        query['tf_source'] = 'tiktok'
    if 'tf_medium' not in query:
        query['tf_medium'] = 'paid_social'
    if 'tf_campaign' not in query:
        query['tf_campaign'] = campaign_name

    new_query = urlencode(query)
    updated_url = urlunparse(parsed_url._replace(query=new_query))
    return updated_url

def extract_impression_tag(raw_string):
    if not isinstance(raw_string, str):
        return ''
    match = re.search(r'"(https://[^"]+)"', raw_string)
    return match.group(1).strip() if match else ''

def match_rows(tiktok_row, tag_df):
    campaign = str(tiktok_row.get('Campaign Name', '')).strip()
    ad_group = str(tiktok_row.get('Ad Group Name', '')).strip()
    ad_name = str(tiktok_row.get('Ad Name', '')).strip()

    for _, tag_row in tag_df.iterrows():
        if (
            str(tag_row.get('Campaign Name', '')).strip() == campaign and
            str(tag_row.get('Placement Name', '')).strip() == ad_group and
            str(tag_row.get('Ad Name', '')).strip() == ad_name
        ):
            return tag_row
    return None

def process_files(tiktok_file, tag_files):
    # Read TikTok Ads file (normal header)
    tiktok_df = pd.read_excel(tiktok_file, sheet_name='Ads')
    required_cols = ['Campaign Name', 'Ad Group Name', 'Ad Name']
    for col in required_cols:
        if col not in tiktok_df.columns:
            raise ValueError(f"Missing required column '{col}' in TikTok Ads sheet")

    # Read tag files (headers in row 11 → header=10)
    tag_dfs = []
    for f in tag_files:
        try:
            df = pd.read_excel(f, header=10)
            if 'Campaign Name' in df.columns:
                tag_dfs.append(df)
        except Exception as e:
            raise ValueError(f"Error reading tag file {f.name}: {e}")
    if not tag_dfs:
        raise ValueError("No valid tag data found. Make sure the sheets include 'Campaign Name'.")
    tags_df = pd.concat(tag_dfs, ignore_index=True)

    # Process each row in TikTok Ads
    if 'Impression tracking URL' not in tiktok_df.columns:
        tiktok_df['Impression tracking URL'] = ''

    for idx, row in tiktok_df.iterrows():
        tag_row = match_rows(row, tags_df)
        campaign = str(row['Campaign Name']).strip()
        url = row['Click URL']

        # Always ensure default parameters are added
        updated_url = update_url_params(url, campaign)

        if tag_row is not None:
            click_tag = tag_row.get('Click Tracker', '')
            impression_tag = extract_impression_tag(tag_row.get('Impression Tracker', ''))

            if click_tag:
                updated_url = click_tag + updated_url
            if impression_tag:
                tiktok_df.at[idx, 'Impression tracking URL'] = impression_tag

        tiktok_df.at[idx, 'Click URL'] = updated_url

    # Write final output
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        tiktok_df.to_excel(writer, index=False, sheet_name='Ads')
    output.seek(0)
    return output
