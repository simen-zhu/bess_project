import sqlite3
import pandas as pd
import os

# Use absolute path based on script location
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path     = os.path.join(script_dir, '../data/bess.db')
output_dir  = os.path.join(script_dir, '../output')

conn = sqlite3.connect(db_path)
print("✅ Connected to bess.db")

q1 = """
SELECT month AS Month, ROUND(MAX(kw),1) AS Peak_Demand_kW,
       ROUND(MAX(kw)*39.22,0) AS Demand_Charge_USD,
       ROUND(MAX(kw)*6.40,0) AS Peak_Demand_Charge_USD
FROM load_profile GROUP BY month ORDER BY month
"""
df1 = pd.read_sql(q1, conn)
df1.to_csv(f'{output_dir}/monthly_demand_analysis.csv', index=False)
print(f"✅ Saved: monthly_demand_analysis.csv")
print(df1.to_string(index=False))

q2 = """
SELECT timestamp AS Timestamp, month AS Month, hour AS Hour,
       ROUND(kw,1) AS Demand_kW,
       CASE WHEN is_weekday=1 THEN 'Weekday' ELSE 'Weekend' END AS Day_Type,
       CASE WHEN is_peak=1 THEN 'Peak' ELSE 'Off-Peak' END AS Period
FROM load_profile ORDER BY kw DESC LIMIT 10
"""
df2 = pd.read_sql(q2, conn)
df2.to_csv(f'{output_dir}/top10_peak_intervals.csv', index=False)
print(f"\n✅ Saved: top10_peak_intervals.csv")
print(df2.to_string(index=False))

q3 = """
SELECT CASE WHEN is_weekday=1 THEN 'Weekday' ELSE 'Weekend' END AS Day_Type,
       CASE WHEN is_peak=1 THEN 'Peak' ELSE 'Off-Peak' END AS Period,
       ROUND(AVG(kw),1) AS Avg_Demand_kW, ROUND(MAX(kw),1) AS Max_Demand_kW,
       ROUND(MIN(kw),1) AS Min_Demand_kW, COUNT(*) AS Data_Points
FROM load_profile GROUP BY is_weekday, is_peak ORDER BY is_weekday DESC, is_peak DESC
"""
df3 = pd.read_sql(q3, conn)
df3.to_csv(f'{output_dir}/weekday_vs_weekend_analysis.csv', index=False)
print(f"\n✅ Saved: weekday_vs_weekend_analysis.csv")
print(df3.to_string(index=False))

q4 = """
SELECT month AS Month, ROUND(MAX(kw),1) AS Original_kW,
       ROUND(MAX(MAX(kw)-55,0),1) AS After_55kW,
       ROUND(MAX(MAX(kw)-80,0),1) AS After_80kW,
       ROUND(MAX(MAX(kw)-100,0),1) AS After_100kW,
       ROUND(MAX(MAX(kw)-150,0),1) AS After_150kW
FROM load_profile WHERE is_peak=1 GROUP BY month ORDER BY month
"""
df4 = pd.read_sql(q4, conn)
NC_RATE = 39.22
df4['Savings_55kW_USD']  = (df4['Original_kW'] - df4['After_55kW'])  * NC_RATE
df4['Savings_80kW_USD']  = (df4['Original_kW'] - df4['After_80kW'])  * NC_RATE
df4['Savings_100kW_USD'] = (df4['Original_kW'] - df4['After_100kW']) * NC_RATE
df4['Savings_150kW_USD'] = (df4['Original_kW'] - df4['After_150kW']) * NC_RATE
df4.to_csv(f'{output_dir}/battery_savings_comparison.csv', index=False)
print(f"\n✅ Saved: battery_savings_comparison.csv")

orig = df4['Original_kW'].sum()
print(f"\nAnnual Savings Summary:")
print(f"  55 kW:  ${(orig-df4['After_55kW'].sum())*NC_RATE:>8,.0f}/yr")
print(f"  80 kW:  ${(orig-df4['After_80kW'].sum())*NC_RATE:>8,.0f}/yr  ← Optimal")
print(f"  100 kW: ${(orig-df4['After_100kW'].sum())*NC_RATE:>8,.0f}/yr")

conn.close()
print("\n✅ Module 5 complete. All CSVs saved to output/")
