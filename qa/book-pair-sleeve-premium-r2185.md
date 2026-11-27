# QA — 袖级溢价第二把尺（r2185 · 2026-11-27）

面：`scripts/book_pair_sleeve_premium.py` → `results/book_pair_sleeve_premium.json` + `.md`
研究页：`research/BOOK_PAIR_SLEEVE_PREMIUM.md`
读者面：`docs/live_usage/LIVE-2026-11-27.md` §⑩b

## 完成判据（本司清单）

| # | 判据 | 结果 | 证据 |
|---|---|---|---|
| 1 | 脚本可跑、产物落盘 | PASS | `run` rc0，三件写盘（JSON/MD/research） |
| 2 | 自检全绿 | PASS | `selftest` **17/17 PASS** |
| 3 | 面自洽可复算 | PASS | `check` → `{"ok": true, "kind": "CHECK OK"}` rc0 |
| 4 | 与父面口径对得上 | PASS | 袖成员重建 `rebalances=141` == 父面 `cb_dual_low.json` 同臂 `rebalances=141`；rebal/phase/n_hold/过滤/打分式逐项同源 |
| 5 | 判词由自己的行算出（禁记忆判词） | PASS | `_verify` 用 `verdict_of()` 复算，自检有「记忆判词被抓」腿 |
| 6 | 漂移自称 STALE（链才肯补写） | PASS | 自检「drift is named STALE」腿；`check` 比 `data/cb_panel.csv.gz` 与 `results/book_pair_blend.json` 的 size+mtime |
| 7 | 缺面/缺读数不当 0 | PASS | 覆盖率 <80% 的月份被丢弃并记 `months_dropped_for_coverage`；缺读数不补值 |
| 8 | 未来数据不进标签 | PASS | 标签只在上一月末读数（`label_months` 共享库）；自检「3y window reads local history」+ 父面「labels never see the future」腿 |
| 9 | 读者面拿到两个数字而不是一个 | PASS | CEO 页 §⑩b 同时印两侧当日读数（70.34% vs 8.77%）与各自贵线；自检四条页断言（含缺面只说「读不到」） |
| 10 | 页面英文散文不新增 | PASS | `zh_page_prose_census run` → `hits=7 inherited=7 new=0`（本轮把 ⑩ 的英文 rule_sentence 改成中文，债从 8 降到 7） |

## 读数（本轮定稿）

| 尺 | 空仓月 | 规则夏普 | 一直持有 | 每月边缘 | 区间 | 判词 |
|---|---|---|---|---|---|---|
| 全市场中位溢价（父面同尺） | 46/81 | 1.383 | 1.215 | +0.144pp | +0.018 … +0.275 | THE_RULE_BEATS_ITS_OWN_EXPOSURE |
| 袖自己 20 只（全史分档） | 3/81 | 1.245 | 1.215 | +0.011pp | −0.026 … +0.057 | RULE_EDGE_NOT_SEPARABLE_FROM_NOISE |
| 袖自己 20 只（近三年窗） | 28/81 | 1.255 | 1.215 | +0.054pp | −0.056 … +0.166 | RULE_EDGE_NOT_SEPARABLE_FROM_NOISE |

- 标签同桶率 **28.4%**（81 个可比月）；「市场说贵、袖自己不贵」**43 个月**，"袖贵市场不贵" 0 个月。
- 今日：市场中位 **70.34%**（贵线 32.64%）＝贵；袖自己 **8.77%**（贵线 15.23%）＝不贵；近三年窗贵线 12.28% 亦判不贵。
- 判词 **THE_ANSWER_DEPENDS_ON_WHICH_RULER**：⑩ 的「收进现金」成立与否取决于拿哪把尺。

## 未验/边界（如实）

- 袖成员是按父面选券公式重建，不是读父面持仓（父面不发布持仓）；父面若改公式，本面会跟着动而两边都不报错。
- 袖读数在调仓日会跳（2026-11-16 换掉 11/20 只，中位 16.09→6.70），故月末读数里含"手里正好是哪 20 只"的成分，覆盖率门看不见这一点。
- 单窗口（81 个可比月、一个溢价周期）。
- 只按月换手；cb/etf 两腿与权重是父面发布臂，本面不重测。
