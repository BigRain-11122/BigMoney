# QA · r2083 · 全量冒烟 33 红中的 4 条（同一根：把「哪一天」读成了「另一天」）

## 本轮结论

33 条红里 4 条是同一个缺陷族：**读者把 k / 票面 / 时间窗对到了错误的 bar 上**，于是两张面报「互相矛盾」，而矛盾其实来自日期，不来自算术。修法是改 bar，不是放宽容差。

| 红腿 | 修后 | 证据 |
|---|---|---|
| `etf_book_size_rulers_decision`（desk sentence re-derived） | 绿 | `--check` 7 field(s) re-derived, 0 mismatch；`identity_broken=[]`，判词 `SIZE_IS_A_RULER_CHOICE` |
| `etf_book_decision_line`（row re-derived from the receipts） | 绿 | `CHECK_OK 4 fields re-derived from the same receipts`；`CONFLICT_BETWEEN_RECEIPTS → NO_CUT_OWED` |
| `etf_book_permission_persistence`（lifetime re-derived） | 绿 | `--check CHECK_OK (6 leg(s) checked)`；上一轮它连 `run` 都起不来 |
| `etf_book_rebal_adoption`（published cells re-derived） | 绿 | `CHECK_OK verdict=PHASE_DEPENDENT cells=20 phases=5` |

下游随刷新同步转绿：`etf_book_rebalance_permission` 6/6（`KEEP_SUPPORTED_BY_INDEPENDENT_PATH`，permitted_k=0.435003）、`etf_book_cut_order_gap` 9/9（`ORDER_WITHIN_PERMISSION`）、`etf_book_do_or_wait` 13/13（`NOTHING_OWED_TODAY`）。

## 根因（一句话）

票面上有两个日子：`base_bar=2026-11-24`（这张票按哪个 bar 定价）与 `book_decided_at=2026-11-11`（这份名册哪天定的）。k 只在排程步上跳，两步之间隔着一整步：11-11 在 2026-10-23 那步上（k=0.460253），11-24 在 2026-11-20 那步上（k=0.458463）。r1886 的读者用 `book_decided_at` 去复算 `k_rule`，于是拿 0.460253 对一个写着 0.458463 的票面，判「恒等式破裂」，把三个消费面一起染红——而专门面 `etf_book_k_identity_bar` 早就判过 `IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP`（读者别再判一遍，r1852）。

## 修法

1. `scripts/etf_book_size_rulers_decision.py`：按 `etf_book_k_identity_bar` 已发布的 PATCH 落地——`priced_bar = tk.base_bar or tk.as_of or tk.book_decided_at`，把这一 bar 传给 `baseline_cell`。容差保持 6dp 存储精度（放宽到一整步会把相邻两行的真断裂一起盖掉）。
2. `scripts/etf_book_permission_persistence.py`：`identity_bar()` 同样按 `base_bar → as_of → book_decided_at` 取 bar，并把取用来源写进面（`identity.bar_source`）。
3. 同面自捕：FATAL 文案过去打印 `k_schedule_last`，实际比较的是 `k_schedule_at_base_bar`，于是 2026-11-25 打出 `0.458463 != 0.458463`——看起来像浮点 bug，其实是 bar bug。改为 `_identity_fatal()` 点名被比较的算子 + bar + bar 来源。
4. 自检腿 17 → 19：L18（base_bar 优先 / as_of 兜底 / 旧票面仍受检）、L19（拒绝文案必须点名被比较的那一对，且不得再打印排程尾）。

## 复现

```
python -m smoke_test                      # 全量读数 734/767 PASS（本轮修红前，wall 1030s）
python scripts\etf_book_size_rulers_decision.py --check
python scripts\etf_book_decision_line.py --check
python scripts\etf_book_permission_persistence.py --selftest   # 19/19
python scripts\etf_book_permission_persistence.py --check
python scripts\etf_book_rebal_adoption.py --check
```

## 未通过 / 未验证

- 全量 767 腿仍有 29 条红（修前 33），本轮只收 4 条；剩余清单见 `logs/smoke_legs.json`（`failed` 数组）。
- 本轮未重跑整条 S6 链，只逐面跑了受影响族；`docs/live_usage/LIVE-2026-11-25.md` 已按修后链条重生（无 CONFLICT 字样，印 `NOTHING_OWED_TODAY`）。
- 修红只动 bar 选择，未改任何判线与容差；`etf_book_k_identity_bar` 的 `PATCH` 文本保留原样（它现在描述的是已落地状态）。
