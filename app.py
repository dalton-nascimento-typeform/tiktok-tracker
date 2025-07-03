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
    query.setdefault('utm_source', 'tiktok')
    query.setdefault('utm_medium', 'paid')
    query.setdefault('utm_campaign', campaign_name)

    # TF defaults
    query.setdefault('tf_source', 'tiktok')
    query.setdefault('tf_medium', 'paid_social')
    query.setdefault('tf_campaign', campaign_name)

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
    # Read TikTok file
    tiktok_df = pd.read_excel(tiktok_file, sheet_name='Ads')
    required_cols = ['Campaign Name', 'Ad Group Name', 'Ad Name', 'Click URL']
    for col in required_cols:
        if col not in tiktok_df.columns:
            raise ValueError(f"Missing required column '{col}' in TikTok Ads sheet")

    # Read tag files (header in row 11)
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

    if 'Impression tracking URL' not in tiktok_df.columns:
        tiktok_df['Impression tracking URL'] = ''

    for idx, row in tiktok_df.iterrows():
        campaign = str(row['Campaign Name']).strip()
        original_url = row.get('Click URL', '')
        updated_url = update_url_params(original_url, campaign)

        tag_row = match_rows(row, tags_df)

        if tag_row is not None:
            click_tag = tag_row.get('Click Tracker', '')
            impression_tag = extract_impression_tag(tag_row.get('Impression Tracker', ''))

            if click_tag:
                updated_url = click_tag + updated_url
            if impression_tag:
                tiktok_df.at[idx, 'Impression tracking URL'] = impression_tag

        tiktok_df.at[idx, 'Click URL'] = updated_url

    # Save to memory buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        tiktok_df.to_excel(writer, sheet_name='Ads', index=False)
    output.seek(0)
    return output
