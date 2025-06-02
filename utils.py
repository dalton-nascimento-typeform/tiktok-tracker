import pandas as pd
import io
import re

REQUIRED_COLUMNS = [
    'Campaign Name', 'Placement Name', 'Ad Name', 'Impression Tag (image)', 'Click Tag'
]

def extract_impression_url(tag):
    if pd.isna(tag): return None
    match = re.search(r'<IMG SRC="([^"]+)"', tag)
    return match.group(1) if match else None

def process_files(tiktok_file, dcm_files):
    # Read TikTok Export file and identify sheet
    df_main_all = pd.read_excel(tiktok_file, sheet_name=None)
    sheet_candidates = [s for s in df_main_all.keys() if "ExportAds" in s]
    if not sheet_candidates:
        raise ValueError("No sheet with 'ExportAds' in the name was found in the TikTok file.")
    df_main = df_main_all[sheet_candidates[0]]

    # Read all DCM sheets and normalize them into a single DataFrame
    df_tags_list = []
    for f in dcm_files:
        try:
            df = pd.read_excel(f)
            if all(col in df.columns for col in REQUIRED_COLUMNS):
                df_tags_list.append(df)
        except Exception as e:
            continue

    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame(columns=REQUIRED_COLUMNS)

    # Update tracking URLs in TikTok file (Column DN)
    if "Campaign Name" in df_main.columns and "Ad Name" in df_main.columns and "Ad Group Name" in df_main.columns:
        for i, row in df_main.iterrows():
            campaign = str(row["Campaign Name"]).strip()
            adgroup = str(row["Ad Group Name"]).strip()
            adname = str(row["Ad Name"]).strip()
            url = row.get("Web URL", "")

            if pd.isna(url): continue

            # Replace existing TF and UTM parameters
            url = re.sub(r'utm_campaign=__CAMPAIGN_NAME__', f'utm_campaign={campaign}', url)
            url = re.sub(r'tf_campaign=([^&]+)', f'tf_campaign={campaign}', url)

            if "utm_campaign" not in url:
                delimiter = "&" if "?" in url else "?"
                url += f"{delimiter}utm_source=tiktok&utm_medium=cpc&utm_campaign={campaign}&tf_campaign={campaign}"

            df_main.at[i, "Web URL"] = url

            # Match tracking data from DCM sheets
            matches = df_tags[
                (df_tags["Campaign Name"].astype(str).str.strip() == campaign) &
                (df_tags["Placement Name"].astype(str).str.strip() == adgroup) &
                (df_tags["Ad Name"].astype(str).str.strip() == adname)
            ]

            if not matches.empty:
                df_main.at[i, "Impression Tracking URL"] = extract_impression_url(matches.iloc[0]["Impression Tag (image)"])
                df_main.at[i, "Click Tracking URL"] = matches.iloc[0]["Click Tag"]

    # Export back to Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_main.to_excel(writer, index=False, sheet_name="Updated_Export")
    output.seek(0)
    return output