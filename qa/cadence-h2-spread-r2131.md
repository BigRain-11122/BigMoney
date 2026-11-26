# QA 卡 · 2025H2 跨书极差三通道分解面（r2131）

**实物**
- `scripts/etf_book_cadence_h2_spread.py`
- `results/etf_book_cadence_h2_spread.json`
- `research/ETF_BOOK_CADENCE_H2_SPREAD.md`

## 验收项

| # | 项 | 证据 | 结果 |
|---|---|---|---|
| 1 | 离线自检全绿 | `python scripts/etf_book_cadence_h2_spread.py selftest` | **31/31 PASS** |
| 2 | 面自洽 + 判决词可由面内数字重算 | `... check` | **CHECK OK quarters=20 readings=20 cells=95**（rc0） |
| 3 | 幂等 | run → sha1 → run → sha1 | **字节恒等**（`2e0108ebadd6` ×2） |
| 4 | 零重实现 | import `etf_book_cadence_regime_split.build_inputs / slice_ret / spread / quartiles` + `etf_variants_null_rolling.fast_next_open` | 面板、切片、引擎、四分位全从家族导入，无复制 |
| 5 | **窗口通道是量出来的不是假设** | 每季 `bars` 由切片那次调用同源印出 | 完整季 56–66 根（中位 60，±15% 内）；2025Q3 是 bar 最多的一季（66）→ `WINDOW_LENGTH_NOT_THE_ANSWER` |
| 6 | **随机零假设存在且保守** | 4 组打乱分数行家族（seed 20261126+d，各 95 格） | 每季取 4 组里的 **最大值** 参与比较；`null.by_quarter` 印 mean/max/runs 三面 |
| 7 | 两季不一致时不许取中位掩盖 | `verdict.h2_ratios` + `per_quarter` | 2025Q3 **0.30**（比随机窄 3.3 倍）/ 2025Q4 **1.56**（宽 56%）→ `H2_QUARTERS_DISAGREE_NOTHING_ABOVE_CHANCE` |
| 8 | 残季不进统计 | `partial_excluded=["2026Q4"]`（35 bar） | 印出但排除在 bar 平直、宽度相关、重叠相关、持久性四档判据之外；自检腿专门钉死「同一残季不标注就会翻面、标注后不翻面」 |
| 9 | 并列不许充证据 | `n_quarters_decisive` 与 `n_quarters_with_ratio` 分列 | ratio 恰 1.0 计入 with_ratio、不进 tighter/wider 两侧；自检腿钉死 |
| 10 | 词表覆盖「算不出」而不只是「不相关」 | 自检腿「常数重叠 → `OVERLAP_UNREADABLE`」 | 初版只有 `DOES_NOT_COINCIDE`，秩全相等分母 0 时错标；已补 UNREADABLE 一档并加腿 |
| 11 | 外部锚（面板漂移）| 自检腿 11：伪造 1999 指纹的面临时落盘 → `check` 必说 STALE 且 rc3 | PASS |
| 12 | 强度断言不是空嘴 | 自检腿 5/6/7/8/9c/9d 双向（chance 解释 / 超过 chance / 两季分歧 / 无一季越过线 / 平直 bar / 残季） | 每类判词都有正反夹具 |

## 本轮真读数（face 内可复算）

- 14 个可判完整季度：真实书比随机书更挤 **12 个**，更宽 **2 个**（2023Q4 1.07、2025Q4 1.56）
- 名字宽度与跨书极差秩相关 **0.30**（< 0.50 线）；持仓 Jaccard 与极差秩相关 **-0.15**
- 2026 年同形：2026Q2 IQR 13.21（宽度 30.16 / 随机 29.63）；2026Q1/Q3/Q4 为 0.33 / 1.37 / 3.07

## 已知限制（不掩盖）

- 随机零假设是打乱分数行，度量「随机挑名字在这片市场会散多宽」，不是「另一套信号会怎样」；
- 持仓是季度内调仓 bar 的名字并集（规则文本可读面），不是引擎内部状态；
- 幸存者偏差（面板只含现存 ETF）/ 无波动目标是家族既有缺口，与本轮无关但同样适用；
- 季度收益不年化、不相加。

## 未做（如实）

- 未接 S6 链腿与 smoke 腿（轮首 `repo_write_contention` **rc=3 CONTENTION**：对端交互宿主 pid 107624 在窗内已写 54 处共享面，`Tools/s6_chain_bmc.py` 与 `smoke_test.py` 属禁改共享面，r1907 同树多宿主律）；
- 未跑全量冒烟，不宣称套件总数；
- r2126 的 `money_rounding_gap_fix --apply`、r2127 的 k_axis 接线仍挂账（同一竞争约束）。
