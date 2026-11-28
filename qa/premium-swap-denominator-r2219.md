# r2219 · 换腿建议的分母：一个 2026-11-28 发布的净值在决定 2026-11-27 的单

## 缺陷（实锚）

同一张 CEO 一页纸（`docs/live_usage/LIVE-2026-11-28.md`，改前）上：

- L245：`159655 这一腿换不换：它自己溢价 +10.36%（多付 ￥8,999）超过换腿门槛 3.0pp`
  → 判词 `RULERS_AGREE_SWAP`：「买孪生 159502，一次省 ￥7,021，来回收敛 9.7% 就划算」。
- L256：`没有任何金额进合计的腿：159655（本场没有可定日的净值，既不算 0 也不算进合计）`

两句话都对，但**只有一句在问分母的日期**。`results/etf_nav/source_dating.json` 对该腿的
读数是 `board_position=NO_DATA · sina_position=PREV_SESSION · sina_nav_date=2026-11-28`：
票面场次是 **2026-11-27**，分母来自**下一个日历日**（美股周五夜盘，QDII 按 T+1 披露）。
换腿面（`scripts/etf_book_premium_choice.py`）读的是同一份同日快照，从未问过这件事，
于是把「做决定时还不存在的净值」乘成人民币，变成一条可执行的换腿建议。

## 修法（三态证据，纯加法）

1. `load_nav_evidence(asof)`：读 r2213 的定日面，要求它自己的 `board_session` == 本票场次，
   否则整面作废（`other session`，昨日证明不能定今日的日）；逐码给三态
   `same-session / prev-session / unproven`，并把 `sina_nav_date` 晚于场次的天数记下来。
2. `decide_leg(..., nav=)`：算术照印（`premium_pct` / `premium_cny` / 三条路一条不少），
   但 `SWAP_AT_BOOK_HORIZON` 需要 `nav.status == "same-session"`；否则
   `STRETCHED_ON_UNPROVEN_NAV`，note 里点名「净值日期 X，晚 N 天」。
3. `face_verdict(legs)`：抽成纯函数，`check()` 与 `paths()` 共用——有未证腿且无已证 SWAP →
   `NO_PROVEN_SWAP_LEG`。
4. `inputs_sig` 收 `nav_evidence_sha`：证据面一动，面即 stale（r1311 族）。
5. CEO 页：`_etf_premium_choice_face` 透传 `premium_is_session_native` 与 `nav_evidence`；
   ⑥ 节在腿下加一句「这句话的分母不是本场的净值……是算术，不是今天能下的决心」，判词行
   分叉为 `NO_PROVEN_SWAP_LEG` 的说法。

## 证据

| 项 | 改前 | 改后 |
|---|---|---|
| 换腿面判词 | `RULERS_AGREE_SWAP` | `NO_PROVEN_SWAP_LEG`（stitched 腿全 unproven） |
| 换腿面 selftest | 25/25 | **32/32**（7 条行为腿，见下） |
| `--check` | ok | `{"ok": true, "problems": []}`，清单新增「denominator-date evidence (status per leg)」 |
| 链腿 premium_choice_write/premium_choice | — | **2/2 rc0**（1.0s + 1.0s，SAME_INPUTS ✓） |
| CEO 页自检 | ALL PASS | ALL PASS（新增正控「unproven 必须扣下建议」+负控「proven 必须把建议放回」） |
| CEO 页 L246/L252 | 无 | 「晚 1 天……是算术，不是今天能下的决心」/ `NO_PROVEN_SWAP_LEG` 白话 |

新增 7 条行为腿：同场照常 SWAP（时间本身不构成证据）／昨收降级且算术仍在／晚一天在 note 点名／
无证据 ≠ 同场（沉默不得读成干净）／面判词随腿走且一条已证腿足以印 SWAP／三桶 + 跨天数／
另一场的证明作废。

## 诚实边界

- 这**不**改变 159655 的贵或便宜：溢价 10.36% 照印，只把「建议」降回「读数」。
- 也**不**回答「它到底多贵」：要回答那个问题，需要 2026-11-27 场次当时可得的净值，而这套系统
  从不留档逐日净值发布史（板面快照只在 11-27 起有全量行）。这是下一步的基础设施缺口，
  不是本轮的结论。
- 孪生 159502 在定日面上没有行（`MISSING`），它的溢价同样未证——本轮按「无证据不升级」处理。
