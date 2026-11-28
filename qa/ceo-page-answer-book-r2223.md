# r2223 — 答案簿上 CEO 一页纸：哪条结论还活着、今天卡在哪一关

## 一句话

桌面累计 **96 行判词**、**6 行候选**，压成 **4 个问题**——这四行在 `research/BENCH-VERDICT-BOOK.md`
里已经躺了两个轮次，而 CEO 打开的那一页一个字都没有：读者既不知道「还有几条结论活着」，
也不知道「每条离下单差什么」，更不知道「今天卡在哪一关」。本轮把答案簿的 `to_order`
搬到一页纸的 ⑪ 节：**4 个问题、今天 0 条能下单**，卡点逐条点名（资本线 IC/IM 两条、
面判词两条），容量数字一起印（4321.8× / 4293.7× 本书）。

## 为什么不能只搬判词

判词 `GO` 本身不是可执行信息。同一页上读者会问三件后续：

| 问题 | 答案住在哪张面 | 判据 |
|---|---|---|
| 这一条要满足什么才算能下单 | 答案簿 `to_order[<卡>]` 的「可下单条件」句 | 逐字引用，页面不重写条件 |
| 今天卡在哪一条 | 同一句的「今天卡在：…」尾巴 | 逐字引用；缺尾巴＝这一关过了 |
| 容量够不够 | 「容量」条目（`bench_basis_capacity` / `bench_cmdty_capacity`） | 印面自己的数字与出处；没有面量过＝「未测不是零」 |

两张基差卡的条件句**完全相同**、两张商品卡的条件句**完全相同**，所以按卡逐行印会把同一个
测量卖两遍（r1911）——本轮按**卡点分组**：一组一个条件句、一个容量数字，组内每卡只印
自己的判词、年化/回撤与「面自己认不认」这一句。

## 落地（只读投影，零新判据）

`scripts/ceo_live_usage.py::_answer_book_face()` 只做搬运：
`rows` 里 `disposition=CANDIDATE` 的行、`to_order` 里每条目的 `what/text/source`。
页面新增 `## ⑪ 今天哪条结论能下单、卡在哪（答案簿·纯读出）`，免责节顺延为 `## ⑫ 诚实免责`：

```
- 答案簿 96 行判词里还活着 **6 行**，收成 **4 个问题**；按它们自己的条件句，**今天能下单 0 条、卡住 4 条**
- **今天卡在「资本线 IC、资本线 IM」的 2 张**：
  - `basis_timing_perm`（basis）：判词 **SIGNIFICANT** · 年化 +10.16%
  - `basis_timing_size`（basis）：判词 **GO** · 年化 +10.16% · 回撤 -1.89%
  - 这一关怎么算过（答案簿原句）：成本按声明的 bp 计 且 IC/IM 首档 1 手买得起（未过） 且 容量至少 1 倍本书。今天卡在：资本线 IC、资本线 IM
  - 容量这一关：CAPACITY_OK_AND_SIZED·总容量 4321.8× 本书（results/bench_basis_capacity.json @2026-11-26T23:22:58+08:00）
- **今天卡在「面判词」的 2 张**：
  - `census_commodity`（census）：判词 **GO** · 年化 +4.99% · 回撤 -21.74%
    - 这张卡自己的证据面判 **CENSUS_LEANS_POSITIVE**，行上的 GO 是单臂/单相读数——面自己没认这个 GO
  - `robust_tsmom_commodity`（robust）：判词 **GO** · 年化 +4.99% · 回撤 -21.74%
    - 这张卡自己的证据面判 **UNSTABLE_ACROSS_PARAMS**，行上的 GO 是单臂/单相读数——面自己没认这个 GO
  - 这一关怎么算过（答案簿原句）：面认这个结论（未过） 且 成本按声明的 bp 计 且 容量至少 1 倍本书。今天卡在：面判词
  - 容量这一关：CAPACITY_OK_FOR_THIS_BOOK·总容量 4293.7× 本书（results/bench_cmdty_capacity.json @2026-11-28T17:51:53+08:00）
- 出处：`results/bench_verdict_book.json`｜cutoff 2026-11-28｜generated 2026-11-28T17:53:42+08:00——**答案簿在链尾重建，这一节印的是它上一趟写下的原话**；它一动，跟在它后面的探针腿会把这一页重画一遍
```

四条纪律（各有一条自检腿，全部**章节切片**断言，r2208 失败即红）：

1. **计数由面自己的句子推**：「今天能下单 N 条」的 N 从 `to_order` 条件句里有没有「今天卡在：」
   数出来，页面不自己判；缺面印「读不到哪些结论还活着」，禁印成「一条都没活」。
2. **卡点逐字来自面**：组标题的卡点串直接取条件句尾巴，负控证明换一个卡点页面就跟着换、
   且旧卡点不再出现。
3. **容量未测不是零**：条目缺容量时印「没有任何面量过」而不是空白或 0。
4. **自印出处时点**：答案簿在链**尾**重建（页面腿在链中段），所以本节必须把引用的那一代
   `generated`/`cutoff` 印出来（r1781）；配套新增探针腿 `ceo_page_answer_book`
   （`scripts/ceo_live_usage.py check`，只比 mtime）——答案簿或容量面比页面新即 STALE，
   链付一次 ~1.2s 重画，读者最多落后一趟链而不是一整天。

## 验证

| 项 | 结果 |
|---|---|
| `scripts/ceo_live_usage.py selftest` | **ALL PASS**（新增 6 条：章节存在 / 每条活卡与卡点 / 自印代数 / 换卡点负控 / 全清空读成可下单 / 缺面读成读不到） |
| 页面重生成 | `docs/live_usage/LIVE-2026-11-28.md`（+ json 孪生 + latest 指针），⑪ 渲染如上 |
| `Tools/page_repeat_guard.py scan` | 4 face，**0 重复句** |
| `python scripts/ceo_live_usage.py check` | rc0 `OK -- the page is at least as new as the answer book` |
| 链腿 `--only=bench_verdict_book,bench_cmdty_capacity,ceo_live_usage,ceo_page_answer_book` | **4/4 rc0**（0.1s / 0.7s / 1.1s / 0.2s） |
| `Tools/s6_chain_bmc.py --selftest` | **17/17 PASS** |
| `Tools/chain_writer_audit.py` | `EVERY_CHECKED_FACE_HAS_A_WRITER`，420 腿 / 163 对 / 202 面 / 0 red（4 条披露为既有） |
| 新冒烟谓词（`smoke_test.ceo_page_answer_book_problems`） | 正面 `[]`；负控（把 `basis_timing_size` 的卡点换成「券商专线没通」）→ 正确发声 |
| 全量冒烟 | 见轮报告（`results/_smoke_r2223.out.txt`） |
