# DIGEST 2026-11-08 · r1446 · supply-gate decision

**问句**：r1445（口径之争）与 r1444（四条判据全盲）并读，能否合成 2026-11-11 调仓的一个答案？

**做法**：`scripts/etf_book_supply_gate_decision.py` 只读四份已发布收据，把 26 本已发布书按
「判决是否随口径改变」分档，再问被执行的那本书落在哪一档。判据先冻结在文件头
（INVARIANT / MOVES_ON_CONTROL_ONLY / MOVES_ON_BLIND_CHECK / MOVES_ON_SEEN_CHECK / UNREADABLE）。

**读到的数**：
- 26 本：INVARIANT 21、只与全完整年对照不一致 1、MOVES_ON_BLIND_CHECK 4、有前向关系档 0。
- 被执行书 `nobond_vt08_adopted`：A/B/P 三口径**同为 CONDITIONAL**（Y4 71.08% / 72.78%，线 70%，
  两种记法都不通过）⇒ 口径之争改不了钱上的这句话。
- 在定价的构造 `ticket_construction_plain_plus_overlay`：A=ADMIT / P=CONDITIONAL，
  正是四个「白送」之一（r1440 已把它的 k_now 复现到 0.0038）。
- 跨收据一致性：wrapper 收据与 caliber 收据对同名臂的 word 全部一致（3/3）。

**判决**：`CALIBER_IRRELEVANT_TO_MONEY` —— 调仓单照已发布判决执行；口径问题不影响它；
但任何**加仓**不得引用四条 gift 臂的 ADMIT（它们的通过只在部分年算作一年时成立）。

**自抓**：首版把「A==P 而 B≠A」读成 UNREADABLE（把正常对照差异当收据缺陷），现已单列
MOVES_ON_CONTROL_ONLY，S6 三条腿（selftest 21/21 · --check 9/9 · run rc0 0.01s）钉住。

**边界**：不重定价、不调引擎、不采纳口径 P；分类只说收据能支持什么。