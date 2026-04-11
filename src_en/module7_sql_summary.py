"""
Module 7 — SQL Analysis Results Summary Chart
Reads real CSV outputs and generates a 4-panel data summary visualization.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir   = os.path.join(script_dir, '../data')
output_dir = os.path.join(script_dir, '../output')

# ── Load CSVs ─────────────────────────────────────────────────────────
df_monthly  = pd.read_csv(f'{output_dir}/monthly_demand_analysis.csv')
df_battery  = pd.read_csv(f'{output_dir}/battery_savings_comparison.csv')
df_top10    = pd.read_csv(f'{output_dir}/top10_peak_intervals.csv')
df_cross    = pd.read_csv(f'{output_dir}/weekday_vs_weekend_analysis.csv')

month_labels = ['Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec']

# ── Figure setup ──────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 16))
fig.patch.set_facecolor('#f8f9fa')

fig.suptitle('BESS Analysis — SQL Query Results Summary',
             fontsize=18, fontweight='bold', color='#1a1a2e', y=0.99)
fig.text(0.5, 0.965,
         'Bay Area Industrial Warehouse  ·  PG&E B19S + Ava Community Energy  '
         '·  Data: NREL CA Climate Zone 3 Warehouse (scaled to ~320 kW peak)',
         ha='center', fontsize=9, color='#718096')

# ── Panel 1 (top-left): Monthly demand charge bar chart ───────────────
ax1 = fig.add_axes([0.04, 0.50, 0.44, 0.41])
ax1.set_facecolor('#ffffff')

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

ax1.set_title('Query 1 — Monthly Peak Demand & Demand Charges',
              fontsize=10, fontweight='bold', pad=8, loc='left')
ax1.set_xlabel('Month', fontsize=9)
ax1.set_ylabel('Demand Charge (USD)', fontsize=9)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(month_labels, fontsize=8)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
ax1.set_ylim(0, df_monthly['Demand_Charge_USD'].max() * 1.18)
ax1.grid(axis='y', alpha=0.3)
ax1.set_facecolor('#f8f9fa')

total = df_monthly['Demand_Charge_USD'].sum()
ax1.text(0.98, 0.95, f'Annual Total: ${total:,.0f}',
         transform=ax1.transAxes, ha='right', va='top',
         fontsize=9, fontweight='bold', color='#e53e3e',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                   edgecolor='#e53e3e', alpha=0.9))

# ── Panel 2 (top-right): Battery savings comparison ───────────────────
ax2 = fig.add_axes([0.54, 0.50, 0.44, 0.41])
ax2.set_facecolor('#f8f9fa')

battery_cols = ['Savings_55kW_USD','Savings_80kW_USD',
                'Savings_100kW_USD','Savings_150kW_USD']
labels_batt  = ['55 kW', '80 kW', '100 kW', '150 kW']
annual_savings = [df_battery[c].sum() for c in battery_cols]
clrs_batt = ['#fc8181','#f6ad55','#68d391','#63b3ed']

bars2 = ax2.bar(labels_batt, annual_savings, color=clrs_batt,
                alpha=0.88, width=0.55, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars2, annual_savings):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 300,
             f'${val:,.0f}', ha='center', fontsize=9,
             fontweight='bold', color='#2d3748')

# Highlight optimal
ax2.patches[1].set_edgecolor('#d69e2e')
ax2.patches[1].set_linewidth(3)
ax2.annotate('Optimal\n(best $/kW)', xy=(1, annual_savings[1]),
             xytext=(1.6, annual_savings[1] * 0.85),
             fontsize=8, color='#d69e2e', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#d69e2e', lw=1.5))

ax2.set_title('Query 4 — Annual Demand Savings by Battery Size',
              fontsize=10, fontweight='bold', pad=8, loc='left')
ax2.set_xlabel('Battery Power Rating', fontsize=9)
ax2.set_ylabel('Annual Savings (USD)', fontsize=9)
ax2.set_ylim(0, max(annual_savings) * 1.2)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax2.grid(axis='y', alpha=0.3)

# ── Panel 3 (bottom-left): Weekday vs Weekend heatmap table ───────────
ax3 = fig.add_axes([0.04, 0.03, 0.44, 0.43])
ax3.set_facecolor('#f8f9fa')
ax3.axis('off')

ax3.text(0, 1.0, 'Query 3 — Demand Profile: Weekday vs Weekend × Peak vs Off-Peak',
         transform=ax3.transAxes, fontsize=10, fontweight='bold',
         va='top', color='#2d3748')

# Draw table manually with colored cells
categories = [('Weekday', 'Peak'), ('Weekday', 'Off-Peak'),
              ('Weekend', 'Peak'), ('Weekend', 'Off-Peak')]
row_colors = ['#bee3f8','#c6f6d5','#fefcbf','#fed7d7']
headers = ['Segment', 'Avg Demand', 'Max Demand', 'Min Demand', 'Data Points']

col_x = [0.0, 0.28, 0.46, 0.64, 0.82]
row_y = [0.85, 0.68, 0.51, 0.34, 0.17]

# Header row
for j, h in enumerate(headers):
    ax3.text(col_x[j], row_y[0], h, transform=ax3.transAxes,
             fontsize=8.5, fontweight='bold', color='#2d3748', va='center')
ax3.plot([0, 1], [row_y[0] - 0.06, row_y[0] - 0.06], color='#cbd5e0',
         linewidth=1.5, transform=ax3.transAxes, clip_on=False)

for i, (day, period) in enumerate(categories):
    row = df_cross[(df_cross['Day_Type']==day) & (df_cross['Period']==period)]
    if len(row) == 0:
        continue
    r = row.iloc[0]
    y = row_y[i+1]

    # Background
    rect = plt.Rectangle((0, y-0.09), 1, 0.18,
                          transform=ax3.transAxes,
                          facecolor=row_colors[i], alpha=0.4,
                          clip_on=False)
    ax3.add_patch(rect)

    vals = [f'{day} / {period}',
            f'{r["Avg_Demand_kW"]:.1f} kW',
            f'{r["Max_Demand_kW"]:.1f} kW',
            f'{r["Min_Demand_kW"]:.1f} kW',
            f'{r["Data_Points"]:,}']
    for j, v in enumerate(vals):
        ax3.text(col_x[j], y, v, transform=ax3.transAxes,
                 fontsize=8.5, va='center',
                 fontweight='bold' if j == 0 else 'normal',
                 color='#2d3748')

# Key insight
ax3.text(0.0, 0.02,
         '⚡ Key insight: Off-peak hours drive higher MAX demand (322.9 kW) '
         'than peak hours — battery strategy must target morning ramp-up, not just 4–9 PM.',
         transform=ax3.transAxes, fontsize=8, color='#744210',
         style='italic',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#fefcbf', alpha=0.8))

# ── Panel 4 (bottom-right): Top 10 peak intervals table ──────────────
ax4 = fig.add_axes([0.54, 0.03, 0.44, 0.43])
ax4.set_facecolor('#f8f9fa')
ax4.axis('off')

ax4.text(0, 1.0, 'Query 2 — Top 10 Highest Demand Intervals (Year)',
         transform=ax4.transAxes, fontsize=10, fontweight='bold',
         va='top', color='#2d3748')

headers4 = ['Rank', 'Timestamp', 'Demand', 'Day Type', 'Period']
col_x4 = [0.0, 0.08, 0.52, 0.68, 0.86]
row_h = 0.075

for j, h in enumerate(headers4):
    ax4.text(col_x4[j], 0.88, h, transform=ax4.transAxes,
             fontsize=8.5, fontweight='bold', color='#2d3748', va='center')
ax4.plot([0, 1], [0.82, 0.82], color='#cbd5e0',
         linewidth=1.5, transform=ax4.transAxes, clip_on=False)

for i, row in df_top10.iterrows():
    y = 0.80 - (i * row_h)
    bg = '#fff5f5' if i % 2 == 0 else '#ffffff'
    rect = plt.Rectangle((0, y - 0.035), 1, row_h,
                          transform=ax4.transAxes,
                          facecolor=bg, alpha=0.8, clip_on=False)
    ax4.add_patch(rect)

    period_color = '#e53e3e' if row['Period'] == 'Peak' else '#3182ce'
    vals = [f'#{i+1}', row['Timestamp'][:16],
            f"{row['Demand_kW']:.1f} kW", row['Day_Type'], row['Period']]
    colors_row = ['#718096','#2d3748','#e53e3e','#2d3748', period_color]
    weights = ['normal','normal','bold','normal','bold']
    for j, (v, c, w) in enumerate(zip(vals, colors_row, weights)):
        ax4.text(col_x4[j], y + 0.005, v, transform=ax4.transAxes,
                 fontsize=7.8, va='center', color=c, fontweight=w)

ax4.text(0.0, 0.02,
         '⚡ Key insight: All top-10 peaks occur in February, '
         'off-peak hours (7–9 AM) on weekends — cold morning startup effect.',
         transform=ax4.transAxes, fontsize=8, color='#744210',
         style='italic',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#fefcbf', alpha=0.8))

plt.savefig(f'{output_dir}/sql_results_summary.png', dpi=150,
            bbox_inches='tight', facecolor='#f8f9fa')
plt.close()
print("✅ Saved: ../output/sql_results_summary.png")
