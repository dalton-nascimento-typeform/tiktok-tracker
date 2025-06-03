import pandas as pd
from io import BytesIO

REQUIRED_COLUMNS = [
    "Campaign Name", "Placement Name", "Ad Name",
    "Impression Tracking URL", "Click Tracking URL", "Final URL"
]

def extract_campaign_name(df):
    for _, row in df.iterrows():
        for cell in row:
            if isinstance(cell, str) and "Campaign Name" in cell:
                return row[row.first_valid_index() + 1]
    return None

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    ads_sheet_name = [s for s in df_main if "Ads" in s][0]
    df_ads = df_main[ads_sheet_name]
    
    df_tags_list = []
    for f in dcm_files:
        df = pd.read_excel(f, header=None)
        campaign_name = extract_campaign_name(df)
        if campaign_name:
            tracking_df = pd.read_excel(f, sheet_name="Tracking Ads", skiprows=10)
            tracking_df["Campaign Name"] = campaign_name
            df_tags_list.append(tracking_df)
    
    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame(columns=REQUIRED_COLUMNS)

    for i, row in df_ads.iterrows():
        campaign = row.get("Campaign Name")
        ad_name = row.get("Ad Name")
        match = df_tags[
            (df_tags["Campaign Name"].astype(str).str.strip() == str(campaign).strip()) &
            (df_tags["Ad Name"].astype(str).str.strip() == str(ad_name).strip())
        ]
        if not match.empty:
            df_ads.at[i, "Click Tracking URL"] = match["Click Tracking URL"].values[0]
            df_ads.at[i, "Impression Tracking URL"] = match["Impression Tracking URL"].values[0]

        # Ensure UTM parameters are added
        final_url = str(row.get("Final URL", ""))
        if final_url and "tf_source=" not in final_url and "tf_medium=" not in final_url:
            sep = "&" if "?" in final_url else "?"
            final_url += f"{sep}tf_source=tiktok&tf_medium=paid_social"
            df_ads.at[i, "Final URL"] = final_url

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ads.to_excel(writer, sheet_name=ads_sheet_name, index=False)
    output.seek(0)
    return output