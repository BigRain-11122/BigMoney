# QA — 一条读不出的轨凭什么让整本书闭嘴（r2071 bm-c）

工作面：`scripts/etf_book_unreadable_rail_floor.py` · 面 `results/etf_book_unreadable_rail_floor.json` · 页面 `research/ETF_BOOK_UNREADABLE_RAIL_FLOOR.md`

## 为什么要这张面

`scripts/etf_book_rebalance_permission.py` 的权限是

```python
permitted_k = min(paths.values())     # 只取 PATH 轨
if unreadable:                        # 任何一条轨无法分类
    verdict = "UNREADABLE"; permitted_k = None; keep_allowed = None
```

而 `unreadable` 那条轨在第 147 行就 `continue` 掉了，**永远不会进 `paths`**。于是「有一条轨读不出」被当成「权限算不出」——两句话不是一句。

2026-11-24 的实际后果（有据）：

| 步骤 | 事实 |
|---|---|
| 断的是哪条 | `baseline_published`：k=0.460253 与票面 k_rule=0.458463 的循环恒等式不成立，无法分类 |
| 三条路径轨 | universe 0.435003 / window 0.747086 / window_x_universe 0.667665 —— 全部可读 |
| 静态轨 | denominator 0.343508（静态，按 producer 自己的规则不进 min） |
| 权限面判词 | `UNREADABLE`、`permitted_k=None`、`keep_allowed=None` |
| 下游 gap 面 | 写了一张没有 `gap_k` 的存根，覆盖掉 2026-11-22 那份可读读数（k=0.435003） |
| 冒烟 | 3 条腿死在这张存根上（2×KeyError、1×TypeError），而不是报告「上游读不出」 |

## 判据（写死在 `floor_from_readings()`，纯函数，不读盘不读钟）

未分类轨只有在**它的数字可能压低地板**时才有权让权限闭嘴：

| 情形 | 判词 |
|---|---|
| 每条未分类轨都有数，且都 ≥ 地板线 `k_now - size_tol` | `FLOOR_IS_COMPUTABLE` → 印 `min(可读路径)`，未分类轨作为声明并列 |
| 任一条未分类轨没有数字，或低于地板线 | `FLOOR_MUST_WAIT` → 它可能才是绑定地板，闭嘴是对的 |
| 一条路径轨都没有 | `FLOOR_MUST_WAIT`（理由必须写「没有决策路径」，不许混进未分类那条） |

边界刻意钉死：`k == 地板线` 判**可算**（不更严），`k == 地板线 - 1e-9` 翻面。

## 今天的读数

- 判词 `FLOOR_IS_COMPUTABLE`
- 权限 **0.435003 = 43.5003%**，绑定轨 `universe`，可保留，应实现 **0.00pp**
- 毛额 **435,003.00 元** vs 票面在册 **434,723.80 元** → 距权限 **279.20 元**
- 已发布面：判词 `UNREADABLE`、`permitted_k` 空 —— 同一份盘上，可读的三条轨已经给出答案
- 下游：gap 面存根（无 `gap_k`），冒烟 765 腿 / 34 红（2026-11-24T20:12:28）其中 **3 条**死在这张存根上

## 证据

- `--selftest` **23/23 OK**（15 组行为腿：今天的面可算且落地恰在在册尺寸、静态轨不进地板、未分类轨低于地板线翻面、无数字翻面、边界恰在地板线不翻、`-1e-9` 翻、无路径轨理由只提路径、判词是函数不是常量、gap 面存根真抛 `KeyError('gap_k')`、权限面真印空、毛额算术、页面块含判词与未分类轨、摘要顺序无关且能抓变更）
- `run` rc0 → `FLOOR_IS_COMPUTABLE permitted_k=0.435003 keep_allowed=True cut_pp=0.0 cascade_legs=3`
- `--check` rc0（面与页面块逐字复核）
- 负控 `results/_r2071bmc_unreadable_rail_floor_negctl.py` **20/20 OK**：
  - 原样副本 → rc0
  - 改 `permitted_k` 一格 → rc3 且含 `CHECK FAILED` 且**不含** `STALE`（不许让 S6 链白跑一次重建）
  - 动 `inputs_digest` → rc3 且含 `STALE` 且不含 `CHECK FAILED`
  - 改页面 marker 块一行 → rc3 且点名 page block（并先断言那一行真在页面里，防真空腿）
  - 每次复原后重跑 → rc0
  - 三个共享面（permission / gap / smoke_legs）前后 sha256 恒等 —— **负控零污染**

## 它不声称什么

- 不改 `etf_book_rebalance_permission.py` 的一行（共享面，竞争窗内禁改）：本面给的是「开口是否必要」的算法与价钱，补丁落地是静窗后的事
- 不把未分类轨当成「没问题」：`FLOOR_IS_COMPUTABLE` 必须在同一页并列那条轨的名字与数字
- 不声称 279.20 元可以下手：那是毛额与在册市值之差，票面自己的 `und` 口径另有一行（434,546.00），两个口径的差额 177.80 元本面只披露不裁定

## 下轮指针

1. 静窗后把 `if unreadable:` 改为 `if unreadable and not paths:` 加「未分类轨 ≥ 地板线」闸，再跑本面看判词与数字是否移动
2. 给 `etf_book_permission_persistence.py:204` 与 `etf_book_cash_roll_today.py:340` 加守卫：上游是存根时报告 `UPSTREAM_UNREADABLE`，禁 KeyError 崩
3. 全量冒烟连续第 16 轮未跑（765 腿 / 34 红仍是 2026-11-24T20:12:28 那份），S6 链连续第 16 轮未跑 —— ≤48h 必须收口
