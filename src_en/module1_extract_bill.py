import pdfplumber
import pandas as pd
import re

pdf_path = "../data/pge_bill_sample.pdf"

REDACTIONS = {
    "FONG TA INVESTMENTS, INC.": "Industrial Warehouse Client (Redacted)",
    "1036 47TH AVE STE D":       "Oakland CA (Address Redacted)",
    "2062 43RD AVE":              "(Address Redacted)",
    "SAN FRANCISCO, CA 94116-1033": "(Address Redacted)",
    "OAKLAND, CA 94601":          "Oakland, CA",
    "7528832585-7":               "XXXX-X",
    "7529249326":                 "XXXXXXX",
    "1010417828":                 "XXXXXXX",
}

def redact(text):
    for original, replacement in REDACTIONS.items():
        text = text.replace(original, replacement)
    return text

daily_records = []

with pdfplumber.open(pdf_path) as pdf:
    page3 = pdf.pages[2]
    text = page3.extract_text()
    text = redact(text)

    print("=== Page 3 Raw Text (Redacted) ===")
    print(text[:500])

    pattern = r'For (\d+/\d+) 2025 kWh used off peak ([\d.]+) Peak ([\d.]+)'
    matches = re.findall(pattern, text)

    for date_str, offpeak, peak in matches:
        daily_records.append({
            'date':        f'2025/{date_str}',
            'offpeak_kwh': float(offpeak),
            'peak_kwh':    float(peak),
            'total_kwh':   float(offpeak) + float(peak),
            'peak_avg_kw': float(peak) / 5
        })

bill_summary = {}

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = redact(page.extract_text() or "")

        m = re.search(r'Max Demand\s+([\d.]+)\s+kW @ \$([\d.]+)', text)
        if m:
            bill_summary['max_demand_kw']  = float(m.group(1))
            bill_summary['nc_rate_per_kw'] = float(m.group(2))

        m = re.search(r'Peak\s+([\d,]+\.?\d*)\s+kWh @ \$([\d.]+)', text)
        if m:
            bill_summary['peak_kwh_total'] = float(m.group(1).replace(',',''))
            bill_summary['peak_rate']      = float(m.group(2))

        m = re.search(r'Off Peak\s+([\d,]+\.?\d*)\s+kWh @ \$([\d.]+)', text)
        if m:
            bill_summary['offpeak_kwh_total'] = float(m.group(1).replace(',',''))
            bill_summary['offpeak_rate']      = float(m.group(2))

        m = re.search(r'Total Usage\s+([\d,]+\.?\d+)\s+kWh', text)
        if m:
            bill_summary['total_kwh'] = float(m.group(1).replace(',',''))

print("\n=== Key Bill Figures ===")
for key, val in bill_summary.items():
    print(f"  {key:30s}: {val}")

print(f"\n=== Daily Usage: {len(daily_records)} days extracted ===")
df = pd.DataFrame(daily_records)
print(df.to_string(index=False))

if 'peak_rate' in bill_summary and 'offpeak_rate' in bill_summary:
    spread = (bill_summary['peak_rate'] + 0.15906) - (bill_summary['offpeak_rate'] + 0.10129)
    print(f"\n=== Peak/Off-Peak Price Spread (Arbitrage Opportunity) ===")
    print(f"  Blended Peak Rate:     ${bill_summary['peak_rate'] + 0.15906:.5f}/kWh")
    print(f"  Blended Off-Peak Rate: ${bill_summary['offpeak_rate'] + 0.10129:.5f}/kWh")
    print(f"  Spread:                ${spread:.5f}/kWh")

df.to_csv('../data/bill_daily_data.csv', index=False)
pd.DataFrame([bill_summary]).to_csv('../data/bill_summary.csv', index=False)
print("\n✅ Saved: ../data/bill_daily_data.csv and ../data/bill_summary.csv")
