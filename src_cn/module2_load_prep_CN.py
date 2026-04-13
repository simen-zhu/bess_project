import pandas as pd

print("正在读取NREL数据，文件较大请稍等...")
df = pd.read_csv('../data/up00-ca-warehouse.csv')
print(f"读取完成：{len(df)} 行，{len(df.columns)} 列")

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour']      = df['timestamp'].dt.hour
df['month']     = df['timestamp'].dt.month
df['date']      = df['timestamp'].dt.date
df['dayofweek'] = df['timestamp'].dt.dayofweek
df['is_weekday'] = df['dayofweek'] < 5

df['kw_raw'] = df['out.electricity.total.energy_consumption.kwh'] * 4

CLIENT_MAX_KW = 322.9
scale = CLIENT_MAX_KW / df['kw_raw'].max()
df['kw'] = df['kw_raw'] * scale
print(f"\n缩放比例: {scale:.6f}")
print(f"缩放后最大需量: {df['kw'].max():.1f} kW（应等于322.9）")

df['is_peak'] = (df['hour'] >= 16) & (df['hour'] < 21)

missing = df['kw'].isna().sum()
print(f"缺失值数量: {missing}")
df['kw'] = df['kw'].fillna(df['kw'].mean())

print("\n=== 缩放后需量统计 ===")
print(f"  全年最大需量:    {df['kw'].max():.1f} kW")
print(f"  全年平均需量:    {df['kw'].mean():.1f} kW")
print(f"  峰时平均需量:    {df[df['is_peak']]['kw'].mean():.1f} kW")
print(f"  谷时平均需量:    {df[~df['is_peak']]['kw'].mean():.1f} kW")
print(f"  工作日峰时均值:  {df[df['is_peak'] & df['is_weekday']]['kw'].mean():.1f} kW")
print(f"  周末峰时均值:    {df[df['is_peak'] & ~df['is_weekday']]['kw'].mean():.1f} kW")

print("\n=== 按月最大需量 ===")
monthly_max = df.groupby('month')['kw'].max()
for month, kw in monthly_max.items():
    fee = kw * 37.37
    bar = '█' * int(kw / 10)
    print(f"  {month:2d}月: {kw:6.1f} kW  需量电费${fee:>8,.0f}/月  {bar}")

df_clean = df[['timestamp','date','hour','month','dayofweek',
               'is_weekday','is_peak','kw']].copy()
df_clean.to_csv('../data/nrel_warehouse_clean.csv', index=False)

print(f"\n✅ 已保存 ../data/nrel_warehouse_clean.csv")
print(f"   行数: {len(df_clean)}")
print(f"   列数: {len(df_clean.columns)}")
print(f"   列名: {list(df_clean.columns)}")
