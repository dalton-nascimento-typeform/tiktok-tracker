
import pandas as pd
import io

def clean_url(url, tf_params, utm_params):
    if not isinstance(url, str) or not url.strip():
        return url
    if "?" not in url:
        url += "?" + "&".join(utm_params + tf_params)
    else:
        parts = url.split("?", 1)
        base, query = parts[0], parts[1]
        existing = query.split("&")
        all_params = {p.split("=")[0]: p.split("=")[1] for p in existing if "=" in p}
        for param in utm_params + tf_params:
            k, v = param.split("=")
            if k not in all_params:
                existing.append(param)
        url = base + "?" + "&".join(existing)
    return url

def extract_impression_url(raw):
    if not isinstance(raw, str):
        return ""
    if '"' in raw:
        parts = raw.split('"')
        for p in parts:
            if p.startswith("http"):
                return p.strip()
    return raw.strip() if raw.startswith("http") else ""

def process_files(tiktok_file, tag_files):
    tiktok_df = pd.read_excel(tiktok_file, sheet_name="Ads")
    required_cols = ["Campaign Name", "Placement Name", "Ad Name", "Click URL"]
    for col in required_cols:
        if col not in tiktok_df.columns:
            raise ValueError(f"'{col}' not found in TikTok Ads sheet")

    tag_dfs = []
    for f in tag_files:
        df = pd.read_excel(f, header=10)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        tag_dfs.append(df)

    all_tags = pd.concat(tag_dfs, ignore_index=True)
    if "Campaign Name" not in all_tags.columns:
        raise ValueError("No valid tag data found. Make sure the sheets include 'Campaign Name'.")

    click_map = {}
    impr_map = {}
    for _, row in all_tags.iterrows():
        key = (
            str(row.get("Campaign Name", "")).strip(),
            str(row.get("Ad Group Name", "")).strip(),
            str(row.get("Ad Name", "")).strip()
        )
        click_map[key] = row.get("Click Tag", "")
        impr_map[key] = extract_impression_url(row.get("Impression Tag", ""))

    updated_rows = []
    for _, row in tiktok_df.iterrows():
        key = (
            str(row["Campaign Name"]).strip(),
            str(row["Placement Name"]).strip(),
            str(row["Ad Name"]).strip()
        )
        updated_row = row.copy()

        utm_params = [
            f"utm_source=tiktok",
            f"utm_medium=paid",
            f"utm_campaign={row['Campaign Name']}"
        ]
        tf_params = [
            f"tf_source=tiktok",
            f"tf_medium=paid_social",
            f"tf_campaign={row['Campaign Name']}"
        ]

        updated_row["Click URL"] = clean_url(click_map.get(key, row["Click URL"]), tf_params, utm_params)
        updated_row["Impression Tracking URL"] = impr_map.get(key, "")
        updated_rows.append(updated_row)

    updated_df = pd.DataFrame(updated_rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        updated_df.to_excel(writer, index=False, sheet_name="Ads")
    output.seek(0)
    return output
