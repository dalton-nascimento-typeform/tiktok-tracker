
import pandas as pd
from io import BytesIO

def clean_url(url, campaign_name):
    if pd.isna(url) or not isinstance(url, str):
        return url
    url = url.strip()
    if "utm_source=" not in url:
        url += ("&" if "?" in url else "?") + "utm_source=tiktok&utm_medium=paid"
    if "utm_campaign=" not in url:
        url += "&utm_campaign=" + campaign_name
    if "tf_campaign=" not in url:
        url += "&tf_campaign=" + campaign_name
    if "tf_source=" not in url:
        url += "&tf_source=tiktok"
    if "tf_medium=" not in url:
        url += "&tf_medium=paid_social"
    return url

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None, header=10)
    sheet_name = "Ads" if "Ads" in df_main else list(df_main.keys())[0]
    df_ads = df_main[sheet_name].copy()

    df_tags_list = [pd.read_excel(f, sheet_name=None, header=10) for f in dcm_files]
    df_tags_combined = pd.concat(
        [df[s] for df in df_tags_list for s in df if "Tracking Ads" in s], ignore_index=True
    )

    for idx, row in df_ads.iterrows():
        try:
            campaign = str(row["Campaign Name"]).strip()
            ad_group = str(row["Ad Group Name"]).strip()
            ad_name = str(row["Ad Name"]).strip()
        except KeyError as e:
            raise ValueError(f"Missing column in Export Ads: {e}")

        matches = df_tags_combined[
            (df_tags_combined["Campaign Name"].astype(str).str.strip() == campaign) &
            (df_tags_combined["Placement Name"].astype(str).str.strip() == ad_group) &
            (df_tags_combined["Ad Name"].astype(str).str.strip() == ad_name)
        ]

        click_tracker = matches["Click Tracking URL"].values[0] if "Click Tracking URL" in matches and not matches.empty else None
        impression_tracker = matches["Impression Tracking URL"].values[0] if "Impression Tracking URL" in matches and not matches.empty else None

        url = row.get("Click URL", "")
        updated_url = clean_url(url, campaign)
        if click_tracker and "[click_tracker]" not in updated_url:
            updated_url += f"&click_tracker={click_tracker}"
        df_ads.at[idx, "Click URL"] = updated_url

        if impression_tracker:
            df_ads.at[idx, "Impression URL"] = impression_tracker

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_ads.to_excel(writer, sheet_name="Ads", index=False)
    output.seek(0)
    return output
