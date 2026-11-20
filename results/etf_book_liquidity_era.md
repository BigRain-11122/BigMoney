# 流动性闸的年代读数：同一条规则，在钱赚得最多的那一段还成不成立

证据截止 2026-11-19 · 门 100 万口径 · 每名需要 ADV 2000.0万 · 槽位 5 · 调仓 20 日

## 判词：NOT_SEPARABLE_IN_THIS_ERA（2024-2026）

在最近这一段里，容量是机械买到的，收益差读不出（2024-2026）：6/35 次调仓里 11 次需要替换，容量最薄日 27.8万 → 102.7万；B-A 0.0233 pp/月 t=0.623，B-R 0.1134 pp/月 t=1.457（35 个月）；对照前段 2020-2023 判 NOT_SEPARABLE_IN_THIS_ERA

| 段 | 调仓 | 触发 | 换名 | 容量中位 A | 容量中位 B | 容量最薄 A | 容量最薄 B | B-A pp/月 | t | B-R pp/月 | t | 判词 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020-2023 | 49 | 9 | 9 | 125.0万 | 130.8万 | 81.0万 | 100.1万 | -0.0147 | -0.671 | -0.0526 | -1.291 | NOT_SEPARABLE_IN_THIS_ERA |
| 2024-2026 | 35 | 6 | 11 | 151.0万 | 155.2万 | 27.8万 | 102.7万 | 0.0233 | 0.623 | 0.1134 | 1.457 | NOT_SEPARABLE_IN_THIS_ERA |
| 2020-2026 | 84 | 15 | 20 | 133.9万 | 145.0万 | 27.8万 | 100.1万 | 0.0015 | 0.076 | 0.0183 | 0.442 | NOT_SEPARABLE_IN_THIS_ERA |

## 触发日落在哪几年

每格=「该年调仓次数 / 其中触发了多少次替换」。**0 次触发但当年有调仓**=这一年两把尺没有分家（读作结论），与「这一年不在窗口里」不是同一件事，所以两种都印出来。

| 段 | 逐年 |
|---|---|
| 2020-2023 | 2020 13/2 · 2021 12/5 · 2022 12/0 · 2023 12/2 |
| 2024-2026 | 2024 12/3 · 2025 12/2 · 2026 11/1 |
| 2020-2026 | 2020 13/2 · 2021 12/5 · 2022 12/0 · 2023 12/2 · 2024 12/3 · 2025 12/2 · 2026 11/1 |

## 三臂全窗（本面自算，供与 r1875 对账）

| 臂 | 年化 | 夏普 | 回撤 | 换手 |
|---|---|---|---|---|
| A 在印书 | 11.38% | 1.122 | -10.56% | 1.082 |
| B 加流动性闸 | 11.40% | 1.126 | -10.56% | 1.075 |
| R 随机换同样多 | 11.15% | 1.105 | -10.56% | 1.074 |

## 与 r1875 对账

- 上游面：etf_book_liquidity_select.json（存在=True，同一证据截止=True）
- 已逐数比对：True；分歧 0 处

## 诚实边界

- the eras are the book's own IS/OOS split: slicing the SAME path twice is not two independent samples, and the late era is shorter (its t is computed on its own months and says so)
- the vol-target overlay is fitted over the whole path before slicing, so an era's sharpe is read off the same weights the published book carries -- this face re-runs the book, it does not re-fit it
- capacity is bought MECHANICALLY by B inside either era (every floored pick clears the need by construction); the uplift is not evidence, the paid price is
- the panel is a survivors sweep (r1319/r1874): names the source never served could not have been ranked in any arm of any era
- nothing here is adopted: this face prices the same rule per era; a rule that pays in only one era is a regime statement, not a gate
