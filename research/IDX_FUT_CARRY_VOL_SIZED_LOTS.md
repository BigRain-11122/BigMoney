# 8 % 的风险预算，摊到实测波动上：一个价差块要多少钱

generated 2026-11-26T00:09:47+08:00 | evidence cutoff 2026-11-25 | nav 1,000,000 元 | 目标波动 8.00 %

> 一句话：**1 个 IC+IM 价差块的实测波动是 13.636 %，不是声明里那个 8.963 %**。按 8 % 预算，1 块要 **1,704,500 元**资本，100 万的书**只能开 0.59 块**；而桌面推荐的那张 4 块票，在最乐观的尺子上也要花掉 **4.48 倍**预算，在压力窗（120 日 p95）下要 **12.27 倍**。

## 1. 每把尺子下的账

| 尺子 | 块波动 % | 1 块波动（元） | 1 块需要资本（元） | 100 万能开（块） | 整块 | 4 块票占用预算倍数 |
|---|---|---|---|---|---|---|
| declaration (ladder's own 4 % per unit notional) | 8.963 | 89,630 | 1,120,375 | 0.8926 | 0 | 4.4815 |
| full sample (2022-07 -> 2026-11) | 13.636 | 136,360 | 1,704,500 | 0.5867 | 0 | 6.8180 |
| 120-day rolling median | 11.691 | 116,910 | 1,461,375 | 0.6843 | 0 | 5.8455 |
| 120-day rolling p95 | 24.546 | 245,460 | 3,068,250 | 0.3259 | 0 | 12.2730 |
| 120-day rolling max | 24.704 | 247,040 | 3,088,000 | 0.3238 | 0 | 12.3520 |

- 声明与实测的差：**4.673 pp**（实测是声明的 **1.52 倍**）
- 压力窗（120 日 p95）：1 块要 **3,068,250 元**资本，100 万只能开 **0.3259 块**
- 判词：`DECLARATION_UNDERSTATES_RISK` / `PRESSURE_BENCHES_THE_BOOK` / `TICKET_EXCEEDS_BUDGET_AT_EVERY_RULER`

## 2. 历史上每 120 个交易日一个窗，能开几块

- 窗数 **933**（2023-01-17 → 2026-11-25）
- 块波动：min **5.656 %** / 中位 **11.691 %** / p95 **24.546 %** / max **24.704 %**
- 100 万能开：min **0.3238 块** / 中位 **0.6843 块** / p95 **1.3433 块** / max **1.4145 块**
- 开得起整 1 块的窗：**27.97 %**；开得起整 2 块的窗：**0.00 %**
- 整块数在历史窗里切换 **3 次**，最多 **1 块**

读法：**这本书在任何历史窗里都没有开满 2 块**，而且只有在块波动最低的那 28 % 的窗里才开得起 1 块。

## 3. 与相邻面不是同一个量（不许平均）

- `idx_fut_carry_ladder_stability`：**CROSS_FACE_MATCHES**（兄弟面 13.636 % vs 本面 13.636 %，差 0.000 pp）
- `idx_fut_carry_sizing_spec`：**DIFFERENT_BOOK_NAMED** —— 它按「1 手 IC 用 IF 对冲后的残差」定价（1 手 **1,132,145 元**），本面按「IC+IM 价差块」定价（1 块 **1,704,500 元**）。两本书不同，数字不该相等，也不该取平均。

## 4. 口径边界

- futures block only (1 lot IC + 1 lot IM); the equity sleeve, financing,
- margin and transaction costs stay in results/idx_fut_carry_ladder_risk.json
- the sizing face prices one IC lot hedged with IF, a different book; the two
- are named side by side on the page and never averaged

## 5. 复算

```
python scripts/idx_fut_carry_vol_sized_lots.py run
python scripts/idx_fut_carry_vol_sized_lots.py check     # 漂移说 STALE，同输入不符说 CHECK FAILED
python scripts/idx_fut_carry_vol_sized_lots.py --selftest
```
