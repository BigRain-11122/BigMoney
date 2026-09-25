# DIGEST 2026-09-25 wave-8 slice-1（face (a)：Bouchaud/CFM 趋势跟踪学术主源核验）

> T-51 slice-1 · bm-a R153 · O-1721 外源常态线 · RESEARCH_MECHANISM v1.1 每周深挖波-8 首片
> 单写者=bm-a；串行 pacing（R109）；零登录零绕墙；fetch-fail 诚实记录；funnel 双列律照报。
> 消费面=进攻军（T-33）补给线证据面（O-0857 盈利模型总动员令：牛市段缺口=第一优先）。

## §〇 通道课

1. **arXiv API = 全开放正道**：`export.arxiv.org/api/query`（http→https 301 重定向照跟）一发命中目标论文，零登录零墙；标题短语查询 `"Two centuries of trend following"` totalResults=1 精确定位。
2. **PDF 全文抽取通道（R168/R149 律照走）**：arXiv PDF（463KB）→ 本地 requests 单取 → pypdf 抽取 17 页 41,026 字符 **0 替换符**（本件 pypdf 干净，无需 PyMuPDF 退档）；抽取文本落 `assets/lemperiere2014_extract.txt` 备查。
3. **Wilmott 标题线索的主源核验结果**：`au:Potters AND trend` arXiv 查询=唯一命中本篇（Wilmott 杂志文「Trend followers lose more often than they gain」无 arXiv 开放对应件，正文在三层会员墙内）→ 借力律判定见 §三。

## §一 主源核验：Two centuries of trend following（arXiv:1404.3274v1）

**书目事实（API+正文页眉实证）**：Y. Lempérié, C. Deremble, P. Seager, M. Potters, J.-P. Bouchaud（Capital Fund Management, Paris）；2014-04-12 提交；q-fin.PM；17 页 9 图 9 表；URL=https://arxiv.org/abs/1404.3274。

**核心主张（摘要+正文逐字，页锚内引用）**：
- 四资产类别（商品/外汇/股指/债券）趋势跟踪超额收益存在且极稳：**t-stat≈5（1960 起）/≈10（1800 起）**，剔除长期漂移后。
- 趋势收益**不能归为风险溢价**（正文：cannot be associated to any sort of risk-premium）。
- **信号构造（Eq.1）**：s_n(t) = [p(t−1) − EMA_n(t−1)] / σ_n(t−1)，月收盘、n 月衰减 EMA、波动率归一。
- **饱和效应**：大信号区收益饱和（双曲正切 tanh 拟合最优；解释=基本面交易者不抵抗弱趋势、自身信号够强才进场）→ 信号映射非线性截断。
- **期限结构（Table 1·1960 起·期货四类合计）**：

| n（月） | SR(T) | t-stat | t-stat(去偏) |
|---|---|---|---|
| 2 | 0.80 | 5.9 | 5.5 |
| 3 | **0.83** | 6.1 | 5.5 |
| 5 | 0.78 | 5.7 | 5.0 |
| 7 | 0.80 | 5.9 | 5.0 |
| 10 | 0.76 | 5.6 | 5.1 |
| 15 | 0.65 | 4.8 | 4.5 |
| 20 | 0.57 | 4.2 | 3.3 |

- **分部门（Table 2·n=5）**：商品 SR 0.80（1960 起）> 外汇 0.57（1973 起）> 债券 0.49（1982 起）> **股指 SR 0.41**（1982 起，t-stat 2.3）。**世纪尺度（Table 8·1800 起）**：合计 SR 0.72/t-stat 10.5；**股指 SR 0.70（1800 起·t-stat 10.2）**=世纪尺度上面股指趋势反强（样本长）。
- **长期趋势两百年从未转负**（never been negative in two centuries）；**~3 日级短趋势自 1990 显著衰减**（Fig.8）；数月级长趋势近期无统计衰减迹象；2011 后策略近乎走平（Fig.6）但作者论证=与统计涨落兼容、「趋势终结」场景理论上证伪为小概率。
- **回撤期望数学**：典型回撤时长=1/S²（年）；S=0.7 → 典型回撤 2 年、4 年回撤不罕见——进攻军成员期望管理/仓位设计用。

## §二 进攻军（T-33）消费面裁定（借力生想法、独立做验证）

经济先验提取（=预注册 §1 α 机制段素材，**非直接采纳**——任何采纳必过 G1' prime/G2 门禁链+随机基线+N 记录+D6 并族条款）：

1. **期限先验**：趋势信号平台区=2-10 月回看（SR 0.76-0.83），n=3 月最优；**~3 日级短趋势 1990 后衰减**=进攻军趋势腿应取月级回看、避开日内/数日级趋势追逐（与 J13 磨坊短周期枯竭证据同向）。
2. **信号形态先验**：波动率归一化价格-EMA 差 + **tanh 饱和映射**（非线性截断）优于线性映射——拥挤/反转保护（基本面对手盘在强信号区进场）。
3. **股指面**：1982 后股指期货趋势 SR 仅 0.41（最弱部门）——我司宇宙=ETF 指数池，趋势腿单部门期望应按低档校准；跨部门组合分散（商品/债券趋势腿在 ETF 宇宙内可由商品 ETF/债券 ETF 部分替代）是 SR 提升正道（四类合计 0.8 vs 股指单类 0.41）。
4. **期望管理**：S≈0.7 级策略 2 年典型回撤=常态非事故——牛市段进攻军的停机/降档判据勿按月级回撤过敏触发。

## §三 Wilmott 标题线索核验裁决（借力律：宣称≠验证）

- 标题级宣称「trend followers lose more often than they gain（低胜率正偏态）」出自 Wilmott 杂志文（Potters/Bouchaud，wave-7 slice-5 标题雷达收录）。
- **开放主源核验结果**：本篇（CFM 同队主源）全文 `hit rate`/`skew` 0 命中——该文以 Sharpe/t-stat 框架呈现，**无胜率/偏态统计口径**；Wilmott 正文=会员墙内，无 arXiv 开放对应件（`au:Potters AND trend` 唯一命中=本篇）。
- **裁决：UNVERIFIED 维持**（标题级线索，无开放主源支撑其具体统计口径）。经济学上与饱和效应/趋势 P&L 形态不矛盾，但按借力律「外源宣称=未验证假设」，该表述**不入证据面**，仅作标题线索存续于 wave-7 slice-5 表内。

## §四 登记与漏斗

- 登记：**趋势族（trend-following）已有在册族的经济先验加深**（ASTYLE_ZOO/短名单内趋势族已存在）→ 本片为**既有族先验补强**（非新族）；新增登记项=tanh 饱和映射变体+期限结构表（先验文档级，供 T-33/T-48 因子混合预注册引用）。
- 拥挤标注：趋势跟踪=CTA 业界最拥挤策略族之一（paper 自证：CTA 近五年表现差=拥挤面实证），采用时按 folklore 五要素作拥挤面披露。
- funnel（本片）：faces 收割 1（Bouchaud/CFM 趋势学术线）/ 过闸 0（先验补强不涉门禁）/ 新族 0 / 采纳 0 / 引擎接线 0。
- fetch-fail：无（arXiv API+PDF 两发全中；Wilmott 会员墙=结构性不可达非 fetch-fail，按无登录律不探）。

## §五 续作指针

- face (b) Wilmott 作者-论文开放通道跟进（Vecer/Wolf/Lehle 标题线索）；face (c) jisilu run-6+hibor run-3（收盘后窗）；face (d) pending-list 首扫新源 1-2 面。
- T-33 消费接线：本表期限结构+tanh 形态先验进 PROSPECT 进攻军候选预注册 §1（引用本 digest）。
