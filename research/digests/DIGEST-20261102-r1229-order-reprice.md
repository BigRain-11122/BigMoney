# DIGEST r1229 bm-a — 一张「可执行」订单纸用的是哪一天的价格

- 日期：2026-11-02 05:xx +08:00
- 轮号：r1229（bm-a）
- 归属：dept 交易 / 工程
- 证据截止：2026-10-30（面板最后一根完整 bar）

## 发现

`results/etf_book_order/ORDER-2026-10-30.md` 头部声明「本单定价 bar：2026-10-30｜判定
current｜落后 0 个交易日」，但表格里每一行的参考价取自**决策 bar（2026-10-14）的收盘**：

| 代码 | 旧参考价（=10-14 收） | 10-30 收 | 漂移 | 手数旧→新 |
|---|---|---|---|---|
| 159501 | 2.229 | 2.158 | −3.19% | 423 → 436 |
| 513100 | 12.271 | 11.453 | −6.67% | 76 → 82 |
| 513690 | 1.137 | 1.123 | −1.23% | 829 → 839 |
| 159577 | 1.750 | 1.662 | −5.03% | 538 → 567 |
| 159263 | 1.148 | 1.129 | −1.66% | 821 → 835 |

旧的「整手取整后欠投 0.13% NAV」是这套十几天前价目表的产物；按当日价重算为 0.08% NAV，
整册 +522 元 / +72 手。

## 为什么权重仍取决策 bar

网格日之间不重排是刻意的（r743：拿面板最后一根 bar 排名，会把引擎没持有的书交给操作者）。
本次只把**价格**换成定价 bar，权重逻辑一字未动。

## 修法与判决

`build_ticket` 跑两臂（legacy=决策 bar 价 / ticket=定价 bar 价，权重同源），
`reprice_block()` 逐名印两价、漂移、手数旧→新、金额旧→新，并对缺价的行留空点名：

- `REPRICED_TO_THE_BAR_YOU_PAY`（本轮回执：5/5 名漂移，最差 6.67%）
- `SAME_PRICES_ON_BOTH_BARS`（两 bar 同价，明说两种读法一样）
- `PRICE_MISSING_ON_PRICED_BAR`（定价 bar 无报价 → 不填、不猜、点名）

## 验证

- `python scripts/etf_book_order.py --selftest` → **85/85 PASS**（新增 leg47a-e）
- 实弹重生成 `results/etf_book_order/ORDER-2026-10-30.md` + `TICKET-2026-10-30.json`
  （`reprice` 键，priced_bar=2026-10-30，与 `evidence_cutoff` 一致）
- `smoke_test.py` 新腿「product: the order sheet prices the bar it says it is priced on」
  从载荷重推：每行 priced_price=票面价、漂移算术自洽、priced_bar=evidence_cutoff、判决属四态

## 边界（照报）

- 参考价≠成交价：滑点、限价、盘中价差未建模，单子 caveats 已写明。
- 本面只覆盖本条车道的单（5 名 β-0.20 单）。卡口径的 12 名单
  （`ORDER-2026-10-30-card.md`）本来就用当日价，本次未改动它。
- 面板里面同代码可能多源（如 `513100.csv` 与 `sh513100.csv` 并存），逐名核价必须走
  `etf_composite_pf.build_panel()` 的去重口径，不能用一份 CSV 直读做第二次实现——
  本轮先用直读得过一个 2.239 的假读数（拆分级），按去重口径复算是 11.453，才与卡一致。