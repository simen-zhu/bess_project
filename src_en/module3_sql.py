import sqlite3
import pandas as pd

conn = sqlite3.connect('../data/bess.db')
print("✅ Database ../data/bess.db created")

df_nrel = pd.read_csv('../data/nrel_warehouse_clean.csv')
df_bill = pd.read_csv('../data/bill_daily_data.csv')

df_nrel.to_sql('load_profile', conn, if_exists='replace', index=False)
df_bill.to_sql('bill_daily',   conn, if_exists='replace', index=False)
print(f"✅ load_profile table: {len(df_nrel)} rows")
print(f"✅ bill_daily table:   {len(df_bill)} rows")

print("\n" + "="*55)
print("Query 1: Monthly Peak Demand → Monthly Demand Charges")
print("="*55)
q1 = """
SELECT month AS Month, ROUND(MAX(kw),1) AS Peak_Demand_kW,
       ROUND(MAX(kw)*39.22,0) AS Demand_Charge_USD
FROM load_profile GROUP BY month ORDER BY month
"""
df1 = pd.read_sql(q1, conn)
print(df1.to_string(index=False))
print(f"\nAnnual demand charge total: ${df1['Demand_Charge_USD'].sum():,.0f}")

print("\n" + "="*55)
print("Query 2: Top 10 Peak Demand Intervals")
print("="*55)
q2 = """
SELECT timestamp AS Timestamp, month AS Month, hour AS Hour,
       ROUND(kw,1) AS Demand_kW,
       CASE WHEN is_weekday=1 THEN 'Weekday' ELSE 'Weekend' END AS Day_Type
FROM load_profile ORDER BY kw DESC LIMIT 10
"""
print(pd.read_sql(q2, conn).to_string(index=False))

print("\n" + "="*55)
print("Query 3: Weekday vs Weekend × Peak vs Off-Peak")
print("="*55)
q3 = """
SELECT CASE WHEN is_weekday=1 THEN 'Weekday' ELSE 'Weekend' END AS Day_Type,
       CASE WHEN is_peak=1 THEN 'Peak' ELSE 'Off-Peak' END AS Period,
       ROUND(AVG(kw),1) AS Avg_kW, ROUND(MAX(kw),1) AS Max_kW, COUNT(*) AS Points
FROM load_profile GROUP BY is_weekday, is_peak ORDER BY is_weekday DESC, is_peak DESC
"""
print(pd.read_sql(q3, conn).to_string(index=False))

print("\n" + "="*55)
print("Query 4: Battery Size → Annual Demand Charge Savings")
print("="*55)
q4 = """
SELECT month AS Month, ROUND(MAX(kw),1) AS Original_kW,
       ROUND(MAX(MAX(kw)-55,0),1) AS After_55kW,
       ROUND(MAX(MAX(kw)-80,0),1) AS After_80kW,
       ROUND(MAX(MAX(kw)-100,0),1) AS After_100kW
FROM load_profile WHERE is_peak=1 GROUP BY month ORDER BY month
"""
df4 = pd.read_sql(q4, conn)
print(df4.to_string(index=False))

NC_RATE = 39.22
orig = df4['Original_kW'].sum()
s55  = df4['After_55kW'].sum()
s80  = df4['After_80kW'].sum()
s100 = df4['After_100kW'].sum()
print(f"\nAnnual demand savings ($39.22/kW × 12 months):")
print(f"  55 kW battery:  saves ${(orig-s55)*NC_RATE:>8,.0f}/yr")
print(f"  80 kW battery:  saves ${(orig-s80)*NC_RATE:>8,.0f}/yr  ← Optimal")
print(f"  100 kW battery: saves ${(orig-s100)*NC_RATE:>8,.0f}/yr")

conn.close()
print("\n✅ Module 3 complete. bess.db saved.")
print("   ├── load_profile  (35,040 rows — NREL hourly load data)")
print("   └── bill_daily    (22 rows  — PG&E daily bill data)")
