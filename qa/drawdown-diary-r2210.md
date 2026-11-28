# QA — 回撤事件日记（r2210 bm-c）

日期：2026-11-28T10:0x+08:00 · 机：bm-c · 轮：2210
产物：`scripts/three_book_drawdown_diary.py` · `results/three_book_drawdown_diary.json` · `research/THREE_BOOK_DRAWDOWN_DIARY.md`

## 本轮回答的问题

「这本书跌下去以后，历史上一般多久回来？」——父面把最深一格印成一个数（-6.72%），把水下天数印成一个占比，两
个都是一个观察的函数。本面把同一根已发布序列切成「峰 → 谷 → 回到原高」的事件，量事件的**分布**。

## 关键读数（可复核）

| 量 | 值 |
|---|---|
| 窗口 | 2020-01-06 → 2026-11-26（1670 bar） |
| 事件数（已恢复 / 仍开着） | 63（62 / 1） |
| 深度 中位 / p90 / 最深 | -0.57% / -0.06% / **-6.72%** |
| 回到原高（bar） 中位 / p90 / 最长 | 6.0 / 63.0 / 208 |
| 深度分档 | <0.5% 28 次中位 2 bar；0.5-1% 12 次 7.5；1-2% 9 次 18；**≥2% 14 次中位 54 bar（78 天）、最长 208** |
| 今天 | 事件 2026-01-29 起、谷底 2026-11-26、-6.72%、水下 **198 bar / 301 天**、深度排第 1 |

判词 `THE_DEEPEST_HOLE_IS_THE_ONE_YOU_ARE_SITTING_IN`：整窗最深的一格就是今天；本窗没有任何已关闭事件
至少这么深，所以「多久回来」没有直接先例——最近的可比尺子（比今天浅的 62 次）中位 6 bar、最长 208 bar，
今天已 198 bar，越过所有更浅先例的长端。

## 验证证据

| 检查 | 结果 |
|---|---|
| `run` | rc=0，写面与文档 |
| `check` | rc=0（无上游漂移；最深事件 == 父面 maxdd；今天与 ride 面 peak/hole/bars 三项一致；事件与新高 bar 恰好铺满窗口） |
| `selftest` | **18/18 PASS** |
| 行为腿（selftest 内） | 改上游 size → `STALE` rc=3；identity 置红 → `CHECK FAILED` rc=2 且文本不含 STALE；改判词 → rc=2；深度印成正数 → rc=2；今天与 ride 面不一致 → rc=2 |
| identity（面内） | `deepest_episode_equals_parent_maxdd=True`、`today_matches_ride_face=True`、`bar_accounting_ok=True` |
| 独立复算 | bar accounting：新高 bar 数 + Σ(事件水下 bar) == 1670；深度档 n 之和 == 63、open 之和 == 1 |

## 未做 / 不宣称

- **未加链腿与冒烟腿**：本轮 `Tools/s6_chain_bmc.py` 正被在飞全链（pid 33880，415 腿）执行，`smoke_test.py`
  正被本轮全量冒烟读取——按 r1907 同树多宿主律本轮只落新增文件面，两条接线记下轮（窗 ≤48h）。
- 事件是过去窗口的形状，不是预测；样本只有 2020-2026，无法说明更长的坑会怎样结束。
- 本面不评价这本书好坏、不碰推荐、不算成本。

## 附：本轮全量冒烟（终局）与一条硬缺陷

全量 **808 腿 / 775 PASS / 33 FAIL**（1077s）。33 红里除一条外全部归因到在飞全链尚未跑到的写者
（premium_percentile_write 链位 146 / etf_book_order 148 / ceo_live_usage 281 / permission_vs_size 342，链当前
115/415）与已知的 `knowledge/METHODOLOGY_ASSETS.md:18125` 一枚 0x08（r2207 已账，被 treasure_guard 硬拒）。

**唯一确认的硬缺陷**：`results/etf_premium/PREMIUM-2026-11-27.json` legs/4 `159519` = `MONEY_ON_FOREIGN_NAV`。

| 证据 | 值 |
|---|---|
| 面 session | 2026-11-27 |
| 该腿 nav_session | 2026-11-26 |
| 该腿打印的 CNY 金额 | -635.17（同时标 `trust=iopv+same-day-nav`） |
| 同文件 159655 的对照 | 11-27 无官方净值 → 正确降级 `unverified` / 金额 None |
| 净值板实测 | 159519 的 2026-11-27 官方单位净值 = **1.7010**（已发布） |
| 面内 IOPV | 1.6974；11-26 官方净值 1.6969 → 钱确实按昨日分母算 |

复现：`python Tools/premium_leg_session_audit.py` → 27 面 / 146 腿，`MONEY_ON_FOREIGN_NAV` 1 例，rc=0。

下一轮 P0 两条候选（本轮不盲改，因为定价语义正是链在飞写者 `etf_book_premium_forward` 的地盘）：
(a) 净值板有当日官方净值时改用官方 NAV 做分母重算 premium 与金额（整族重发）；
(b) 保守档：分母非本 session 一律降级 `unverified` 且金额置 None。
