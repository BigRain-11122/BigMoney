# r2155 — 让上游面自己折叠复印格（r2153 的 §五 第 1、2 条）

**改的是什么**：`scripts/etf_book_cadence_regime_split.py` 的 `channels()` 过去把 6 个起跑日全当独立读数，
而 r2153 实测 2022-09-01 与 2024-03-01 从 2024Q2 起是同一本书（两条腿收益差 1.5e-13、两个成本档全对）。
现在每个分组先按 `DEDUPE_TOL_PP = 1e-9` 折叠，再算极差；`n_independent` 与 `collapsed_*` 印进逐季表，
去重前的数字保留在 `*_raw` 字段，老读者能对上历史读数。

## 一、真实面板上的读数（cutoff 2026-11-26，142 格 / 50 个 hole）

| 量 | 印出（去重后·现读数） | 去重前（raw） |
|---|---|---|
| 路径通道中位极差 | **1.997 pp**（11 个可用季度） | 1.728 pp |
| 行情段通道中位极差 | **4.454 pp**（6 本可用书） | 4.454 pp |
| 判词 | `REGIME_DOMINATES \| BOTH_CHANNELS_READ` | 同 |
| 被折叠的季度 | 2024Q2、2024Q3、2024Q4、2025Q1、2025Q2、2025Q3、2025Q4 | — |
| 被折叠的书 | 无 | — |

三个互不依赖的面在去重后给出同一个数：上游面 1.997 pp、r2153 独立检测面 2.00 pp（本次重生后）、
r2153 文档 2.00 pp。行情段通道一处未动（4.454 pp），因为没有任何一本书在自己跨季度的读数里重复 ——
这与「复印只发生在同一季度内两个起跑日之间」的物理读法一致。

## 二、闸（这次接上了，之前是孤儿面）

1. **S6 链两条腿**（`Tools/s6_chain_bmc.py` 尾部，writer 在前）：
   - `cadence_regime_split`：`check` 探针 + `run` 付费刷新。探针在旧面上确实先说 `STALE face predates the de-duped pass`
     或 `STALE input panel moved`（本轮两种都实测到），刷新后才转绿。
   - `cadence_cell_independence`：r2153 的独立检测面，读上游面字节指纹；上游重生后它立刻报
     `STALE source face moved: ... 6ba9d5636fb3 -> d87fa3e2725f`，重生后 `copies=14`。
2. **冒烟两条腿**（新子命令 `assert-dedup --leg {independent,channel}`）：
   - `independent`：任何持有复印格的季度没有被声明 → 红。
   - `channel`：去重后行情段通道不再胜过路径通道 2× → 红（判词不得靠复印撑着）。

## 三、验证记录（全部本窗实跑）

| 项 | 结果 |
|---|---|
| `etf_book_cadence_regime_split.py selftest` | **24/24 PASS**（新增 6 腿：折叠 1e-13 内、放过 1e-6、复印格正是 10.28→2.75 的成因、n_independent<n_books、collapsed 命名、raw 可印） |
| `run`（重生成面） | 58s，`REGIME_DOMINATES \| BOTH_CHANNELS_READ` |
| `check` | `CHECK_OK REGIME_SPLIT_CONSISTENT cells=142 holes=50` rc0 |
| `assert-dedup` / `--leg channel` | 均 rc0，`collapsed=2024Q2..2025Q4 path=1.997 regime=4.454` |
| 负控一（篡改 collapsed=[]） | rc1，点名「2024Q2..2025Q4 != []」 |
| 负控二（regime 篡改成 0.1） | rc1，「0.100 pp no longer clears 2.0x path 1.997 pp」 |
| 链腿 `--only=cadence_regime_split,cadence_cell_independence` | **2/2 rc0**（48.0s + 0.2s） |
| `etf_book_cadence_cell_independence.py check`（重生前） | rc3 `STALE source face moved` → 重生后 rc0（证明这张读表的腿真的跟着上游走） |

## 四、这一轮没做什么

- 没有改判词阈值（`PATH_DOMINATES_RATIO` / `REGIME_DOMINATES_RATIO` 仍是冻结值 2.0）；去重改变的是输入格数，不是门。
- 没有改 `polish()`：双因素抛光仍吃全部格（复印会同时抬高行效应与列效应的稳定性，但那属于另一个问题，
  本轮只让 spread 的那一半不再重复计数）。
- 没有回到「起跑日 vs 行情段」的上游问题；REGIME_DOMINATES 不变，只是它现在不靠复印撑着。
- 去重的容差 1e-9 pp 与 r2153 检测面同一阈值；面板上所谓「同价」实测是 1.5e-13，离 1e-9 有六个量级余量，
  离任何真实 delta 差（最小非零 gap 也是 0.05 pp 量级）有八个量级 —— 不会误折叠。
