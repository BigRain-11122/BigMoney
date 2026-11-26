# QA — 修好 donchian 的单位之后，判词翻不翻（r2144, bm-c）

验收对象：`scripts/bench_donchian_repair_rerun.py` + `results/bench_donchian_repair_rerun.json`
+ `research/BENCH-DONCHIAN-REPAIR-RERUN.md`

## 一、可运行（L1 确定性、零网络、幂等）

| 检查 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts/bench_donchian_repair_rerun.py --selftest` | **10/10 PASS**，rc=0 |
| 生成 | `... run` | rc=0，`ok=true`，checks=[]，80 s |
| 结构/算术复核 | `... --check` | **failures=[]**，rc=0 |
| 全量重派生比对 | `... --verify` | **MATCH**（除 `generated` 外逐字段相同），90 s |

确定性来源：随机对照沿用 `bench_core.random_sign_control`（固定种子 20261122、100 次），
三次派生（run / verify / check）逐字段相同。

## 二、判据可证伪（自检腿逐条说明）

| 腿 | 钉死什么 |
|---|---|
| raw units never go long (the defect's signature) | 人造面板上，发布口径的做多占比必须恰为 0——缺陷存在时这条腿才绿 |
| per-bar repair trades both ways | 修好之后必须真能往两边做（做多占比 > 0） |
| per-bar repair keeps high/close on the same bar | 乘子不许错位一根 bar：`high_adj/close_adj` 与 `high_raw/close_raw` 全样本最大差 2.2e-16 |
| first-close repair leaves the roll jump in the channel | 人造 8% 换月跳空后，`first_close` 的通道/收盘比从 1.0100 跳到 1.0908——「两种修法不同解」有数字 |
| scaling the whole price space leaves the signal unchanged | 三组序列同乘常数，信号逐格不变（防止把「只缩放高低价」误当不变性） |
| robust pooled rule ×3 | 复刻 `bench_generic.run_cell` 的 robust 判词分支：同号且越 MDE=STABLE，异号/MDE 内=UNSTABLE |
| donchian semantics pinned | 手造 5 根 bar 钉死 1=多 / -1=空 / 0 丢弃；上游改语义这条腿先红 |
| check() reports a broken defect signature | 把做多占比改成 0.42，`check()` 必须报红——审计器不会永远绿 |

## 三、页面工艺

- 每张表逐行由 JSON 渲染，无手抄数字；`--verify` 证明可重派生。
- 两种候选修法的差（`fut_trend` +10.72pp/年）单独成节，两列并列印出，不挑一个。
- 口径选定写明是**口径论证**（收益面已剔除换月跳空 → 信号面不能对着跳空决策），不是收益论证。
- 忠实度：三张 bench_generic 卡与发布件最大差 0.23pp（面板比发布时长了 2 天），`fut_trend` 原始口径 −13.35% 与发布值逐位相同。

## 四、未验证（如实）

1. 本件**不改** `bench_generic.sig_donchian` / `bench_fut_trend.sig_donchian`，不改任何已发布卡片，
   也不应用判词翻面——两个文件是共享代码面，本轮 `repo_write_contention` rc=3（对端 interactive 宿主 pid 107624 仍在），
   按 r1907 同树多宿主律只落新增文件面。
2. `per_bar` 的乘子来自同 bar 收盘，滚动窗口仍可能横跨换月；更严格的修法是回测层面用后复权连续合约（数据面工程，不在本件）。
3. 随机对照换的是权重符号，不检验入场时点。
4. 判据门槛未重标定（沿用各卡自己的 5pp / 6pp 档）。
5. `first_close` 是敏感性口径，不推荐。

## 五、与既有面的关系

- 上游：r2142 `results/bench_donchian_unit_audit.json`（单卡逐臂审计）、r2143 `results/bench_signal_scale_invariance.json`（全族扰动普查）。
- 本件新增的是**结果面**：同面板下三种单位的收益/夏普/回撤/可分辨性/判词，以及「修法选错会把死风格抬成 4/5 门候选」的实锚。
- 下游待办：无竞争窗时修共享代码面并重跑四张卡 + 重 derive r2140 答卷册 / r2141 去重面。
