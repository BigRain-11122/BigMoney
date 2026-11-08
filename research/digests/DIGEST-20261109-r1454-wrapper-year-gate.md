# DIGEST-20261109-r1454-wrapper-year-gate

**问句**：执行台真正跑的那个对象（账簿 + beta 0.20 覆盖 + GC001 现金腿），与年闸从建立起一直在判的那个对象（裸账簿），面对的是同一个判词吗？

**产物**：`scripts/etf_book_wrapper_year_gate.py`（selftest 8/8、`--check` 15/15、`run` 60s）
+ `results/etf_book_year_gate/WRAPPER-GATE.json` + S6 腿 `wrapper_year_gate` + 2 条 smoke 腿 + 卡 E460。

## 三条臂，同一窗口 2020-07-17..2026-11-06（1529 bars）

| 臂 | 构造 | k 均值 | top-2 占比 | 判词 |
|---|---|---|---|---|
| `plain_book_n5_r20_vt08` | 已采用书（8% 波动目标），无包装 | — | 0.7574 | CONDITIONAL |
| `book_plus_execution_wrapper` | 同一本书 + beta 0.20 覆盖 + repo 现金 | 0.9958 | 0.7588 | CONDITIONAL |
| `ticket_construction_plain_plus_overlay` | 票据真实构造：未加波动目标的裸书 + 同一覆盖 | 0.232~0.473 | 0.6752 | ADMIT |

- **flipped = []**：包装层没有移动任何一条判据（Y1/Y2/Y3 全过，Y4 两条臂都红）。
- **票据臂 ADMIT**，但它的 k 只有 0.23~0.47——这条通过来自「少持有」，不是来自「书更好」。面里以 `compression_note` 明写，不给干净健康证。
- 两臂 C1 容量：票据臂 4,867 万·一日 5%，已过地板；裸书/包装臂按脸尺未检（null），未伪造绿。

## 顺带抓到的两件事

1. **同一 beta 目标 ≠ 同一条 k 路径**：波动目标那本书的 beta 已被压到 0.20 附近，覆盖上去 k≈1；票据那本书覆盖后 k≈0.46。同一条规则在两处实现，起点不同即另一条路径。
2. **k 复现**：票据臂 k_last 0.464029 vs 票据 `k_now` 0.460253，gap 0.003776 —— 差来自最后一个决策 bar 不同（闸窗口延伸到 11-06，票据决策停在 10-14）。gap 已印在面上并由 `--check` 每轮重算，禁手抄。

## 未做 / 未验

- 全链本轮未整跑（同树他窗在跑 smoke，pid 26048）；新腿单独跑过：selftest 8/8、`--check` 15/15。
- 票据臂的 ADMIT 不构成加仓许可：本轮只证明「判词落在哪本书上」，不证明「这本书值得更多钱」。