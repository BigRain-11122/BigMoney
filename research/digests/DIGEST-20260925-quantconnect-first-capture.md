# DIGEST-20260925-quantconnect-first-capture · QuantConnect 社区面首捕获（O-1721 常态链 · T-47 wave-6 slice-4 · bm-a R145）

> 执行人：bm-a（OS iteration loop R145 · T-2026-09-25-47 face：RESEARCH_MECHANISM 待扫源清单 QuantConnect 社区面）
> 性质：内部研究用途，不构成采纳建议；社区数字一律【社区声称·未实证】；未经我方门禁复验不得作为采纳依据。

## 〇、通道实况（R124 发现梯实录）

- **robots.txt → sitemap 命中**：quantconnect.com/robots.txt 列 8 个 sitemap（主/terminal/main/learning/research/lean/announcements/community posts）＝**种子库全量登记**（未来片直取，零目录列举）。
- **community.posts.sitemap.xml**：1 fetch 全量捕获（~500+ `<loc>` 逐字在案，含 /forum/discussion/<id>/<slug>/ 全形态）；forum 落地面=营销壳（全量阅读需登录），**sitemap=发现+捕获双通道**（R138 feed 家族第 6 例：sitemap 面）。
- **帖子正文公开可读**：3 讨论页零登录全文渲染（20419/21291/20417），无付费墙无 403。

## 一、深捕获三标的（关键句逐字忠实转述）

### 1.1 【标的一】151-3.1 Price-Momentum：27 年长窗诚实负（discussion/20419 · Ney Torres 系列）

Kakushadze《151 Trading Strategies》#3.1 复现（Jegadeesh-Titman 1993 基）：top-500 美股按成交额排名、12 月收益跳过最近 1 月、做多前十档做空后十档、等权月调。27 年（1998-2025）结果【社区声称·未实证·QC 回测引擎】：

> Sharpe Ratio: 0.089 … CAGR: 2.155% … Max Drawdown: 80.5%（2008-09 momentum crash）… PSR: 0.000%
> "A 0.089 Sharpe over 27 years is noise." / "CAGR of 2.155% - worse than Treasury bills." / "PSR of 0.000% means no statistical evidence of skill."
> Lessons: "Classic momentum as pure long/short with no risk management fails. The 2008-2009 momentum crash destroyed returns. **Needs volatility targeting and drawdown limits.**"

### 1.2 【标的二】23,824 Doors：把交易想法变成可证伪实验的七门协议（discussion/21291 · Evidence-Based Trading Lab/SERGII）

证据状态自标 **DIAGNOSTIC**（"describes a research protocol, not a confirmed profitable strategy"）。核心 verbatim：

> "Behind each one [of 23,824 doors] is a different threshold, lookback, asset filter, holding period, or entry rule. If we keep opening doors long enough, eventually one room will contain an impressive equity curve. That curve may be a discovery. **It may also be the inevitable winner of a large search.**"
> 七门：①Hypothesis（预注册假设+失败判据）②**Rule freeze**（锁数据身份/信号时点/下单时点/成本/指标/对照集）③Development ④Calibration（结果是否依赖单一便利历史段）⑤**Locked final**（未触段只开一次；"If it is inspected and used to repair the model, it becomes development data for a new version"）⑥Stress tests（恶化成本/删最佳交易/保胜负簇不洗牌）⑦Verdict（显式状态 DIAGNOSTIC/REJECTED/DATA_NO_GO/**CONFIRMED only after sufficiently strong evidence**）。
> "Each change may look defensible on its own. Together they turn an experiment into a story written backward." / "Our defense is procedural. **Before the decisive run, we freeze the question, data contract, execution model, cost model, comparison family, and failure conditions.**"

### 1.3 【标的三】HMM 回撤态金对冲轮动 SPY/GLD：窗口有利性衰减实证（discussion/20417 · 同作者系列）

HMM 检测 SPY 高回撤态→轮动 GLD，常态回 SPY；50 周 HMM 窗+20 周回撤窗、周频再平衡、分钟线。数字【社区声称·未实证】：6 年窗（2019-2025）Sharpe 0.823/PSR 43.781%/DD 27.1% vs 20 年窗（2005-2025）Sharpe 0.469/PSR **1.337%**/DD 41%/CAGR 12.197%。作者自曝：

> "the Sharpe dropped from 0.823 to 0.469 … the 6-year window was clearly a favorable period." / "PSR dropped dramatically … statistical significance of the Sharpe is weak over the longer period." / "QC flags this as **'Likely Overfitting' due to 16 parameters**, which is a valid concern."

## 二、harvest 登记与裁定（采集≠入册）

1. **进攻军风险面设计约束卡（登记不排批）**：20419 诚实负+学术动量崩塌文献同向（slice-3 Lesmond 成本面+本片崩塌面双证）——O-0857 约束①攻击线（T-33/T-48 动量/突破成员）入列门须含**波动率目标化与回撤限位面**；「无风控裸动量长窗=噪声」为进攻军成员 G2 证据包的必备检查面。现有 face：PAPER_LEVELS 各员已有 tiered TP/硬止损（engine/exit_rules.py 不动），vol-targeting 面=未来 prereg 候选输入，**不新增机制不排批**（O-0857 反重复声明）。
2. **窗口有利性衰减律卡（C 级）**：20417 的 6y→20y Sharpe 减半+PSR 崩落＝我方「海量虚拟时点+指定起点窗」纪律的外部同构实证；其 16 参数 HMM 被 QC 判 Likely Overfitting＝**简律佐证**（我方 REGIME_GUARD=预冻结 MA 确定性线、零拟合参数，正确路线的外部背书）。零新机制。
3. **七门协议卡（C 级·纪律互证）**：21291 与我方 prereg/science_gates 纪律近逐条镜像（冻结在先/成本恒开/单开样本外/显式判词），其 Locked-final 污染律（「检视即变开发数据」）＝我方「样本外恒盲」执法面同义；外部背书记档，零改动零新增。其显式判词词表（DIAGNOSTIC/REJECTED/DATA_NO_GO/CONFIRMED）与 post_review 三态标注律同构。
4. **无新候选族**：三标的均=既有族面（动量族诚实负/regime 轮动族变体/方法论协议），无新信号族、无新数据 feed（P1 数据扩容署名律不触发）。
5. **种子库登记**：QuantConnect 8 sitemap（community/research/learning/lean/announcements posts）全量在案＝未来片直取面；本片社区 sitemap ~500+ URL 全录中 momentum/mean-reversion/regime/overfitting 高相关 slug 已筛出（20960 流动性扫 76%WR 类=社区夸大面诚实样本、20140 稳健回测指南、20416 一月效应 27 年崩坏=同作者系列）＝下片候选。

## 三、funnel 双列（O-1721 报告律·本片）

| 面 | 收割数 | 过闸数 |
|---|---|---|
| 深捕获标的（社区帖 verbatim） | 3（20419 动量诚实负/21291 七门协议/20417 窗口衰减） | 0（设计输入+纪律互证级，无采纳） |
| 跨源校验 | 1（20419 动量脆弱性 vs slice-3 Lesmond 成本集中律同向=动量「存在≠可收割」双面证） | — |
| 参照卡 | 2（进攻军风险面约束/窗口有利性衰减律）+1（七门协议互证卡） | 0 |
| 种子库 | 1（8 sitemap 全量登记） | — |
| 死面记录 | 0（三页全公开可读；forum 落地面营销壳已记） | — |

**harvested != passed**：本片零采纳零注册零引擎改动零跑批。

## 四、下步指针

- wave-6 余面：米筐（miqian）/优矿（youkuang）社区（预期登录墙风险高，诚实死面记录）+券商金工公开流转版；本站社区 sitemap 内高相关 slug 直取（20960/20140/20416/19360/19216）。
- T-45 承接重试道（guorn/hibor/PBCSF/CJoE）仍待排；AA Academic Research Insight 类目定向待排。
- arXiv 2607.01550 正文深挖（免费全文在案，低优先）。
