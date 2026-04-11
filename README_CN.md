# 储能系统（BESS）投资分析 — 加州工商业设施

基于 Python 的储能经济性分析工具，针对加州湾区一处高负荷工商业设施，适用于 PG&E B19S 费率（含 Ava Community Energy 发电部分）。

---

## 项目背景

加州工商业电费高企，月账单常超 **5万美元**，其中需量电费占比 30–50%。本项目以真实账单数据为基础，构建完整的数据分析流程，测算储能系统在需量削峰、峰谷套利、需量响应三个维度的投资回报。

**基础方案测算结果（400 kWh / 150 kW 系统）：**
- 补贴后净安装成本：约 $33,600
- 月度综合节省：约 $4,900
- 静态回收期：约 2.3 年
- 10年 NPV（折现率 5%）：约 $390,000
- IRR：约 140%

---

## 项目结构

```
bess_project/
├── src_en/                        # 英文注释版（对外展示）
├── src_cn/                        # 中文注释版（本文件夹）
│   ├── module1_extract_bill_CN.py    # PDF账单解析与数据提取
│   ├── module2_load_prep_CN.py       # NREL负荷数据清洗与缩放
│   ├── python3_module3_sql_CN.py     # SQLite数据库查询分析
│   └── module4_visualization_CN.py   # 四合一需量分析图表
├── data/                          # 数据文件（两个版本共用）
│   ├── bill_daily_data.csv        # 每日用电数据（M1输出）
│   ├── bill_summary.csv           # 账单关键参数（M1输出）
│   ├── nrel_warehouse_clean.csv   # 缩放后负荷数据（M2输出）
│   └── bess.db                    # SQLite数据库（M3输出）
├── output/
│   └── chart_final_4in1.png       # 四合一图表输出
├── README.md                      # 英文说明
└── README_CN.md                   # 中文说明（本文件）
```

---

## 四个模块说明

### Module 1 — 账单解析
使用 `pdfplumber` 和正则表达式从 PG&E PDF 账单中提取结构化数据，输出每日峰/谷用电量及关键费率参数。

### Module 2 — 负荷数据处理
加载 NREL 商业参考建筑数据集（加州气候区3，仓库类型），按比例缩放至客户实际最大需量约 320 kW，标记 PG&E 峰时段（每日 16:00–21:00）。

### Module 3 — SQL 分析
将清洗后的数据导入 SQLite，执行四个分析查询：每月需量电费测算、全年需量最高时刻、工作日/周末交叉分析、不同电池容量削峰效果模拟。

### Module 4 — 可视化
生成四合一 matplotlib 图表：全年热力图、月度需量对比、年度节省柱状图、边际效益递减曲线。

---

## 费率结构（PG&E B19S + Ava Community Energy）

| 费率项目 | 标准 |
|---|---|
| 非重合需量电价 | $39.22 / kW·月 |
| 峰时需量电价（PG&E + Ava 合计） | $6.40 / kW·月 |
| 综合峰时电价 | ¢34.36 / kWh |
| 综合谷时电价 | ¢22.81 / kWh |
| 峰谷价差（套利空间） | ¢11.55 / kWh |

---

## 已建模激励政策

| 项目 | 收益 |
|---|---|
| SGIP 加州自发电激励计划 | $200/kWh，上限为设备成本的90% |
| 联邦 ITC 投资税收抵免（IRA 2022） | SGIP 后净成本的 30% |
| PG&E Option S 费率 | 日度需量计费，储能友好 |
| 需量响应（容量竞价计划 CBP） | 约 $60,000/MW·年额外收入 |

---

## 数据来源

- **PG&E 账单数据**：真实账单（所有客户信息已脱敏），加州湾区工业仓库设施
- **NREL 负荷数据**：[商业参考建筑数据集](https://openei.org/wiki/Commercial_Reference_Buildings) — 加州气候区3，仓库类型

---

## 技术栈

```
Python 3.14    pdfplumber    pandas    sqlite3
matplotlib     numpy         re
```

---

## 运行方式

```bash
pip install pdfplumber pandas matplotlib numpy

cd src_cn
python module1_extract_bill_CN.py
python module2_load_prep_CN.py
python python3_module3_sql_CN.py
python module4_visualization_CN.py
```

---

## 关于作者

本项目以真实加州工商业客户案例为素材，将储能投资分析与 Python / SQL / 数据可视化学习相结合。

**作者：** Simen Zhu（朱杰鹏）
**LinkedIn：** [linkedin.com/in/simen-zhu](https://linkedin.com/in/simen-zhu)
**GitHub：** [github.com/HappyPigSummer](https://github.com/HappyPigSummer)
**微信：** 13701038811
