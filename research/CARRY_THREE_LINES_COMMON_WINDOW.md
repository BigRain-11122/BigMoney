# 三条 carry 读数放到同一本日历上之后

- 面：`results/carry_three_lines_common_window.json`｜机器：bm-c｜生成：2026-11-27T23:47:55+08:00
- 数据截止：2026-11-25｜共同窗：2018-10-22..2026-11-20｜复现腿：basis=MATCH / 两臂=MATCH

## 判词

**ORDERING_HOLDS_ON_ONE_CALENDAR** — 同一天历（2018-10-22..2026-11-20）上名次=basis_nominal > excess_hedged > carry_unhedged，所以 r2190 那张表的名次不是日历给的

第二个判词：**THE_EXTRA_DAYS_DO_NOT_BUY_THE_SHARPE**

## 同一段日历上的三条读数

| 线 | 单位 | bar | Sharpe(252) | Sharpe(244) | 年化均值 | 年化波动 | 回撤 | 同尺复现 |
|---|---|---|---|---|---|---|---|---|
| basis_nominal | compounded % | 1962 | 3.0693 | 3.0202 | 10.3116% | 3.2677% | -1.8896% | MATCH |
| excess_hedged | index points per lot | 1961 | 1.4162 | 1.3936 | 503.05 点/年 | 355.2 点/年 | -364.16 点 (-6.4% 资本) | MATCH |
| carry_unhedged | index points per lot | 1961 | 0.5057 | 0.4976 | 735.72 点/年 | 1454.81 点/年 | -2655.0 点 (-46.67% 资本) | MATCH |

点数换钱：乘数 200 元/点（`results/idx_fut_carry_one_lot_ruler.json` 的每跳金额反推），一手资本 1137862.5 元（`results/idx_fut_carry_capacity_lots.json`）。

窗口 bar 数：basis 窗内 1962 条（含锚日）/1961 条（去掉锚日，与两臂同口径），两臂 1961 条。
去掉锚日的 basis Sharpe = 3.0045（1962 条那版为 3.0202），两个切片都在这条线上方，读者不必信一个挑过的数。

## 被剪掉的那 647 天自己干了什么

| 窗口 | bar | Sharpe | CAGR | 年化波动 | 回撤 |
|---|---|---|---|---|---|
| 2017-01-18..2018-10-19 | 425 | 2.8072 | 9.0802% | 3.1138% | -1.201% |

## 逐年（basis，自己的一段日历）

| 年 | bar | Sharpe | CAGR | 回撤 |
|---|---|---|---|---|
| 2017 | 232 | 3.5742 | 6.5677% | -0.5012% |
| 2018 | 243 | 2.8049 | 11.8723% | -1.201% |
| 2019 | 244 | 3.5819 | 14.5772% | -1.2618% |
| 2020 | 243 | 3.8995 | 16.7593% | -0.8498% |
| 2021 | 243 | 3.5728 | 10.3241% | -0.6346% |
| 2022 | 242 | 2.6128 | 8.0179% | -0.7063% |
| 2023 | 242 | 3.334 | 5.2026% | -0.6188% |
| 2024 | 242 | 1.9742 | 6.2394% | -1.8896% |
| 2025 | 243 | 3.2348 | 12.4357% | -1.2237% |
| 2026 | 217 | 2.5082 | 9.8864% | -1.6569% |

## 一个被顺手发现的别扭

basis 那条按 244.0 天年化，两臂的父面按 252.0 天年化，同一天数的 Sharpe 在两种口径下差 1.0163 倍。这不是差距的来源，但它说明「三个数字并排」时连分母都没统一过。

## 同名不同窗，两个都印

- hedged arm annual vol, per lot, CNY：本面 71040.0 元/年 ↔ `results/idx_fut_carry_open_capital.json` 印 91029.0；两张面用的窗口不同（本面=两臂父面的十年回放窗，另一面=它自己的窗口）；两个都能真，读者不该拿一个去改另一个

## 现在可以说的话

- 剪到共同窗后 basis 的 Sharpe = 3.0202（252 口径 3.0693），父面印的 2.972 不是在多出的 647 天上挣的
- 三条读数现在用的是同一段日历（2018-10-22..2026-11-20），可以并排，仍不能跨单位相加
- 多出的 425 个 bar 自己的 Sharpe 也不低：剪掉它既没抬高也没压低结论，r2191 的混窗是呈现缺陷，不是数字缺陷

## 还不能说的

- 两臂的点数换成 % 借的是「一手资本」这条面：一手是一个不可分割的单位，资本更小或更大时 % 会变，点数是唯一不随账户变的读数
- 对冲残差与点位收益没有 CAGR —— 点数序列可以算复合增长，但那要求一个账户与一次不中断的滚仓，这不是本面能替读者假定的

## 复现两条腿的明细

```json
{
 "basis_own_window": {
  "bars_published": 2390,
  "bars_recomputed": 2390,
  "fields": {
   "ann_vol_pct": {
    "match": true,
    "published": 3.2463,
    "recomputed": 3.2463
   },
   "cagr_pct": {
    "match": true,
    "published": 10.069,
    "recomputed": 10.069
   },
   "days": {
    "match": true,
    "published": 2390,
    "recomputed": 2390
   },
   "mdd_pct": {
    "match": true,
    "published": -1.8896,
    "recomputed": -1.8896
   },
   "sharpe": {
    "match": true,
    "published": 2.972,
    "recomputed": 2.972
   }
  },
  "how": "CS.replay(IC, 1.5) 截父面窗口后按父面口径（244 天、复利）重算",
  "verdict": "MATCH",
  "window": [
   "2017-01-18",
   "2026-11-25"
  ]
 },
 "two_arms_common_window": {
  "bars": 1961,
  "carry_unhedged": {
   "match": true,
   "published": 0.5057,
   "recomputed": 0.5057
  },
  "excess_hedged": {
   "match": true,
   "published": 1.4162,
   "recomputed": 1.4162
  },
  "how": "CP.position_series(IC) 截 2026-11-20 + per_lot_daily(years=10)，按父面口径（252 天）重算",
  "verdict": "MATCH",
  "window": [
   "2018-10-22",
   "2026-11-20"
  ]
 }
}
```

## 怎么跑

```
python scripts/carry_three_lines_common_window.py            # 重算并写面
python scripts/carry_three_lines_common_window.py --check     # 只比对，不写
python scripts/carry_three_lines_common_window.py --selftest  # 离线自检
```

