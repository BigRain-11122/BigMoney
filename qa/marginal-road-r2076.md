# QA — 1,129,566 元放哪：三只书同一把尺（r2076·bm-c）

- 面：`scripts/capital_marginal_road.py` → `results/capital_marginal_road.json`
- 页：`research/CAPITAL_MARGINAL_ROAD.md`（marker 块由 `--check` 逐字复核）
- 运行：`python scripts/capital_marginal_road.py | --check | --selftest`
- 负控：`python results/_r2076bmc_marginal_road_negctl.py`

## 验收清单

| 项 | 判据 | 实测 | 结论 |
|---|---|---|---|
| 能跑 | `run` rc0 且打印判词 | rc0，`THE_STEP_IS_PRICED_WORSE_AND_THE_RICHER_BOOK_HAS_NO_ROOM` | PASS |
| 能看 | 页面给出「同一笔钱三只书」与「下一笔钱三去处」两张表 + 判词 + 五条 caveat | `research/CAPITAL_MARGINAL_ROAD.md` marker 块 | PASS |
| 能复核 | `--check` rc0 且重算逐字段相等 + 页面块逐字相等 | `CHECK OK` rc0 | PASS |
| 离线自检 | `--selftest` 全腿 | 14/14 OK | PASS |
| 负控 | 改数→CHECK FAILED 且点名叶子；动 inputs_digest→STALE 且不含 CHECK FAILED；改页→page block；页块丢 marker→rc3；缺面→STALE face missing；复原→绿；七张上游面 sha256 恒等 | 9/9 PASS | PASS |
| 判词可分支 | 四条判词分支各有可达样例腿（含现金档分支，改版时首版该腿不可达已当场修） | selftest 6/7/8/9 腿 | PASS |
| 自证与自身一致 | 发布面必须哈希到自己的 `facts_digest`（首版漏此条，负控当场抓出「改数被页块先拦、要点名的叶子没点名」，已加 `_leaf_diffs` 与自哈希腿） | 负控腿 2 点名 `books.carry.income_cny_upper` | PASS |
| 口径不混算 | carry 收益是「一张合约名义额的 carry」而非「保证金回报」，页面 caveat 明写；回报率行按 8% 波动预算的资金梯级折算 | 页面 caveat 2 | PASS |
| 对 carry 最有利读数取上界 | 判词用 basis 面 6.599pp（上界），tape 面 6.361pp 并列印出 | 页面第一表 note 列 | PASS |
| 零污染 | 负控前后七张上游面 sha256 恒等 | 腿已断言恒等 | PASS |

## 如实未做

- 未改任何共享面（`round_reports-bm-c.md` 轮报告行与本卡属轮记账；`ceo_live_usage.py` / 冒烟腿 / S6 腿均未触碰）：本窗竞争探针 rc=3 CONTENTION，按 r1907/r1927 只落新增文件面。
- 未跑全量冒烟、未重跑 S6 链（连续第 20 轮，竞争窗；红腿读数仍是 2026-11-24T20:12:28 的 765 腿/34 红）。
- 未改心跳面 `fleet/machines/bm-c.json`（对端执行体在写）。
- ETF 书的 11.11% 是「容量线不束时」的读数，本面不改这个前提，只把它与容量事实并排印出。

## 读数（ETF 面截止 2026-11-24 / carry 面截止 2026-11-23）

- 同一笔 1,129,565.88 元：ETF 复合书 **125,495/年**（11.11%）、1 手 IC carry **79,953/年**（对资金 7.078%；tape 净读数 77,070）、现金 **20,002/年**（1.7708%）。
- carry 比 ETF 少 **45,541/年**（tape 读数少 48,425）；这不是噪声问题，是两本书的价差。
- 下一笔 129,565.88 元：进 ETF 书 14,395/年，但 ETF 书今天的容量线在 1,043,800.91，走完这一步超线 **85,764.97**，且这笔资金 60 个交易日里只有 4 天在 1% ADV 线内（6.67%）；跳 carry 一级 0→1 手，要一次拿够 1,129,566（缺 12.96%），换来的是 7.078% 而不是 11.11%。
- 结论句：钱不是瓶颈，容量与整手才是——所以下一份研究该找的是「接得住的第三条腿」，而不是把现有两本书加钱。
