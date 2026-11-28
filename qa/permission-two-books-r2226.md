# QA — 同一张单的许可词，现在各自说出属于哪本书（r2226）

日期：2026-11-28 21:3x（本机 bm-c）
轮次：2226

## 问题（读者那一页上的一处自相矛盾）

CEO 一页纸 ⑥ 节原句：

> 整手面在 2026-11-27 读 **TRADABLE_AT_1000000**（100 份一手、残差 0.075% NAV），同一天供给闸读
> **ADMIT**（唯一没过的是 （闸没写哪条））。

两处病：

1. **自相矛盾**：判词说 `ADMIT`（已许可），紧接着的子句却说「唯一没过的是」——括号里还写着
   「闸没写哪条」。成因是**票记的那本构造**（`ticket_construction_plain_plus_overlay`）五项检查全过，
   `failing` 为空列表，而模板对空列表走了一个「闸没写哪条」的兜底串。给读者看的句子不能既说通过、
   又说有一条没过。
2. **两本书被印成一句话**：同一张单上其实挂着两个许可词，`ADMIT` 属于**票实际记的那本构造**，
   `CONDITIONAL` 属于**被判的那本书**（`nobond_vt08_adopted`，唯一没过 `Y4_top2_share`，
   两年集中度 73.45% vs 线 70.00%）。原句只印了前者，后一本书的词只出现在下一段的白话里，
   读者无法判断「那我到底能不能买」。

## 改法（不动任何判词）

- `scripts/etf_book_permission_vs_size.py`
  - 新增 `check_phrase(checks)`：全过时印「五项全过：Y1_…、C1_capacity」；有不过时**点名**该检查；
    检查表缺失时印「检查表未公布」。**任何分支都不再产生「闸没写哪条」**。
  - 新增 `two_books_sentence(...)`：分别说清「票记的那本」与「被判的那本」，各自带自己的词与数字。
  - 面 JSON 增 `permission.checks / permission.check_phrase / judged_book / words_on_the_ticket`。
  - `check` 增一条：已发布句子里若出现占位串 → `CHECK FAILED`（不带 STALE 字样）。
- `scripts/ceo_live_usage.py`
  - `_etf_permission_face()` 透传 `permission_checks / permission_check_phrase / judged / words_on_the_ticket`。
  - ⑥ 节改两行：整手面一行（保留「整手面在 <日期> 读 **」句式，日词审计规则不受影响）+
    许可词一/许可词二两行，各写自己的书与检查。
  - 自检新增三条腿（见下）。

## 验证（可复跑）

| 门 | 命令 | 结果 |
|---|---|---|
| 面自检 | `python scripts\etf_book_permission_vs_size.py selftest` | **21/21 PASS**（原 13 腿 + 8 条新腿：全过不编造失败子句 / 失败检查被点名 / 无检查表≠全过 / 占位串已消失 / 两本书都被点名 / 被判书数字随词同行 / 缺面不读 ADMIT） |
| 面重算 | `python scripts\etf_book_permission_vs_size.py check` | `CHECK OK: permission=ADMIT lot=TRADABLE_AT_1000000 verdict=SIZE_IS_THE_ONLY_KNOB rows=5` rc=0 |
| 页自检 | `python scripts\ceo_live_usage.py selftest` | **ALL PASS**（+3 新腿：两块各点名自己的书 / 全页无「闸没写哪条」且无「唯一没过的是 （」 / 被判书缺失时印「没有在册判词」） |
| 重复句守卫 | `python Tools\page_repeat_guard.py scan` | 4 face, **0 repeated sentence** |
| 日词审计 | `python scripts\live_usage_day_words.py` | 判词 `PRINTED_BUT_UNANCHORED`（13 date_claims / 10 printed）——与改前 **逐项相同**，非本轮回归（面自身长期欠账：8 行日词无规则覆盖） |
| 全量冒烟 | `python -m smoke_test` | 见轮报告（本轮改码发生在其运行中段，故另跑相关腿复核） |

## 读者现在读到什么（docs/live_usage/LIVE-2026-11-28.md ⑥ 节）

> - **「下得进」和「许不准持有」是两个词，属于两本不同的书**：整手面在 2026-11-27 读 **TRADABLE_AT_1000000**
>   （100 份一手、残差 0.075% NAV）——它数的是手，不是许可。
>   - 许可词一·**这张票实际记的构造** `ticket_construction_plain_plus_overlay` 读 **ADMIT**
>     （五项全过：Y1_positive_years_share、Y2_median_positive、Y3_worst_year、Y4_top2_share、C1_capacity）
>     ——问的是「这张票能不能记」。
>   - 许可词二·**被判的那本书** `nobond_vt08_adopted` 读 **CONDITIONAL**，没过的是 Y4_top2_share
>     （两年集中度 73.45% vs 线 70.00%）——问的是「这本书的年份形状准不准持有」。

## 未改的事（如实）

- 判词未动：`SIZE_IS_THE_ONLY_KNOB` / `ADMIT` / `CONDITIONAL` / `TRADABLE_AT_1000000` 全部原样。
- 「两年年份集中度 73.45% vs 线 70.00%」这一关仍然没过——本轮只把它印清楚，没有放宽判线。
