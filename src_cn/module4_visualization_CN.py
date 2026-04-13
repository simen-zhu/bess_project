import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.colors import TwoSlopeNorm

matplotlib.rcParams['font.family'] = 'Arial Unicode MS'
matplotlib.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('../data/nrel_warehouse_clean.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
peak_df = df[df['is_peak']].copy()
peak_df['month'] = peak_df['timestamp'].dt.month
monthly_peak = peak_df.groupby('month')['kw'].max()

battery_sizes = [55, 80, 100, 150]
NC_RATE = 37.37
months_list = range(1, 13)
month_labels = ['1月','2月','3月','4月','5月','6月',
                '7月','8月','9月','10月','11月','12月']

savings = []
for batt in battery_sizes:
    orig    = sum([monthly_peak[m] for m in months_list])
    reduced = sum([max(monthly_peak[m]-batt, 0) for m in months_list])
    savings.append((orig - reduced) * NC_RATE)
marginals = [savings[0]] + [savings[i]-savings[i-1] for i in range(1, len(savings))]

print("开始生成四合一图表...")
fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor('#f8f9fa')

ax1 = fig.add_subplot(2, 2, 1)
pivot = df.pivot_table(values='kw', index=df['timestamp'].dt.dayofyear, columns='hour', aggfunc='max')
norm = TwoSlopeNorm(vmin=np.percentile(pivot.values,5), vcenter=np.percentile(pivot.values,50), vmax=np.percentile(pivot.values,97))
im = ax1.imshow(pivot, aspect='auto', cmap='RdYlBu_r', interpolation='bilinear', norm=norm)
plt.colorbar(im, ax=ax1, fraction=0.04, pad=0.02, label='需量 (kW)')
month_start_days = [1,32,60,91,121,152,182,213,244,274,305,335]
month_names = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
ax1.set_yticks(month_start_days); ax1.set_yticklabels(month_names, fontsize=8)
ax1.set_xticks(range(0,24,3)); ax1.set_xticklabels([f'{h:02d}:00' for h in range(0,24,3)], fontsize=7)
ax1.axvspan(16,21,alpha=0.12,color='#1a237e',zorder=2)
ax1.axvline(x=16,color='#1a237e',linewidth=1.2,linestyle='--',alpha=0.7)
ax1.axvline(x=21,color='#1a237e',linewidth=1.2,linestyle='--',alpha=0.7)
ax1.text(18.5,8,'PG&E峰时\n16-21点',ha='center',va='top',fontsize=7,color='#1a237e',fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2',facecolor='white',alpha=0.8,edgecolor='#1a237e',linewidth=0.7))
for day in month_start_days[1:]: ax1.axhline(y=day,color='white',linewidth=0.4,alpha=0.5)
ax1.set_title('全年逐小时需量热力图\n蓝=低负荷  红=高负荷',fontsize=10,fontweight='bold')
ax1.set_xlabel('时刻',fontsize=9); ax1.set_ylabel('月份',fontsize=9); ax1.set_facecolor('#f8f9fa')

ax2 = fig.add_subplot(2, 2, 2)
peak_monthly_max  = peak_df.groupby('month')['kw'].max()
peak_monthly_mean = peak_df.groupby('month')['kw'].mean()
ax2.bar(months_list,peak_monthly_max,color='#e74c3c',alpha=0.7,label='峰时最高需量',width=0.6)
ax2.bar(months_list,peak_monthly_mean,color='#3498db',alpha=0.7,label='峰时平均需量',width=0.6)
ax2.axhline(y=55,color='#f39c12',linestyle='--',linewidth=1.8,label='55kW削减线')
ax2.axhline(y=80,color='#27ae60',linestyle='--',linewidth=1.8,label='80kW削减线（推荐）')
for m,val in zip(months_list,peak_monthly_max):
    ax2.text(m,val+1.5,f'{val:.0f}',ha='center',fontsize=7,color='#c0392b',fontweight='bold')
ax2.set_title('PG&E峰时段（16-21点）每月需量\n电池削减线对比',fontsize=10,fontweight='bold')
ax2.set_xlabel('月份',fontsize=9); ax2.set_ylabel('需量 (kW)',fontsize=9)
ax2.set_xticks(list(months_list)); ax2.set_xticklabels(month_labels,fontsize=8)
ax2.legend(fontsize=7,loc='upper right'); ax2.grid(axis='y',alpha=0.3)
ax2.set_ylim(0,200); ax2.set_facecolor('#f8f9fa')

ax3 = fig.add_subplot(2, 2, 3)
bar_labels_sz = ['55kW','80kW','100kW','150kW']
bar_colors = ['#e74c3c','#e67e22','#27ae60','#3498db']
bars = ax3.bar(bar_labels_sz,savings,color=bar_colors,alpha=0.85,width=0.5,edgecolor='white',linewidth=1.5)
for bar,saving in zip(bars,savings):
    ax3.text(bar.get_x()+bar.get_width()/2,bar.get_height()/2,f'${saving:,.0f}',
             ha='center',va='center',fontsize=11,fontweight='bold',color='white')
ax3.annotate('最优性价比',xy=(1,savings[1]),xytext=(1,savings[1]+3000),
             ha='center',fontsize=9,color='#e67e22',fontweight='bold',
             arrowprops=dict(arrowstyle='->',color='#e67e22',lw=1.5))
ax3.set_title('不同电池容量的年度需量节省',fontsize=10,fontweight='bold')
ax3.set_xlabel('电池规格',fontsize=9); ax3.set_ylabel('年度节省 (USD)',fontsize=9)
ax3.set_ylim(0,max(savings)*1.2); ax3.grid(axis='y',alpha=0.3); ax3.set_facecolor('#f8f9fa')

ax4 = fig.add_subplot(2, 2, 4)
ax4.plot(bar_labels_sz,marginals,'o-',color='#8e44ad',linewidth=2.5,
         markersize=10,markerfacecolor='white',markeredgewidth=2.5)
ax4.fill_between(range(len(marginals)),marginals,alpha=0.12,color='#8e44ad')
offsets = [2000,-2800,2000,-2800]
for i,(label,m) in enumerate(zip(bar_labels_sz,marginals)):
    ax4.text(i,m+offsets[i],f'+${m:,.0f}',ha='center',fontsize=9,fontweight='bold',color='#6c3483')
ax4.scatter([1],[marginals[1]],s=180,color='#e67e22',zorder=5)
ax4.text(1.1,marginals[1],'← 最优 80kW',fontsize=9,color='#e67e22',fontweight='bold',va='center')
ax4.set_title('边际效益递减分析\n每升一个档位比上一档多省多少',fontsize=10,fontweight='bold')
ax4.set_xlabel('电池规格',fontsize=9); ax4.set_ylabel('边际增益 (USD)',fontsize=9)
ax4.set_ylim(0,max(marginals)*1.45); ax4.set_xticks(range(len(bar_labels_sz)))
ax4.set_xticklabels(bar_labels_sz); ax4.grid(axis='y',alpha=0.3); ax4.set_facecolor('#f8f9fa')

plt.suptitle('BESS储能系统分析报告\nOakland工业仓库 | PG&E B19S + Ava Community Energy',
             fontsize=14,fontweight='bold',y=1.01)
plt.tight_layout()
plt.savefig('../output/chart_final_4in1.png',dpi=160,bbox_inches='tight',facecolor='#f8f9fa')
plt.close()
print("✅ 已保存 ../output/chart_final_4in1.png")
