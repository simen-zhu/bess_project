"""
Module 7 — SQL分析结果汇总图
直接读取CSV输出文件，生成四合一数据可视化汇总图
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

matplotlib.rcParams['font.family'] = 'Arial Unicode MS'
matplotlib.rcParams['axes.unicode_minus'] = False

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '../output')

# ── 读取CSV ───────────────────────────────────────────────────────────
df_monthly = pd.read_csv(f'{output_dir}/monthly_demand_analysis.csv')
df_battery = pd.read_csv(f'{output_dir}/battery_savings_comparison.csv')
df_top10   = pd.read_csv(f'{output_dir}/top10_peak_intervals.csv')
df_cross   = pd.read_csv(f'{output_dir}/weekday_vs_weekend_analysis.csv')

month_labels = ['1月','2月','3月','4月','5月','6月',
                '7月','8月','9月','10月','11月','12月']

fig = plt.figure(figsize=(18, 16))
fig.patch.set_facecolor('#f8f9fa')

fig.suptitle('BESS分析 — SQL查询结果汇总', fontsize=18, fontweight='bold',
             color='#1a1a2e', y=0.99)
fig.text(0.5, 0.965,
         '湾区工业仓库  ·  PG&E B19S + Ava Community Energy  '
         '·  数据来源：NREL加州气候区3仓库（缩放至约320kW峰值）',
         ha='center', fontsize=9, color='#718096')

# ── 图1（左上）：每月需量电费柱状图 ─────────────────────────────────
ax1 = fig.add_axes([0.04, 0.50, 0.44, 0.41])
ax1.set_facecolor('#f8f9fa')

colors = ['#e53e3e' if v == df_monthly['Peak_Demand_kW'].max()
          else '#3182ce' for v in df_monthly['Peak_Demand_kW']]
bars = ax1.bar(range(1, 13), df_monthly['Demand_Charge_USD'],
               color=colors, alpha=0.85, width=0.65,
               edgecolor='white', linewidth=1)
for bar, val, kw in zip(bars, df_monthly['Demand_Charge_USD'], df_monthly['Peak_Demand_kW']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
             f'${val/1000:.1f}k', ha='center', fontsize=7.5,
             color='#2d3748', fontweight='bold')
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
             f'{kw:.0f}kW', ha='center', fontsize=7,
             color='white', fontweight='bold')

ax1.set_title('查询1 — 每月最高需量及需量电费', fontsize=10, fontweight='bold', pad=8, loc='left')
ax1.set_xlabel('月份', fontsize=9)
ax1.set_ylabel('需量电费（美元）', fontsize=9)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(month_labels, fontsize=8)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
ax1.set_ylim(0, df_monthly['Demand_Charge_USD'].max() * 1.18)
ax1.grid(axis='y', alpha=0.3)

total = df_monthly['Demand_Charge_USD'].sum()
ax1.text(0.98, 0.95, f'年度合计：${total:,.0f}',
         transform=ax1.transAxes, ha='right', va='top',
         fontsize=9, fontweight='bold', color='#e53e3e',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                   edgecolor='#e53e3e', alpha=0.9))

# ── 图2（右上）：电池容量节省对比 ────────────────────────────────────
ax2 = fig.add_axes([0.54, 0.50, 0.44, 0.41])
ax2.set_facecolor('#f8f9fa')

battery_cols  = ['Savings_55kW_USD','Savings_80kW_USD',
                 'Savings_100kW_USD','Savings_150kW_USD']
labels_batt   = ['55 kW', '80 kW', '100 kW', '150 kW']
annual_savings = [df_battery[c].sum() for c in battery_cols]
clrs_batt = ['#fc8181','#f6ad55','#68d391','#63b3ed']

bars2 = ax2.bar(labels_batt, annual_savings, color=clrs_batt,
                alpha=0.88, width=0.55, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars2, annual_savings):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 300,
             f'${val:,.0f}', ha='center', fontsize=9,
             fontweight='bold', color='#2d3748')

ax2.patches[1].set_edgecolor('#d69e2e')
ax2.patches[1].set_linewidth(3)
ax2.annotate('最优\n（性价比最高）', xy=(1, annual_savings[1]),
             xytext=(1.6, annual_savings[1] * 0.85),
             fontsize=8, color='#d69e2e', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#d69e2e', lw=1.5))

ax2.set_title('查询4 — 不同电池容量年度需量节省', fontsize=10, fontweight='bold', pad=8, loc='left')
ax2.set_xlabel('电池功率规格', fontsize=9)
ax2.set_ylabel('年度节省（美元）', fontsize=9)
ax2.set_ylim(0, max(annual_savings) * 1.2)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax2.grid(axis='y', alpha=0.3)

# ── 图3（左下）：工作日vs周末交叉分析表 ──────────────────────────────
ax3 = fig.add_axes([0.04, 0.03, 0.44, 0.43])
ax3.set_facecolor('#f8f9fa')
ax3.axis('off')

ax3.text(0, 1.0, '查询3 — 需量特征：工作日 vs 周末 × 峰时 vs 谷时',
         transform=ax3.transAxes, fontsize=10, fontweight='bold',
         va='top', color='#2d3748')

categories = [('Weekday','Peak'), ('Weekday','Off-Peak'),
              ('Weekend','Peak'), ('Weekend','Off-Peak')]
seg_labels  = ['工作日 / 峰时', '工作日 / 谷时', '周末 / 峰时', '周末 / 谷时']
row_colors  = ['#bee3f8','#c6f6d5','#fefcbf','#fed7d7']
headers     = ['分类', '平均需量', '最高需量', '最低需量', '数据点数']
col_x       = [0.0, 0.28, 0.46, 0.64, 0.82]
row_y       = [0.85, 0.68, 0.51, 0.34, 0.17]

for j, h in enumerate(headers):
    ax3.text(col_x[j], row_y[0], h, transform=ax3.transAxes,
             fontsize=8.5, fontweight='bold', color='#2d3748', va='center')
ax3.plot([0, 1], [row_y[0] - 0.06, row_y[0] - 0.06], color='#cbd5e0',
         linewidth=1.5, transform=ax3.transAxes, clip_on=False)

for i, ((day, period), seg_label) in enumerate(zip(categories, seg_labels)):
    row = df_cross[(df_cross['Day_Type']==day) & (df_cross['Period']==period)]
    if len(row) == 0:
        continue
    r = row.iloc[0]
    y = row_y[i+1]
    rect = plt.Rectangle((0, y-0.09), 1, 0.18, transform=ax3.transAxes,
                          facecolor=row_colors[i], alpha=0.4, clip_on=False)
    ax3.add_patch(rect)
    vals = [seg_label, f'{r["Avg_Demand_kW"]:.1f} kW',
            f'{r["Max_Demand_kW"]:.1f} kW',
            f'{r["Min_Demand_kW"]:.1f} kW', f'{r["Data_Points"]:,}']
    for j, v in enumerate(vals):
        ax3.text(col_x[j], y, v, transform=ax3.transAxes,
                 fontsize=8.5, va='center',
                 fontweight='bold' if j == 0 else 'normal',
                 color='#2d3748')

ax3.text(0.0, 0.02,
         '⚡ 关键发现：谷时最高需量（322.9 kW）高于峰时——'
         '电池策略需覆盖早晨启动时段，不能只看16-21点。',
         transform=ax3.transAxes, fontsize=8, color='#744210', style='italic',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#fefcbf', alpha=0.8))

# ── 图4（右下）：全年最高需量Top10表格 ───────────────────────────────
ax4 = fig.add_axes([0.54, 0.03, 0.44, 0.43])
ax4.set_facecolor('#f8f9fa')
ax4.axis('off')

ax4.text(0, 1.0, '查询2 — 全年最高需量Top10时刻',
         transform=ax4.transAxes, fontsize=10, fontweight='bold',
         va='top', color='#2d3748')

headers4 = ['排名', '时间', '需量', '类型', '时段']
col_x4   = [0.0, 0.08, 0.52, 0.68, 0.86]
row_h    = 0.075

for j, h in enumerate(headers4):
    ax4.text(col_x4[j], 0.88, h, transform=ax4.transAxes,
             fontsize=8.5, fontweight='bold', color='#2d3748', va='center')
ax4.plot([0, 1], [0.82, 0.82], color='#cbd5e0',
         linewidth=1.5, transform=ax4.transAxes, clip_on=False)

type_map   = {'Weekday':'工作日', 'Weekend':'周末'}
period_map = {'Peak':'峰时', 'Off-Peak':'谷时'}

for i, row in df_top10.iterrows():
    y  = 0.80 - (i * row_h)
    bg = '#fff5f5' if i % 2 == 0 else '#ffffff'
    rect = plt.Rectangle((0, y-0.035), 1, row_h, transform=ax4.transAxes,
                          facecolor=bg, alpha=0.8, clip_on=False)
    ax4.add_patch(rect)
    period_color = '#e53e3e' if row['Period'] == 'Peak' else '#3182ce'
    vals = [f'#{i+1}', row['Timestamp'][:16],
            f"{row['Demand_kW']:.1f} kW",
            type_map.get(row['Day_Type'], row['Day_Type']),
            period_map.get(row['Period'], row['Period'])]
    colors_row = ['#718096','#2d3748','#e53e3e','#2d3748', period_color]
    weights    = ['normal','normal','bold','normal','bold']
    for j, (v, c, w) in enumerate(zip(vals, colors_row, weights)):
        ax4.text(col_x4[j], y + 0.005, v, transform=ax4.transAxes,
                 fontsize=7.8, va='center', color=c, fontweight=w)

ax4.text(0.0, 0.02,
         '⚡ 关键发现：Top10全部集中在2月，周末谷时07-09点——'
         '典型冷启动效应，与PG&E峰时段无关。',
         transform=ax4.transAxes, fontsize=8, color='#744210', style='italic',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#fefcbf', alpha=0.8))

plt.savefig(f'{output_dir}/sql_results_summary.png', dpi=150,
            bbox_inches='tight', facecolor='#f8f9fa')
plt.close()
print("✅ 已保存：../output/sql_results_summary.png")
