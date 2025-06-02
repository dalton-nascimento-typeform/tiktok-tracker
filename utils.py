
import pandas as pd
import re
import os

def process_files(tiktok_path, dcm_files):
    df_main = pd.read_excel(tiktok_path, sheet_name=None)
    if 'Ads' not in df_main:
        raise ValueError("No sheet named 'Ads' found in the TikTok file.")
    df_ads = df_main['Ads']

    df_tags_list = []
    for f in dcm_files:
        df = pd.read_excel(f)
        df_tags_list.append(df)

    if not df_tags_list:
        return tiktok_path

    df_tags = pd.concat(df_tags_list, ignore_index=True)

    for idx, row in df_ads.iterrows():
        campaign = str(row.get("Campaign Name", "")).strip()
        adgroup = str(row.get("Ad Group Name", "")).strip()
        adname = str(row.get("Ad Name", "")).strip()

        matched_tags = df_tags[
            (df_tags["Campaign Name"].astype(str).str.strip() == campaign) &
            (df_tags["Placement Name"].astype(str).str.strip() == adgroup) &
            (df_tags["Ad"].astype(str).str.strip() == adname)
        ]

        if not matched_tags.empty:
            imp_tag_raw = str(matched_tags.iloc[0].get("Impression Tag (image)", ""))
            click_tag = str(matched_tags.iloc[0].get("Click Tag", ""))

            # Extract URL from within first double quotes in the impression tag
            match = re.search(r'\"(https://[^"]+)\"', imp_tag_raw.replace('"', '\"'))
            if not match:
                match = re.search(r'"(https://[^"]+)"', imp_tag_raw)
            if match:
                df_ads.at[idx, "Impression Tracking URL"] = match.group(1)

            if click_tag:
                df_ads.at[idx, "Click Tracking URL"] = click_tag

        # UTM/TF update logic
        url = str(row.get("Web URL", ""))
        if url:
            if "utm_campaign=" in url:
                url = re.sub(r'utm_campaign=[^&]+', f"utm_campaign={campaign}", url)
            else:
                url += f"&utm_campaign={campaign}"
            if "tf_campaign=" in url:
                url = re.sub(r'tf_campaign=[^&]+', f"tf_campaign={campaign}", url)
            else:
                url += f"&tf_campaign={campaign}"
            df_ads.at[idx, "Web URL"] = url

    output_path = "/mnt/data/Updated_TikTok_File.xlsx"
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        df_ads.to_excel(writer, sheet_name="Ads", index=False)
    return output_path
