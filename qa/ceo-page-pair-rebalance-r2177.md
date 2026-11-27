# r2177 — the pair-rebalance answer reaches the CEO page; smoke reds classified

## 本轮产品增量

`scripts/ceo_live_usage.py` 新增 ⑨ 节「一笔钱分两本书 · 多久搬一次、搬钱吃掉多少」，
把 r2176 已算出却从未上页的 `results/book_pair_rebalance.json` 送上 CEO 一页纸
（r1782：不在读者那一页上的读数不算产品）。

页上印的（全部引自面，零重算）：

| 项 | 数 |
|---|---|
| 判词 | REBALANCE_PAYS（对持有 +0.022 Sharpe） |
| 不搬钱 | 年化 8.87% / SR 1.043 / MDD −8.92%；转债半边 6.9 年后只剩 25.4%（最大偏离 8.9pp） |
| 按季搬（10bp/边） | 年化 9.12% / SR 1.065 / MDD −9.25%；27 次搬运 / 单边换手 0.05/年 / 成本拖累 0.01pp |
| 诚实的一半 | 付费最优 1.065 vs 零成本日再平衡 1.066（差 0.0011）＝ 搬钱买回的是纸面数，不是第二个收益源 |
| 成本敏感 | 5/10/20bp 三档 cadence_still_ahead 全 True |

自检新增 4 腿（缺面不读 0 / 判词与双读数与出处同时在页 / 纸面数句必须在场 /
改一个数页面跟着动）：`ceo_live_usage.py selftest` 207/207 ALL PASS。
`Tools/page_repeat_guard.py scan` = 4 faces / 0 repeated（r1911 无重复出处）。

## 两处自捕（当窗修掉，未上链）

1. 「期末 30/25.4」误把目标权重当期末 → 改为直接印面自己的 `drift.end_w_cb`。
2. 「零成本日再平衡 1.044」是用 `hold_sharpe + gap` 自造的 → 改读面自己的
   `recovery.paper_sharpe`（1.066）。r1234：读者拿到的数必须是生产者的数。

## 全量冒烟读数（detached，796 腿 / 1142.3s，15:26→15:45）

`794 PASS / 11 FAIL`，按 r1934 契约词分类：

### 已在本轮修掉（重派生面 / 面代差）

| 红 | 处置 |
|---|---|
| `etf_book_year_gate (published verdicts re-derived) exit=2 stale 2026-11-26 vs calendar 2026-11-27` | 重跑 `scripts/etf_book_year_gate.py` → rc0，YEAR-GATE.json 重生（ADMIT/CALIBER_KEEPS_Y4） |
| `chain contract-word audit exit=1 STALE the chain's leg table…` | 重跑 `scripts/chain_contract_word_audit.py` → rc0（401 腿/144 写者/13 候选/0 永久红） |
| `the CEO page prices the whole book in one line / the cash the sheet leaves behind` | 页面在 15:40 生成而 `t35_paper_export` 15:41 才把账本推到 11-27（roll-up 5,908,548.84 vs 5,934,743.99）→ 16:05 重生成页面 |
| `fleet: a lane green inside its own window…`（2 条，dashboard 窗口 17/19 vs board） | `python -m monitor.build_status` stale-takeover derive rc0（bm-a 心跳 12,714min 陈旧） |
| `paper_equity_recheck R3 VOLATILITY-CE-01` | `scripts/daily_scorecard.py` stale-takeover derive rc0 |
| `the sheet's swap-section freshness is re-derived` / `a stale swap leg says who can move it` | `scripts/etf_book_order.py run` 重写 `ORDER-2026-11-26.md`，等待句「还在等谁 / lane owner」已落页 |

### 未修（如实留账，同根一组 + 1 独立）

| 红 | 根因（本轮实证） | 下一步 |
|---|---|---|
| `swap section freshness (every face on the calendar's close) exit=2` | 10 条腿要 `data/etf_premium/snap/2026-11-27.csv`；该快照的 NAV 列当日才可得，生产历史全在 16:10–22:00 之间落盘（11-20 15:58 / 11-24 17:27 / 11-25 16:10 / 11-26 22:00） | 15:30 门只是下界，真正的可得面是 NAV 发布（约 22:00）。两条路：①给 `swap_freshness` 加「今日快照未到发布时间＝TODAY_PENDING」第三态（r1861 族），②把 snapshot 腿挪到 22:00 后再跑。两者都要预注册，本轮不动 |
| `a stale swap leg…` 第一半（`还在等谁` 已落页，判据另一半靠同一张 STALE 面） | 同上 | 同上 |
| `live-quote section and the panel's own lane agree on tonight`（retirement heading） | 页面 payload 无 `live_quote` 键（实查 `LIVE-2026-11-27.json` 该键为 None），而腿在 `status=="panel_current"` 分支要求「今晚的收盘」字样；冒烟跑在 11-27 面板刚落地、页面仍是 11-26 内容的那 20 分钟窗内 | 下轮先复现该腿的 `_pgq` 来源（不是 CEO 页 payload），再决定是补键还是改判据 |

## 数据面（S6 快腿，全 rc0）

`update_daily`（新 bar → live.paper hook）/ `data_lane_freshness`（verdict=attention，worst=heat）
/ `compute_audit`（flags pool_starvation,supply_floor —— 供给地板 3 件缺口，calendar 因由）
/ `market_regime`（hs300<MA200 第 10 日 + vol20>p80）；纸盘链 7 腿 rc0（alloc/system_v1 为
他机车道诚实 no-op）；`t35_open_fill_verify` PASS（matched 1 / breach 0）。

`attrition_ledger_guard scan` = CLEAN（4 账本，3 处历史缩行 healed）。
`Bigmoney-IterationLoop` 运行中 + `Bigmoney-LoopWatchdog` 就绪（均未重注册）；
LogonType 仍为 Interactive（S4U 翻转属管理员提权面，如实注记，未重复尝试）。
