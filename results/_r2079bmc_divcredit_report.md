# r2079 bm-c 轮报告（新增面版·竞争窗）

- 时间：2026-11-25T07:2x +08:00
- 机器：bm-c ｜ 轮号：2079 ｜ dept：研究/策略
- 竞争探针：rc=3 CONTENTION（对端 codely.exe pid 79608 自 2026-11-24T22:39 起仍活；轮首前 19 张共享面被对端写过、overlap 内不可归属写 0；证据 `results/_repo_write_contention.bm-c.json`）
  → 按 r1907/r1927：本轮只落新增文件面，未改共享面、未重跑 S6 链、未跑全量冒烟
- 孤儿面=0（py_faces=7 / orphans=0 / resident_servers=2，`results/_orphan_face_probe.bm-c.json`）
- watermark：本轮未跑 py_watermark（竞争窗，与 S6/冒烟同列延后；上一可见读数沿用 r2076 的 red=false/healthy）

## CEO 三行

- 当前活：回答「我们一直报的书年化 10%，是不是因为没算分红而低报了很多」——**不是**，只差 0.33pp/年
- 最近实物：`K:\Fluxgroup\FluxGroup\quant\bigmoney\research\ETF_BOOK_DIVIDEND_CREDIT.md`（2026-11-25T07:19，selftest 5/5，--check rc0）
- 下个里程碑：把「分红差 0.33pp vs 执行晚一天 1.03pp」一句接进 CEO 一页纸（≤48h，需他宿主静默）

## 本轮产品：这本书的分红盲区值多少钱

### 做了什么

同一引擎（`etf_robust_pf.open_to_open_equity`）、同一规则（20 日调仓 / 5 名 / 10bp 单边 / 8% 波动目标）、同一张打分表，只把价格面板换成「含分红再投资」：

1. 先用引擎自己的 `diag` 记账取「它真的买过谁」——122 名 + 今日在册 3 名 = 125 名；
2. 对 125 名抓 sina 累计分红（`fund_etf_dividend_sina`，缓存 `data/etf_dividend/*.csv`）；
3. 每名按 `factor_t = factor_{t-1} × (1 + 派息_t / 除息日收盘)` 复利成总回报因子，再缩放开盘价（引擎收益只吃开盘价）重跑两次（lag0 / lag1）。

### 结果

| 口径 | 年化 | 夏普 | 最大回撤 |
|---|---|---|---|
| 价格（已发布口径）lag0 | 11.11% | 1.096 | -10.56% |
| 价格 lag1 | 10.08% | 0.993 | -10.11% |
| 含分红 lag0 | 11.47% | 1.129 | -10.31% |
| 含分红 lag1 | 10.41% | 1.024 | -9.86% |

- **分红信用 = +0.33 pp/年（lag1）/ +0.36 pp（lag0）**，夏普 +0.031，回撤改善 0.25pp
- 同一把尺子：没算分红 0.33pp vs 决策当天收盘看到、下一开盘才买到 1.03pp → **分红盲区只有执行罚金的三分之一（0.32 倍）**
- 分段：IS 4.21%→4.23%，OOS 18.74%→19.58%（分红主要落在 OOS 段，因 2020-2023 段半仓在债/防御）
- 判词 `DIVIDENDS_ARE_NOISE`（阈值 0.5pp）

### 诚实面

- 覆盖：125 名中 sina 有分红记录 56 名、窗内真派息 **34 名（27.2%）**；缺记录按 0 计 → 差额只会偏小
- 单次派息 > 原始收盘 10% 的事件一律丢弃并计数（份额折算不是现金分红）——6 只各 1 次：510230 / 512040 / 512160 / 512690 / 515100 / 515450
- **自捕一枚**：首版因子把「修复后的价格」当分母，510230 在 2020-08-17 份额折算（-77%，repair_flips 会前向重定基）使 2018/2019 的三笔派息变成 54.7%/23.7%/20.0% 的假分红 → 因子 +140.8%；改为「原始收盘价当分母 + >10% 丢弃」后该名跌出榜、数字稳定（三次跑逐位一致）
- 局限：打分仍是价格因子（`compute_all` 未重建），派息多的名字在选股里仍被低估 → 差额是**下界**；sina 分红史可能不全（511010 在 2015→2025 只有一次跳变）

### 证据

- `scripts/etf_book_dividend_credit.py`（selftest **5/5**，`--check` **check ok** rc0，幂等三次跑逐位一致）
- `results/etf_book_dividend_credit.json`、`research/ETF_BOOK_DIVIDEND_CREDIT.md`
- `data/etf_dividend/`（125 名分红缓存，新增数据面）
- 送达：commit `6423493f6f` 已进 origin/main（`git ls-tree` 点名 3 件 + 125 个缓存全在位）

### 送达事故（如实）

CAS 直投首跑把文件清单取成 `git diff --cached`（本地已 commit，清单为空）→ 推出**空提交** `4fb13d65c5`（parent 只有 variation，无内容变化）；当场发现，改用 `HEAD~1..HEAD` 重做 → `6423493f6f` 带 128 件落地。空提交留痕不改史。

## 未做（如实）

- `ceo_live_usage.py` 一页纸未接（共享面）——建议补一句「分红盲区 0.33pp 只有执行晚一天的三分之一，见 ETF_BOOK_DIVIDEND_CREDIT」
- 本面未接冒烟腿 / S6 腿（共享面改动，竞争窗禁用）→ **孤儿风险**：下轮静窗必须接线，否则刷新不会触发
- 全量冒烟连续第 21 轮未跑（红腿读数仍是 2026-11-24T20:12:28 的 765 腿/34 红）
- S6 链连续第 21 轮未跑
- 心跳面（`fleet/machines/bm-c.json`）由对端在写，本窗不覆盖

## S0.5 / 法面

- fleet/orders **117 件**，心跳 orders_ack 331 条，未回执 44 件（2026-11 内 **0 件**，全为他机 lane 广播，按 r2066 判例不逐令补 ack）
- 集团 `origin/main:docs/decisions.md` 原生字节 **250,586B**、sha256 前 16 位 **79E3083B85C130B8** == 自持水位 `79e3083b85c130b8…` → 零新决策零动作（git cat-file 直落临时件再 Get-FileHash，r1911/r2048 律）
- fleet/inbox 空

## 本地未达 origin commit 数

本轮收口后实测（reset 到 origin/main）**= 0**（此前 origin/main…HEAD 为 5/1，已按内容已在 origin 的判据 `git reset --mixed origin/main` 收敛；我的 128 件与 origin blob 零差异实证）
