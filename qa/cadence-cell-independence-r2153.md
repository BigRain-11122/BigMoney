# QA · 节奏表单元独立性面 r2153

实物：`scripts/etf_book_cadence_cell_independence.py` / `results/etf_book_cadence_cell_independence.json` /
`research/ETF_BOOK_CADENCE_CELL_INDEPENDENCE.md`

## 验收

| 项 | 判据 | 实测 |
|---|---|---|
| selftest | 全绿 | **13/13 PASS**（rc0） |
| run | 落盘 + 桌面句可读 | rc0，`RUN_OK ... verdict=WIDENING_IS_NOT_STRUCTURAL widest=2025Q4,2025Q3` |
| check（幂等） | 同输入重算逐字相等 | **CHECK_OK CELL_INDEPENDENCE_CONSISTENT copies=14**（rc0） |
| 外部锚 | 上游面字节变即 STALE（不是自算自的） | 自检行为腿：临时副本改动 `evidence_cutoff` 一位 → rc3 + 文字含 STALE |
| 算术镜像 | IQR 与上游 `quartiles()` 逐位一致 | 自检腿按上游插值手算 10.2825 对齐 |
| 复印不冒充独立 | 1e-9 内视为一个读数 | 实测复印对差 **1.5e-13**（8bp）/ 1.1e-13→1.5e-13（1bp） |
| 复印不是巧合 | 两个成本档 × 7 个季度全对 | `systematic_copies`=2 组，2022-09-01 ≡ 2024-03-01（2024Q2..2025Q4） |
| n 无偏读数在位 | mspd 复制一格不动 | 自检腿：复制一格 mspd 变化 0.000、IQR 变化 7.53 |
| 认得出「一格扛着数」 | 去掉一格腰斩即命名 | 2025Q3：印 5.21 → 去掉 +11.71 后 0.65 |
| 认得出「复印扛着数」 | 去重腰斩即命名 | 2025Q4：印 10.28 → 去重 2.75 |
| 不把真离散当伪影 | 无复印的宽季仍判 BROAD | 自检合成季 [-9..9] 判 BROAD_DISPERSION |
| 薄格不当 0 | <4 点即 UNREADABLE | 2022Q1（1 本）/ 2022Q2（2 本）/ 2022Q3 / 2022Q4 / 2023Q1 无 IQR，表内印 — |

## 本轮读数（8bp 主档）

- 路径通道中位 spread：印 **1.73 pp** → 去重 **2.00 pp**；行情段通道 **4.45 pp**（去重 5.13 pp）。
  → 上游 `REGIME_DOMINATES` 不变，比例反而变大。
- 2025Q4 的 10.28 pp 是复印造出来的：六格排序 [-8.00, -8.00, 2.84, 3.20, 5.59, 6.16]，
  去掉一个重复的 -8.00 后 q1 从 -5.29 跳到 2.84，spread 掉到 2.75。
- 2025Q3 的 5.21 pp 是一格扛出来的：去掉 +11.71（2022-03-01）后只剩 0.65 pp。
- 复印不全往大推：2024Q3/2024Q4/2025Q1/2025Q2/2025Q3 去重后反而变大（1.33→1.39、1.73→1.97、
  1.50→2.00、1.55→2.06、5.21→6.74）。所以这张表读的是秩间隙，不是路径离散度。

## 本轮未做（如实）

- **未改上游 `etf_book_cadence_regime_split.py`**（应在建网格时先折叠 1e-9 内重复格并把
  `n_independent` 印进逐季表）：本轮同树另有宿主在动共享面（`repo_write_contention` rc3，
  peer pid=116576 起 23:45:30，正跑 `scripts/etf_book_vol_target_gate.py run`），按 r1907 只落新增文件面。
- **未接 S6 链、未加冒烟腿**：同上，改链文属共享面。
- 冒烟本轮 3 红（如实上报，非本面产物）：index-futures proxy noise 重算漂移；
  carry-vs-ETF swap rulers check 3 problem；「substitution rulers reach the CEO page」缺块
  （`results/capital_substitution.json` 生成于 2026-11-26T21:17，CEO 页尚无该节 —— 上游在飞项）。
