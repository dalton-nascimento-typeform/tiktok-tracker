import pandas as pd
import io
import re
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

def extract_impression_url(s):
    if not isinstance(s, str):
        return ''
    m = re.search(r'"(https://[^"]+)"', s)
    return m.group(1) if m else ''

def ensure_params(url, campaign):
    if not isinstance(url, str):
        return url
    parsed = urlparse(url)
    params = dict(parse_qsl(parsed.query))
    params.setdefault('utm_source', 'tiktok')
    params.setdefault('utm_medium', 'paid')
    params.setdefault('utm_campaign', campaign)
    params.setdefault('tf_source', 'tiktok')
    params.setdefault('tf_medium', 'paid_social')
    params.setdefault('tf_campaign', campaign)
    new_query = urlencode(params)
    return urlunparse(parsed._replace(query=new_query))

def process_files(tiktok_file, tag_files):
    df_ads = pd.read_excel(tiktok_file, sheet_name='Ads')
    tag_dfs = [pd.read_excel(f, header=10) for f in tag_files]
    df_tags = pd.concat(tag_dfs, ignore_index=True)

    for idx, row in df_ads.iterrows():
        campaign = str(row['Campaign Name']).strip()
        adgroup = str(row['Ad Group Name']).strip()
        adname = str(row['Ad Name']).strip()

        tag_match = df_tags[
            (df_tags['Campaign Name'].astype(str).str.strip() == campaign) &
            (df_tags['Placement Name'].astype(str).str.strip() == adgroup) &
            (df_tags['Ad Name'].astype(str).str.strip() == adname)
        ]

        # Web URL: always ensure params
        web_url = row['Web URL']
        df_ads.at[idx, 'Web URL'] = ensure_params(web_url, campaign)

        # Click Tracking URL: only if match
        if not tag_match.empty:
            click_tracker = tag_match.iloc[0].get('Click Tag') or tag_match.iloc[0].get('Click Tracker', '')
            if pd.notna(click_tracker):
                df_ads.at[idx, 'Click Tracking URL'] = click_tracker

            # Impression Tracking URL: only if match
            imp_tag = tag_match.iloc[0].get('Impression Tag') or tag_match.iloc[0].get('Impression Tracker', '')
            if pd.notna(imp_tag):
                df_ads.at[idx, 'Impression Tracking URL'] = extract_impression_url(str(imp_tag))

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ads.to_excel(writer, sheet_name='Ads', index=False)
    output.seek(0)
    return output
