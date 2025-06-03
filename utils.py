
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, parse_qsl

def extract_campaign_name(df):
    try:
        return df.iloc[10]['Campaign Name']
    except KeyError:
        for col in df.columns:
            if str(col).strip().lower() == 'campaign name':
                return df.iloc[10][col]
    raise KeyError("'Campaign Name'")

def add_tracking_to_url(url, utm, tf):
    if not isinstance(url, str) or not url.startswith("http"):
        return url
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))
    query.update({k: v for k, v in utm.items() if k not in query})
    query.update({k: v for k, v in tf.items() if k not in query})
    new_url = urlunparse(parsed._replace(query=urlencode(query)))
    return new_url

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    sheet_name = [s for s in df_main.keys() if "ads" in s.lower()][0]
    df_ads = df_main[sheet_name]

    df_tags_list = []
    for f in dcm_files:
        df = pd.read_excel(f, sheet_name=None)
        for sname, sheet in df.items():
            if "tracking ads" in sname.lower():
                df_tags_list.append(sheet)

    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame()

    try:
        campaign = extract_campaign_name(df_tags_list[0])
    except Exception:
        campaign = ""

    utm_params = {
        "utm_source": "tiktok",
        "utm_medium": "paid",
        "utm_campaign": campaign
    }
    tf_params = {
        "tf_campaign": campaign,
        "tf_source": "tiktok",
        "tf_medium": "paid_social"
    }

    df_ads["Click URL"] = df_ads["Click URL"].apply(lambda url: add_tracking_to_url(url, utm_params, tf_params))

    # Add Impression and Click Tracking columns
    df_ads["Impression Tracking URL"] = None
    df_ads["Click Tracking URL"] = None

    for _, tag_row in df_tags.iterrows():
        ad_name = str(tag_row.get("Ad Name", "")).strip()
        impression = str(tag_row.get("Impression Tag", "")).strip()
        click = str(tag_row.get("Click Tag", "")).strip()
        match_rows = df_ads["Ad Name"].astype(str).str.strip() == ad_name
        df_ads.loc[match_rows, "Impression Tracking URL"] = impression
        df_ads.loc[match_rows, "Click Tracking URL"] = click

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_ads.to_excel(writer, sheet_name="Ads", index=False)
    output.seek(0)
    return output
