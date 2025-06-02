
import pandas as pd
import io
import re

REQUIRED_COLUMNS = ['Campaign Name', 'Placement Name', 'Ad Name', 'Impression Tag (image)', 'Click Tag']

def extract_url_from_img_tag(tag):
    match = re.search(r'<IMG SRC="([^"]+)"', str(tag))
    return match.group(1) if match else None

def process_files(tiktok_file, dcm_files):
    df_ads = pd.read_excel(tiktok_file, sheet_name=None)
    df_main = df_ads[list(df_ads.keys())[0]]

    df_tags_list = []
    for file in dcm_files:
        df = pd.read_excel(file)
        if set(REQUIRED_COLUMNS).issubset(set(df.columns)):
            df_tags_list.append(df)
    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame(columns=REQUIRED_COLUMNS)

    # Normalize columns for matching
    df_tags['Campaign Name'] = df_tags['Campaign Name'].astype(str).str.strip().str.lower()
    df_tags['Placement Name'] = df_tags['Placement Name'].astype(str).str.strip().str.lower()
    df_tags['Ad Name'] = df_tags['Ad Name'].astype(str).str.strip().str.lower()

    for i, row in df_main.iterrows():
        campaign = str(row['Campaign Name']).strip().lower()
        adgroup = str(row['Ad Group Name']).strip().lower()
        adname = str(row['Ad Name']).strip().lower()

        tag_row = df_tags[
            (df_tags['Campaign Name'] == campaign) &
            (df_tags['Placement Name'] == adgroup) &
            (df_tags['Ad Name'] == adname)
        ]

        if not tag_row.empty:
            df_main.at[i, 'Impression Tracking URL'] = extract_url_from_img_tag(tag_row.iloc[0].get('Impression Tag (image)', ''))
            df_main.at[i, 'Click Tracking URL'] = tag_row.iloc[0].get('Click Tag', '')

        url = str(row['Web URL'])
        has_utm = "utm_campaign=" in url and "tf_campaign=" in url
        if has_utm:
            url = re.sub(r'utm_campaign=[^&]+', f'utm_campaign={row["Campaign Name"]}', url)
            url = re.sub(r'tf_campaign=[^&]+', f'tf_campaign={row["Campaign Name"]}', url)
        else:
            if '?' not in url:
                url += f"?utm_source=tiktok&utm_medium=cpc&utm_campaign={row['Campaign Name']}&tf_campaign={row['Campaign Name']}"
            else:
                url += f"&utm_source=tiktok&utm_medium=cpc&utm_campaign={row['Campaign Name']}&tf_campaign={row['Campaign Name']}"
        df_main.at[i, 'Web URL'] = url

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_main.to_excel(writer, index=False, sheet_name='ExportedAds')
    output.seek(0)
    return output
