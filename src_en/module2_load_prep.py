import pandas as pd

print("Loading NREL dataset, this may take a moment...")
df = pd.read_csv('../data/up00-ca-warehouse.csv')
print(f"Loaded: {len(df)} rows, {len(df.columns)} columns")

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
print(f"\nScale factor: {scale:.6f}")
print(f"Scaled max demand: {df['kw'].max():.1f} kW (should equal 322.9)")

df['is_peak'] = (df['hour'] >= 16) & (df['hour'] < 21)

missing = df['kw'].isna().sum()
print(f"Missing values: {missing}")
df['kw'] = df['kw'].fillna(df['kw'].mean())

print("\n=== Scaled Demand Statistics ===")
print(f"  Annual max demand:          {df['kw'].max():.1f} kW")
print(f"  Annual avg demand:          {df['kw'].mean():.1f} kW")
print(f"  Peak-hour avg demand:       {df[df['is_peak']]['kw'].mean():.1f} kW")
print(f"  Off-peak avg demand:        {df[~df['is_peak']]['kw'].mean():.1f} kW")
print(f"  Weekday peak avg:           {df[df['is_peak'] & df['is_weekday']]['kw'].mean():.1f} kW")
print(f"  Weekend peak avg:           {df[df['is_peak'] & ~df['is_weekday']]['kw'].mean():.1f} kW")

print("\n=== Monthly Max Demand ===")
monthly_max = df.groupby('month')['kw'].max()
for month, kw in monthly_max.items():
    fee = kw * 37.37
    bar = '█' * int(kw / 10)
    print(f"  Month {month:2d}: {kw:6.1f} kW  Demand charge ${fee:>8,.0f}/mo  {bar}")

df_clean = df[['timestamp','date','hour','month','dayofweek',
               'is_weekday','is_peak','kw']].copy()
df_clean.to_csv('../data/nrel_warehouse_clean.csv', index=False)

print(f"\n✅ Saved: ../data/nrel_warehouse_clean.csv")
print(f"   Rows: {len(df_clean)}")
print(f"   Columns: {len(df_clean.columns)}")
print(f"   Column names: {list(df_clean.columns)}")
