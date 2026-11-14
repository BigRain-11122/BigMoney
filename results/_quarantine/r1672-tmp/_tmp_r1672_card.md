
### E634 · 第二个读者面上同一句话：把一页纸的「今日」交给它自己那根 bar（r1672 bm-c）

CEO 周六打开 `docs/live_usage/LIVE-*.md`，读到的是 **`今日 +¥0（对比 2026-11-13）`** 与 **`杀跌日，今日 否`**——读者自己的那天没有开盘，这两个数都属于 2026-11-13。E631/E632/E633 把这条审计教给了 ETF 书那一页，但 CEO 打开的是两张纸，而第二张从头到尾没人核过。

**做法（复用而非复制）**：`scripts/live_usage_day_words.py` 直接 `import live_book_day_words as LBW` 取 `_date_claims`（r1671 那套「句子 → 它引用的字段」匹配器），只给它这张纸自己的 24 条规则（页首→`day`、生成→`generated`、各面截至→`freshness.rows`/`market.asof`/`risk_tape.cutoff`、播种→`etf_book.first_bar`、决策 bar→`book_identity.ledger/ticket.bar`…）。写手侧加 `day_word(page_day, as_of)`：页面日 ≠ 那根 bar 时**印日期不印「今日」**，于是这两句变成 `较 2026-11-13 收盘 +¥0（本页无新 bar）` 与 `杀跌日（bar 2026-11-13）否`。链腿 `live_usage_day_words`（check+run）已入 S6。

**可复用四条**：

1. **行过滤器不能跨纸继承**。`_printed_census` 只留含日词的行（那张纸上两问同句）；一页纸 23 处日期只有 5 处挨着日词，照抄过滤器就只核 5 处、把剩下 18 处当「未映射」——**量错了纸**。正解=日期审计读全部行，日词审计读日词子集。
2. **「诚实句」要单列，否则会压死绿牌**。`今日尚未有 bar`、`今日 09:15 起随源点亮` 说的是「这天还没东西」，是解药不是病；把它们算进 `undated` 债里，页面永远红。分开成 `n_honest` 后 `n_undated` 才归零。
3. **规则常量与数据声明必须分桶**。`月界（2026-10-01）` 是政策日期，没有任何字段能反驳它；把它留在 `unmapped` 会让这面永久红，把它并进 `ok` 就是「未映射偷偷变绿」。第三桶 `n_policy`：既不核对也不阻塞，且**计数打印出来**。
4. **病句会连带弄坏规则**。第一版把 P&L 句写成 `{dw} …（对比 {day_prior}）`，dw 取的是对比日 → 纸上出现 `2026-11-13 +¥0（对比 2026-11-13）`（同一个日期印两遍）。正确对象是**那根 bar 的收盘**，不是对比基期。

**读数**：`live_usage_day_words selftest 16/16`；实跑 **PRINTED_DATES_AGREE·23/23 处日期对上各自字段、0 未映射、0 判不了、0 处 stale 日词**；`live_book_day_words selftest 33/33` 未回归（`_date_claims` 加 `rules=` 参数、`_doc_value` 加列表下标支持，均向后兼容）；`s6_chain --only etf_book_ceo_page,live_book_day_words,live_usage_day_words` **3/3 rc0**。
