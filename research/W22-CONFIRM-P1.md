# W22-CONFIRM-P1 — 节前效应收窄确认（hol_pre1 × h∈{3,4}）

> 性质：**确认面，不是发现面**。W22 十格便宜筛查 `results/trial_labor_w22/w22_cheap_screen.json`
> 判 `SCREEN_ZERO_SURVIVOR`（family p=0.0398，K=200 下限 0.00498，零 Holm 存活）。收窄依据
> = 筛查摘要 `research/digests/DIGEST-20261020-w22-cheap-screen.md` 第 2 条：唯一可辩护的续作
> = hol_pre1、h∈{3,4} 的**前向新窗确认**。收窄属事后选择，故只能在新数据上判。
> 本件起草=bm-b r1086，冻结先于任何烧录（R250 一步例：seed 同 commit 登记）。

## §0 身份与来源

- 上游：`TRIAL_LABOR_W22_PREREG.md`（十格草案，未烧）
- 筛查：`scripts/w22_null_screen.py` → `w22_cheap_screen.json`（selftest 15/15，3.0s，零网络）
- 本面 runner：`scripts/w22_confirm.py`（status / judge / selftest）
- 车道：bm-b（data-locality，E23 日面）

## §0.5 冻结前硬闸

1. 冻结先于烧录：本件与 seed 登记同 commit，任何 forward 判读发生在本件落链之后。
2. **fence=2026-10-19（含等号排除）**：证据日一律 `date > 2026-10-19`；筛查用过的 180 个窗口
   一天也不进确认面。
3. 零窗口 = `AWAITING_FORWARD_WINDOWS` 诚实态（不是失败，不造数）。
4. 不追跑到达标为止：停规则固定（§7），样本不足=等，不改判线。

## §1 α 机制段

- 机制选型（四选一）：**日历季节性（事件驱动）**——节前最后交易日（hol_pre1）的年化日历结构。
- 机理陈述：长假前避险与仓位调整带来可预测的短窗漂移；持有 h∈{3,4} 个交易日吃该漂移。
- 已知混杂：与「低波/防御」风格可能同向。D6 同族 `max|corr| ≥ 0.7` 拒收仍须在 judge 报告
  以在册六员 forward 面相关性给出（确认不豁免 D6 披露）。

## §2 实验面与数据

- 面板：`data/cache/p1c_local`（E23 日等权面，单一事实源，禁横截面拼池）。
- 观测：每日一个观测；forward 收益向量 = `seasonal_horizon_stability.horizon_matrix(d, valid, h)`。
- 基线池：forward 区内所有有效 h-窗日（**同区同 h**，与信号日同尺）。
- 统计量：`mean(fwd[signal]) - mean(fwd[forward_pool])`。

## §3 冻结参数（机读镜像 = `scripts/w22_confirm.py` 常量 + `spec_sha16`）

| 项 | 值 |
|---|---|
| cells | `[("hol_pre1",3), ("hol_pre1",4)]` |
| fence | `2026-10-19` |
| null | 同尺无放回安慰抽样，双侧，K=1000 |
| seed | `20670500`（SEED_REGISTRY: `w22_confirm_p1_nulls`） |
| 多重性 | Holm step-down，m=2，α=0.05（阈值 0.025 / 0.05） |
| 停规则 | 每 cell ≥ 12 个 forward 窗 |

## §4 判据（冻结，禁结果后改线）

- 每 cell：`p_two_sided = (1 + #{|null| ≥ |obs|}) / (K+1)`。
- 确认通过 = **至少一个 cell 过 Holm**（`p ≤ α/(m-i)` 且 step-down 未断）。
- 无 cell 过 → `JUDGED_NOT_CONFIRMED`（如实判负，不得改判线重跑）。
- 判据库：`science_gates.g1_prime_v2` / `g2_registration_v2` 共用；本面为确认面，不新增
  注册线（若通过，注册走 §8 消费方流程）。

## §5 事前预测（写于结果前，密封）

- 若节前效应为真：`hol_pre1@h4` forward 面 excess 应为**正**且量级接近筛查值的 30–100%
  （窗口更少，噪声更大，允许区间宽）。
- 若 forward 面符号翻负或 |z|<1 连续两批 → 机理判负，家族进 `axed` 行，不重开（重开须新证据
  新预注册，O-20260925-1105 口径）。

## §6 出场轴（显式门 · TRIAL_LABOR_LAW §4 ②）

`strategy_own`：**精确 h 根 bar 收盘平仓**，引擎缺省出场栈**显式禁用**。本面无止损/止盈叠加层。

## §7 收口与停止规则

- `status` 每轮幂等可跑（零网络、确定性），把累计窗口数与 excess 写
  `results/trial_labor_w22_confirm/w22_confirm_state.json`。
- `judge` 仅在 `READY_TO_JUDGE`（两 cell 各 ≥12 窗）时开跑；提前调用 rc=2 并输出停规则
  实况，**禁绕过**。
- 预计首个可判窗：2026 年内剩余长假前一日（日历由面板推进自动带出，不手填日期）。

## §8 产物与消费方

- 产物：`results/trial_labor_w22_confirm/w22_confirm_state.json`（+judge 后同件扩写）。
- 消费方：`TRIAL_LABOR_W22_PREREG.md` §5 供给决策（收窄确认 vs 家族砍线）；
  通过则进 W22 正式 runner 供给队列，未通过则家族 `axed`。
- 记账：本面零试验账增量（无烧录）；judge 时按实际 cell 数入 ledger。