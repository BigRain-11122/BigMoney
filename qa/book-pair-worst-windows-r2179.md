# QA · book_pair_worst_windows · r2179

## 本司清单

| 项 | 判据 | 结果 | 证据 |
|---|---|---|---|
| 能跑 | `run` / `check` / `selftest` 三入口 | PASS | `run` 出 JSON+MD；`check` rc0 `{"ok": true, "problems": []}` |
| 算术自证 | selftest 全绿 | PASS | `SELFTEST 12/12 ALL PASS` |
| 已知真值对账 | 用父面的尺子重算，与父面已发布值 1e-6 内一致 | PASS | `reconciliation.cagr.matched=true` / `.sharpe.matched=true` |
| 规则不重写 | 只 import 父面 `load_cb/load_etf/align/blend_daily/local_stats`，权重读 `best.w_cb` | PASS | `build()` 内无策略/权重选择代码 |
| 漂移可检 | 父面数字或转债面板字节动即 STALE | PASS（代码路径） | `check()` 分支：`STALE sleeve weight moved` / `STALE blend window moved` / `STALE cb panel bytes moved` |
| 不合成数据 | 无缩放/置换/造年 | PASS | `method.no_synthesis` 字段 + 代码只做 `b/a-1` |
| 未验证如实 | 坏月≠坏年、滚动窗重叠、权重继承乐观 | PASS | 面内 `unverified[3]` 与 MD 末节逐条印出 |
| 不碰共享面 | 只新增 5 张文件，未改 `Tools/s6_chain_bmc.py` | PASS（本轮纪律） | `git status` 只含新增件 |

## 与父面的关系（探针跑过的两处，如实记录）

- 首版用「反转 years = bars/243」重算 CAGR/Sharpe → 与父面对账 **False/False**；改为调用父面 `local_stats(base=1.0)`（父面按日历日/365.25）后 **True/True**。教训：对账要用对方那把尺子，别自己造尺。
- 首版 `window_ret_at` 用 `series.loc[(date)]` 取窗口端点，实跑返回 `None`（父面 `bl` 是 `cumprod` 派生的 DatetimeIndex 序列，取法在本环境不稳）→ 改为先把索引拍成 `{str(date): 值}` 再查，重跑得到 ETF -6.62% / 组合 -4.97% / 转债 -1.83%。

## 未完成（如实）

- **未接链**：`Tools/s6_chain_bmc.py` 属共享面，本轮 `repo_write_contention` 判 `rc=3 CONTENTION`（另一宿主在写同一批共享面），按 r1927/r1907 纪律本轮禁改共享面 → 链腿留待下轮接（`--only=...` 一条腿即可）。
- **未加冒烟腿**：同上理由（`smoke_test.py` 是共享面）。
- **未跑全量冒烟**：10 分钟轮窗装不下 1142s 套件，禁读成已全绿。

## 结论

面可跑、可看、算术自证与父面对账全绿，读数（组合在最坏 12 个月少亏 1.65pp，但亏损月只有 16/32 更好，均值靠转债不跟跌）已发布到 `results/book_pair_worst_windows.md` 与 `research/BOOK_PAIR_WORST_WINDOWS.md`。**未过「上链 + 冒烟腿」这两项即未完成全部收口**，如实留账。
