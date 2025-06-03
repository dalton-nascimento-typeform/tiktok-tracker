
import pandas as pd
import io

REQUIRED_COLUMNS = ["Campaign Name", "Placement Name", "Ad Name", "Impression Tag", "Click Tag"]


def extract_sheet_with_keywords(excel_file, keyword):
    df_all = pd.read_excel(excel_file, sheet_name=None, header=None)
    for sheet_name, sheet_df in df_all.items():
        if keyword.lower() in sheet_name.lower():
            return sheet_df, sheet_name
    raise ValueError(f"No sheet with '{keyword}' in the name was found.")


def extract_tags_data(file):
    df = pd.read_excel(file, sheet_name=None, header=None)
    for sheet in df.values():
        header_row_idx = 10
        sheet.columns = sheet.iloc[header_row_idx]
        sheet = sheet.iloc[header_row_idx + 1:]
        if all(col in sheet.columns for col in REQUIRED_COLUMNS):
            return sheet.dropna(subset=["Campaign Name", "Placement Name", "Ad Name"])
    return pd.DataFrame(columns=REQUIRED_COLUMNS)


def clean_url(url):
    if pd.isna(url):
        return ""
    return str(url).strip()


def append_params(url, campaign):
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    if "utm_source" not in query:
        query["utm_source"] = ["tiktok"]
    if "utm_medium" not in query:
        query["utm_medium"] = ["paid"]
    if "utm_campaign" not in query:
        query["utm_campaign"] = [campaign]
    if "tf_campaign" not in query:
        query["tf_campaign"] = [campaign]
    if "tf_source" not in query:
        query["tf_source"] = ["tiktok"]
    if "tf_medium" not in query:
        query["tf_medium"] = ["paid_social"]

    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def process_files(tiktok_file, dcm_files):
    ads_df_raw, _ = extract_sheet_with_keywords(tiktok_file, "ads")
    ads_df_raw.columns = ads_df_raw.iloc[10]
    ads_df = ads_df_raw.iloc[11:].copy()
    ads_df = ads_df.dropna(subset=["Ad Name", "Placement Name"])

    tag_df = pd.concat([extract_tags_data(f) for f in dcm_files], ignore_index=True)

    for idx, row in ads_df.iterrows():
        campaign = str(row.get("Campaign Name", "")).strip()
        placement = str(row.get("Placement Name", "")).strip()
        ad = str(row.get("Ad Name", "")).strip()

        match = tag_df[
            (tag_df["Campaign Name"].astype(str).str.strip() == campaign) &
            (tag_df["Placement Name"].astype(str).str.strip() == placement) &
            (tag_df["Ad Name"].astype(str).str.strip() == ad)
        ]

        url = clean_url(row.get("Click URL", ""))
        if url:
            ads_df.at[idx, "Click URL"] = append_params(url, campaign)

        if not match.empty:
            ads_df.at[idx, "Impression URL"] = match.iloc[0]["Impression Tag"]
            ads_df.at[idx, "Click Tracking URL"] = match.iloc[0]["Click Tag"]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        ads_df.to_excel(writer, index=False, sheet_name="Ads")
    output.seek(0)
    return output
