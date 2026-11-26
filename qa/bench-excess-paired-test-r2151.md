# QA — 配对超额检验（r2151 bm-c）

本轮产物：`scripts/bench_excess_paired_test.py`、`results/bench_excess_paired_test.json`、
`research/BENCH_EXCESS_PAIRED_TEST.md`。

## 完成定义与证据

| 项 | 判据 | 证据 | 结论 |
|---|---|---|---|
| 可运行 | `python scripts\bench_excess_paired_test.py` rc0 | 17 面 / 59 臂 / 2.2s | 过 |
| 自检 | `--selftest` 全绿 | 16/16 腿（含三条防复发腿） | 过 |
| 重建保真 | 每条重建臂与出版年化 ≤ ±0.05pp | 59/59 复现、0 条失配（json `n_arms_reproduced_within_0_05pp`） | 过 |
| 判据自洽 | se95 == 1.96×mean/t（读者手算能对上） | 自检腿「mean, t and the half width tell the same story」 | 过 |
| 覆盖诚实 | 不能重建的面逐条列出、不猜 | json `faces_skipped` 33 张 + 页面「没审的面」节 | 过 |
| 不改共享面 | 不重写任何 `results/bench_*.json`、不改 `bench_generic` | 本轮仅新增 4 个文件路径 | 过 |
| 证据时间戳 | 顶层 `evidence_cutoff` 字段 | `2026-11-26`（取自被审面各自的 evidence_cutoff 最大值） | 过 |

## 本轮抓到的两处自身缺陷（都已修并被自检钉住）

1. **SE 归一化错维度**：首版写 `se95 = 1.96·sd_annual/√bars`，分母该是 √years。
   错版让配对宽度缩水 √244≈15.6 倍，会把每一分超额都读成「显著」，且页面会自证自洽。
   修法=改用年数归一，并新增自检腿用 `se95 == 1.96·mean/t` 这个读者手算恒等式交叉校验
   ——公式写错的版本过不了这条腿。
2. **同序列相除除零**：「一本书减自己」时 sd=0 → 首版抛 ZeroDivisionError 崩，
   修成 `t=None`（无变异≠无超额），并由 `paired_clears` 归为「不过线」而不是「不可判」。

## 未做（诚实记）

- 未跑全量冒烟 `python -m smoke_test`、未跑 S6 链：本轮同宿主写入竞争
  （`results/_repo_write_contention.bm-c.json`，rc=3，对端 pid 88420 起于 23:18:12），
  按 r1907 同树多宿主律只落新增文件面。
- 未改闸：把 H1 换成任一条超额尺子要动 `bench_generic` 的 `verdict_of` 面的共享代码，
  留待拥有工作树的轮次。
