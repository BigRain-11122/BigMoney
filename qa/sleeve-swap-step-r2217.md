# r2217 — 袖读数的档位里，有多少是「挂着哪 20 只」

**本轮产品面**：CEO 一页纸 ⑩b（`docs/live_usage/LIVE-2026-11-28.md`）现在在印「袖自己 20 只」的溢价读数之后，紧跟一行说明这一格档位有多少来自成员而不是贵不贵；数据源是 `results/book_pair_sleeve_turnover.json`（r2215 之前只写面、无消费者、无链腿、无冒烟腿）。

## 为什么需要这一行

⑩b 把袖自己的读数（今天 11.42%，自己的贵线 15.23%，判「不贵」）印在贵线旁边，读者会把它当成一个答案。但那个读数是「规则今天持有的 20 只券的溢价中位数」，而一次调仓会换掉其中一半（全窗 140 次换仓，中位换手 25%）。同一张面上：

| 量 | 读数 |
|---|---|
| 一次换仓单独造成的中位步长（同一天读两次，市场不动） | **2.30pp**（p90 5.98pp） |
| 普通一天（非换仓日）的读数变化中位 | 0.78pp |
| 步长 / 普通日 | **2.95x** |
| 今天读数离最近档位线的距离 | **2.17pp** |
| 全窗 81 个月末里，桶被换仓换掉的 | **16 个** |

今天 2.17pp < 2.30pp → `inside_the_swap_noise = true`：本月的档位有一部分是成员，不是贵不贵。

## 做了什么

1. **`scripts/ceo_live_usage.py`**：新增 `SLEEVE_TURNOVER_JSON/_REL` 常量与 `_sleeve_swap_step_face()`（纯引用，不重算）；⑩b 在「今天两边的读数」之后印一行判据句（步长 > 余量 / 余量 > 步长两态），并带产出面自己的 `generated`/`cutoff` 与路径（r1781 自印律）；缺面时印「今天的档位里有多少是换仓换来的，读不到」，不给 0。
2. **`Tools/s6_chain_bmc.py`**：新增链腿 `book_pair_sleeve_turnover`（check=`check`，writer=`build`），位置在父面 `book_pair_sleeve_premium` 之后、`ceo_live_usage` 之前（r1318 生产者先于消费者）。链现 417 腿。
3. **`smoke_test.py`**：新增产品腿「the sleeve page says how much of today's label is membership (r2217)」——从面自己的行重算 `inside = |margin| < step`，再核对**CEO 实际打开的那一页**（`LIVE-latest.md` ⑩b）同时印出两个数、所处那一侧的句子与产出面名（r1782/r1788 两族）。

## 证据

- `python scripts/book_pair_sleeve_turnover.py build` → `reconciled=True max_abs_diff=0.0 over 3490 days`，`verdict=THE_SWAP_ALONE_CAN_CHANGE_THE_BUCKET`
- `python scripts/book_pair_sleeve_turnover.py check` → `CHECK OK`（修的是「面停在旧输入」，用的是它自己的写者，未放宽任何腿）
- `python scripts/book_pair_sleeve_turnover.py selftest` → **14/14**
- `python scripts/ceo_live_usage.py selftest` → **ALL PASS**，含本轮两条新腿：`the second-ruler block says how much of today's label is membership (r2217)`、`the swap-step line carries the turnover face's own stamps (r2217)`
- `python Tools/s6_chain_bmc.py 2217 --only=book_pair_sleeve_turnover,ceo_live_usage` → `2/2 rc0`
- `python Tools/s6_chain_bmc.py --selftest` → **17/17 PASS**
- 全量冒烟（本轮树，跑于本改动之前的一代）：**809/810**，唯一红 `etf_book_permission_vs_size` 因 `DECISION.json` 在跑中被重写判 STALE → 用其写者 `run` 重 derive 后 `check` **CHECK OK**（未改腿）

## 诚实边界（面自带，逐条可查）

1. 成员是按父面选券公式重建的（父面不公布持仓），1e-9 对账只证明两套实现一致，不证明等于实盘书；
2. 反事实读数会丢掉换仓后摘牌的券，因此「换仓救回一个违约名字」的月份会高估换仓前的水平；
3. 三分位是粗尺：3pp 的移动落在 mid 桶里这张面看不见；
4. `churn_pp` 是中位数的中位数：两组 20 只可以有同样的中位而每只都不同，所以它是成员噪声的**下界**。
