
import pandas as pd
import io

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    sheet_name = [s for s in df_main.keys() if s.lower().strip() == "ads"][0]
    df_ads = df_main[sheet_name]

    df_tags_list = []
    for f in dcm_files:
        df = pd.read_excel(f, sheet_name=None)
        for sheet in df.values():
            if "Campaign Name" in sheet.columns:
                campaign_name = sheet["Campaign Name"].iloc[0]
                tags = sheet.dropna(subset=["Placement Name", "Impression Tracking URL", "Click Tracking URL"], how="all")
                tags["Campaign Name"] = campaign_name
                df_tags_list.append(tags)

    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame()

    if df_tags.empty:
        raise ValueError("No valid tag data found. Make sure the sheets include 'Campaign Name'.")

    def update_url(row):
        url = str(row["Click URL"]).strip()
        if not url or url.lower() == "nan":
            return url

        if "utm_source" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}utm_source=tiktok&utm_medium=paid&utm_campaign={row['Campaign Name']}&tf_campaign={row['Campaign Name']}"
        if "tf_source" not in url:
            url += "&tf_source=tiktok"
        if "tf_medium" not in url:
            url += "&tf_medium=paid_social"
        return url

    df_ads["Click URL"] = df_ads.apply(update_url, axis=1)

    for _, tag in df_tags.iterrows():
        match = df_ads["Ad Name"].astype(str).str.strip() == str(tag["Placement Name"]).strip()
        if "Click Tracking URL" in tag and pd.notna(tag["Click Tracking URL"]):
            df_ads.loc[match, "Click URL"] = tag["Click Tracking URL"]
        if "Impression Tracking URL" in tag and pd.notna(tag["Impression Tracking URL"]):
            df_ads.loc[match, "Impression URL"] = tag["Impression Tracking URL"]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_ads.to_excel(writer, index=False, sheet_name="Ads")
    output.seek(0)
    return output
