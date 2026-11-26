# QA — 信号族单位普查（r2143, bm-c）

验收对象：`scripts/bench_signal_scale_invariance.py` + `results/bench_signal_scale_invariance.json`
+ `research/BENCH-SIGNAL-SCALE-INVARIANCE.md`

## 一、可运行（L1 确定性、零网络、幂等）

| 检查 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts/bench_signal_scale_invariance.py --selftest` | **11/11 PASS**，rc=0 |
| 生成 | `... run` | rc=0，判词 `UNIT_MIX_AND_FIX_ITSELF_DIFFERS` |
| 结构/算术复核 | `... --check` | **0 failure(s)**，rc=0 |
| 全量重派生比对 | `... --verify` | **MATCH**（除 `generated` 外逐字段相同） |

## 二、判据可证伪（自检腿逐条说明）

| 腿 | 钉死什么 |
|---|---|
| probe: ratio rule is INVARIANT | 探针本身不会把所有规则都报成缺陷 |
| probe: absolute threshold is SCALE_DEPENDENT | 存在绝对价位阈值时，共标度必须被抓到 |
| probe: mixed-unit rule is CROSS_UNIT_SENSITIVE | 混用两套单位时，只缩放收盘必须被抓到 |
| additive shift is diagnostic, never a verdict | 解释「加法位移翻不动时间序列比值规则、但会翻动横截面排名」这一算术事实，并证明它不进判词 |
| real bench_generic/bft non-donchian families are INVARIANT | 真代码上，不消费高低价的族在扰动下逐格不变 |
| real donchian survives rescale but not closes-only | 真 donchian 在共标度下不动、在只缩放收盘下大量翻动 |
| adjustment factor identity when no roll exists | 无换月时调整因子恒为 1，一致化修法不改变任何格 |
| two fixes diverge once a level step exists | 人为制造 30% 价位台阶，两条候选修法必然不同解 |
| hist accounting adds up | 多空 bar 数之和等于在位 bar 数 |
| diff_cells detects exactly one changed cell | 差异计数器的分辨率是 1 格 |
| perturb keeps close series and scales high/low | 扰动只改高低价、不动收盘序列 |

## 三、页面工艺

- 字节：8,842 B；CRLF 计数 = 0（LF 单制）；`%%` 残迹 = 0；判词 token 出现在正文（`--check` 断言项）。
- 每张表逐行由 JSON 渲染，无手抄数字；两处口径差异（全样本 5.04pp vs 卡片窗口 9.19pp）并列印出而不是挑一个。

## 四、未验证（如实）

1. 本件不重算任何收益，也不改任何卡片判词——收益面结论仍由 r2142 面承担。
2. 换月检出用 `bench_core` 自己的判据（8× 中位绝对变动且 >0.5%），检出数只表示序列里有几次换月，不保证完备。
3. 射程只到 `bench_generic` / `bench_fut_trend` 的公开信号函数；ETF／指数／债券侧自建引擎不在本件。
4. 修正动作未执行：`bench_generic` / `bench_fut_trend` 是共享代码面，本轮竞争探针 rc=3，按 r1907 同树多宿主律不动。

## 五、与既有面的关系

- 上游：r2142 `results/bench_donchian_unit_audit.json`（本件读它做交叉核对，得出「两条修法不同解」）。
- 下游待办：修法选定后重跑三张卡、重 derive r2140 答卷册与 r2141 去重面。
