# DIGEST 2026-11-12 r1572 — 承诺有了回执，两个敞口第一次被点名是两本书

**问题（两半，源自上一窗的两处活）**

1. r1571 把「明天开盘要成交的是哪本书、换手多少、花多少钱」发布成 `pending_fill`，但账本的
   行是每次重算的：`filled/turn` 只活在当根 bar 上。承诺在成交当天就消失，操作员昨天读到的
   「12.60bp＝CNY 1,280」第二天无处可核。
2. CEO 页（`docs/live_book/LIVE-BOOK-*.md`）从不提这笔待成交，也从不印这本账已经付过多少
   交易成本——「我持有的书」和「开盘后我将持有的书」在纸上完全同形。

**做了什么（产品）**

- 账本（`scripts/etf_book_forward.py`，上一窗遗产、本轮验后采纳）：`save_ledger()` 落盘前
  追加 `sync_fill_log()`（逐 `filled` 行一条回执：换手、成本 bp、CNY、口径），并把
  `pending_fill_audit()` 的判词写进同一文件的 `pending_fill_check`——承诺、回执、自检三件同住一处。
- CEO 页（`scripts/etf_book_ceo_page.py`，本轮新增）：`fill_face()/fill_block()` 把「今天开盘
  要成交的是什么」＋「已成交回执」＋「这笔承诺与账面行对不对得上」三节印在**下单清单之前**；
  句子直接 import 执行单的 `pending_fill_md`（E289），判词只抄 `pending_fill_check`，不重判。
- 同一张纸上的两个敞口被点名：账本那本 **k=0.9094／12 名**（规则目标）vs 清单那本
  **k=0.4322／5 名**（额度门签发）——句子由数值分支生成，不是写死的文案（E561）。
- 套件新增可单独回放的活面腿 `_leg_page_fill_section()`（并在缺节的页面上实测判红）。

**读数（2026-11-11 面板，机读）**

- 决策 2026-11-11 收盘 → 成交：**下一根 bar 还没出现**（`fills_at_bar=None`，不拿决策 bar 冒充成交日）。
- 待成交：k 0.7008→0.9094（现金 29.9%→9.1%）｜换手 **1.259772**｜**12.60bp**｜**CNY 1,280**
  ｜进 9 名／出 9 名（12 名里 3 名重叠）。
- 已成交回执：**0 条**（这本账自 10-23 起还没有一次开盘成交落地）——页面因此印「没有任何已记录的成交」
  而不是留白。
- 账本自检：`pending_fill_check ok`（决策 bar 在行里、现金与那一行一致、成本＝换手×单边×那一行净值×资本）。

**修红（S1）**：上一窗遗留的全量套件 **562/563，1 FAIL** ——
`a gate that flips on the decision phase is not a gate`：`results/etf_book_scale_floor.json`
的 floor=0 基线仍停在旧面板（CONDITIONAL/0.7067），而 `YEAR-GATE.json` 已用 11-11 新 bar 翻面
（ADMIT/0.6995）。判定＝**陈旧发布件，不是判据坏**（E559 同族）。修法＝按当前面板重发该面
（52s），floor=0 现在逐位复现 ADMIT/0.6995，单腿回放 PASS。不改容差、不改探针。

**验证**：`etf_book_ceo_page selftest` **241/241**（新增 L207-L214：抄不重判／回执印钱／
自检红即印红／读不到＝无法核验／空回执要说话／节在清单之前／两本书分支／同一本书分支）·
`etf_book_forward --selftest` OK（含 7 条新腿）· `etf_book_order --selftest` **174/174**（leg69/70）·
`check-ticket-days` **AGREE** · `live_book_section_bars check` **CHECK_OK** ·
`_leg_pending_fill_receipt` / `_leg_page_fill_section` 单腿回放 **双 True**，且后者在缺节页面上判红 ·
`etf_book_scale_floor` 重发后 leg PASS。

**未验证（如实）**：全量套件 08:52 起后台在飞（`results/_smoke_r1572.out`），收轮时未收口；
本轮以 241/241＋174/174＋两条单腿回放为据。bm-a 心跳静默 31.4h，其车道（heat/LHB/regime5）
数据不在本机盘上，市场时钟面因此停在 2026-11-06——本轮不接管、只点名。

**读法**：一张纸说「今天开盘要买什么」而不说「昨天决定的那笔今天怎么结算」，读者只能靠记忆。
把承诺、回执、对账三件放进同一个文件、同一张纸，是让「我说过会买」变成「我知道我付了多少」的最小闭环。
方法论卡＝E560（承诺与回执同文件）、E561（两个敞口必须由数值分支命名）。
