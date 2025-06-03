
import pandas as pd
import io
import re

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    sheet_name = [s for s in df_main.keys() if "ads" in s.lower()][0]
    df_ads = df_main[sheet_name]

    df_tags_list = []
    for f in dcm_files:
        try:
            df_tags_list.append(pd.read_excel(f, sheet_name="Tracking Ads"))
        except:
            df_tags_list.append(pd.read_excel(f))  # fallback

    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame()

    if df_tags.empty:
        raise ValueError("No tracking tags found.")

    def get_tag(campaign, placement, tag_type):
        subset = df_tags[
            (df_tags['Campaign Name'].astype(str).str.strip() == campaign) &
            (df_tags['Placement Name'].astype(str).str.strip() == placement)
        ]
        if subset.empty:
            return ""
        return subset.iloc[0][f"{tag_type} Tag"] if f"{tag_type} Tag" in subset.columns else ""

    for i, row in df_ads.iterrows():
        campaign = str(row.get('Campaign Name', '')).strip()
        placement = str(row.get('Placement Name', '')).strip()
        url = str(row.get('Ad Click URL', '')).strip()

        click_tag = get_tag(campaign, placement, 'Click')
        imp_tag = get_tag(campaign, placement, 'Impression')

        # Replace placeholders with actual tags
        if "[INSERT_CLICK_TRACKER_HERE]" in url and click_tag:
            url = url.replace("[INSERT_CLICK_TRACKER_HERE]", click_tag)
        if "[INSERT_IMPRESSION_TRACKER_HERE]" in url and imp_tag:
            url = url.replace("[INSERT_IMPRESSION_TRACKER_HERE]", imp_tag)

        # Append tf_source and tf_medium if not present
        if "tf_source=" not in url:
            url += "&tf_source=tiktok"
        if "tf_medium=" not in url:
            url += "&tf_medium=paid_social"

        # Fix incorrect '?' placement
        if '?' not in str(row.get('Ad Click URL', '')):
            url = url.replace('&', '?', 1)

        df_ads.at[i, 'Ad Click URL'] = url

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ads.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output
