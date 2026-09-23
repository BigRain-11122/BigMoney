# 调研纪要 DIGEST-20260923 · 全风格首扫（styles sweep）

> 执行：quant 专管会话（总经理）· 2026-09-23 16:36-16:50 · 令 O-20260923-1636 · 机制首场实证

## 来源实抓记录

| 来源 | 结果 | 相关性评级 | 动作 |
|---|---|---|---|
| arxiv.org/list/q-fin/recent | **低效**：单页仅 1 篇非相关 econ 论文（预测市场/AMM） | — | 坑入机制来源清单：改用分类页 q-fin.PM/STR+关键词搜索 |
| github.com/microsoft/qlib README | **高价值**：①Alpha158/360 因子集 zoo ②22 个模型基准（LightGBM/LSTM/Transformer/TRA/HIST…）③DDG-DA 滚动再训练应对市场漂移 ④**RD-Agent（LLM 自动因子挖掘+模型优化，arXiv 2505.15155，MIT 系）** | **A**（方法论参照）/C（整框架引入） | RD-Agent 深读=下场外调队；与 J13 LLM 助理迭代方向同构；qlib 按需取件 |
| github.com/10mohi6/stock-pairs-trading-python | MIT·Kalman filter 配对·pip 可装·协整/回测/最新信号三用例 | **A-**（配对族入门参照） | 记入图鉴 #9 参照；不整库下载（pip 研究环境按需） |
| GitHub 搜索面（alpha101/GTJA191/pairs 三轮） | 全部命中且 O-1545 已入库 292 因子 | A | 台账：`research/shortline/external/SOURCES.md` |

## 结论与动作

1. **全风格图鉴 V1 落地**：`research/styles/QUANT_STYLE_ATLAS.md`（20 风格×现状×评级：A 11 项 / B 3 项 / C 3 项 / D 4 项（含交叉））。
2. **机制固化**：`research/RESEARCH_MECHANISM.md`（类型/来源/格式/管线/KPI）——周巡检随周进化轮，本纪要即首场产出。
3. **下场外调主题排队**：①资金流数据源专项（图鉴 #17 已批立项配套）②qlib Alpha158 因子表全量导出评估（对照 GTJA191 补缺）③RD-Agent 深读（J13 迭代参照）。

—— quant 专管会话 · 2026-09-23
