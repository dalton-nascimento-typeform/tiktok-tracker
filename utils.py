
import pandas as pd
import io
import re

REQUIRED_COLUMNS = [
    "Campaign Name", "Placement Name", "Ad Name", "Impression Tag (image)", "Click Tag"
]

def clean_tag_url(tag):
    match = re.search(r'\"(https[^"]+)\"', tag)
    return match.group(1) if match else ""

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    sheet_name = [s for s in df_main.keys() if s.startswith("ExportAds")][0]
    df_tiktok = df_main[sheet_name]

    # Normalize columns
    df_tiktok.columns = df_tiktok.columns.str.strip()

    df_tags_list = []
    for f in dcm_files:
        # Try to read with header at row 10 (zero-indexed row 9)
        try:
            df = pd.read_excel(f, header=10)
            if not all(col in df.columns for col in REQUIRED_COLUMNS):
                continue
            df_tags_list.append(df)
        except Exception:
            continue

    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame(columns=REQUIRED_COLUMNS)

    # UTM and tf_campaign updates
    def update_url(row):
        url = row['Web URL']
        campaign = str(row['Campaign Name']).strip()
        if not isinstance(url, str):
            return url

        # Replace tokens
        if "__CAMPAIGN_NAME__" in url:
            url = re.sub(r'utm_campaign=__CAMPAIGN_NAME__', f'utm_campaign={campaign}', url)
        if "tf_campaign=" in url:
            url = re.sub(r'tf_campaign=[^&]*', f'tf_campaign={campaign}', url)

        # If no UTM, add default
        if "utm_campaign" not in url and "tf_campaign" not in url:
            separator = '&' if '?' in url else '?'
            url += f"{separator}utm_source=tiktok&utm_medium=cpc&utm_campaign={campaign}&tf_source=tiktok&utm_term=ad&tf_campaign={campaign}"
        return url

    df_tiktok['Web URL'] = df_tiktok.apply(update_url, axis=1)

    # Match DCM tags
    def get_tag(camp, placement, adname, col):
        df_match = df_tags[
            (df_tags['Campaign Name'].astype(str).str.strip() == str(camp).strip()) &
            (df_tags['Placement Name'].astype(str).str.strip() == str(placement).strip()) &
            (df_tags['Ad Name'].astype(str).str.strip() == str(adname).strip())
        ]
        if not df_match.empty:
            val = df_match.iloc[0][col]
            return clean_tag_url(val) if pd.notna(val) else ""
        return ""

    df_tiktok['Impression Tracking URL'] = df_tiktok.apply(
        lambda row: get_tag(row['Campaign Name'], row['Ad Group Name'], row['Ad Name'], 'Impression Tag (image)'), axis=1
    )
    df_tiktok['Click Tracking URL'] = df_tiktok.apply(
        lambda row: get_tag(row['Campaign Name'], row['Ad Group Name'], row['Ad Name'], 'Click Tag'), axis=1
    )

    # Write output to buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_tiktok.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output
