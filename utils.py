import pandas as pd
from io import BytesIO
import re

def clean_url(url):
    url = str(url)
    url = re.sub(r"[?&](utm|tf)_[^=]+=[^&]*", "", url)
    url = re.sub(r"[?&]$", "", url)
    return url

def append_params(url, utm, tf):
    if "?" in url:
        url += "&" + utm + "&" + tf
    else:
        url += "?" + utm + "&" + tf
    return url

def ensure_tf_source_medium(url):
    url = str(url)
    if "&tf_source=" not in url:
        url += "&tf_source=tiktok"
    if "&tf_medium=" not in url:
        url += "&tf_medium=paid_social"
    return url

def process_files(tiktok_file, dcm_files):
    df_ads = pd.read_excel(tiktok_file, sheet_name="Ads")

    df_ads["Click URL"] = df_ads["Click URL"].astype(str)

    df_tags_list = []
    for f in dcm_files:
        df_tag = pd.read_excel(f, header=10)
        df_tags_list.append(df_tag)
    df_tags = pd.concat(df_tags_list, ignore_index=True)

    for i, row in df_ads.iterrows():
        campaign = row["Campaign Name"]
        ad = row["Ad Name"]

        match = df_tags[
            (df_tags["Campaign Name"].astype(str).str.strip() == str(campaign).strip()) &
            (df_tags["Ad Name"].astype(str).str.strip() == str(ad).strip())
        ]

        if not match.empty:
            tag_row = match.iloc[0]
            utm_params = tag_row.get("Click Tracker URL", "")
            imp_tag = tag_row.get("Impression Tracker URL", "")
            tf_params = tag_row.get("TF Tracking URL", "")

            if pd.notna(utm_params) or pd.notna(tf_params):
                clean = clean_url(row["Click URL"])
                combined_url = append_params(clean, utm_params, tf_params)
                combined_url = ensure_tf_source_medium(combined_url)
                df_ads.at[i, "Click URL"] = combined_url

            if pd.notna(imp_tag):
                df_ads.at[i, "Impression Tracking URL"] = imp_tag

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_ads.to_excel(writer, sheet_name="Ads", index=False)
    output.seek(0)
    return output
