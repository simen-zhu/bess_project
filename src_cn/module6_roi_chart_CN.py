"""
Module 6 — 投资回报（ROI）摘要图
生成单页投资回报可视化，包含10年现金流、月度收益拆解、激励政策叠加
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
import numpy as np
import os

matplotlib.rcParams['font.family'] = 'Arial Unicode MS'
matplotlib.rcParams['axes.unicode_minus'] = False

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '../output')

# ── 财务参数（基础方案：400 kWh / 150 kW）────────────────────────────
总成本     = 112_000   # 400 kWh × $280/kWh
SGIP补贴   = 80_000    # 400 kWh × $200/kWh
ITC抵扣    = 9_600     # 30% × (112k - 80k)
净成本     = 22_400    # 补贴后净成本
月度节省   = 4_900
年度节省   = 月度节省 * 12
年运维费   = 总成本 * 0.015
电价涨幅   = 0.035
折现率     = 0.05
静态回收期 = 净成本 / 年度节省

# 10年现金流
years = list(range(0, 11))
cf  = [-净成本]
cum = [-净成本]
npv = -净成本
for y in range(1, 11):
    e = (1 + 电价涨幅) ** (y - 1)
    annual = 年度节省 * e - 年运维费
    cf.append(annual)
    cum.append(cum[-1] + annual)
    npv += annual / (1 + 折现率) ** y

def calc_irr(cashflows):
    lo, hi = 0.01, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        pv = sum(c / (1 + mid) ** i for i, c in enumerate(cashflows))
        if pv > 0: lo = mid
        else: hi = mid
    return mid

irr = calc_irr(cf)

fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('#f8f9fa')

fig.suptitle('BESS储能投资回报摘要', fontsize=18, fontweight='bold', color='#1a1a2e', y=0.99)
fig.text(0.5, 0.965,
         '湾区工业仓库  ·  PG&E B19S + Ava Community Energy  ·  基础方案：400 kWh / 150 kW',
         ha='center', fontsize=9, color='#718096')

# ── KPI卡片 ───────────────────────────────────────────────────────────
kpis = [
    ('净安装成本',  f'${净成本:,.0f}',      'SGIP + ITC补贴后',     '#e53e3e'),
    ('月度节省',    f'${月度节省:,.0f}',     '需量+套利+需量响应',   '#38a169'),
    ('静态回收期',  f'{静态回收期:.1f}年',   '加州C&I典型：2-4年',   '#d69e2e'),
    ('10年NPV',     f'${npv/1000:.0f}k',     f'折现率{折现率*100:.0f}%', '#3182ce'),
    ('内部收益率',  f'{irr*100:.0f}%',       'IRR',                   '#805ad5'),
]
for i, (label, value, sub, color) in enumerate(kpis):
    x = 0.02 + i * 0.196
    ax = fig.add_axes([x, 0.72, 0.185, 0.14])
    ax.set_facecolor('white')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    for spine in ['top','bottom','left','right']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_color(color)
        ax.spines[spine].set_linewidth(2)
    ax.text(0.5, 0.78, label, ha='center', fontsize=9,  color='#718096')
    ax.text(0.5, 0.45, value, ha='center', fontsize=18, fontweight='bold', color=color)
    ax.text(0.5, 0.12, sub,   ha='center', fontsize=8,  color='#a0aec0')

# ── 左图：10年现金流 ──────────────────────────────────────────────────
ax1 = fig.add_axes([0.04, 0.08, 0.42, 0.58])
ax1.set_facecolor('#f8f9fa')
ax1.bar(years, cf, color=['#e53e3e'] + ['#68d391'] * 10, alpha=0.7, width=0.6, zorder=2)
ax1.plot(years, cum, 'o-', color='#3182ce', linewidth=2.5,
         markersize=7, markerfacecolor='white', markeredgewidth=2, zorder=3,
         label='累计现金流')
ax1.axhline(y=0, color='#2d3748', linewidth=1, linestyle='--', alpha=0.5)
ax1.fill_between(years, cum, 0, where=[c >= 0 for c in cum],
                 alpha=0.08, color='#38a169', interpolate=True)
ax1.axvline(x=静态回收期, color='#d69e2e', linewidth=1.5, linestyle=':', alpha=0.8)
ax1.text(静态回收期 + 0.15, min(cum) * 0.7,
         f'回收期\n{静态回收期:.1f}年',
         fontsize=8, color='#d69e2e', fontweight='bold')
ax1.set_title('10年现金流预测', fontsize=11, fontweight='bold', pad=10)
ax1.set_xlabel('年份', fontsize=9)
ax1.set_ylabel('现金流（美元）', fontsize=9)
ax1.set_xticks(years)
ax1.set_xticklabels(['初始'] + [f'第{y}年' for y in range(1,11)], fontsize=7)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
ax1.legend(fontsize=8, loc='upper left')
ax1.grid(axis='y', alpha=0.3, zorder=1)

# ── 右图：月度收益拆解 ────────────────────────────────────────────────
ax2 = fig.add_axes([0.54, 0.08, 0.42, 0.58])
ax2.set_facecolor('#f8f9fa')
dc_monthly  = 55 * (39.22 + 6.40)
arb_monthly = 300 * 0.92 * 0.1155
dr_monthly  = (150/1000) * 60000 / 12
total_monthly = dc_monthly + arb_monthly + dr_monthly
sizes  = [dc_monthly, arb_monthly, dr_monthly]
clrs   = ['#3182ce', '#38a169', '#d69e2e']
labels = [f'需量削峰\n${dc_monthly:,.0f}/月',
          f'峰谷套利\n${arb_monthly:,.0f}/月',
          f'需量响应\n${dr_monthly:,.0f}/月']
ax2.pie(sizes, colors=clrs, startangle=90,
        wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2))
ax2.text(0, 0, f'${total_monthly:,.0f}\n每月节省',
         ha='center', va='center', fontsize=13, fontweight='bold', color='#2d3748')
ax2.set_title('月度收益来源拆解', fontsize=11, fontweight='bold', pad=10)
legend_patches = [mpatches.Patch(color=c, label=l) for c, l in zip(clrs, labels)]
ax2.legend(handles=legend_patches, loc='lower center',
           bbox_to_anchor=(0.5, -0.22), fontsize=8.5, frameon=False, ncol=1)

# 激励政策叠加小表
ax3 = fig.add_axes([0.54, 0.08, 0.20, 0.22])
ax3.set_facecolor('white')
ax3.set_xlim(0, 1); ax3.set_ylim(0, 1)
ax3.axis('off')
ax3.text(0.5, 0.92, '激励政策叠加', ha='center', fontsize=8,
         fontweight='bold', color='#2d3748')
items = [
    ('总安装成本', f'${总成本:,.0f}',  '#2d3748'),
    ('— SGIP补贴', f'-${SGIP补贴:,.0f}', '#38a169'),
    ('— ITC 30%',  f'-${ITC抵扣:,.0f}',  '#38a169'),
    ('净成本',     f'${净成本:,.0f}',  '#e53e3e'),
]
for i, (label, val, color) in enumerate(items):
    y = 0.72 - i * 0.18
    ax3.text(0.05, y, label, fontsize=7.5, color='#718096')
    ax3.text(0.95, y, val, fontsize=7.5, color=color, ha='right',
             fontweight='bold' if i == 3 else 'normal')
    if i == 2:
        ax3.plot([0.05, 0.95], [y - 0.08, y - 0.08], color='#cbd5e0',
                 linewidth=0.8, transform=ax3.transAxes)

plt.savefig(f'{output_dir}/roi_summary_chart.png', dpi=160,
            bbox_inches='tight', facecolor='#f8f9fa')
plt.close()
print("✅ 已保存：../output/roi_summary_chart.png")
