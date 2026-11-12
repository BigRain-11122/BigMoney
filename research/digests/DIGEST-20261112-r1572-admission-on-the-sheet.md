# DIGEST 2026-11-12 r1572 — 准入判词第一次印在操作员手上，并当场自证是脆的

**问题**：11-11 那本 k=0.9094 的书今天开盘就要成交（r1571 新增 `pending_fill`），但纸上
没有一个字说这本书**允不允许吃新增资本**。年度闸的判词只活在 `results/etf_book_year_gate/
YEAR-GATE.json` 里，且带自己的 as-of 日期——一张今天印的纸可以引用一个三天前面板算出来的
结论，读者无从分辨。

**做了什么（产品）**
1. `scripts/etf_book_order.py` 新增 `admission_read/admission_md`：从闸面**机读**判决、未过项、
   距线距离、上一版判决与口径并列，印进卡片执行单的 `## 准入判决` 节。缺面＝「无法核验」、
   没判过本书＝「未评估」，两者都不许读成通过（3 条自检腿钉死）。
2. `scripts/etf_book_year_gate.py` 新增 `margin_to_line` 与 `prior` 块（上一版 verdict/top2，
   翻面时带移动量），`check` 增 6 条腿（24/24）。
3. `smoke_test.py` 新增活面腿：闸面无距线/无翻面字段，或卡片缺该节，即红。

**读数（2026-11-11 面板，均为机读）**
- 单相位年度闸：top2 **0.6995**（线 0.7000，距线 **+0.05pp**）→ **ADMIT**；两小时前
  同一张脸（数据止 11-09）是 0.7067 → CONDITIONAL。两根 bar 移动 **0.72pp**。
- 只算完整年口径 **72.78%**（仍在线之上），冻结口径含 partial 年 69.95% —— 方向相反。
- 五相位面（同书五个起点）：中位 **78.89%**、spread **9.04pp** > margin 8.89pp →
  **UNADJUDICABLE_PHASE**。
- 卡片首行因此写成：`判决：**ADMIT**（单相位）——与五相位面 **UNADJUDICABLE_PHASE** 冲突`

**读法**：这不是「书变好了」也不是「书变坏了」，是一把只量 bar-to-bar 的尺子在一根幸运
bar 上给出的通过；同一本书换一个决策起点能飘 9pp。方法论卡＝E556。

**验证**：`etf_book_order --selftest` **170/170**（新增 legA-F）｜`etf_book_year_gate
check` **24/24**｜`etf_book_year_gate selftest` 10/10｜卡片纸实况含冲突行与「不得扩资本」。
