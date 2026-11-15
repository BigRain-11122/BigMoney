# LHB「机构砸盘」腿 · 全史参考批

> 机械生成件：本页由 `scripts/moneyflow_ic_reference.py lhb-sellleg` 从 `results/lhb_sellleg.json` 直接生成，数字与判词都不是手写；
> 改数字或改判词必须重跑工具，手改本页即与 JSON 不一致。

## 一、问题

r1733 在 122 天窗口（2026-05-14 → 2026-11-10）里量到：机构净卖出那一腿未来 5 日超额 **-0.90%（t=-1.89）**，而机构净买入那一腿只有 **0.3835%（t=0.887）**。
同一批数据里卖腿的分辨率高一倍、方向为负——但 r1733 同时写下「122 天是单一政体，符号可能整个是这段行情的产物」。

本批就是那句话的判决：把同一个问题放到 LHB 全史（2020-01-02 起）上，并且**把生成这个假设的窗口排除在判决集之外**——判决集是 2020-01-02 → 2026-05-13，假设窗只作对照。

## 二、判据（看数之前冻结）

| 判据 | 阈值 | 含义 |
|---|---|---|
| C1 卖腿自身 | 均值 < 0 且 \|t\| ≥ 2.0 | 砸盘之后确实跑输，不是噪声 |
| C2 双腿价差 | 卖腿减买腿 ≤ -2.0（双样本 t） | 方向来自「净卖占比」而不是「上榜」 |
| C3 逐年一致 | ≥ 6 个自然年同号 | 不是某一年行情的产物 |
| C4 事件内对照 | 卖腿减「其它龙虎榜事件」 ≤ -2.0（双样本 t） | 不是「上榜股天生跑输」 |

四项全过才 ADMIT；ADMIT 也只买一行候选，不买袖面。

## 三、读数

| 腿 | 事件数 | 未来 5 日超额 | t |
|---|---|---|---|
| 机构净买入（占比 top 20%） | 10232 | +1.8262% | +12.914 |
| 机构净卖出（占比 bottom 20%） | 10232 | +0.0357% | +0.226 |
| 全部龙虎榜事件（对照） | 51157 | -0.1025% | -1.501 |

卖腿减买腿 -1.7905%（双样本 t=-8.438）；卖腿减其它事件 +0.1728%（t=+0.985）。

## 四、逐年（判决集）

| 年 | 事件数 | 卖腿超额 | 卖腿 t |
|---|---|---|---|
| 2020 | 1249 | +2.0108% | +3.979 |
| 2021 | 1619 | +1.5561% | +3.586 |
| 2022 | 1503 | -0.0189% | -0.047 |
| 2023 | 1520 | -1.6131% | -4.296 |
| 2024 | 1718 | -0.0552% | -0.147 |
| 2025 | 1890 | -0.2100% | -0.556 |
| 2026 | 735 | -1.4748% | -2.746 |

## 五、能不能买到（同一套四分位，换成可成交价）

龙虎榜是**当日收盘后**披露的，所以最早能买的是**次日开盘**；本表把入场从 D 日收盘换成 D+1 开盘、出场仍是 D+5 收盘，双边各扣 13.041bp（COST_X1）。

| 腿 | 事件数 | 扣费后超额 | t |
|---|---|---|---|
| 机构净买入（占比 top 20%） | 10189 | +0.3432% | +2.654 |
| 机构净卖出（占比 bottom 20%） | 10189 | +0.3327% | +2.409 |

信息面 +1.8262% → 可成交 +0.3432%，保留比例 18.8%（缺口=隔夜跳空+双边成本）。

两腿价差从信息面的 -1.7905pp 收窄到可成交面的 -0.0105pp：**排序几乎全部落在收盘到次日开盘的那一个缺口里**（买腿 +1.83pp 的信息里有 +1.48pp 在开盘时就跳掉了，剩下的差被双边成本吃掉）。

逐年扣费后买腿：2020 +1.66%、2021 +0.99%、2022 +0.31%、2023 -0.33%、2024 -0.34%、2025 +0.11%、2026 +0.13%。

**执行判：NOT_TRADABLE**（C1 净超额 t 过 / C3 逐年 5/7 年为正 不过 / C4 保留 ≥50% 不过）

## 六、判

**REJECT**（C1 不过 / C2 过 / C3 不过 / C4 不过；判决集 51157 事件，7 个自然年，其中 5 年同号）

全史对照（含假设窗，仅作上下文，不参与判决）：2020-01-02 → 2026-11-06，56808 事件，卖腿 -0.0977%（t=-0.651），买腿 +1.6613%（t=+12.356）。

## 七、诚实边界

- the test set is the panel before 2026-05-14, which removes the 122 days that generated the hypothesis but does not remove r1733's own reasoning from the author's head -- this is a cleaner test, not a pristine one
- excess is close-to-close 5-day against that day's cross-sectional median over the price universe: no cost, no open-to-open execution. This is an information test, not a tradable return
- quintile cut is computed inside whichever window is being read, so the test-set cut is not the cut the full history would pick
- LHB names are volatile by construction; C4 exists because r1733 had no control for 'being on the list' at all
- no parameter search: one horizon (5), one smoothing (none -- LHB is an event, not a series), one share definition, two legs named before the run
- the priced leg is a measurement, not a blind test: this run's own information table named the top leg before the execution panel was built, so 'tradable' here means 'the number survives cost and the overnight gap', not 'nobody had looked'
- the priced leg needs a quote on both exact sessions; a name halted on the entry or exit day is dropped instead of bridged, which removes the most volatile names from the priced sample rather than from the information one
