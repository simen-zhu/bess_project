import sqlite3
import pandas as pd

conn = sqlite3.connect('../data/bess.db')
print("✅ 数据库 ../data/bess.db 已创建")

df_nrel = pd.read_csv('../data/nrel_warehouse_clean.csv')
df_bill = pd.read_csv('../data/bill_daily_data.csv')

df_nrel.to_sql('load_profile', conn, if_exists='replace', index=False)
df_bill.to_sql('bill_daily',   conn, if_exists='replace', index=False)
print(f"✅ load_profile 表：{len(df_nrel)} 行")
print(f"✅ bill_daily 表：{len(df_bill)} 行")

print("\n" + "="*55)
print("【查询1】每月最高需量 → 对应每月需量电费")
print("="*55)
q1 = """
SELECT month AS 月份, ROUND(MAX(kw),1) AS 最高需量kW,
       ROUND(MAX(kw)*37.37,0) AS 需量电费USD
FROM load_profile GROUP BY month ORDER BY month
"""
df1 = pd.read_sql(q1, conn)
print(df1.to_string(index=False))
print(f"\n全年需量电费合计: ${df1['需量电费USD'].sum():,.0f}")

print("\n" + "="*55)
print("【查询2】全年需量最高的10个时间点")
print("="*55)
q2 = """
SELECT timestamp AS 时间, month AS 月, hour AS 时,
       ROUND(kw,1) AS 需量kW,
       CASE WHEN is_weekday=1 THEN '工作日' ELSE '周末' END AS 类型
FROM load_profile ORDER BY kw DESC LIMIT 10
"""
print(pd.read_sql(q2, conn).to_string(index=False))

print("\n" + "="*55)
print("【查询3】工作日 vs 周末 × 峰时 vs 谷时")
print("="*55)
q3 = """
SELECT CASE WHEN is_weekday=1 THEN '工作日' ELSE '周末' END AS 日类型,
       CASE WHEN is_peak=1 THEN '峰时' ELSE '谷时' END AS 时段,
       ROUND(AVG(kw),1) AS 平均需量kW, ROUND(MAX(kw),1) AS 最高需量kW, COUNT(*) AS 数据点数
FROM load_profile GROUP BY is_weekday, is_peak ORDER BY is_weekday DESC, is_peak DESC
"""
print(pd.read_sql(q3, conn).to_string(index=False))

print("\n" + "="*55)
print("【查询4】不同电池容量 → 年度需量节省金额")
print("="*55)
q4 = """
SELECT month AS 月份, ROUND(MAX(kw),1) AS 原始需量kW,
       ROUND(MAX(MAX(kw)-55,0),1) AS 装55kW后kW,
       ROUND(MAX(MAX(kw)-80,0),1) AS 装80kW后kW,
       ROUND(MAX(MAX(kw)-100,0),1) AS 装100kW后kW
FROM load_profile WHERE is_peak=1 GROUP BY month ORDER BY month
"""
df4 = pd.read_sql(q4, conn)
print(df4.to_string(index=False))

NC_RATE = 37.37
orig = df4['原始需量kW'].sum()
s55  = df4['装55kW后kW'].sum()
s80  = df4['装80kW后kW'].sum()
s100 = df4['装100kW后kW'].sum()
print(f"\n年度需量节省对比（$37.37/kW×12月）：")
print(f"  装55kW电池:  节省 ${(orig-s55)*NC_RATE:>8,.0f}/年")
print(f"  装80kW电池:  节省 ${(orig-s80)*NC_RATE:>8,.0f}/年  ← 最优")
print(f"  装100kW电池: 节省 ${(orig-s100)*NC_RATE:>8,.0f}/年")

conn.close()
print("\n✅ Module 3完成，../data/bess.db 已保存")
print("   ├── load_profile  (35,040行 NREL负荷数据)")
print("   └── bill_daily    (22行 账单每日数据)")
