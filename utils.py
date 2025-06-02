import pandas as pd
from io import BytesIO

REQUIRED_COLUMNS = ['Campaign Name', 'Ad Group Name', 'Ad Name', 'Impression Tag (image)', 'Click Tag']

def extract_first_quote(text):
    try:
        return text.split('"')[1]
    except (IndexError, AttributeError):
        return None

def update_url(url, campaign_name):
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    if not isinstance(url, str):
        return url

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Update or add utm_campaign and tf_campaign
    query["utm_campaign"] = [campaign_name]
    query["tf_campaign"] = [campaign_name]

    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    sheet_name = [s for s in df_main.keys() if s.startswith("ExportAds")][0]
    df_main = df_main[sheet_name]

    df_tags_list = []
    for f in dcm_files:
        df = pd.read_excel(f)
        if set(REQUIRED_COLUMNS).issubset(df.columns):
            df_tags_list.append(df)

    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame(columns=REQUIRED_COLUMNS)

    for idx, row in df_main.iterrows():
        campaign = str(row["Campaign Name"]).strip()
        adgroup = str(row["Ad Group Name"]).strip()
        adname = str(row["Ad Name"]).strip()

        # Update Web URL with UTM & TF parameters
        if "Web URL" in df_main.columns:
            original_url = row["Web URL"]
            updated_url = update_url(original_url, campaign)
            df_main.at[idx, "Web URL"] = updated_url

        # Match tags
        match = df_tags[
            (df_tags['Campaign Name'].astype(str).str.strip() == campaign) &
            (df_tags['Ad Group Name'].astype(str).str.strip() == adgroup) &
            (df_tags['Ad Name'].astype(str).str.strip() == adname)
        ]

        if not match.empty:
            imp_tag = extract_first_quote(match.iloc[0]['Impression Tag (image)'])
            click_tag = match.iloc[0]['Click Tag']
            if "Impression Tracking URL" in df_main.columns:
                df_main.at[idx, "Impression Tracking URL"] = imp_tag
            if "Click Tracking URL" in df_main.columns:
                df_main.at[idx, "Click Tracking URL"] = click_tag

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_main.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output