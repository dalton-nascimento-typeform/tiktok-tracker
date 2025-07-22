import pandas as pd
import io
import re
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

def extract_impression_url(s):
    if pd.isna(s):
        return ''
    match = re.search(r'"(https://[^"]+)"', s)
    return match.group(1) if match else ''

def ensure_params(url, campaign):
    if pd.isna(url):
        return ''
    parsed_url = urlparse(url)
    params = dict(parse_qsl(parsed_url.query))

    params['utm_source'] = 'tiktok'
    params['utm_medium'] = 'paid'
    params['utm_campaign'] = campaign  # Actual campaign name
    params['tf_source'] = 'tiktok'
    params['tf_medium'] = 'paid_social'
    params['tf_campaign'] = campaign   # Actual campaign name

    return urlunparse(parsed_url._replace(query=urlencode(params)))

def process_files(tiktok_file, tag_files):
    df_ads = pd.read_excel(tiktok_file, sheet_name='Ads')
    tag_dfs = [pd.read_excel(f, header=10) for f in tag_files]
    df_tags = pd.concat(tag_dfs, ignore_index=True)

    # Ensure columns exist
    for col in ['Click Tracking URL', 'Impression Tracking URL']:
        if col not in df_ads.columns:
            df_ads[col] = ''

    for idx, row in df_ads.iterrows():
        campaign = row['Campaign Name'].strip()
        ad_group = row['Ad Group Name'].strip()
        ad_name = row['Ad Name'].strip()

        matched_tag = df_tags[
            (df_tags['Campaign Name'].astype(str).str.strip() == campaign) &
            (df_tags['Placement Name'].astype(str).str.strip() == ad_group) &
            (df_tags['Ad Name'].astype(str).str.strip() == ad_name)
        ]

        # Update Web URL (UTM/TF)
        original_url = row['Web URL']
        updated_url = ensure_params(original_url, campaign)
        df_ads.at[idx, 'Web URL'] = updated_url

        if not matched_tag.empty:
            matched_row = matched_tag.iloc[0]

            # Click Tracking URL
            click_tag = matched_row.get('Click Tag') or matched_row.get('Click Tracker')
            if pd.notna(click_tag):
                df_ads.at[idx, 'Click Tracking URL'] = click_tag.strip()

            # Impression Tracking URL
            impression_tag = matched_row.get('Impression Tag') or matched_row.get('Impression Tracker')
            impression_url = extract_impression_url(impression_tag)
            df_ads.at[idx, 'Impression Tracking URL'] = impression_url.strip()

    # Save to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ads.to_excel(writer, index=False, sheet_name='Ads')
    output.seek(0)
    return output
