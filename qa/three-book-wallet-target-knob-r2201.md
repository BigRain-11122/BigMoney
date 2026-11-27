# QA — three_book_wallet_target_knob (r2201 bm-c)

面：`results/three_book_wallet_target_knob.json` + `research/THREE_BOOK_WALLET_TARGET_KNOB.md`
脚本：`scripts/three_book_wallet_target_knob.py`
父面：`results/three_book_wallet.json`（r2198）/ `results/three_book_wallet_ladder.json`（r2200）

## 1. 问题是否被回答

| 问题 | 面里答案 |
|---|---|
| 拧风险目标能买到第三本书吗？ | 能，但只在跨过 9.1029% 之后；9.10% 这一档还差 318.7 元，仍买不到 |
| 拧目标本身值钱吗？ | 不值钱。vol 缩放是常数倍，Sharpe 逐位不变（5% 与 12% 两档忽略门槛时最优权重相同，Sharpe 差 0.0） |
| 拧目标唯一能改变答案的方式 | 移动 carry 的资本门槛（=91,029/目标），让之前买不起的权重格子进场 |
| 跳变有多大 | 9.1%→10% 一段：Sharpe 1.0604→1.4965（+0.4361），年化 7.40%→14.74% |
| 门什么时候完全消失 | 18.206%（此时忽略门槛的最优权重 [0.35,0.15,0.50] 也进门） |

## 2. 与父面的对账（硬门）

- 本面 8% 档 `w=[0.65,0.35,0.0]`、cagr 0.065078、sharpe 1.060401、vol 0.061235、maxdd -0.067237
- 父面 `best_inside_gate` 四项读数 → **最大绝对差 0.0**（容差 1e-6，`reconcile_vs_parent.ok=true`）
- 实施过程中真抓到一次口径错：首版按「先缩放后对齐」跑，8% 档 vol 印 6.58% 而父面 6.12%；改为父面的「先对齐后缩放」后才归位。这条已写成 `reconcile_vs_parent` 字段，`check` 缺它即红。

## 3. 自检与行为腿

- `selftest` **250/250 PASS**：门槛算术（budget/target 单调下降）、cb/etf 门槛目标无关、gate_open 与父面 `feasible()` 在 231 个格子上逐格一致、缩放定理（同序列两档 Sharpe 差 <1e-9）、常数序列 Sharpe 不为 inf、判词四分支、1M 一手机刻度精确、9.10% 判不可行。
- `check` rc=0，内建：每档 vol 不超自身目标、carry 门槛严格等于 budget/target、宣称 carry 可行必须 weight×wallet ≥ floor、缩放定理未破、一手机刻度算术、判词在白名单、页面必须印自家判词、**每段「权重没变」必须同时 Sharpe 没变**。
- 行为腿（本地毒化-复原，已复原）：
  - 改 `reconcile_vs_parent.max_abs_delta=0.5, ok=false` → rc3 + `8% arm does not reproduce the parent's gate answer`
  - 改 `knob_effect_bands[0].sharpe_jump=0.3`（权重仍标未变）→ rc3 + `band 0.05->0.06 says weights unchanged but Sharpe moved 0.3`
  - 按字节还原 → rc0

## 4. 诚实边界（面里已印）

- 12% 档实际交付波动 9.79%（标称目标是风险预算上限，不是交付承诺）
- 不重算任何一本书的回测；三本序列全部来自各自已发布面
- 不假设放大资金对同一批标的的冲击成本
- 本面不接线进生产书

## 5. 状态

完成。三条自检全绿，对账 0.0，未宣称任何未经复算的数字。
