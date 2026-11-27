# QA — 袖读数里的「换了哪 20 只」（r2186 · 2026-11-27）

面：`scripts/book_pair_sleeve_turnover.py` → `results/book_pair_sleeve_turnover.json` + `.md`
研究页：`research/BOOK_PAIR_SLEEVE_TURNOVER.md`
父面：`scripts/book_pair_sleeve_premium.py`（r2185）
本轮形态：`repo_write_contention` **rc=3 CONTENTION**（三个交互宿主并发）→ 只落**新增文件面**，未改 `Tools/s6_chain_bmc.py`、未碰 `smoke_test.py`、未跑 S6 链、未改 CEO 页。

## 完成判据（本司清单）

| # | 判据 | 结果 | 证据 |
|---|---|---|---|
| 1 | 脚本可跑、产物落盘 | PASS | `build` rc0，三件写盘（JSON 25KB / MD / research） |
| 2 | 自检全绿 | PASS | `selftest` **14/14 PASS** |
| 3 | 面自洽可复算 | PASS | `check` → `{"ok": true, "verdict": "THE_SWAP_ALONE_CAN_CHANGE_THE_BUCKET", "kind": "CHECK OK"}` rc0 |
| 4 | 与父面口径对得上 | PASS | 逐 bar 对账 **3,489 天，max\|diff\| = 0.0**（容差 1e-9）；`rebalances=141` 与父面同 |
| 5 | 判词由自己的行算出（禁记忆判词） | PASS | `_verify` 调 `verdict_of()` 复算；自检「记忆判词被抓」腿 |
| 6 | 漂移自称 STALE（链才肯补写） | PASS | `check` 比 `data/cb_panel.csv.gz` 与父面 JSON 的 size+mtime；自检 STALE 腿 |
| 7 | 缺面/不可测不当 0 | PASS | 覆盖率 <80% 的一侧不入统计；**崩盘后补仓（restart）与 swap 分名记录**，自检 14 号腿钉死 |
| 8 | 未来数据不进读数 | PASS | 换手两侧都读**同一个交易日**的溢价；作比较的闸线取「上一月末的实际序列三分位」并两侧共用，尺子不随读数漂移 |
| 9 | 读数与尺子同单位并列 | PASS | 页面同时印 churn（pp）与当日价差（pp）与普通日波动（pp），并明写「今天落在换手台阶内=yes」 |
| 10 | 沉默不等于干净 | PASS | 被跳过的换手写 `why_skipped`（thin coverage / restart），不静默丢弃 |

## 读数（本轮定稿）

| 量 | 值 |
|---|---|
| 换手次数（两侧都定价） | **139 / 140**（1 次为崩盘补仓，按名字排除） |
| 每次换手中位换掉比例 | **25%**（20 只里换 5 只） |
| 成员台阶 median \|churn\| | **2.30 pp** |
| 成员台阶 p90 | **5.98 pp** |
| 成员台阶最大 | **13.63 pp**（2026-07-17） |
| 普通日（非换手）median \|变动\| | **0.78 pp** |
| 普通日 p90 | **2.71 pp** |
| churn median ÷ 普通日 median | **2.95×** |
| 最大换手 ÷ 普通日 p90 | **5.04×** |
| 81 个月末里落在换手 10 bar 内 | **52** |
| 其中「不换手就会是另一个桶」 | **16** |

- 今日：读数 **8.769%**，距最近闸线（cheap 9.246%）**0.48 pp**，而换手台阶 p90 = **5.98 pp** → **今天落在换手噪声里**；父面在册标签仍是 10-31 读的 **rich**（→ 现金）。
- 反例月：2026-04-30 实际读数判 cheap，若不换手则读 21.66%（rich）。

## 未做（如实）

- 链腿 / 冒烟腿 / CEO 一页纸小节：**三者都在共享面**，本轮 CONTENTION 禁碰（r2181/r2183 之后第三次留账）。
- 全量冒烟未跑（约 1,100s，装不进 10 分钟窗）；不作「套件全绿」宣称。
