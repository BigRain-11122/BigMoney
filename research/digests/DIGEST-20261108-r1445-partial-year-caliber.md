# DIGEST r1445 — 部分年在年度门里既是保护也是白送

**一句话**：年度门把不足一年的窗口算成一年，这在「最差年」上是保护、在「top-2 占比」上是让利；
已发布的 26 本书里，同一条记法**既批准了三本、也否决了一本**。

**实物**
- `scripts/etf_book_partial_year_caliber.py`（selftest 12/12 · --check 0.15s · run 0.12s）
- `results/etf_book_partial_year_caliber/CALIBER.json`（26 本书 × 三口径）
- `research/ETF_BOOK_PARTIAL_YEAR_CALIBER.md` · 卡 E450 · S6 腿 `partial_year_caliber`（run 形）

**读数**
- 口径 A（生产，含部分年）8 ADMIT / 14 CONDITIONAL / 4 REFUSE；B（只完整年）7/15/4；
  P（保护一致：Y1/Y2/Y4 只完整年、Y3 全部年）6/16/4。
- A→P 翻转 4 处：`nobond_base` 68.98→71.76、`ticket_construction_plain_plus_overlay`
  67.52→77.57、`n5_r20_plain` 68.98→71.76（三本 ADMIT 消失）；`admission/ALL`
  79.34→69.57（一本 CONDITIONAL 反被批准）。
- 身份腿：26 本书口径 A 的判决逐本等于它自己发布的 verdict，0 破。

**意义**：r1440 的「在跑的书 ADMIT」有一半来自记法而非选择——把部分年拿掉它读 77.57% 不过线。
但同一记法也让 `admission/ALL` 被拒，所以本轮不能推出门偏松或偏严，只能推出「同一规则两个方向」。

**未采纳 / 未测**：口径 P 是建议，生产仍是 A，改口径须 2026-11-11 决策轮 + 预注册；
P 是否更准无证据（r1444 已证四条判据对下一年全盲），P 的合法性只来自「按判据语义一致」。

**坑**：首版夹具（L2）让部分年自己成了 top-2，于是「让利方向」那一腿打不断——部分年必须贡献
分母而不进分子才成立；L7 的三通过映射写错两通过，靠断言当场抓住。夹具不能只摆正确样本，
要摆**它声称能区分的那一类**样本（r1371 同族）。