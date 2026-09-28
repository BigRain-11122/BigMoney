# DIGEST 2026-09-29 W6 供给圈外源扫描（volconf-gate 量能确认门·O-1721 借力律先行·bm-a r410）

> 执行者：bm-a（OS iteration loop r410 · TRIAL_LABOR_LAW §1 常供线起草窗 · 起草本体无门禁=W2-W5 同例；冻结步才开票认领〔W5 先例=r162 bm-c 起草→r405 bm-a 冻结开票 T-114〕）。
> 性质：内部研究用途，不构成决策建议；一切外部内容未经我方门禁复验不得作为决策依据；无登入、无绕墙、披露同步（R109 律）。外源文本仅做规则逻辑提取+短引注记。
> 票据：无票起草（W2-W5 同例·冻结步开票）；本件=RESEARCH_MECHANISM v1.1 常态双频线 2026-09-29 件。

## 〇、采集面 funnel（收前数 vs 过时数）

- 本轮 2 次 search 全记：**全成 2 / 歧义重定向 0 / 器官页 0 / 中断 0**。
  - 成 1：Gervais-Kaniel-Mingelgrin 2001《The High-Volume Return Premium》（JoF 56:877-919；Wiley/JSTOR/Duke/SSRN 多镜像摘要面，未取正文全文）——「stocks experiencing unusually high (low) trading volume over a day or a week tend to appreciate (depreciate) over the course of the following month」+可见性机制（visibility→后续需求→价格），风险补偿/公告效应不能解释。
  - 成 2：A 股量价民俗判据族（toutiao/zhihu/xueqiu/zpyztech 多源）：口诀语料「量增价涨才靠谱」「缩量回调再放量是新机会」「放量不涨，行情见顶」「缩量上涨还能涨」「天量见天价、地量见地价」+操作化之问（zpyztech：「什么叫增？相对昨天、5 日均量、还是 20 日均量？」——民俗判据不落地=不可回测，须数值门化=CEO 1522 导向「把国内民俗判据形式化为数值门」正例）。

## 一、五要素提取（volconf-gate 映射到试用语法轴五要素框架）

| 要素 | 提取 | 趋同度 |
|---|---|---|
| ①状态定义（可编码核） | 信号日 volume(d) vs 滚动 20 bar 成交量中位 med20(d)（min_periods=20·含 d）：**surge=volume>med20（放量确认）/ dry=volume≤med20（缩量）**；19 bar 预热窗 gate-closed 诚实（vs YANG 零预热/VOL 519 bar） | **强**（20 日均量参照=zpyztech 操作化之问的默认答；本方冻结结编码+探针实证） |
| ②入场 | 态在信号日 d 收盘信息集上判定→d+1 开盘入场许可（T+1 因果律；E1 映射先例 grammar 层实现） | **强**（机制面=与 GATE/VOL/YANG 同构叠加层） |
| ③止损 | 轴域外（X 轴既有域） | 不适用 |
| ④出场 | 轴域外（X 轴既有域） | 不适用 |
| ⑤仓位 | 轴域外（S 轴既有域） | 不适用 |

## 二、外源证据链与仓内交叉验

- **外源锚（弱直接·如实）**：① GKM 2001 高量收益溢价=放量面方向先验（美国个股截面·月前向窗）；2) A 股量价口诀族=国内打法原生判据（CEO 1522 导向：民俗判据优先立项科学照常验证）——**口诀族内部方向矛盾**（「放量上涨必回调」vs「量增价涨才靠谱」）=条件化门价值而非方向宣称。
- **仓内交叉验三源（主证面）**：① O-1855④ 时序门普查=量族 VSTD20_q20 中位 t=+1.746（61% 工具 |t|>2）ETF 宇宙正信号（research/GATE_CENSUS_SUPPLY.md 在册）；② 探针实证（_r410bma_volconf_probe.py·r410）：510300 全史 surge 率 50.26%（近半开窗=面样本结构均衡）且 **GATE 态几乎不载 surge 率**（bull 49.66%/bear 50.89%）**、VOL 态几乎不载 surge 率**（calm 50.76%/wild 49.87%）=第四独立条件维；③ VCONF×YANG 交叉四格全非空非支配（yang∧surge 924/yang∧dry 819/red∧surge 817/red∧dry 904；yang 日 surge 率 53.01% vs red 日 47.47%=价量同动结构事实·非收益宣称）。
- **门裁定：PASS（带边界三披露）**——volconf-gate 拟入 W6 语法轴：**(a)** GKM 2001=美国个股截面月前向窗，与本方 A 股 ETF 逐腿日频 T+1 门=口径错位 → 方向先验两向殉死如实（主证让位仓内探针+普查）；**(b)** yang 日 surge 率不对称（53.01/47.47）=结构性共动事实非收益效应——VCONF 与 YANG 交叉面载信息但非同构（四格非空）；**(c)** 极端日面=七极端日 **6/7 surge**（2016-01-04 熔断 2.05x/2024-09-24 政策脉冲 3.21x/2024-09-30 5.06x/2025-04-07 外生缺口 7.78x/2026-01-19 3.26x/2024-02-28 微盘崩 1.51x；例外 2015-07-27=0.52x dry 停牌潮如实）→ **surge 面危机日敞口保持（vs YANG 门崩盘日结构性关=互补非同构）、dry 面危机日结构性收敛**——整窗判读+dd 线非单点检测（W5 §5 载体律沿用）。
