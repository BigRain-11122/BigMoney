# DIGEST 2026-11-26 · r1679 bm-b · E661 计数键载体到底是些什么文件

**问题**：E652/E658 发布「有多少文件背着计数行键」（3,873 三臂合流），E654 却发现它定价的 16 个站点
全部是读自己诊断 JSON 的轮脚本。本轮把同一问题放到语料规模：这些载体文件里，多少是会被再跑一次的代码？

**读数**（13,122 个 py 文件走查 → 3,879 个载体）

| 类 | 文件数 | 占比 | 规则原文 |
|---|---|---|---|
| round_script | 2,408 | 62.1% | stem 匹配 `_r<3+位数字>` 或以 `_probe` 开头 |
| results_scratch | 368 | 9.5% | 仓内路径以 `results/` 或 `state/` 开头 |
| test_or_smoke_leg | 94 | 2.4% | stem 以 `run_<x>_smoke_leg` / `smoke_test` / `_?test_` 开头 |
| live_module | 958 | 24.7% | 路径以 `scripts/` `Tools/` `firm/` `live/` 开头 |
| other | 51 | 1.3% | 其余 |

**考古件（轮脚本 + results 草稿）= 2,776 = 71.6%**；活模块不到四分之一。
按 stem 形态交叉：plain 1,018 / round_script 2,408 / test_or_smoke 94 / 下划线临时 359。
每文件命名键数 1→2,951 / 2→869 / 3→54 / 4→5；命名 0 个键 0（定义上不可能）。
解析洞照发：**304 个文件不解析**、4 个超尺寸帽——分母不是「全部文件」。

**三条臂的对账（本轮重走 vs 上游发布）**

| 臂 | E658 发布 | 本轮重走 |
|---|---|---|
| literal only | 3,850 | 3,856 |
| literal + subscript | 3,864 | 3,879 |
| all three | 3,873 | 3,879 |

E652 另一个口径 3,860 → 3,879（+19）。方向只允许增长并披露：缩水=硬红。

**判据**
1. 按名字分类是**名字承诺**，不是身份判定——普通名发布的探针会读成 live module；规则原文与优先级
   必须与计数同时发布。
2. **体积不是资产**：3,879 若被读成「代码生态规模」就错了，其中七成不会被再跑。
3. 对账**按臂不按数**：三条臂各自比，不拿一个总数比另一个总数。
4. **洞要进分母**：不解析/超尺寸的文件写进 `holes`，3,879 才可复核。

**产物**：`scripts/e661_volume_vintage.py`（selftest 18/18，verify problems=[]）·
`results/state_tilt/VOLUMEVINTAGE.json` + `volumevintage_latest.json` ·
`scripts/run_e661_smoke_leg.py`（1/1 PASS；`--doctor` red_legs=1 且面字节还回 sha `1256191e392b`）·
`smoke_test.py` leg E661 · S6 leg `volume_vintage` · 方法论卡 E661。

**下一问**：E662 —— 958 个 live_module 是不是又一层名字承诺（路径前缀），有没有任何别的文件 import 它。
