# QA — ETF 复合书帽子差额的分辨能力（r2074·bm-c）

- 面：`scripts/etf_book_cap_beta_power.py` → `results/etf_book_cap_beta_power.json`
- 页：`research/ETF_BOOK_CAP_BETA_POWER.md`（marker 块由 `--check` 逐字复核）
- 运行：`python scripts/etf_book_cap_beta_power.py run | --check | --selftest`
- 负控：`python results/_r2074bmc_cap_beta_power_negctl.py`

## 验收清单

| 项 | 判据 | 实测 | 结论 |
|---|---|---|---|
| 能跑 | `run` rc0 且打印判词 | rc0，`UNRESOLVABLE_BY_MEASUREMENT` | PASS |
| 能复核 | `--check` rc0 且重算逐字段相等 + 页面块逐字相等 | `CHECK OK` rc0 | PASS |
| 离线自检 | `--selftest` 全腿 | 17/17 OK | PASS |
| 负控 | 改数→CHECK FAILED 且点名；动 inputs→STALE 且不含 CHECK FAILED；改页→page block；缺面→STALE face missing；复原→绿 | 8/8 PASS | PASS |
| 零污染 | 负控前后两张上游面 sha256 恒等 | 恒等（腿已断言） | PASS |
| 口径不混算 | 差额与阈值同一口径（票面 k=0.435003），帽子面 β 当量口径单列并披露 +4.70% | 页面第三节三行并列 | PASS |
| 判词不靠弱证据 | 判词只用「单窗抽样抖动 ÷ 差额」，与漂移分解无关；分解段自印自由度 4.45 与区间 [0.0000, 0.2572] | 页面第一/四节 | PASS |

## 如实未做

- 未接冒烟腿 / S6 链腿（共享面，本机另有执行体在飞，按 r1907/r1927 只落新增文件面）。
- 未改 CEO 一页纸（`scripts/ceo_live_usage.py`）——待静窗后把「这个差额量不出来」一句接到帽子行。
- 未采纳任何尺子：三种读数并列，`adopted: false`。

## 读数（2026-11-24 截止）

- 争议差额 0.941pp（β 差 0.021627），帽隐含 β 0.459767。
- 单窗（306 根）抽样抖动 0.141809（β），是差额的 **6.56 倍**。
- 让差额自己达到 95% 可辨：**50,541 根日线 ≈ 207.1 年**。
- 一次读数（306 根）最小可辨超帽：**12.091pp / 120,907.12 元**（是今天差额的 12.8 倍）。
- 抖动 1σ = 61,687.30 元，是要削掉的差额（19,543.03 元）的 **3.16 倍**。
