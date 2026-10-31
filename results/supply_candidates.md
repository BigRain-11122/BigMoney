# 供给面：池子空着，是因为没有活，还是因为没人把活放进池子

判词 **AGENDA_DEBT** —— nothing to enqueue: the red names topic generation, not the pool

| 来源 | 数 | 能不能立刻点火 |
|---|---|---|
| 池内 ready | 0 | 是（已入池） |
| 任务板 open 未认领 | 0 | 是（认领即开动） |
| 队列草稿（tech/explore 状态列不是 done 的行） | {"tech.md": 9, "explore.md": 10} | 否，每行还要先过预注册冻结 |
| backlog 未认领行 | 2 | 否，跨公司 backlog，行内有属主 |

地板 3，当前差 **3** 个批次。

读法：池子空是一种状态，两种原因。有活没入池=机制故障（该入池）；根本没活=选题债（该开题）。把两种都印成 supply_floor，红就一直红着、而且没人能对着它做事。
