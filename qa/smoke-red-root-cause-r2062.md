# QA · smoke 红腿根因面（r2062 · bm-c · 2026-11-25）

对象：`scripts/smoke_red_root_cause.py` → `results/smoke_red_root_cause.json` + `research/SMOKE-RED-ROOT-CAUSE.md`
问题：34 条红腿是 34 个缺陷，还是一条上游面停答造成的成片红？修的时候按什么顺序？

## 结论

**PERMISSION_UNREADABLE_BECAUSE_IDENTITY_BROKEN** — 29/34 条红腿在书家族里，根因是
`results/etf_book_size_rulers_decision.json` 自报 `IDENTITY_BROKEN`（identity leg
`ticket_k_reproduced` 在 2026-10-23 的 bar 上比对、而票面决定在 2026-11-11），
→ `etf_book_rebalance_permission.json` 因 baseline 读数不可分类而 `permitted_k=null`
→ `etf_book_cut_order_gap.json` 输出 `UNREADABLE / incomplete_receipts`（不写 `gap_k`）
→ 下游尺寸/票面/阶梯腿成片红。

反事实读数：三条可读 path 读数给出 `permitted_k=0.435003`（来自 `universe`），
在册尺寸 `k=0.435003`、容差 `0.005` → **KEEP_ALLOWED**。即这张面今天什么都不说，
而它可以说的是一句「允许保持尺寸」。此数是算术反事实，不是许可。

## 验证记录（实弹）

| 项 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts/smoke_red_root_cause.py selftest` | **12/12 PASS** |
| 生成面 | `python scripts/smoke_red_root_cause.py run` | rc0 · root 检出 · book_family=29 outside=5 |
| 复核 | `python scripts/smoke_red_root_cause.py check` | rc0 |
| 负控 A | 手改 md 一格（29→28） | rc1 `CHECK FAILED ... (not STALE: same inputs, different text)` |
| 负控 B | 删 json 面 | rc3 `STALE face missing` |
| 负控 B' | `run` 复原 | json **逐字节相同**、check 转绿、md 逐字节相同 |
| 负控汇总 | `python results/_r2062bmc_negctl.py` | **6/6 PASS** |

漂移分类遵循 r1934：源面数字动 = STALE（付钱补写）；同输入文本不等 = CHECK FAILED（真缺陷，不加 STALE 字样）。

## 未验证（如实）

1. 34 红取自 `logs/smoke_legs.json` 的 **2026-11-24T20:12:28** 读数（已 285.9min 旧），本轮未重跑全量冒烟（竞争窗，连续第 10 轮）。
2. 2 条 KeyError 腿（`permission_persistence: 'gap_k'`、`cash_roll_today: 'cash_cny'`）中 `cash_cny` 一条可能另有二因，未被本面证明同根。
3. 5 条家族外红腿（discount subset / paper book / astock_resid / futures TSMOM / live-quote）本面不表态。
4. 重建链写共享面，本轮**未执行**；重生后腿是否转绿必须重跑冒烟才算数。

## 复现

```
python scripts/smoke_red_root_cause.py selftest
python scripts/smoke_red_root_cause.py run
python scripts/smoke_red_root_cause.py check
python results/_r2062bmc_negctl.py
```
