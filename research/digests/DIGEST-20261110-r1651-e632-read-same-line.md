# DIGEST — r1651 bm-b — E632: one physical line, two reads?

**问题**：E631 按行号计读点，自陈局限「同一物理行的两次读读作一次」。这张卡问：那 13 条被计数的读行
里，有没有一行真的装了两次读？如果有，E631 留下的重复分母就少算一格。

**做法**：把 E631 发布的 13 条读行逐条回源，`ast` 重解析所在模块，用 E623 同一分类器取该键全部读节点，
按 `lineno` 归行、按 `col_offset` 发布列号。行级类别三档：恰好一个节点 / 多于一个节点 / 一个都不解析。

**读数**：
- 计数读行 13 → 读节点 13
- 恰好一个节点 13 行，多于一个节点 **0** 行，解析不到 0 行
- 4 个重复行中，坐在「会动的行」上的 **0 个**

**判决**：`no_counted_read_line_carries_two_read_nodes_so_on_this_population_the_line_level_count_equals_the_node_level_count`

**保留条**：（1）分类器与 E623/E625 共用，分类器认不出的读法（`key in d`、`d.keys()`、变量下标）在
节点级同样不可见 → 已种子 E633；（2）只重读 E631 计过的行，它没列的行不会出现——这张卡给它拿到的
总体定价，不给总体本身定价；（3）列号随缩进走，节点数不变而列号会移位。

**证据**：`scripts/e632_read_same_line.py`（selftest 23/23）+ `results/state_tilt/READSAMELINE.json` +
`readsameline_latest.json` + `scripts/run_e632_smoke_leg.py`（1/1 PASS，--doctor 红，面字节还原）+
smoke_test.py leg E632 + S6 leg `read_same_line`（rc=0 0.05s）。