# 你在执行一本自己拒收的书（r1438 bm-c）

**现象（2026-11-08 18:4x 实弹）**：同一张桌面同一天印出两句话——

- 供给面板（`results/supply_calendar.json`）：`nobond_vt08_adopted` = **refuse**，
  理由 `years_for_half median 2 vs line 3 (FAIL)`；compute_audit 的 `supply_floor`
  已连红 40 轮（ready 0 / floor 3）。
- 下单页（`results/etf_book_order/TICKET-2026-11-06.json`）：**book_weight 0.4603**，
  ¥459,796 分 5 只（159501/513100/513690/159577/159263）+ 现金 ¥540,204 挂 GC001。

两句话各自都有出处、各自都合法，**没有任何一面把它们放在同一句里**，于是读者看到的是
「今天没有合法供给」和「买这五只」并排的桌子。这与 r1199（供给旗只量了一半成因）/
r1422（已烧光与终审打回印成同一个词）同族，只是这次两个词落在**两张不同的页**上。

## 判据（跑前冻结，先证明身份再谈冲突）

身份不是一个字段，是四条同时成立、且每条把两侧的值都印出来：

| 条件 | 执行侧 | 被审侧 |
|---|---|---|
| I1 n_hold | ticket 5 | phase_gate 5 |
| I2 风险设定 | card vol_target 0.08 | candidate 0.08 / floor 0.0 |
| I3 无债券袖 | card classes = equity,commodity,convertible | candidate 名 `nobond_*` |
| I4 票是卡的宽度前缀 | same_decision_bar & ticket_is_prefix_of_card = true | — |

四条任一不成立 → `UNMATCHED_IDENTITY`（**不是**「有冲突」）。多本候选同风险设定 →
`ambiguous` 并点名，**不许按顺序挑一本**。缺 receipt → `UNKNOWN`，未知不是判决。

判决词：`EXECUTES_REFUSED_BOOK` / `EXECUTES_ADMITTED_BOOK` / `NOT_EXECUTING` /
`UNMATCHED_IDENTITY` / `UNKNOWN`。

## 两个可复用结论

1. **被审对象 ≠ 被执行对象（本族最贵的一条）**：gate 判的是**去掉执行壳的书**；
   票跑的是 `beta 0.20 × 书 + GC001 现金腿`（r1253 已证现金腿不是装饰：+1.53/+1.00/+0.46pp
   @beta 0.10/0.20/0.30）。candidate receipt 里没有任何 beta/cash 键 →
   `wrapper.gated=false` 如实印出。**一个从来没被审过的壳，正用真金在跑**。
2. **「两面各自合法」不是矛盾，是缺一句话**：把两个面并排成一句需要身份证明，
   而身份证明恰好是不能靠「名字像」解决的那件事（本轮四条里最容易蒙对的是 I1/I2，
   最容易蒙错的是 I4——票是卡的**前缀**，不是同一张卡）。

## 自捕两枚

- 夹具协变：`_fx()` 首版把 n_hold/vol_target 同时喂给票与被审侧，于是「打断身份」的三条腿
  打不断（`n_hold -> EXECUTES_REFUSED_BOOK`，改一改两侧一起动）——**一个失败不了的腿不是证据**
  （r1371 臂类教训同族）。正法=被审侧单独参数化（judged_n_hold / judged_vol_target）。
- 已发布 receipt 的 verdict 必须属于五个冻结词之一（L19），否则读者会遇到「没收据词」。

## 诚实的未测面

- 带壳（beta+cash）的年度形状**本轮没测**：phase_gate 的年度表现在是裸书的。
  下一个转仓日（2026-11-11）之前应把壳送进同一把年度尺子——这是本轮点名的下一步，
  不是本轮结论。
- 票的 5 只里有 4 只 `crossborder` 类，而 card config 的 universe_classes 是
  equity/commodity/convertible：**分类名不同源**（票侧叫 crossborder）。本轮不据此改判，
  只记一行，供下一轮核对分类映射是否同一套。

正身 = `scripts/etf_book_execution_admission_gap.py`（selftest 18/18 · run rc0 ·
--check OK）+ `results/etf_book_execution_admission_gap.json` + S6 腿
`execution_admission_gap`（0.1s rc0，`run` 形式防陈旧）。