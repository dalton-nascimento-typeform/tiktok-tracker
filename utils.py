
import pandas as pd
import io

REQUIRED_COLUMNS = [
    "Campaign Name", "Placement Name", "Ad Name",
    "Impression Tag (image)", "Click Tag"
]

def extract_first_quote_content(tag: str):
    if isinstance(tag, str) and '"' in tag:
        return tag.split('"')[1]
    return ""

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    ads_sheet_name = [s for s in df_main.keys() if s.lower().startswith("ads")][0]
    df_ads = df_main[ads_sheet_name]

    df_tags_list = []
    for f in dcm_files:
        df = pd.read_excel(f, sheet_name="Tracking Ads", header=10)
        df_tags_list.append(df)

    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame(columns=REQUIRED_COLUMNS)

    updated_rows = []
    for idx, row in df_ads.iterrows():
        campaign = str(row.get("Campaign Name", "")).strip()
        placement = str(row.get("Ad Group Name", "")).strip()
        ad = str(row.get("Ad Name", "")).strip()

        matching = df_tags[
            (df_tags["Campaign Name"].astype(str).str.strip() == campaign) &
            (df_tags["Placement Name"].astype(str).str.strip() == placement) &
            (df_tags["Ad Name"].astype(str).str.strip() == ad)
        ]
        if not matching.empty:
            match = matching.iloc[0]
            df_ads.at[idx, "Impression Tracking URL"] = extract_first_quote_content(match.get("Impression Tag (image)", ""))
            df_ads.at[idx, "Click Tracking URL"] = match.get("Click Tag", "")

        # Update or insert UTM and tf_campaign if not present
        url = str(row.get("Web URL", "")).strip()
        if "utm_campaign=" in url:
            url = url.replace("__CAMPAIGN_NAME__", campaign)
        else:
            sep = "&" if "?" in url else "?"
            url += f"{sep}utm_source=tiktok&utm_medium=paid&utm_campaign={campaign}&tf_campaign={campaign}"
        url = url.replace("tf_campaign=__CAMPAIGN_NAME__", f"tf_campaign={campaign}")
        df_ads.at[idx, "Web URL"] = url

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ads.to_excel(writer, index=False, sheet_name="Ads")
    output.seek(0)
    return output



def ensure_tf_parameters(url):
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Ensure tf_source and tf_medium
    if 'tf_source' not in query:
        query['tf_source'] = ['tiktok']
    if 'tf_medium' not in query:
        query['tf_medium'] = ['paid_social']

    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url
