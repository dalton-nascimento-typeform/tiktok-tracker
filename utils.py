
import pandas as pd
from io import BytesIO

def process_files(tiktok_file, dcm_files):
    df_ads = pd.read_excel(tiktok_file, sheet_name="Ads", header=10)
    df_ads.columns = df_ads.columns.str.strip()

    df_tags_list = []
    for f in dcm_files:
        xls = pd.ExcelFile(f)
        sheet = [s for s in xls.sheet_names if "Tracking Ads" in s][0]
        df_tag = pd.read_excel(xls, sheet_name=sheet, header=10)
        df_tag.columns = df_tag.columns.str.strip()
        df_tags_list.append(df_tag)

    df_tags = pd.concat(df_tags_list, ignore_index=True)

    def clean_url(url):
        if isinstance(url, str):
            url = url.strip()
            if not url.startswith("http"):
                return url
            if "?" not in url:
                url += "?"
            if "utm_source" not in url:
                url += "&utm_source=tiktok&utm_medium=paid"
            if "tf_source" not in url:
                url += "&tf_source=tiktok&tf_medium=paid_social"
        return url

    for i, row in df_ads.iterrows():
        match = df_tags[
            (df_tags["Campaign Name"].astype(str).str.strip() == str(row["Campaign Name"]).strip()) &
            (df_tags["Placement Name"].astype(str).str.strip() == str(row["Ad Group Name"]).strip()) &
            (df_tags["Ad Name"].astype(str).str.strip() == str(row["Ad Name"]).strip())
        ]
        if not match.empty:
            df_ads.at[i, "Impression Tracking URL"] = match["Impression URL"].values[0]
            df_ads.at[i, "Click Tracking URL"] = match["Click URL"].values[0]
        df_ads.at[i, "Final URL"] = clean_url(row["Final URL"])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_ads.to_excel(writer, sheet_name="Ads", index=False)
    output.seek(0)
    return output
