
import pandas as pd
from io import BytesIO

def process_files(tiktok_file, tag_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None, header=10)
    sheet_name = "Ads" if "Ads" in df_main else list(df_main.keys())[0]
    df_ads = df_main[sheet_name]

    df_ads.columns = df_ads.columns.str.strip()
    required_cols = ["Campaign Name", "Ad Group Name", "Ad Name", "Click URL"]
    for col in required_cols:
        if col not in df_ads.columns:
            raise KeyError(f"{col}")

    df_tags_list = []
    for f in tag_files:
        tags_df = pd.read_excel(f, header=10)
        tags_df.columns = tags_df.columns.str.strip()
        if "Campaign Name" not in tags_df.columns:
            continue
        df_tags_list.append(tags_df)

    if not df_tags_list:
        raise ValueError("No valid tag data found. Make sure the sheets include 'Campaign Name'.")

    df_tags = pd.concat(df_tags_list, ignore_index=True)

    for idx, row in df_ads.iterrows():
        campaign = str(row["Campaign Name"]).strip()
        placement = str(row["Ad Group Name"]).strip()
        ad_name = str(row["Ad Name"]).strip()

        match = df_tags[
            (df_tags["Campaign Name"].astype(str).str.strip() == campaign) &
            (df_tags["Placement Name"].astype(str).str.strip() == placement) &
            (df_tags["Ad Name"].astype(str).str.strip() == ad_name)
        ]

        original_url = row["Click URL"]
        new_url = str(original_url) if pd.notna(original_url) else ""

        if pd.notna(original_url):
            if "utm_source=" not in new_url:
                new_url += f"?utm_source=tiktok&utm_medium=paid&utm_campaign={campaign}&tf_campaign={campaign}"
            if "tf_source=" not in new_url:
                new_url += "&tf_source=tiktok"
            if "tf_medium=" not in new_url:
                new_url += "&tf_medium=paid_social"

        if not match.empty:
            click_url = match.iloc[0].get("Click Tracker", "")
            imp_url = match.iloc[0].get("Impression Tracker", "")

            if click_url:
                df_ads.at[idx, "Click URL"] = click_url
            else:
                df_ads.at[idx, "Click URL"] = new_url

            if "Impression URL" in df_ads.columns:
                df_ads.at[idx, "Impression URL"] = imp_url
        else:
            df_ads.at[idx, "Click URL"] = new_url

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_ads.to_excel(writer, sheet_name="Ads", index=False)
    output.seek(0)
    return output
