# QA — 把四张 carry 面接上链，并把「上游动了一格」从缺陷改回漂移

轮次：r2098（bm-c）｜日期：2026-11-25

## 为什么做这件事

上轮（r2097）把五张 carry 面收敛成一个决定（IC 可报 0.03pp 尺子差、IM 无可报数、两条腿都不能下单），
并如实记下缺口：**这个面没有链腿也没有冒烟腿**。同一晚 r2095（容量面）、r2094（always-on 价面）、
r2096（移仓台阶面）也全部欠着腿。而决定面读的四个输入里，有三个就是这些没有腿的面。

后果在今天的冒烟里直接看得见：767 腿跑出 **43 条红**，其中一族是同一个形状——
「the panel moved under this face -- stale」。面板推进了，面停在旧的一天，没有任何腿会替它重算。

## 改了什么（四处）

1. **决定面 check 的两态**（`scripts/idx_fut_carry_decision_face.py`）
   原先只把「admitted-ruler numbers moved」判为 STALE，其余一律 CHECK FAILED。今天实锚：
   资本线推进一个 session，IC 缺口 129,565.88 → 128,410.62，check 报 `CHECK FAILED: IC gap ...`，
   而链的 `run_leg` 只在文案含 STALE 时才付费重写（r1850 的合同词）→ 这张面会天天红。
   正法：面里本来就记着每个输入的 digest，**先比输入字节**——动了说 STALE，一样才说缺陷。

2. **移仓台阶面 check 的两态**（`scripts/idx_fut_carry_roll_step_reversal.py`）
   原来只有 CHECK FAILED / CHECK_OK。加一条：`evidence_cutoff` 前进 = STALE。

3. **容量面 check 的两态**（`scripts/idx_fut_carry_capacity_lots.py`）
   原来只比 panel window digest，而每手 carry 来自 always-on 价面（链在前几腿会重写它）。
   链上一次跑的内部实锚：`IM strictest capacity_carry_cny 98,952,854.0 -> 94,012,131.08`，判成缺陷。
   正法同上：先比 `inputs.price_face / spec_face` 的 sha256。

4. **接线**：`Tools/s6_chain_bmc.py` 加 4 条腿（always_on_price / roll_step_reversal /
   capacity_lots / decision_face，均为 `(check, run)` 对，排在 margin 之后、capital_substitution 之前，
   保证决定面读到的上游都已重算）；`smoke_test.py` 加 8 条腿（四张面各 selftest + check）。

## 证据

- `python scripts/idx_fut_carry_decision_face.py --selftest` → **26/26**
  （含「手改面 = 缺陷，不含 STALE 字样」「上游动 = STALE」两条行为腿）
- 现场漂移：改前 `CHECK FAILED: IC gap 129565.88 -> 128410.62`；改后
  `STALE: input face(s) moved: capacity -- rebuild this face`，rc=3
- `python scripts/idx_fut_carry_capacity_lots.py --selftest` → **15/15**
  （含「改数 = CHECK FAILED」「面板 digest 动 = STALE」）
- `python scripts/idx_fut_carry_roll_step_reversal.py --selftest` → **12/12**
- 链点名实跑两遍：
  - 第一遍 `--only=...` → **3/4 rc0**，容量面 rc3 暴露上面第 3 项缺陷
  - 修完第二遍 → **4/4 rc0**，其中
    `idx_fut_carry_capacity_lots ... CHECK_OK (2026-11-25, verdict MARKET_IS_NOT_THE_GATE) +refresh(rc=0,0.2s)`
    即这条腿自己从 STALE 变成补写再变绿（r1934 要的行为）
- 持仓账本两条红现场自愈：`positions_ledger_write` 重写（ledger 14 bar）→
  `positions_ledger CHECK_OK: PRINTED_ROWS_REBUILD_THE_BOOK`，证明那两条 FAIL 是代差不是算法错

## 本轮面推进（产品增量）

| 面 | 改前 | 改后 |
|---|---|---|
| `results/idx_fut_carry_capacity_lots.json` | cutoff 2026-11-23 | **2026-11-25**（468/752 手 @1% 线，余量 234x/376x） |
| `results/idx_fut_carry_roll_step_reversal.json` | cutoff 2026-11-24 | **2026-11-25**（MIXED_BY_PRODUCT，IC 两把尺子 COST_BOOKED_BY_LATER_CARRY） |
| `results/idx_fut_carry_decision_face.json` | cutoff 2026-11-23 | **2026-11-24**（NO_ORDER_ON_BOTH_LEGS；IC 差首档 128,410.62 元；IM 口径未定） |

## 未做（如实）

- 冒烟全量本轮在改代码前跑过一次：**765 腿 / 43 FAIL**，形状以「面板推进、面无腿」为主。
  本轮跑完 S6 全链后需再跑一次冒烟确认收敛（链结果见轮报告）。
- 43 条里另有一条独立缺陷族不在本轮射程：CEO 页三节（bets / derisk / k_gap）落后且
  `provenance=no_writer`，属页面写者缺口，需单独一刀。
