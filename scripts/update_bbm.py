import gspread
import pandas as pd
import json
import os
import re

# ============================================================
# CONFIG
# ============================================================
SPREADSHEET_ID = '1R0eDj-1FEAh21wHK8wUl67VtM6gQb1Gv884krKcI050'

# Sheet yang di-SKIP (bukan data site)
SKIP_SHEETS = ['Pivot Table 2', 'Sheet1', 'Summary', 'README', 'Rekap']

# Output folder
OUTPUT_DIR = 'data'

# ============================================================
# AUTH
# ============================================================
creds_json = os.environ['GOOGLE_CREDENTIALS']
creds_dict = json.loads(creds_json)

scopes = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
from google.oauth2.service_account import Credentials
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)

# ============================================================
# EXPORT SEMUA SHEET
# ============================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheets = spreadsheet.worksheets()

print(f"Total sheets ditemukan: {len(worksheets)}")
print()

exported = 0
skipped = 0

for ws in worksheets:
    name = ws.title.strip()

    # Skip sheet non-data
    if name in SKIP_SHEETS:
        print(f"⏭️  Skip: {name}")
        skipped += 1
        continue

    try:
        data = ws.get_all_records()
        if not data:
            print(f"⚠️  Empty: {name} — skip")
            skipped += 1
            continue

        df = pd.DataFrame(data)

        # Validasi kolom BBM
        required_cols = ["Delivery Date", "Fuel's Type", "Qty Fuel"]
        if not all(c in df.columns for c in required_cols):
            print(f"⚠️  Kolom tidak sesuai: {name} — skip")
            skipped += 1
            continue

        # Nama file: sanitize nama sheet jadi filename
        filename = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_').upper()
        filepath = f"{OUTPUT_DIR}/{filename}.csv"

        df.to_csv(filepath, index=False)
        print(f"✅ {name} → {filename}.csv ({len(df)} rows)")
        exported += 1

    except Exception as e:
        print(f"❌ Error {name}: {e}")
        skipped += 1

print()
print(f"Done! {exported} site exported, {skipped} skipped.")
