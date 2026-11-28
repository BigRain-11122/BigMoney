# 商品资本线：用的是今天的价，还是 120 根的中位价？

generated 2026-11-28T22:48:15.302527+08:00 | cutoff 2026-11-27 | 本书 1000000 元 · 目标波动 8% · 活腿 3 条 · 并列尺 0.046188

问题：`results/bench_cmdty_open_capital.json` 的每手名义直接继承容量面的 `notional_cny_per_lot`，而容量面按 **120 根中位收盘价** 给一手定价。容量问「一个窗口里市场能吃多少」，用中位价是对的；资本问「今天持一手要多少钱」，是时点决策——收盘价漂离中位价越远，这条资本线说的数字就越不像今天的一手。

## 两把尺子并排（同一批腿、同一个 60 根波动窗）

| 腿 | 中位价 | 最后一根收盘 | 价差 | 年化波动 | 一手名义(中位) | 一手名义(今收) | 一手要的资本(中位) | 一手要的资本(今收) | 差 | 放得下(中位/今收) |
|---|---|---|---|---|---|---|---|---|---|---|
| AU | 901.75 | 785.84 | -12.85% | 23.82% | 901,750 | 785,840 | 4,651,094 | 4,053,247 | -12.85% | **不是** / **不是** |
| RB | 3076.00 | 3077.00 | +0.03% | 10.99% | 30,760 | 30,770 | 73,213 | 73,237 | +0.03% | **不是** / **不是** |
| SC | 585.95 | 602.40 | +2.81% | 61.04% | 585,950 | 602,400 | 7,743,710 | 7,961,107 | +2.81% | **不是** / **不是** |

**这本书各开一手的资本门槛**：中位价尺 **7,743,710** 元 → 今日收盘尺 **7,961,107** 元（差 +217,397 元 / +2.81%），绑定腿 SC → SC。

**判决**：中位价尺 `BOOK_TOO_SMALL_FOR_ONE_LOT_EACH` → 今日收盘尺 `BOOK_TOO_SMALL_FOR_ONE_LOT_EACH`；判决不变，但数字要按今天的价说。

## 这个口径往下传到哪里

一手名义不是停在这张面上的：

1. `scripts/bench_cmdty_capacity.py` 用 **120 根中位收盘价 × 乘数** 写出 `notional_cny_per_lot`；
2. `scripts/bench_cmdty_open_capital.py`（r2227）把这个数直接当每手名义，算出「各开一手要多少资本」；
3. `scripts/bench_verdict_book.py` 读那张资本面，把它印进答案簿的「离下单还差什么」一行；
4. 答案簿再被 CEO 页的 `to_order` 节消费。

也就是说，CEO 页上「商品线各开一手要 7,743,710 元」这句话，是按 120 根中位价说的。今天 AU 已经比它的中位价低 12.85%，这条腿单独的资本门槛因此被高估了 12.85%。

**为什么中位价在容量面是对的**：容量问「一个窗口里市场能吃多少」，锚在中位成交/中位价上，单日极值不该左右答案。**为什么它在资本面不对**：资本问「今天我带多少钱去开户」，是一张时点票；用窗口统计量给时点票定价，就会在金价跌 13% 的日子里报出一个买不起的旧价。

## 建议（不改任何共享面）

- 资本面（`bench_cmdty_open_capital.py`）的每手名义改用面板最后一根收盘；容量面继续用中位价。
- 若保留中位价，就必须在资本面 `limits` 里点名「每手名义按 120 根中位价，非当日价」并把当日价与中位价的价差印在同一行（今天 AU 就差 12.85%）。
- 判决今天不受影响（两把尺子都给 `BOOK_TOO_SMALL_FOR_ONE_LOT_EACH`），但 AU 那条腿的波动超额倍数会被中位价夸大：一手波动占该腿名额 **4.05x（今日价） vs 4.65x（中位价）**。

## 自检

- `median_basis_reproduces_capacity_notional` OK — diffs: 0
- `median_basis_reproduces_published_capital` OK — diffs>0.5%: 0
- `basis_gap_is_measured_not_assumed` OK — max |price drift| = 12.85% ; max |capital diff| = 12.85% (printed, not thresholded)
- `verdict_survives_the_basis_change` OK — median=BOOK_TOO_SMALL_FOR_ONE_LOT_EACH last=BOOK_TOO_SMALL_FOR_ONE_LOT_EACH agree=True

## 没有回答的问题

- the last close is one bar; a single settlement print is not a tradable price for size
- the median basis is not wrong for capacity; it is wrong for a point-in-time capital line
- neither basis models margin, which is unpriced in this repo for commodities
