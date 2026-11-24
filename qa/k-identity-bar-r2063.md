# QA · k 身份面在「哪一步」（r2063 · bm-c · 2026-11-25 01:2x）

对象：`scripts/etf_book_k_identity_bar.py` → `results/etf_book_k_identity_bar.json` + `research/ETF_BOOK_K_IDENTITY_BAR.md`
问题：r2062 把 29 条书家族红腿归到 `ticket_k_reproduced` 这一条 identity 腿，说它「在 2026-10-23 的 bar 上比、
而票面决定在 2026-11-11」。这一层是不是真断？断在哪一步、差多少钱、怎么修？

## 结论

**IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP** — 两个数不是两个说法，是**同一张 beta 调度上的两个相邻步**：

| bar | k | 谁在读 |
|---|---|---|
| 2026-10-23 | 0.460253 | 腿：`step_in_force(sched, book_decided_at=2026-11-11)` |
| 2026-11-20 | 0.458463 | 票面 `k_rule`：票面 `base_bar=2026-11-24` 之前最后一步 |

k 只在调度步上变。票面定价日的尺寸 = 定价日之前最后一步 = 2026-11-20 的 0.458463；
腿却取「名册决定日」之前最后一步 = 2026-10-23 的 0.460253。两 bar 之间正好夹着一个 **0.179pp**
的步（1,000,000 元票面 = **1,790 元**），于是腿在名册决定后的第一个 session 起恒红，一直红到今天。

身份的正形式（本面三条腿同时成立）：票面 k 必须是调度上的**唯一点**、且是定价 bar 之前**最后**一点。
「等于我挑的那根 bar 上的 step」不是身份。

漂移画像（同一张调度 78 步）：相邻步 |Δk| 中位 **0.2599pp**、最大 **6.7573pp**、**46/77** 步 ≥ 本文这个
0.179pp 弧 —— 也就是说，任何「键错 bar」的腿只要两 bar 之间夹了任何一步就会红，而夹步是常态。

## 验证记录（实弹）

| 项 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts/etf_book_k_identity_bar.py --selftest` | **14/14 OK** |
| 生成面 | `python scripts/etf_book_k_identity_bar.py run` | rc0 · INTACT · priced=2026-11-20 leg=2026-10-23 · dk=-0.1790pp |
| 复核 | `python scripts/etf_book_k_identity_bar.py --check` | rc0 `CHECK OK` |
| 幂等 | `run` 连跑两次取 SHA256 | json **逐字节相同**、md **逐字节相同** |
| 负控 | `python results/_r2063bmc_kbar_negctl.py` | **10/10 OK** |

负控覆盖：非调度值必须拒；真调度点但非定价 bar 前最后一步必须拒；定价 bar 挪到腿那一步必须拒；
名册日挪到票面那一步必须说「两行同步、本诊断不适用」；6dp 存储容差的必要性（1e-12 下同族值会假红）；
金额单位（pp/100×票面，不是 pp×票面）；判词与 legs 必须一致；局限必须印出。

## 未验证（如实）

1. **没有改共享面**：竞争窗 rc=3（对端 interactive pid 79608 22:39 起在写共享面，19 张面在轮首前被动过），
   按 r1907 只落新增文件面。腿本身、permission 面、cut-order-gap 面本轮**零改动**。
2. **没有重跑冒烟**：腿转绿必须等 patch 落地后由冒烟腿自己说话，本面不代它宣称。
3. 调度只在本 ticket（`TICKET-2026-11-24.json`）上核对过；漂移画像给的是「这种弧有多常见」，不是「历史上有多少张票踩过」。
4. 书家族外 5 条红腿本面不表态（r2062 已点数）。
5. `results/etf_book_k_gap.json` 盘上是 2026-11-20 一代（cutoff 2026-11-20、verdict FLOOR_CUT_THIS_SHEET），
   与 r2062 快照里的 UNREADABLE 不同代 —— 本面按盘上实况记录，不跨代拼接。

## 修复规格（静窗后一行照抄）

```diff
# scripts/etf_book_size_rulers_decision.py, inside run()
-    cells["baseline_published"], k_dec_bar, k_at_dec = baseline_cell(arms["published"], tk)
+    priced_bar = tk.get("base_bar") or tk.get("as_of") or tk.get("book_decided_at")
+    cells["baseline_published"], k_dec_bar, k_at_dec = baseline_cell(
+        arms["published"], dict(tk, book_decided_at=priced_bar))
```

禁用替代方案：把腿容差放宽到 0.1pp 也会转绿，但会掩盖相邻两行之间**真实**的断裂。修 bar，不动容差。

## 复现

```
python scripts/etf_book_k_identity_bar.py --selftest
python scripts/etf_book_k_identity_bar.py run
python scripts/etf_book_k_identity_bar.py --check
python results/_r2063bmc_kbar_negctl.py
```
