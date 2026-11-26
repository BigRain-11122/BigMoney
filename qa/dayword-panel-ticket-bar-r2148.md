# QA — 日线面板 bar 与票面 bar 是同一天吗（r2148 · bm-c）

## 缺陷（读者能看到的那一句）

`docs/live_book/LIVE-BOOK-20261126.md`，live-quote 段：

```
## 2026-11-26 的收盘，面板自己有了
日线面板自己已经吃到 **2026-11-26** 的收盘：…
上面那张票面就是按这根 bar 算的，本页的价、仓位、溢价都同一天。
```

而同一页的 `priced_bar` 是 **2026-11-25**（订单面比日线面板晚一根）。也就是说：

- 前半句（面板吃到 11-26）**是对的**，它说的是 `live_quote.panel_bar`；
- 后半句（票面按这根算、价/仓位/溢价同一天）**是错的**，票面按 11-25 算。

读者在一张纸上看到「面板有了今天」＋「票面也是这根」，会把隔了一根 bar 的价格当成当天的。

同一处还有两个审计面的错位：

1. `scripts/live_book_day_words.py` 把「已经吃到 **X** 的收盘」和标题「## X 的收盘，面板自己有了」
   都映射到 `priced_bar` —— 两句话说的是**日线面板的 cutoff**，映射错了对象
   （r1788：日期判据要对到产出那个数的那张面）。面板与票面同日时看不出来，面板走在前面的
   那个晚上就变红，且红的是对的句子。
2. 同一个文件的 verdict 判据把 `n_unmapped`（散文日期：解释「两个日子对不上」这类句子，
   不引用任何字段）算作欠账，而 r1813 已经裁定「unmapped prose date is information, not a
   defect」，并且只把这条裁定教给了自检腿。于是 `_owed` 与自检腿各判各的
   （r2144「第四红是腿的 regex，不是页面」同族）。

## 修法

`scripts/etf_book_ceo_page.py`

- `live_quote_block(lq, page_day=None, ticket_bar=None)`：新增 `ticket_bar`（票面定价 bar）。
- 面板 bar 与票面 bar 不同时，印：

  > 上面那张票面是按 **2026-11-25** 那根 bar 算的（订单面比日线面板晚一根，要等它的下一根
  > bar 才跟上来）——本节说的「面板已经吃到 2026-11-26 的收盘」只指日线面板，不是那张票的定价日。

- 两者同日时保留原句「本页的价、仓位、溢价都同一天」。
- 调用点传 `ticket_bar=p.get("priced_bar")`（页面 JSON 的票面定价日）。
- 新增自检腿 **L144b / L144c**：
  - L144b：`ticket_bar="2026-11-03"`（面板 11-04）时必须印出两个日子、且**不**印「都同一天」；
  - L144c：`ticket_bar="2026-11-04"` 时仍印「都同一天」——防止修法把正常情况也改坏。

`scripts/etf_book_order.py`

- `pending_fill_md` 的同日标题由「## 今天开盘要成交的是什么…」改为
  「## 今天（2026-11-26）开盘要成交的是什么…」：`今天` 保留（该 bar 确为页面自己的日子），
  但把日子写进标题。原来它只有日词没有日期，审计面按 `undated` 计数（r1849「缺日期时不印
  日词，禁编今天」的反面：有日期就直接印）。
- 对应自检 L212c 的断言同步改成新文案（旧断言在改文案后必然红）。

`scripts/live_book_day_words.py`

- 「已经吃到 **X** 的收盘」→ `live_quote.panel_bar`（该句断言面板 cutoff）。
- 新增规则：标题「## X 的收盘，面板自己有了」→ `live_quote.panel_bar`。
- 新增规则：「票面是按 **X** 那根 bar 算的」→ `priced_bar`（页面新增的那句，自印票面价日）。
- `_owed` 去掉 `n_unmapped`，与 r1813 的裁定对齐；`n_unmapped` 仍照印（信息不消失，只是不欠账）。
- 自检样本表补两条对应新规则的样句（`len(_samples) == len(CLAIM_RULES)` 一一对齐）。

## 验证

| 检查 | 结果 |
|---|---|
| `python scripts/etf_book_ceo_page.py selftest` | **477/479 PASS**，2 FAIL 为**既有红**（L228a/L230：priced band 表的 bar 名，与本次改动无关；stash 后基线同样 2 FAIL） |
| `python scripts/live_book_day_words.py --selftest` | **46/46 PASS**（改前同文件 45/46，红的是与 verdict 打架的那条） |
| `python scripts/live_book_day_words.py run` | **ANCHORED rc=0**（改前 `PRINTED_DATE_MISMATCH rc=1`，1 处 mismatch） |
| 页面重建 `etf_book_ceo_page.py run` | LIVE-BOOK-20261126.md 两处文案已落：标题「今天（2026-11-26）开盘要成交…」，live-quote 段随两 bar 同步而保留同日句（tar 分支由 L144b 夹具钉死） |
| 上游两腿 `capacity_edge,capacity_ticket` | 2/2 rc0（面板推进到 11-26 后两节滞后，重跑后日词面转 ANCHORED） |

## 未做（如实）

- `live_book_section_bars` 仍报 `PAGE_MIXES_BARS`（页面 74 个带日期节里 33 节在 11-26，其余滞后；
  最旧停在 2026-11-17，alias_census 落后 7 个交易日）——**既有债务**，本轮未动。
- `etf_book_ceo_page` 的 L228a/L230 两红未修（priced band 行的 bar 名归属），既有。
- 全量冒烟未跑（连续多轮），本轮不宣称套件总数。
