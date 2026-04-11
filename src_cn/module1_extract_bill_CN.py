import pdfplumber
import pandas as pd
import re

pdf_path = "../data/pge_bill_sample.pdf"

REDACTIONS = {
    "FONG TA INVESTMENTS, INC.": "某工业仓库客户（已脱敏）",
    "1036 47TH AVE STE D":       "Oakland CA（地址已脱敏）",
    "2062 43RD AVE":              "（地址已脱敏）",
    "SAN FRANCISCO, CA 94116-1033": "（地址已脱敏）",
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

    print("=== 第3页原始文字（脱敏后）===")
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

print("\n=== 账单关键数字 ===")
for key, val in bill_summary.items():
    print(f"  {key:30s}: {val}")

print(f"\n=== 每日用电：提取到 {len(daily_records)} 天 ===")
df = pd.DataFrame(daily_records)
print(df.to_string(index=False))

if 'peak_rate' in bill_summary and 'offpeak_rate' in bill_summary:
    spread = (bill_summary['peak_rate'] + 0.15906) - (bill_summary['offpeak_rate'] + 0.10129)
    print(f"\n=== 峰谷价差（套利空间）===")
    print(f"  综合峰时: ${bill_summary['peak_rate'] + 0.15906:.5f}/kWh")
    print(f"  综合谷时: ${bill_summary['offpeak_rate'] + 0.10129:.5f}/kWh")
    print(f"  价差:     ${spread:.5f}/kWh")

df.to_csv('../data/bill_daily_data.csv', index=False)
pd.DataFrame([bill_summary]).to_csv('../data/bill_summary.csv', index=False)
print("\n✅ 已保存 ../data/bill_daily_data.csv 和 ../data/bill_summary.csv")
