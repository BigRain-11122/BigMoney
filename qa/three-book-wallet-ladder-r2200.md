# QA · three-book-wallet-ladder · r2200 (bm-c)

日期：2026-11-28 03:0x +0800 · 审判面：`results/three_book_wallet_ladder.json`
页面：`research/THREE_BOOK_WALLET_LADDER.md` · 脚本：`scripts/three_book_wallet_ladder.py`

本轮受同宿主竞争约束（`results/_repo_write_contention.bm-c.json` rc=3 CONTENTION，对端 interactive pid 30500 自 2026-11-27T21:54:41 存活；peer 先写 13 张共享面、重叠窗 0）：只落**新增文件面**，未改 `Tools/s6_chain_bmc.py` / `smoke_test.py` / `ceo_live_usage.py` / `CODELY.md` / 任何既有 results 面，未跑 S6 链与全量冒烟。

## 判据清单

| # | 判据 | 证据 | 结果 |
|---|---|---|---|
| 1 | 面可生成（rc0） | `python scripts\three_book_wallet_ladder.py run` → 15 档、判词 `THE_THIRD_BOOK_ENTERS_AS_ONE_CONTRACT_NOT_AS_A_WEIGHT` | PASS |
| 2 | 自检全绿 | `selftest` → **18/18 PASS** | PASS |
| 3 | 漂移守卫可用 | `check` → `OK ... 15 rungs to 2026-11-26, first lot at 1,137,862 CNY, gate closes at 2,275,725` rc0 | PASS |
| 4 | **父面锚（不自洽门）** | 1,000,000 档必须等于 `results/three_book_wallet.json` 的 `best_inside_gate`：权重 `[0.65,0.35,0.0]` 逐位相同、Sharpe 1.060401 差 0（容差 1e-6），不等即 `CHECK FAILED` | MATCH |
| 5 | **可行性重算** | `check` 对每一档重算 `wallet*w >= floor`（carry floor 1,137,862.5 / cb 25,850.2 / etf 0），15 档全过；selftest 第三条腿用 1,000,000 钱包放 50% carry 的假面证明它会红（`needs` 字样） | PASS |
| 6 | **单调性** | 可行集随钱包只增不减 ⇒ 各档最优 Sharpe 必须不降；`check` 断言此性质，selftest 用「2M 的 Sharpe 低于 1M」的假面证明它报 `CHECK FAILED` 且**不带 STALE 字样**（r1935 判据词合同） | PASS |
| 7 | 漂移说 STALE | selftest 把 inputs 的时间戳改成 1970 → rc3 且 stdout 含 `STALE` | PASS |
| 8 | 数值幂等 | 连跑两次 run，去掉 `generated` 后 JSON 稳定哈希相同 | PASS |
| 9 | 结构点由算术派生 | 首档 = 一手合约资本（91,029 / 8% = 1,137,862.5）、想要权重档 = floor / 50% = 2,275,725、两书混合首档 = floor / 0.95 = 1,197,750 —— 全部代码内计算，非手抄 | PASS |
| 10 | 不重算任何一本书 | 全部读数经 `three_book_wallet.load_books / align / vol_scale / stats / blend / weight_grid / feasible` 复用，本面只重跑「哪些格子这只钱包买得起」的搜索 | PASS |
| 11 | 不自造钱 | 页面第 5 节把 `8%×Sharpe`（父面恒等式）与 `money_cny_per_year`（各档自身波动）分列，并印 `leverage_to_8pct` 与 r2199 实测融资价 -0.217；无不含融资的杠杆收益宣称 | PASS |
| 12 | 风险漂移不隐藏 | 首档 vol 8.00% vs 1,000,000 档 6.12%，页面与 caveats 明写「跳升里有一部分是风险位移」 | PASS |

## 本轮读数（面自印）

| 钱包 | 最好组合 | Sharpe | 门还收 |
|---|---|---|---|
| 1,000,000 | ETF 65 / 转债 35 / carry 0 | 1.060 | 0.784 |
| 1,137,862（第一手） | carry 100 | 1.445 | 0.400 |
| 1,500,000 | ETF 20 / carry 80 | 1.652 | 0.193 |
| 2,000,000 | ETF 30 / 转债 10 / carry 60 | 1.815 | 0.029 |
| 2,275,725（想要权重） | ETF 35 / 转债 15 / carry 50 | 1.844 | 0.000 |

第一跳 +0.384 Sharpe 吃掉门总价 49%，代价 137,862 元（+13.79% 资本）；之后每一档的边际夏普/百万：0.87 → 0.62 → 0.36 → 0.29 → 0.11 → 0。

## 自捕（本窗）

1. 首版把 `FLOORS["carry"]`（已是 8% 预算下的一手资本）再除一次 8%，印出 14,223,281 元的假首档、跳升 0.000 —— 页面文字立刻自曝「jump 0.000 却宣称 49%」，当场改成直接用 floor。判据补两处 selftest 腿钉住。
2. 渲染串里裸 `8%` / `100%` 撞 `%` 运算符，连崩三次（ValueError: unsupported format character）——已全部转义。
3. 「这一档多花的钱买到的夏普/百万」首版用**相对 1,000,000 的平均值**冒充边际值（1.5M 档印 1.18，真实边际 0.62）——改读 `step.sharpe_per_million_cny`，表头改成「比上一档多花的钱」。
4. 机制表首行把「一手合约占用的 8% 波动预算」写成 1,137,862 元（其实是资本），改印两行：91,029 元波动消耗 / 1,137,862 元所需资本。
5. 页面 5b 与 caveats 一度把 5%/12% 档的数字各印一遍（同一测量印两次，r1639 族）——caveats 改成只指路，数字只留在表里。
6. selftest 首版有两条假腿：`no feasible cell returns None` 用了 etf（floor=0 恒可行）与一条 `or True` 的恒真断言 —— 都换成真断言（cb-only 面 / 杠杆与恒等式算术）。
