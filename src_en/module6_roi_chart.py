import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '../output')

GROSS_COST     = 112_000
SGIP           = 80_000
ITC            = 9_600
NET_COST       = 22_400
MONTHLY_SAVING = 4_900
ANNUAL_SAVING  = MONTHLY_SAVING * 12
OM_ANNUAL      = GROSS_COST * 0.015
ESC_RATE       = 0.035
DISC_RATE      = 0.05
PAYBACK        = NET_COST / ANNUAL_SAVING

years = list(range(0, 11))
cf  = [-NET_COST]
cum = [-NET_COST]
npv = -NET_COST
for y in range(1, 11):
    e = (1 + ESC_RATE) ** (y - 1)
    annual = ANNUAL_SAVING * e - OM_ANNUAL
    cf.append(annual)
    cum.append(cum[-1] + annual)
    npv += annual / (1 + DISC_RATE) ** y

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

ax_title = fig.add_axes([0, 0.88, 1, 0.12])
ax_title.set_facecolor('#1a1a2e')
ax_title.axis('off')
ax_title.text(0.5, 0.65, 'BESS Investment ROI Summary',
              ha='center', va='center', fontsize=20, fontweight='bold',
              color='white', transform=ax_title.transAxes)
ax_title.text(0.5, 0.25, 'Bay Area Industrial Warehouse  ·  PG&E B19S + Ava Community Energy  ·  Base Case: 400 kWh / 150 kW',
              ha='center', va='center', fontsize=10, color='#a0aec0',
              transform=ax_title.transAxes)

kpis = [
    ('Net Installed Cost',  f'${NET_COST:,.0f}',      'After SGIP + ITC',         '#e53e3e'),
    ('Monthly Savings',     f'${MONTHLY_SAVING:,.0f}', 'Demand + Arbitrage + DR',  '#38a169'),
    ('Simple Payback',      f'{PAYBACK:.1f} yrs',      'CA C&I typical: 2–4 yrs',  '#d69e2e'),
    ('10-Year NPV',         f'${npv/1000:.0f}k',       f'Discount rate {DISC_RATE*100:.0f}%', '#3182ce'),
    ('IRR',                 f'{irr*100:.0f}%',          'Internal rate of return',  '#805ad5'),
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

ax1 = fig.add_axes([0.04, 0.08, 0.42, 0.58])
ax1.set_facecolor('#f8f9fa')
ax1.bar(years, cf, color=['#e53e3e'] + ['#68d391'] * 10, alpha=0.7, width=0.6, zorder=2)
ax1.plot(years, cum, 'o-', color='#3182ce', linewidth=2.5,
         markersize=7, markerfacecolor='white', markeredgewidth=2, zorder=3,
         label='Cumulative cash flow')
ax1.axhline(y=0, color='#2d3748', linewidth=1, linestyle='--', alpha=0.5)
ax1.fill_between(years, cum, 0, where=[c >= 0 for c in cum],
                 alpha=0.08, color='#38a169', interpolate=True)
ax1.axvline(x=PAYBACK, color='#d69e2e', linewidth=1.5, linestyle=':', alpha=0.8)
ax1.text(PAYBACK + 0.15, min(cum) * 0.7, f'Payback\n{PAYBACK:.1f} yrs',
         fontsize=8, color='#d69e2e', fontweight='bold')
ax1.set_title('10-Year Cash Flow Projection', fontsize=11, fontweight='bold', pad=10)
ax1.set_xlabel('Year', fontsize=9)
ax1.set_ylabel('Cash Flow (USD)', fontsize=9)
ax1.set_xticks(years)
ax1.set_xticklabels(['Init'] + [f'Y{y}' for y in range(1,11)], fontsize=8)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
ax1.legend(fontsize=8, loc='upper left')
ax1.grid(axis='y', alpha=0.3, zorder=1)

ax2 = fig.add_axes([0.54, 0.08, 0.42, 0.58])
ax2.set_facecolor('#f8f9fa')
dc_monthly  = 55 * (39.22 + 6.40)
arb_monthly = 300 * 0.92 * 0.1155
dr_monthly  = (150/1000) * 60000 / 12
total_monthly = dc_monthly + arb_monthly + dr_monthly
sizes  = [dc_monthly, arb_monthly, dr_monthly]
clrs   = ['#3182ce', '#38a169', '#d69e2e']
labels = [f'Demand Reduction\n${dc_monthly:,.0f}/mo',
          f'Peak Arbitrage\n${arb_monthly:,.0f}/mo',
          f'Demand Response\n${dr_monthly:,.0f}/mo']
ax2.pie(sizes, colors=clrs, startangle=90,
        wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2))
ax2.text(0, 0, f'${total_monthly:,.0f}\nper month',
         ha='center', va='center', fontsize=13, fontweight='bold', color='#2d3748')
ax2.set_title('Monthly Revenue Breakdown', fontsize=11, fontweight='bold', pad=10)
legend_patches = [mpatches.Patch(color=c, label=l) for c, l in zip(clrs, labels)]
ax2.legend(handles=legend_patches, loc='lower center',
           bbox_to_anchor=(0.5, -0.22), fontsize=8.5, frameon=False, ncol=1)

# Incentive stack inset
ax3 = fig.add_axes([0.54, 0.08, 0.20, 0.22])
ax3.set_facecolor('white')
ax3.set_xlim(0, 1); ax3.set_ylim(0, 1)
ax3.axis('off')
ax3.text(0.5, 0.92, 'Incentive Stack', ha='center', fontsize=8,
         fontweight='bold', color='#2d3748')
items = [
    ('Gross Cost', f'${GROSS_COST:,.0f}', '#2d3748'),
    ('— SGIP',     f'-${SGIP:,.0f}',      '#38a169'),
    ('— ITC 30%',  f'-${ITC:,.0f}',       '#38a169'),
    ('Net Cost',   f'${NET_COST:,.0f}',   '#e53e3e'),
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
print("✅ Saved: roi_summary_chart.png")
