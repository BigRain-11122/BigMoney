# DIGEST-20260924 strategy-wave1 三源策略调研波（O-20260924-1536）

调研人：研发部外部策略调研员
日期：2026-09-24（Asia/Shanghai）
性质：内部研究用途，不构成采纳；所有内容仅供研究部判定流程参考。
说明：每条信息尽量标注来源 URL；社区/帖子声称的收益数字均标注「社区声称·未实证」。

---

## 源一：Microsoft qlib Alpha360（fetch 成功）

### 1. Alpha360 特征集包含哪些特征族（与 Alpha158 的差异）

依据 Alpha360DL 源码（loader.py）：
- https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py
- https://raw.githubusercontent.com/microsoft/qlib/main/qlib/contrib/data/loader.py

Alpha360 共 6 个特征族，每族 60 列（过去 59 日 + 当日），合计 360 列：
- CLOSE 族：CLOSE59...CLOSE0，公式 Ref($close, N)/$close（归一化到最新收盘价，最新值为 1）
- OPEN 族：OPEN59...OPEN0，Ref($open, N)/$close
- HIGH 族：HIGH59...HIGH0，Ref($high, N)/$close
- LOW 族：LOW59...LOW0，Ref($low, N)/$close
- VWAP 族：VWAP59...VWAP0，Ref($vwap, N)/$close
- VOLUME 族：VOLUME59...VOLUME0，Ref($volume, N)/($volume+1e-12)

源码注释原文要点（意译）："Alpha360 试图提供带原始价格数据的数据集，包含过去 60 天的价格与成交量；所有价格和成交量都除以最新的 $close/$volume 做归一化，因此最新归一化 $close 为 1（名为 CLOSE0），最新归一化 $volume 为 1（名为 VOLUME0）。"

与 Alpha158 的差异（同一源码文件 + examples/benchmarks/README.md）：
- Alpha158 为人工特征工程的表格数据集，族包括：
  - KBAR 族（9 列：KMID, KLEN, KMID2, KUP, KUP2, KLOW, KLOW2, KSFT, KSFT2）
  - PRICE 族（OPEN/HIGH/LOW/CLOSE/VWAP × 5 日窗口，默认 20 列）
  - VOLUME 族（VOLUME0-4）
  - ROLLING 族（窗口 5/10/20/30/60 日 × 约 29 个算子：ROC, MA, STD, BETA, RSQR, RESI, MAX, MIN, QTLU, QTLD, RANK, RSV, IMAX, IMIN, IMXD, CORR, CORD, CNTP, CNTN, CNTD, SUMP, SUMN, SUMD, VMA, VSTD, WVMA, VSUMP, VSUMN, VSUMD）
- README 原文对比："Alpha158 是表格数据集，特征间空间关系较少，每个特征由人工精心设计（即特征工程）；Alpha360 包含未经太多特征工程的原始价量数据，特征在时间维度上有强空间关系（strong spatial relationships in the time dimension）。"
- 定位差异：Alpha360 面向深度学习/时序模型（LSTM、ALSTM、GATs、TR A 等 *_ts.py 模型），Alpha158 面向树模型/表格模型（LightGBM、XGBoost、CatBoost、DoubleEnsemble）。

### 2. 许可证类型

依据 LICENSE 文件：https://github.com/microsoft/qlib/blob/main/LICENSE
- MIT License，Copyright (c) Microsoft Corporation。
- 允许自由使用、复制、修改、合并、发布、分发、再许可及销售；唯一条件是保留版权声明与本许可声明；软件按"现状"提供，不提供任何形式的担保。MIT 为宽松许可，对内部商用与研究复用基本无障碍（注意：qlib 官方数据集本身另需遵守其数据来源条款）。

### 3. Alpha360 特征在 A 股的公开实证结论

依据官方 benchmark 表（examples/benchmarks/README.md）：
https://github.com/microsoft/qlib/blob/main/examples/benchmarks/README.md
该页面为官方在 A 股（中国）CSI300 数据上以 Alpha360/Alpha158 两个数据集分别跑出的完整 workflow 结果（20 个随机种子的均值±标准差）。要点：

- 结论一：Alpha360 上表现最好的模型（CSI300）：
  - HIST：IC 0.0522，Rank IC 0.0667，年化收益 0.0987，信息比率 1.3726，最大回撤 -0.0681
  - IGMTF：年化 0.0946，IR 1.3509，最大回撤 -0.0716
  - TRA：年化 0.0920，IR 1.2789
  - TCTS：年化 0.0893，IR 1.2256
  - GATs：年化 0.0824；ALSTM：年化 0.0626；GRU：年化 0.0720；LSTM：年化 0.0647
  - 失败案例：Transformer（年化 -0.0270）、TabNet（-0.0369）、KRNN（-0.0465）、Sandwich（0.0005）——说明 Alpha360 原始序列对模型选择非常敏感。
- 结论二：Alpha158 上最好的是 DoubleEnsemble（年化 0.1158，IC 0.0521）、LightGBM（年化 0.0901）、MLP（0.0895）；在 CSI300 上 Alpha158 表格特征 + 树模型整体不弱于甚至略优于多数 Alpha360 深度模型。
- 结论三：CSI500（中证500）结果不完整，官方 Alpha360 表仅 4 个模型（LightGBM 年化 0.0505 / CatBoost 0.0297 / MLP 0.0022 / DoubleEnsemble 0.0382）；Alpha158 的 LightGBM 在 CSI500 年化 0.1284、IR 1.5650。官方明言"Results on CSI500 is not complete"。
- 结论四：官方提示回测口径自 0.8.0 起变动较大，且 v1/v2 数据源（YahooFinance 采集）结果会有差异，引用数字须注明版本口径。
- 官方 qlib 论文《Qlib: An AI-oriented Quantitative Investment Platform》（arXiv:2009.11189，2020-09-22，Xiao Yang, Weiqing Liu, Dong Zhou, Jiang Bian, Tie-Yan Liu，微软）：https://arxiv.org/abs/2009.11189 —— 摘要确认 qlib 是面向 AI 的量化平台，数据基础设施 + 上层模型工作流；本页为摘要页，全文数字以 benchmark README 为准。

对我们判定流程的含义（研究员注，非实证）：Alpha360 的"原始价量 60 日窗口 + 归一化"构造对 A 股横截面选股有公开可复现的基线（IC 约 0.04-0.05，年化约 5%-10%），但其价值高度依赖模型选择；作为特征基线可用，作为策略本体尚不足以构成可采纳策略。

fetch 记录：源一全部子项 fetch 成功（GitHub 主页、loader.py 源码、LICENSE、benchmarks README、arxiv 摘要页）。

---

## 源二：国内量化社区 ETF/短线策略（fetch 部分成功）

### fetch 状态说明（如实记录）

- 聚宽社区首页 https://www.joinquant.com/community —— fetch 返回空内容（页面需登录/前端渲染），未达。
- BigQuant wiki 首页 https://bigquant.com/wiki/ —— fetch 成功但仅返回导航/页脚，无策略文章正文。
- 知乎专栏 https://zhuanlan.zhihu.com/p/24155902542 —— 403 Forbidden，未达。
- 雪球 https://xueqiu.com/8903395540/406189464 —— 被 WAF 拦截，返回加密挑战内容，正文未达；但其搜索摘要可佐证（见下文标注）。
- 策引 https://www.myinvestpilot.com/docs/strategies/momentum-rotation —— fetch 操作中止（超时），未达。
- 替代路径：通过 DuckDuckGo 检索 + 直接抓取可公开访问的社区页面（次方量化知识库、BigQuant wiki 单页、CSDN、GitHub），已获得实质内容。

### 1. A 股 ETF 轮动/动量类策略的常见构造（多来源汇总）

依据次方量化《ETF动量轮动策略系统》技术说明（fetch 成功）：
https://www.cifangquant.com/docs/current-momentum-strategy-system-explanation.html
- 动量窗口：默认 20 日（可调 1~60 日）；四种动量算法：区间涨幅（simple）、RSRS 动量（Z-Score）、斜率动量（=年化收益率×R²）、加权斜率动量（近期加权，1→2 线性）。
- 调仓：简单版为固定周期（每周/每月）；进阶版为「每日检查 + 最小持有期」（默认 8 天，止损可打破）。
- 持仓数量 Top N：1~10 只，默认 1 只；ETF 池 1~50 只（平台支持全市场 1600+ ETF/LOF）。
- 交易成本默认：佣金单边万 2.5、滑点 0.10%；执行时间默认 14:30（收盘前 30 分钟）。
- 风控：动量上下限阈值过滤（默认下限 0.01，即绝对动量过滤）、涨跌停/停牌过滤、均线条件过滤（价格>60日均线、20日>60日均线多头）、大盘择时（默认沪深300 ETF 510300 动量作为门槛，全部弱于大盘则空仓或切备选）、止盈 18%（冷却 8 天）、跌幅止损 8%/高点回撤止损 5%（止损冷却 0-90 天）。
- 备选防御资产（内置）：10年国债ETF 511260、银华日利货币ETF 511880、招商双债LOF 161716、黄金ETF 518880。

依据《ETF动量轮动策略深度拆解》（同站，fetch 成功）：
https://www.cifangquant.com/docs/etf-rotation-strategy-deep-dive
- 「双动量四层过滤」原文框架：相对动量排名（池内选强）→ 绝对动量过滤（得分须为正，解决"矮子里挑将军"）→ 均线过滤（二次确认）→ 极端条件过滤（涨跌停/停牌剔除）。
- 该文对风险如实提示：震荡市连续止损磨损是方法论内生边界；极易过拟合（选池时倾向放入过去涨得好的标的）。

依据 CSDN《QMT量化实战系列：复现聚宽年化30%+的ETF轮动策略》（fetch 成功）：
https://blog.csdn.net/qq_46262068/article/details/149083100
- 原聚宽流传策略构造：4 只 ETF 池（518880 黄金 / 513100 纳指100 / 159915 创业板100 / 510180 上证180，覆盖商品、海外、成长、价值四类低相关资产）；动量 = 近 25 日对数价格线性回归斜率年化 × R²；持有得分最高 1 只；每日调仓。
- 同作者系列还提及：「etf动量轮动+大盘择时：年化30%的策略」用 20 日斜率动量 + RSRS(18,600) 大盘择时（择时为卖则全平仓）；「年化29.6%：基于ETF评分的轮动策略再优化」。

依据 BigQuant wiki 策略页（fetch 成功，页面为策略集列表，含多篇 ETF 策略描述）：
https://bigquant.com/wiki/doc/3bkTmkRUSW
- 「趋势稳健性动量ETF策略」：年化收益率×R² 双因子评分，黄金、纳指等 4 只 ETF，25 天滚动窗口，每 5 个交易日选评分最高 2 只等权调仓。
- 「双轨复合ETF优选策略」：趋势评分（25 天年化收益×R²）+ 20 日价格变动率 + 量比（5日/20日成交量均值比），每日选 1 只全仓，18 日收益率超 15% 止盈。
- 目标文档《基于多周期风险加权双重动量的ETF选基策略》正文未直接渲染，其定义经搜索摘要佐证：相对动量=候选池中选过去表现最强的 ETF；绝对动量=判断标的是否处于上升趋势（如价格高于长期均线或动量为正），避免买入趋势下跌的资产。（搜索摘要来源：DuckDuckGo 检索「双动量 绝对动量 A股 ETF」）

依据 agents-quant.com 博客（fetch 成功）：
https://agents-quant.com/blog/etf-rotation-strategy/
- 30 只选池 = 8 宽基（510050/510300/510500/159915/588000/159949/512100/516970）+ 14 行业主题 + 海外/商品；动量评分 + R² 可投资性过滤双因子；平均每 5 个交易日调仓一次，年化双向换手约 800%；通过 Ptrade（聚宽交易终端）实盘运行。

其他佐证（搜索摘要，正文未 fetch）：
- GitHub cloudinbanana/etf-rotation-strategy：多因子（乖离动量、斜率动量、效率动量）加权评分 + 调仓阈值。
- GitHub roverway/etf-momentum-rotation：纯 Python 每日调仓、AKShare 数据。
- blog.cifangquant.com/post/21.html：《聚宽平台直接运行的ETF轮动》：每月调仓一次的动量选基（次方量化官方博客）。
- wzetf.cn《聚宽600策略下载和分类分析》：2020-2026 收集的 605 份聚宽策略中 ETF 轮动为独立大类方向（说明该品类在聚宽社区存量很大）。

### 2. 公开帖子声称的年化/回撤数字（全部为社区声称·未实证）

- 「聚宽年化30%+的ETF轮动策略」——社区流传标题口径，出处为聚宽社区策略、经 CSDN 博客复现转述（URL 同上）。【社区声称·未实证】
- agents-quant.com：2023-01~2026-06 回测：年化 18.6%（基准沪深300 -2.3%）、最大回撤 -9.2%（基准 -32.5%）、夏普 1.28、胜率 55.3%、盈亏比 1.42；分年：2023 +12.5%、2024 +21.3%、2025 +27.6%、2026H1 +5.8%；自称 2025 年 4 月 A 股大跌期间两周 +3.7%（相对沪深300 超额 16.5%）。【社区声称·未实证】
- GitHub CTAAgents/quant-skills（SKILL.md）：A股行业ETF双动量轮动策略（绝对动量择时+相对动量轮动+估值分位刹车，沪深300ETF 判牛熊、熊市切货币 ETF），自称年化 44.30%、夏普 1.275。【社区声称·未实证】来源：https://raw.githubusercontent.com/CTAAgents/quant-skills/refs/heads/main/a-share-etf-momentum/SKILL.md （搜索摘要）
- CSDN stars580《近4个月狂揽62%！年化飙升453%！六年11倍「ETF双池动量轮动」》：自称近 4 个月 62.61%（年化 453.97%）、6 年累计超 11 倍；静态精选池+动态流动性池、双均线趋势过滤、8% 止损，实盘 3 只分仓。【社区声称·未实证，数字明显含营销夸大，仅记录】
- 同花顺量化社区 quant.10jqka.com.cn 帖《近4个月狂揽62%!六年11倍 ETF双池动量轮动》：与上条同源系列。【社区声称·未实证】
- 次方量化平台本身为参数化工具，未在抓取页内给出统一收益承诺数字（其平台默认成本假设为佣金万2.5+滑点0.1%）。

### 3. 「双动量」「绝对动量过滤」在 A 股的讨论情况

结论：讨论广泛存在，且已有工程化产品。
- BigQuant 社区文档明确给出双动量定义（相对动量选强 + 绝对动量判趋势，见上文 3bkTmkRUSW 相关页）。来源：https://bigquant.com/wiki/doc/3bkTmkRUSW
- 次方量化把双动量做成内置参数模式：第一动量（如 20 日涨幅）做主排名，第二动量（如 60 日斜率）做阈值过滤——"大周期趋势背书、小周期排名"，规避"短期反弹但大趋势已坏"的标的。来源：https://www.cifangquant.com/docs/current-momentum-strategy-system-explanation.html
- CTAAgents 开源 skill：绝对动量择时（沪深300ETF）+ 相对动量轮动（最强行业ETF）+ 熊市切货币 ETF。来源：https://github.com/CTAAgents/etf-skills （搜索摘要）
- 雪球有多篇双动量 ETF 应用文（如 xueqiu.com/4953012890/330194195「主观双动量ETF基金策略」、xueqiu.com/4588772839/299370006「双动量策略在ETF上的应用」——正文被 WAF 拦截未 fetch，摘要明确讨论"熊市中绝对动量很重要"与 ETF 数量众多、跟踪指数约 400 个的选池问题）。【fetch 未达·仅摘要佐证】
- 知乎《量化策略图鉴13_双动量与时序动量》（zhuanlan.zhihu.com/p/2079616005039453593）摘要明确引用 Gary Antonacci 双动量与 Jegadeesh & Titman 1993 动量文献。【fetch 未达·仅摘要佐证】
- 雪球《ETF 动量轮动策略研究·10年+可靠回测》摘要显示有人做 Antonacci GEM 的 A 股本土化（510300/513100/511260 替代 SPY/EFA/AGG）并补跑 PBO/CSCV 与参数高原热力图——方法论意识在社区已出现。【fetch 未达·仅摘要佐证】来源：https://xueqiu.com/8903395540/406189464

研究员注：社区数字离散度极大（年化 18.6%~453%），且几乎全部未提供可审计回测口径，必须经我方门禁复验；但「选池低相关化、动量窗口 20-25 日、斜率×R² 评分、绝对动量/大盘择时过滤、防御资产切换」这五要素在国内社区高度趋同，可视为共识性 folklore。

---

## 源三：海外 ETF 实务模型（fetch 成功为主）

### 1. 双动量（Gary Antonacci 的 Dual Momentum）核心规则

依据 Gary Antonacci 官方网站（fetch 成功）：
https://www.optimalmomentum.com/
- 原文定义："Dual momentum uses relative strength momentum to choose between risky assets and trend following absolute momentum to manage portfolio risk."（双动量 = 用相对强度动量在风险资产之间做选择 + 用趋势跟踪的绝对动量管理组合风险。）
- 出处脉络：Antonacci 2012 年论文《Risk Premia Harvesting Through Dual Momentum》、2014 年著作《Dual Momentum Investing: An Innovative Strategy for Higher Returns with Lower Risk》（该书获 2014 USA Best Book Awards 个人理财/投资类 Winner、2015 International Book Awards Finalist——官网原文确认）。

依据 ensemble.markets《Dual Momentum: The Rules, The Evidence, and A Backtest》（fetch 成功）：
https://www.ensemble.markets/strategies/dual-momentum
- 原文规则："Dual momentum is a monthly rule with two parts. Relative momentum picks the asset that has performed best over the past twelve months. Absolute momentum asks whether that asset has actually gone up over the same period, and moves to Treasury bills if it has not."（月频规则：相对动量选过去 12 个月表现最强的资产；绝对动量检查该资产同期是否真的上涨，若未上涨则转入国库券。）
- 回看期依据：12 个月来自学术动量文献（Jegadeesh & Titman 1993），6~12 个月区间历史上结果相近；更短回看换手高易被震荡打脸（whipsaw），更长反应太慢。
- 该站实测口径：SPY（美国大盘股）、EFA（发达市场国际股）、BIL（1-3 个月国库券 ETF），每月最后一个交易日决策。

### 2. 防御资产轮动（GEM 模型）

依据 ensemble.markets（同上 URL）：GEM = Global Equities Momentum，是 Antonacci 双动量的旗舰具体实现："compares US and international equities on 12-month return, holds the winner, and moves to bonds when the winner has underperformed Treasury bills"（比较美国与国际股票 12 个月收益，持有胜者；当胜者跑输国库券时转入债券）。书籍原版 GEM 防御仓用综合债券基金（aggregate bond fund）替代国库券。

依据 backtestedstrategies.com《Dual Momentum (Antonacci GEM) Backtest》（fetch 成功）：
https://www.backtestedstrategies.com/strategies/dual-momentum-backtest/
- 完整机制：标的 SPY / ACWX / AGG；12 个月回看；绝对动量门槛 = SPY 的 12 个月收益对比 3 个月期国库券收益（hurdle）；门槛通过（equity gate open）→ 持有 SPY 与 ACWX 中 12 个月动量较强者；门槛不通过 → 全仓 AGG（综合债）。
- 该站回测（2010-2025，16 年）：策略 CAGR 10.6%（对照基准 8.6%）、夏普 0.8（0.7）、最大回撤 -21.1%（-22.8%）、波动率 14.1%（12.0%）、Calmar 0.5（0.4）、年均交易 5.6 次、胜率 50%。【第三方回测数字·非我方实证】
- 佐证（搜索摘要）：bestfolio.app 称 GEM 1986-02~2026-09 回测 CAGR 12.3%、夏普 0.99、最大回撤 -33.7%，月频、单资产满仓轮换；bestfolio 博客称 CAGR 11.3%。【社区/站点声称·未实证，数字口径不一，仅供参照】
- quantifiedstrategies.com《Dual Momentum Trading Strategy》页面 fetch 未达（返回机器人验证页），已尝试 URL：https://www.quantifiedstrategies.com/dual-momentum-trading-strategy/ ；其搜索摘要确认："GEM 在股票强势时持有美国或非美股票指数，用债券作避风港"。

### 3. 波动率目标（Volatility Targeting）在 ETF 组合的用法

依据 Quantpedia《An Introduction to Volatility Targeting》（fetch 成功）：
https://quantpedia.com/an-introduction-to-volatility-targeting/
- 定义："The main aim of the volatility targeting technique is to manage the portfolio's exposure in such a way that the volatility of a portfolio is as close to the target value as possible... to ensure that the amount of dollar risk remains the same."（管理组合敞口使组合波动率尽量贴近目标值，即保持美元风险敞口恒定。）波动率上升→收缩组合；波动率下降→加杠杆。
- 该文 14 年示例：原始组合 CAR 8.64%、夏普 0.75、最大回撤 -31.39%；波动率目标化后 CAR 10.07%、夏普 0.88、最大回撤 -21.35%（回撤改善 10.05 个百分点）。另一示例 CAR 8.86%→10.76%、夏普 0.79→1.02、最大回撤 -31.39%→-19.48%。【作者回测数字·非我方实证】
- 结论要点：波动率目标的主要效果是"平滑波动"（smooth volatility 更易预测），不必然提升收益，但历史示例中显著压缩了尾部回撤。

依据 daytrading.com《Volatility Targeting in Trading and Portfolio Construction》（fetch 成功）：
https://www.daytrading.com/volatility-targeting
- 实施步骤：① 设定目标波动率（机构常用 12%/15%/18%/24%，标普500 历史约 15%）；② 用标准差或 GARCH 模型估计当前波动率；③ 当前波动低于目标时加仓、高于目标时减仓，再平衡使实际波动贴合目标。
- 风险提示：效果依赖波动率估计的准确性；存在对历史数据过拟合的风险。该文亦指出许多量化对冲基金用它做实时仓位风险管理。

佐证（搜索摘要）：Man Group《The Impact of Volatility Targeting》：https://www.man.com/insights/the-impact-of-volatility-targeting ——"Volatility targeting seeks to counter the fluctuations in volatility. It leads to leveraging a portfolio at times of low volatility."（低波动时期加杠杆。）

fetch 记录：源三核心子项 fetch 成功（optimalmomentum 官网、backtestedstrategies、ensemble.markets、quantpedia、daytrading）；quantifiedstrategies 页面被反爬拦截未达（已记 URL）；investopedia 无直接"volatility targeting"专文命中，改用 Quantpedia/Man Group 等知名量化来源替代。

---

## 候选族登记（供研究部按门禁检验；登记≠采纳）

1. ETF 动量轮动（斜率×R² 评分）——25 日对数价回归斜率年化×R² 评分、持 Top1-3、每日检查+最小持有期，选池 4-30 只低相关 ETF。理由：国内社区构造高度趋同（聚宽流传版/次方量化/BigQuant 同构），实现成本低、可复现性强，适合作为首批进门的基线族。来源：https://blog.csdn.net/qq_46262068/article/details/149083100 ；https://www.cifangquant.com/docs/current-momentum-strategy-system-explanation.html
2. ETF 双动量轮动（相对动量排名 + 绝对动量阈值过滤）——短周期（20 日）排名选强 + 长周期（60 日）动量为正过滤，不达标切防御。理由：海外有 Antonacci 框架与学术动量文献背书，国内已有工程化产品（次方量化内置、BigQuant 社区文档、CTAAgents 开源），防御逻辑明确可检验。来源：https://www.cifangquant.com/docs/current-momentum-strategy-deep-dive ；https://bigquant.com/wiki/doc/3bkTmkRUSW
3. GEM 本土化（月频 12 个月双动量 + 国债 ETF 防御）——A 股版：沪深300ETF vs 纳指/恒生 ETF 12 个月动量比较，胜者弱于货币/短债则切 10 年国债 ETF(511260)。理由：规则一句话可述、月频低换手、样本期长（海外 1986 年起回测），雪球已有人做 510300/513100/511260 本土适配与 PBO/CSCV 检验的意识，是门槛最低的"教科书对照族"。来源：https://www.ensemble.markets/strategies/dual-momentum ；https://www.backtestedstrategies.com/strategies/dual-momentum-backtest/ ；https://xueqiu.com/8903395540/406189464 （正文 fetch 未达，摘要佐证）
4. 大盘择时开关（沪深300 动量门槛 / RSRS 择时）——池内标的动量须强于大盘指数动量，否则空仓或切防御资产；或 RSRS(18,600) 牛熊开关。理由：A 股系统性回撤深，社区把"择时开关"视为轮动策略的标配防御层，独立可检验且与轮动主体可解耦。来源：https://www.cifangquant.com/docs/current-momentum-strategy-system-explanation.html ；https://blog.csdn.net/qq_46262068/article/details/149083100 （系列内 RSRS 择时帖）
5. 波动率目标仓位层（volatility targeting overlay）——按目标年化波动率（如 12%-15%）动态缩放 ETF 组合总敞口，估计用 EWMA/GARCH。理由：与轮动/择时类信号正交，Quantpedia 14 年示例显示最大回撤可改善约 10-12 个百分点；作为风险覆盖层可与候选 1-4 叠加检验。来源：https://quantpedia.com/an-introduction-to-volatility-targeting/ ；https://www.daytrading.com/volatility-targeting
6. Alpha360 横截面基线（对照组，低优先）——qlib 官方 A 股 CSI300 基准：时序深度模型 IC 约 0.04-0.05、年化约 5%-10%。理由：不作为候选策略采纳，而是作为我方选股/轮动研究的公开可复现对照组与特征工程参照（MIT 许可可自由复用）。来源：https://github.com/microsoft/qlib/blob/main/examples/benchmarks/README.md

---

## 纪律声明

- 本文所有社区/博客/平台声称的收益、回撤、夏普等数字均标注【社区声称·未实证】或注明"第三方回测数字·非我方实证"，未经我方门禁复验，不得作为采纳依据。
- 调研为内部研究用途，不构成采纳；所有候选族进入判定流程前须通过我方回测口径、样本外检验与过拟合检验（社区帖中"年化 453%"类数字仅作反面教材记录）。
- 全部来源 URL 已随条目标注；fetch 未达之页已如实记录 URL 与失败原因。

（完）



