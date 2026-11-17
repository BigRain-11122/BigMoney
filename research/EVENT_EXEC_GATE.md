# 事件因子的「披露即定价」闸

> 机械生成件：本页由 `scripts/event_exec_gate.py run` 从 `results/event_exec_gate.json` 生成，数字与判词都不是手写；改数字或改判词必须重跑工具，手改本页即与 JSON 不一致。

## 一、闸在量什么

所有事件族都在**同一批事件**上读三个面板，因此下面三栏是相减关系，不是三次抽样：

| 面板 | 口径 |
|---|---|
| 信息面 info | 收盘(D) → 收盘(D+5) —— 面板「知道」多少 |
| 毛可成交 gross | 次日开盘(D+1) → 收盘(D+5) —— 一个账本不用付佣金能买到多少 |
| 净可成交 net | gross 双边各扣 13.041bp —— 真正留下的 |

`隔夜缺口 = info − gross`（披露时钟拿走的）｜`成本 = gross − net`（券商拿走的）｜`保留率 = net / info`。

判词三态：**TRADABLE**（净腿自己站得住 + 足够多年份同号 + 保住 ≥50%）／**NOT_TRADABLE**（数存在但门是关的）／**NOT_JUDGEABLE**（历史太短，短日历不等于死边缘）。

## 二、读数（超额口径，判词挂在这一栏）

| 族 | 方向 | 定价事件／总事件 | 信息面 | 隔夜缺口 | 佣金残差 | 净可成交 | 净腿 t | 保留率 | 判 |
|---|---|---|---|---|---|---|---|---|---|
| 龙虎榜·机构净买 top20% | 多 | 10200／10236 | +1.8251% | +1.4847% | +0.0009% | +0.3395% | +2.63 | 18.6% | **NOT_TRADABLE** |
| 龙虎榜·机构净卖 bottom20% | 空 | 10189／10236 | +0.0035% | +0.3328% | -0.0008% | -0.3285% | -2.38 | 0.0% | **NOT_TRADABLE** |
| 涨停池·次日跟随(全部事件) | 多 | 1148／1644 | +1.3197% | +2.1643% | -0.0022% | -0.8424% | -2.15 | — | **NOT_JUDGEABLE** |

> **这一栏不是成本**：一笔对所有人都收的佣金在「减去当天的中位股票」那一步就被一起减掉了，所以「佣金残差」栏里剩下的是近似 0 的余数（本级最大 0.0022%），把它读成佣金就会得出「成本可以忽略」。真实佣金在下一张表，那才是有符号、有量纲的钱。

### 同一批事件的绝对收益（钱在哪儿）

超额是「比当天的中位股票好多少」；一笔**对所有人都一样**的佣金会在减去中位数的那一步一起被减掉，所以在超额栏里看不出代价。下表是同一批事件的绝对收益，把缺口与成本换算成钱，并给出钱面的 t 与保留率（钱面保留率 = 钱面净 / 钱面信息面）：

| 族 | 信息面 | 隔夜缺口 | 佣金成本 | 净可成交 | 净腿 t | 钱面保留率 | 每股每边成本 |
|---|---|---|---|---|---|---|---|
| 龙虎榜·机构净买 top20% | +1.7405% | +1.4547% | +0.2613% | +0.0245% | +0.18 | 1.4% | 13.065bp |
| 龙虎榜·机构净卖 bottom20% | -0.2108% | +0.3883% | -0.2621% | -0.3370% | -2.27 | 无信息可保留 | 13.105bp |
| 涨停池·次日跟随(全部事件) | -0.6679% | +1.8256% | +0.2540% | -2.7475% | -6.76 | — | 12.700bp |

（缺口与成本两栏的符号随方向：空头被扣佣时为负。可自行验算 `信息面 − 缺口 − 成本 = 净可成交`。）

### 逐年（净可成交面，符号为可交易方向）

- **龙虎榜·机构净买 top20%**：2020 +1.29%（1548）、2021 +0.77%（1902）、2022 +0.32%（1517）、2023 -0.37%（1486）、2024 -0.19%（1255）、2025 +0.22%（1681）、2026 -0.09%（811）
- **龙虎榜·机构净卖 bottom20%**：2020 -1.94%（1258）、2021 -1.76%（1313）、2022 -0.39%（1456）、2023 +1.10%（1776）、2024 -0.56%（1945）、2025 +0.13%（1683）、2026 +1.16%（758）
- **涨停池·次日跟随(全部事件)**：2026 -0.84%（1148）

## 三、判

- **龙虎榜·机构净买 top20%**：NOT_TRADABLE —— 4 of 7 years keep the sign; retains 18.6% of the information number (needs 50%)
  - 信息面 +1.74% 里，**1.45%（84%）在次日开盘就没了，0.26%（15%）交给佣金**，真正留下 +0.02%（t=0.18）；超额口径保留 18.6%。
- **龙虎榜·机构净卖 bottom20%**：NOT_TRADABLE —— the priced leg does not stand on its own (-0.3285%, t=-2.38); 3 of 7 years keep the sign; no information on this side to retain (info 0.0035%)
  - 这个方向本身没有信息：信息面 -0.21%（按这个方向做也已经是亏的），扣佣后 -0.34%（t=-2.27）——不存在「被缺口或成本吃掉」的问题，起点就是负的。
- **涨停池·次日跟随(全部事件)**：NOT_JUDGEABLE —— 1 calendar year(s) of priced history (<6): a short calendar is not a dead edge
  - 钱面（绝对值，不判词）：信息面 -0.67% → 次日开盘能买到的 -2.49% → 扣佣后 -2.75%。历史只有 1 个自然年，这里只报数不判生死。

## 四、被剔除的事件（每页都要说）

- 龙虎榜·机构净买 top20%：总 10236，信息面可读 10236，三面板同批 10200；无前瞻 bar 0（事件落在面板尾后 5 个 bar 内），入场/出场当日无报价 36（停牌不桥接）。
- 龙虎榜·机构净卖 bottom20%：总 10236，信息面可读 10236，三面板同批 10189；无前瞻 bar 0（事件落在面板尾后 5 个 bar 内），入场/出场当日无报价 47（停牌不桥接）。
- 涨停池·次日跟随(全部事件)：总 1644，信息面可读 1153，三面板同批 1148；无前瞻 bar 491（事件落在面板尾后 5 个 bar 内），入场/出场当日无报价 5（停牌不桥接）。

## 五、诚实边界

- excess is against that day's cross-sectional median over the price universe, so every number answers 'better than a random name that day', not 'up'
- the priced panels need a quote on both the exact entry and the exact exit session: a halted name is dropped, not bridged, so the priced sample is the less volatile one by construction -- the dropped count is printed, not hidden
- one horizon (5), one smoothing (none: these are events, not series), no parameter search; the bars were frozen before any bucket was read
- the LHB test set stops at 2026-05-13, the window that generated the hypothesis, and the gate is applied to the legs r1734 already named -- this face adds the decomposition, not a new look at the data
- TRADABLE buys a candidate row on a desk sheet; it does not size a sleeve and it does not open a lane
- the 涨停池 family is forward-accumulating since 2026-10-08, so its verdict is NOT_JUDGEABLE by construction -- that is the gate refusing, not a dead edge
