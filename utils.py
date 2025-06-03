import pandas as pd
import io

def clean_campaign_name(name):
    return str(name).strip().replace("\n", " ").replace("  ", " ")

def extract_campaign_name(sheet):
    for i in range(1, 30):
        for col in sheet.columns:
            val = sheet.at[i, col] if i in sheet.index else None
            if str(val).strip().lower() == "campaign name":
                return sheet.at[i+1, col]
    return None

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    ads_sheet_name = [s for s in df_main.keys() if "ads" in s.lower()][0]
    df_ads = df_main[ads_sheet_name]

    # Read and combine all tag files
    df_tags_list = []
    for f in dcm_files:
        df_tag = pd.read_excel(f, sheet_name=None)
        for sheet_name, sheet_df in df_tag.items():
            campaign = extract_campaign_name(sheet_df)
            if campaign:
                sheet_df["Campaign Name"] = clean_campaign_name(campaign)
                df_tags_list.append(sheet_df)

    if not df_tags_list:
        raise ValueError("No valid tag data found. Make sure the sheets include 'Campaign Name'.")

    df_tags = pd.concat(df_tags_list, ignore_index=True)
    df_tags["Campaign Name"] = df_tags["Campaign Name"].apply(clean_campaign_name)

    # Match and update tracking
    updated_rows = 0
    for idx, ad in df_ads.iterrows():
        camp = clean_campaign_name(ad.get("Campaign Name", ""))
        group = str(ad.get("Ad Group Name", "")).strip()
        name = str(ad.get("Ad Name", "")).strip()

        matched = df_tags[
            (df_tags["Campaign Name"] == camp) &
            (df_tags["Placement Name"].astype(str).str.strip() == group) &
            (df_tags["Ad Name"].astype(str).str.strip() == name)
        ]

        if not matched.empty:
            click = matched["Click Tracking URL"].values[0] if "Click Tracking URL" in matched else ""
            imp = matched["Impression Tracking URL"].values[0] if "Impression Tracking URL" in matched else ""

            # Update Click URL
            current_url = str(ad.get("Click URL", ""))
            if current_url:
                if "utm_source" not in current_url:
                    current_url += f"?utm_source=tiktok&utm_medium=paid&utm_campaign={camp}&tf_campaign={camp}"
                    if "&" not in current_url.split("?")[-1]:
                        current_url += "&tf_source=tiktok&tf_medium=paid_social"
                if "tf_source=" not in current_url:
                    current_url += "&tf_source=tiktok"
                if "tf_medium=" not in current_url:
                    current_url += "&tf_medium=paid_social"
                df_ads.at[idx, "Click URL"] = current_url

            if click:
                df_ads.at[idx, "Click Tracking URL"] = click
            if imp:
                df_ads.at[idx, "Impression Tracking URL"] = imp
            updated_rows += 1

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_ads.to_excel(writer, index=False, sheet_name=ads_sheet_name)
    output.seek(0)
    return output
