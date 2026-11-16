# 隔夜差：同一根 bar 上，这页动了哪些数（r1761）

- 比较：`LIVE-BOOK-20261115.json` → `LIVE-BOOK-20261116.json`
- 价格依据：2026-11-13（前一天 2026-11-13）｜数据截止：2026-11-13（前一天 2026-11-13）
- 判决：**EXPLAINED_MOVES**

## 一句话
两天**是同一根 bar**（没有新数据进来），这页有 **6** 个数变了；其中 **4** 个是钟面（机器多久没说话之类，本来就该走）、**2** 个能给出解释（旧数还在页上或口径句改了）、**0** 个没解释。新增 **57** 个数字叶子、消失 **0** 个。

## 动的数（全部 6 个）

| 数字 | 昨天 | 今天 | 判读 | 依据 |
|---|---|---|---|---|
| `/authority/owner_silent_h` | 41.4 | 57.0 | CLOCK |  |
| `/cash_money/forward/gap_bp` | 50.81 | 77.79 | RECOVERED_OLD_VALUE | 昨天的 50.81 今天仍在这页上：`/cash_money/forward/gap_bp_gross`（改名，不是重算） |
| `/cash_money/forward/gap_cny` | 182.0 | 279.0 | DECLARED_RULER | 同块口径句改了：`/cash_money/forward/ruler` |
| `/fleet/rows/0/age_h` | 40.52 | 46.25 | CLOCK |  |
| `/fleet/rows/1/age_h` | 387.0 | 392.73 | CLOCK |  |
| `/fleet/rows/2/age_h` | 0.17 | 0.36 | CLOCK |  |

## 今天新出现的数（57 个）落在这几块上

- `/cash_money/block`
- `/cash_money/forward`
- `/entry_gate/gates`
- `/entry_gate/shipped_median_names`
- `/entry_gate/shipped_min_names`
- `/entry_gate/thinnest_day_names`
- `/idle_cash/arm_gap`
- `/idle_cash/arms`

## 钱的两处（同一根 bar 上改了定价口径）

- `/cash_money/forward/gap_bp`：**50.81 → 77.79**（差 26.98）｜RECOVERED_OLD_VALUE｜昨天的 50.81 今天仍在这页上：`/cash_money/forward/gap_bp_gross`（改名，不是重算）
- `/cash_money/forward/gap_cny`：**182.0 → 279.0**（差 97.0）｜DECLARED_RULER｜同块口径句改了：`/cash_money/forward/ruler`

同一个隔夜、同一根 bar、同一笔钱，这页昨天给一个答案、今天给另一个。两个答案不可能都对：走 `RECOVERED_OLD_VALUE`／`DECLARED_RULER` 的那一条说明**是新答案改了算法**（旧数还在页上或口径句改了），读的人要按新口径重读昨天的判断；没有这两条说明的，就是这页偷偷换了数。

## 怎么读

- `CLOCK`＝钟面（`age_h`/`silent_h`/`lag_days` 这类）：没有新 bar 也该走，不构成问题；但它的存在说明「哪些数允许自己走」是**名单制**的，名单写在本脚本顶部，不由数据推出来。
- `DATA_ADVANCED`＝数据推进了，所有定价读数都允许动。
- `RECOVERED_OLD_VALUE`＝昨天那个数今天还在页上，只是换了名字——那是**改名**不是重算；读的人必须知道这一点，否则会把「口径换了」读成「今天变了」。
- `DECLARED_RULER`＝同一块里的口径句（`ruler`/`basis`/`convention`）改了，位移由它自己声明；句子改了而读者没看见，等于数被悄悄换了定义。
- `UNEXPLAINED`＝既没有旧值留存、也没有口径声明——**这一档非零就是本面要报的事**。

## 未验证（如实）

- 只比**相邻两天**：更早的口径变更若在两页之前发生，本面看不见（可手工指定更多日页，未做）。
- 「旧值仍在」靠数值相等判定（相对 1e-9）：两个无关的数恰好相等的概率不低，所以 `RECOVERED_OLD_VALUE` 是**线索**不是证明，行里同时印出它在哪个键上，供人核。
- 钟面名单是写死的：新出现的钟面字段会被算成 `MOVED`，本面会如实报（宁可多报）。
- 本面不判「这个改动是否合理」，也不碰任何生产件；它只读已发布日页。
