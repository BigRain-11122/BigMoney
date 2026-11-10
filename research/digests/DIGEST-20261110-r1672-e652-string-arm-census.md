# DIGEST 2026-11-10 r1672 bm-b —— E652：字符串臂的语料规模

**问题**：E646 说「模块若经 importlib 或路径字符串到达读模块，它看不见」，E647 只在那 6 个命中模块里
把这条臂量了（0 条字面量命名目标）。那 6 个模块没有通路，不等于树上没有通路。

**做法**：同一件仪器铺满全语料、铺满全部 6 个读数模块；每条可测字符串先按 E647 的拼写类匹配，再按
消费它的调用分类（module_import / file_open / exec_or_eval / sys_path / path_join / other_call /
no_call），最后把它所在的文件与「是否拼写或下标了一个计数行键」交叉。目标模块拼自己的名字（stem、
FACE/LATEST 常量）不算通路，按路径排除并计数。

**读数**：13,108 文件 / 12,800 扫成 / 304 不解析 / 4 超 1MB；1,482,453 条字符串，89,667 条表达式生成；
23 个拼写者 / 28 条字面量 / 14 个带计数行键 / **1 个严格通路**（`scripts/run_e590_smoke_leg.py` 导入
`e590_cash_silence`，同时拼写 `bar`、`rows`）；24 对里 21 对 no_call 消费。

**结论**：字符串臂是树的性质。但它的规模是 1，而且那一个还是测试腿——所以「隐形通路」在语料里存在，
却是罕见的、且落在不该承载语义的地方。

**坑**：①目标自身恒真（首版 6 个读数模块把自己算成拼写者，selftest 当场红）；②拼写数与通路数不能混报；
③token_contains_stem 是**整 token** 匹配（`run_target_mod_now` 不命中，`target_mod.json` 命中），
把 substring 当名字会把 23 抬成几百。

**证据**：`results/state_tilt/STRINGARMCENSUS.json`（`--doctor` 翻转 verdict 后逐字节回原 sha
`5ebfc5c10fba`）、`scripts/e652_string_arm_census.py`（selftest 17/17）、S6 leg `string_arm_census`。
