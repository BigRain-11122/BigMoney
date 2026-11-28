# QA · etf_book_losing_odds（bm-c r2233）

面：`results/etf_book_losing_odds.json` · 页面：`research/ETF_BOOK_LOSING_ODDS.md` · 脚本：`scripts/etf_book_losing_odds.py`

## 1. 本条回答了什么（决策相关面）

发布面一直在印平均（一年 9~11%）与最差年（-0.72%），从没印过**「随便哪天买入、持有一年，亏钱的起点有几成、最差亏多少人民币」**。
本条只量路径，不改任何判据：

| 读数（canonical 口径 = honesty lag1） | 值 |
|---|---|
| 12 个月起点总数 / 其中亏钱 | 1428 / **93（6.5%）** |
| 12 个月中位 / 最差（百万元钱包） | +9.24%（+92,404）/ **-6.47%（-64,665）** |
| 24 个月亏钱起点 | 3 / 1184（0.3%），最差 -0.16% |
| 36 个月亏钱起点 | 0 / 940，最差 +6.77% |
| 不重叠年份亏了几个 | 0 / 6 |
| 完整年份（2020-2025）最差 | 2023 +2.38%（+23,839），六年无一亏 |
| 最深洞 / 拖多久 | -10.11%（2024-07-11→2024-09-12），水下 138 bar，2025-02-11 填平 |
| 今天 | 自 2026-08-04 起仍在洞中，当前 -5.69%，已 76 bar |

## 2. 两种口径

| 口径 | 12 个月亏钱起点 | 中位 | 最差 | 最差年（含未走完 2026） |
|---|---:|---:|---:|---:|
| published_lag0（发布面一直用的） | 51 / 1428（3.6%） | +10.89% | -4.50% | -0.72% |
| honest_lag1（下单可交付的） | 93 / 1428（6.5%） | +9.24% | -6.47% | +1.22% |

一天之差把亏钱起点从 51 个推到 93 个、中位一年少 1.65pp。**判词取 honest_lag1**。

## 3. 门与证据

| 门 | 结果 |
|---|---|
| `python scripts/etf_book_losing_odds.py selftest` | **8/8 PASS**（单调上行零亏损 / 单调下行全亏 / 不重叠计数 / V 形回撤单段且填平日正确 / 未填平不报恢复 / 亏损历史永不被判成"不会亏" / 薄样本标 THIN / 年度切分保 partial 标记） |
| `python scripts/etf_book_losing_odds.py run` | rc0，写 JSON+页面（引擎重算 ≈84 s） |
| `python scripts/etf_book_losing_odds.py check` | **rc0**（页面逐字由数据重渲染比对） |
| 负控（手改页面 `93 (6.5%)` → `92 (6.4%)`） | **rc4 CHECK FAILED @char 1335**，还原 → rc0 |
| 对账（本条 lag0 重建 vs 发布面 `etf_nobond_vt.json` arm nobond_vt08） | 最深回撤 -10.56% vs -10.56%；最差年 -0.72% vs -0.72% → **REPRODUCED** |

对账是全条的承重腿：若重建序列不是发布面那条，赔率一律不可引用（`MISMATCH` 时页面会自己说出来）。

## 4. 读数边界（已知且写进页面）

- 现金腿在引擎里按 0% 计息、波动目标只降不升 → 这是策略赔率，不是货币基金赔率（已升级为卡 `etf_loss_odds_cash_rate`）。
- 票池是现存 ETF，带生存者偏差，方向偏乐观，本条不重估。
- 重叠窗口不独立：一年判词背后只有 6 个独立观测，三年只有 2 个；页面把不重叠子样本和计数并排印出，禁止把 6.5% 读成"未来概率"。
- 93 个亏钱起点不是 93 次独立亏损：2020 年 20 个、2021 年 67 个、2023 年 5 个、2025 年 1 个，挤在同一段回撤前。

## 5. 本轮约束（CONTENTION）

`results/_repo_write_contention.bm-c.json` = **rc3 CONTENTION**（同机另有 interactive 宿主 pid 52748 在写 19 个共享面）。
按 r1907 本轮只做**新增文件面**：未改 docs/live_usage、dashboard_status、Tools/s6_chain_bmc.py、knowledge/METHODOLOGY_ASSETS.md 等共享面，未重跑 S6 链 / 全量冒烟 / watermark / compute_audit / dualrun。
