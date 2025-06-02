
import pandas as pd
import io
import re

REQUIRED_COLUMNS = [
    'Campaign Name', 'Placement Name', 'Ad Name',
    'Impression Tag (image)', 'Click Tag'
]

def process_files(tiktok_file, dcm_files):
    df_main = pd.read_excel(tiktok_file, sheet_name=None)
    sheet_name = [s for s in df_main.keys() if s.startswith("ExportAds")][0]
    df_main = df_main[sheet_name]

    df_main['Campaign Name norm'] = df_main['Campaign Name'].astype(str).str.strip().str.lower()
    df_main['Ad Group Name norm'] = df_main['Ad Group Name'].astype(str).str.strip().str.lower()
    df_main['Ad Name norm'] = df_main['Ad Name'].astype(str).str.strip().str.lower()

    df_tags_list = []
    for f in dcm_files:
        df = pd.read_excel(f)
        if all(col in df.columns for col in REQUIRED_COLUMNS):
            df['Campaign Name'] = df['Campaign Name'].astype(str).str.strip().str.lower()
            df['Placement Name'] = df['Placement Name'].astype(str).str.strip().str.lower()
            df['Ad Name'] = df['Ad Name'].astype(str).str.strip().str.lower()
            df_tags_list.append(df)

    df_tags = pd.concat(df_tags_list, ignore_index=True) if df_tags_list else pd.DataFrame(columns=list(REQUIRED_COLUMNS))

    for idx, row in df_main.iterrows():
        web_url = str(row['Web URL'])
        campaign = str(row['Campaign Name'])

        if 'utm_campaign=' in web_url:
            web_url = web_url.replace('__CAMPAIGN_NAME__', campaign)
            web_url = re.sub(r'tf_campaign=[^&]+', f'tf_campaign={campaign}', web_url)
        elif '?' not in web_url:
            web_url += f'?utm_source=tiktok&utm_medium=paid&utm_campaign={campaign}&tf_source=tiktok&utm_term=ad&tf_campaign={campaign}'
        df_main.at[idx, 'Web URL'] = web_url

        match = df_tags[
            (df_tags['Campaign Name'] == row['Campaign Name norm']) &
            (df_tags['Placement Name'] == row['Ad Group Name norm']) &
            (df_tags['Ad Name'] == row['Ad Name norm'])
        ]
        if not match.empty:
            imp = str(match.iloc[0]['Impression Tag (image)'])
            click = str(match.iloc[0]['Click Tag'])
            imp_url = imp.split('"')[1] if '"' in imp else ''
            df_main.at[idx, 'Impression Tracking URL'] = imp_url
            df_main.at[idx, 'Click Tracking URL'] = click

    df_main.drop(columns=['Campaign Name norm', 'Ad Group Name norm', 'Ad Name norm'], inplace=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_main.to_excel(writer, index=False)
    output.seek(0)
    return output
