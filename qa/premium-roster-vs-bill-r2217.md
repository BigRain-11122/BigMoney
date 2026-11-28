# r2217 — 名单与账单必须数同一批腿（溢价面）

## 一句话

溢价面同一张页上印着两句话：一句说「哪几腿的净值日期只算标签」（名单），一句说「闸按哪几腿的不确定度算钱」
（账单）。2026-11-27 那张票面上，名单**只列了两腿**（159655、513690），账单却**按三腿**加宽（159519 也在算），
于是读者按名单去核「还有哪些日期没证」时，会漏掉一腿——而那一腿的钱已经进了闸的数字里。

## 根因

`build_face` 里做日期普查时用的键是「换基了没有」而不是「这条腿自己怎么判日期」：

```python
key = ("rebased-onto-session" if r.get("trust") == "nav-rebased-same-day"
       else (r.get("date_proof") or "unknown"))
```

一条腿只要被换基过，它的 `date_proof`（`label-only`）就被这个键**顶掉**，掉出 `label_only` 名单。
159519 正是这种腿：板面分母属另一场（标签如此说）、价格路径判不了日、本场公布了净值 → 换基重定价。

## 正法（两件事，一件事一个面）

1. **普查按腿自己的判据分桶**：`by_proof` 现在 5 腿全在（3 label-only + 2 path-proven），
   `label_only` 名单 = 159655、513690、159519；换基另立一维 `rebased_onto_session`，两个维度不再互相顶掉。
2. **换基过的腿不进闸的账单**：`normalize_nav_board` 只保留「在该 session 公布了单位净值」的基金，
   所以换基用的分母**按构造就是本场的**——这次换基已经把「分母是哪一天」这个问题答了。
   再按旧的不确定度加宽，就是把一个已经回答的问题继续算钱；而同一张面对 `path-overrules-label`
   的换基腿早就是「不charge」，两条腿做的是同一个动作，闸的待遇不该不一样。

## 盘上实读（2026-11-27 场，重渲染后）

| 项 | 改前 | 改后 |
|---|---|---|
| 名单 `label_only` | 159655、513690（**漏 159519**） | 159655、513690、159519 |
| 账单 `unproven` | 513690、159519 | 513690 |
| 不确定度 `exposure_cny` | 883.15 元 | 625.88 元 |
| 最坏情况 `bounded_total_cny` | -301.05 元 | -558.32 元 |
| 判词 `verdict` | `clean-even-worst-case` | `clean-even-worst-case`（不变） |

判词不变是对的：两条读法都在阈值内，改的只是「这笔账算得对不对」，不是「结论松不松」。

## 自检

`python scripts/etf_premium_face.py selftest` → **63/63 PASS**（原 60/60，+3 条行为腿）

- **L52** 换基的标签腿同时在名单上、不在账单上：`label_only=["513690"]`、`rebased_onto_session=["513690"]`、
  `ambiguity_charged=[]`、`unproven=[]`、`verdict=clean`、`settled_by_rebase=["513690"]`，页面印「换基定死」「不计入上面的不确定度」。
- **L53** 负控一：把换基拿掉（本场没公布净值）→ 该腿转 `nav-cross-date`、不被定价，账单仍为空。
- **L53b** 负控二：标签说本场、路径判不了日、又没有换基 → 该腿**照样**进账单（`ambiguity_charged=["513690"]`，
  判词不是 clean），证明 L52 不是在「什么都别算」的面上的假绿。

## 链路与页面

- `python Tools/s6_chain_bmc.py 2217 --only=etf_premium` → 1/1 rc0（周六 fetch no-op，check 步过）。
- `python Tools/page_repeat_guard.py scan` → 4 face, 0 repeated sentence（同一事实只在闸那一节说一次）。
- `render` 重渲染 `results/etf_premium/PREMIUM-2026-11-27.{json,md}`，逐腿读数与改前一致（改的只是两句话的名单与账单）。

## 未做（如实）

- 没把 `over_hurdle.verdict` 搬进 CEO 一页纸：CEO 页读的是另一张 `etf_book_premium_leak` 面，
  两面的读数口径不同（一个是相对净值的钱，一个是执行闸的不确定度），搬之前要先把「读者拿它做什么」写清楚，
  本轮不做，留作下一窗。
- 全量冒烟在本轮跑（见轮报告），本文件只覆盖溢价面这一族的证据。
