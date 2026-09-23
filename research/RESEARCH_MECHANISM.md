# 外部调研机制（研究部常设职能 · 2026-09-23 CEO 令 O-20260923-1636）

> 「给我出去调研，并建立调研机制」——本文件=机制章程；研究部 mandate 的执行细则（`firm/org_chart.md` v2 研究部行）。

## 一、调研类型与节奏

| 类型 | 触发 | 节奏 |
|---|---|---|
| **周巡检** | 常设 | 随周进化轮（PLAN §4.1）：扫来源清单→无新则纪要一行留痕，有新则纪要 |
| **专项调研** | CEO 令/总经理令/KPI 异常 | 随时（如 O-1545 短线能力建设、O-1636 全风格图鉴） |
| **事件调研** | 市场结构/监管/数据源变更 | 触发即启 |

## 二、来源清单（实效优先，薄表）

- **学术**：arXiv q-fin（坑：`/list/q-fin/recent` 单页低效，改用分类页 q-fin.PM/STR+关键词搜索）、SSRN、Wilmott。
- **代码**：GitHub 搜索式（`alpha`/`factor`/`pairs`/`backtest`/`quant strategy` 已实证有效）；qlib（Alpha158/360 因子集+22 模型 zoo+DDG-DA 漂移适应+**RD-Agent LLM 自动挖因子**）；已入库 `external/` 台账。
- **中文研报/社区**：光大/国君/海通金工公开流传版；聚宽/JoinQuant 社区（AI 抓取受限时靠专项令人工补源）。
- **数据能力**：akshare 接口变更（数据部协同，20s 超时纪律）。

## 三、产出格式（调研纪要）

- 落 `research/digests/DIGEST-YYYYMMDD-<topic>.md`：来源 URL / 要点 / **相关性评级**（A=ETF 日线即用 · B=已批域开工 · C=需数据源/基础设施 · D=知识储备）/ 建议动作。
- 有价值资产下载 → `research/styles/external/`（或短线 `research/shortline/external/`）+ `SOURCES.md` 台账登记（出处+许可）。

## 四、集成管线

```
纪要 → A/B 级项入对应 playbook/图鉴 → 研究部排期（IC 批测→合成→G1'/G2 门禁）→ 周报汇总
     → C/D 级项入观察池，季度复核
```

## 五、KPI（接 org_chart 研究部行）

外调轮执行率（周巡检不缺席）· 新知识入库量 · 纪要→采纳转化率。
