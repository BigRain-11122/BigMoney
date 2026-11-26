# QA — cash yardstick for every published bench arm (r2158)

- 面：`results/bench_cash_yardstick.json`（schema `bench-cash-yardstick/v1`）
- 页：`research/BENCH_CASH_YARDSTICK.md`
- 工具：`scripts/bench_cash_yardstick.py`
- 证据截止：2026-11-26 ｜ 现金腿：`data/repo_daily/GC001.csv`（2011-05-13 → 2026-11-25）

## 一、本司清单

| 项 | 判据 | 实测 | 结论 |
|---|---|---|---|
| 可跑 | `python scripts\bench_cash_yardstick.py` rc0 | rc0，17 faces / 59 arms | PASS |
| 可复算 | `--check` 从现金腿与各臂自己面板重推导，与盘面逐字段比对 | `CHECK OK: 17 faces / 59 arms` | PASS |
| 行为腿 | `--selftest` 6 腿（口径/自然日/ffill-无前视/无变异 t/判词/缺腿） | `selftest 6/6 OK` | PASS |
| 诚实腿 | 重建臂年化必须与已发布值差 ≤0.05pp，否则该臂不计入读数 | 59/59 复现（0 条被剔） | PASS |
| 上链 | `Tools\s6_chain_bmc.py` 有 check/run 对，且 check 在前 | 第 389 腿，`--only` 实跑 3.4s rc0 | PASS |
| 上冒烟 | selftest 腿 + 「面由行派生/在链上/页面带判词」腿 | 已加（r2158 两条） | 已接线（全量套件本窗未跑完，见下） |
| 面板无前视 | 现金利率取「前一根 bar 当天可观测的收盘价」，后印的利率不得回到更早 | selftest 第 3/6 腿钉死 | PASS |
| 不改共享判词 | 不写任何 bench 面、不重发 verdict | 只写自有 results/research 两件 | PASS |

## 二、读数（本轮产出）

- 17 张面、59 条臂：**跑赢现金（点估计）38 条；显著（配对 t≥1.96）1 条；显著跑输 2 条**。
- 唯一显著跑赢：`trend_single_AU_long`（2008-01→2026-11，黄金单品种趋势），超额 **+5.78 pp/年**，t=2.94。
- 显著跑输：`reversal_commodity_5d` **−6.44 pp/年**（t=−3.08）、`pair_bond_curve_60d` **−4.39 pp/年**（t=−2.25）。
- 多重比较：59 条臂按 2.5% 单边期待约 **1.5 条**假阳性，实测 1 条 → 判词 `NO_ARM_SURVIVES_MULTIPLICITY`：
  **这张面上没有任何一条臂能被证明打得过「借钱出去」。**
- 现金腿本身在各窗口年化 **2.22%~2.49%**，所以 H1 的 4.0% 绝对线里只有 **1.51~1.78 pp** 在买策略，其余买的是资金利率。

## 三、自捕（当窗修正）

1. 首版把现金年化按 `n/252` 折年，而利息按自然日累积 → 2.5% 的平价利率被印成 2.36%，
   等于悄悄压低对手。selftest 第 1 腿当场抓红，改为按**日历跨度**折年，臂与现金同口径。
2. `_as_date` 首版用 `isinstance(x, datetime.date)` 判，pandas Timestamp 是 `datetime.datetime`
   的子类 → 17 张面全部 `TypeError: Cannot compare Timestamp with datetime.date`。改为按类型恒等判。
3. 页面首版把 `%` 直接写进 `%` 格式串（`ValueError: unsupported format character`）；
   并把「单臂口径」与「本面口径」两个判词并排印，避免读者只读到前一句就走。

## 四、未做（如实）

1. 全量 `smoke_test` 未跑完（本机窗口 >10min，且 S6 全链由另一宿主在跑）；本窗以 selftest 6/6、
   `--check` rc0、链单腿实跑 rc0 直证两条新腿判据，**不宣称套件总数**。
2. 现金腿只有 GC001 一个期限、按收盘价计息；零售实际可得量与券源限制未建模。
3. 未把这张面接进 CEO 一页纸（`ceo_live_usage.py` 正被在跑的全链使用中，改共享面需另窗），
   列为下一里程碑。
4. 未改任何 bench 判词与 H1 阈值——本面只改问「对手是谁」。
