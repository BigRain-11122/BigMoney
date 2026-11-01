# 供给面：池子空着，是因为没有活，还是因为没人把活放进池子

判词 **AGENDA_DEBT** —— nothing to enqueue: the red names topic generation, not the pool

| 来源 | 数 | 能不能立刻点火 |
|---|---|---|
| 池内 ready | 0 | 是（已入池） |
| 任务板 open 未认领 | 0 | 是（认领即开动） |
| 队列活草稿（状态列是 open/pending/draft） | {"tech.md": 0, "explore.md": 1} | 否，每行还要先过预注册冻结 |
| 队列已消耗行（状态列 done/closed，含 rNNN 后缀） | {"tech.md": 26, "explore.md": 26} | 无需动作 |
| 队列状态不可读行（状态列里是测量值，按名列出） | {"tech.md": [], "explore.md": [["E16", "0.455 ＞ null family p95 0.077·n_ok 200/200·CENSUS-2026-10-09.json·refuse-if-exis"]]} | 不是草稿，是队列卫生项 |
| backlog 未认领行 | 2 | 否，跨公司 backlog，行内有属主 |

地板 3，当前差 **3** 个批次。

读法：池子空是一种状态，两种原因。有活没入池=机制故障（该入池）；根本没活=选题债（该开题）。把两种都印成 supply_floor，红就一直红着、而且没人能对着它做事。
