"""
Module 5 — 导出SQL分析结果为CSV文件
读取bess.db数据库，运行四个分析查询，将结果保存至output/文件夹
"""

import sqlite3
import pandas as pd
import os

# 根据脚本位置自动定位数据库和输出文件夹
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path    = os.path.join(script_dir, '../data/bess.db')
output_dir = os.path.join(script_dir, '../output')

conn = sqlite3.connect(db_path)
print("✅ 已连接数据库 bess.db")

# ── 查询1：每月最高需量和需量电费 ────────────────────────────────────
q1 = """
SELECT
    month                           AS 月份,
    ROUND(MAX(kw), 1)              AS 最高需量kW,
    ROUND(MAX(kw) * 37.37, 0)     AS 需量电费USD,
    ROUND(MAX(kw) * 6.40, 0)      AS 峰时需量电费USD
FROM load_profile
GROUP BY month
ORDER BY month
"""
df1 = pd.read_sql(q1, conn)
df1.to_csv(f'{output_dir}/monthly_demand_analysis.csv', index=False)
print(f"✅ 已保存：monthly_demand_analysis.csv")
print(df1.to_string(index=False))

# ── 查询2：全年需量最高的10个时间点 ──────────────────────────────────
q2 = """
SELECT
    timestamp                      AS 时间,
    month                          AS 月,
    hour                           AS 时,
    ROUND(kw, 1)                   AS 需量kW,
    CASE WHEN is_weekday = 1
         THEN '工作日' ELSE '周末' END AS 类型,
    CASE WHEN is_peak = 1
         THEN '峰时' ELSE '谷时' END AS 时段
FROM load_profile
ORDER BY kw DESC
LIMIT 10
"""
df2 = pd.read_sql(q2, conn)
df2.to_csv(f'{output_dir}/top10_peak_intervals.csv', index=False)
print(f"\n✅ 已保存：top10_peak_intervals.csv")
print(df2.to_string(index=False))

# ── 查询3：工作日 vs 周末 × 峰时 vs 谷时 ────────────────────────────
q3 = """
SELECT
    CASE WHEN is_weekday = 1 THEN '工作日' ELSE '周末' END AS 日类型,
    CASE WHEN is_peak    = 1 THEN '峰时'   ELSE '谷时' END AS 时段,
    ROUND(AVG(kw), 1)   AS 平均需量kW,
    ROUND(MAX(kw), 1)   AS 最高需量kW,
    ROUND(MIN(kw), 1)   AS 最低需量kW,
    COUNT(*)            AS 数据点数
FROM load_profile
GROUP BY is_weekday, is_peak
ORDER BY is_weekday DESC, is_peak DESC
"""
df3 = pd.read_sql(q3, conn)
df3.to_csv(f'{output_dir}/weekday_vs_weekend_analysis.csv', index=False)
print(f"\n✅ 已保存：weekday_vs_weekend_analysis.csv")
print(df3.to_string(index=False))

# ── 查询4：不同电池容量的年度节省对比 ───────────────────────────────
q4 = """
SELECT
    month                                          AS 月份,
    ROUND(MAX(kw), 1)                             AS 原始需量kW,
    ROUND(MAX(MAX(kw) - 55,  0), 1)              AS 装55kW后kW,
    ROUND(MAX(MAX(kw) - 80,  0), 1)              AS 装80kW后kW,
    ROUND(MAX(MAX(kw) - 100, 0), 1)              AS 装100kW后kW,
    ROUND(MAX(MAX(kw) - 150, 0), 1)              AS 装150kW后kW
FROM load_profile
WHERE is_peak = 1
GROUP BY month
ORDER BY month
"""
df4 = pd.read_sql(q4, conn)
NC_RATE = 37.37
df4['55kW节省USD']  = (df4['原始需量kW'] - df4['装55kW后kW'])  * NC_RATE
df4['80kW节省USD']  = (df4['原始需量kW'] - df4['装80kW后kW'])  * NC_RATE
df4['100kW节省USD'] = (df4['原始需量kW'] - df4['装100kW后kW']) * NC_RATE
df4['150kW节省USD'] = (df4['原始需量kW'] - df4['装150kW后kW']) * NC_RATE
df4.to_csv(f'{output_dir}/battery_savings_comparison.csv', index=False)
print(f"\n✅ 已保存：battery_savings_comparison.csv")

orig = df4['原始需量kW'].sum()
print(f"\n年度需量节省对比（$37.37/kW × 12月）：")
print(f"  装55kW电池:  节省 ${(orig-df4['装55kW后kW'].sum())*NC_RATE:>8,.0f}/年")
print(f"  装80kW电池:  节省 ${(orig-df4['装80kW后kW'].sum())*NC_RATE:>8,.0f}/年  ← 最优")
print(f"  装100kW电池: 节省 ${(orig-df4['装100kW后kW'].sum())*NC_RATE:>8,.0f}/年")

conn.close()
print("\n✅ Module 5完成，所有CSV已保存至output/")
print("   ├── monthly_demand_analysis.csv")
print("   ├── top10_peak_intervals.csv")
print("   ├── weekday_vs_weekend_analysis.csv")
print("   └── battery_savings_comparison.csv")
