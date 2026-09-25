# DIGEST-20260925-qoppac-first-capture · Rob Carver 博客首捕获（O-1721 常态链 · T-47 wave-6 slice-1 · bm-a R142）

> 执行人：bm-a（OS iteration loop R142 · T-2026-09-25-47 face-a 首扫：RESEARCH_MECHANISM 待探源清单）
> 性质：内部研究用途，不构成采纳建议；博客论断一律【社区声称·未实证】；未经我方门禁复验不得作为采纳依据。

## 〇、通道实况（1 fetch）

- `https://qoppac.blogspot.com`（Rob Carver 博客 qoppac）1 fetch 首页全量：可达、零登录、3 篇近期帖全文随首页渲染（09-04 出书公告 / 07-03 pooling by asset class / 06-29 rolling estimates 诚实负）。
- 源级定性：**可常态周挖源**——档案 100+ 帖带主题标签（portfolio optimization 54/implicit fitting/shrinkage/pysystemtrade 36），未来片可按标签定向拉取（比 SSRN 429 面与登录墙面便宜）。作者=ex-AHL 基金经理、Systematic Trading 等五书作者、开源 pysystemtrade（github.com/robcarver17）。

## 一、深捕获三帖要点（忠实转述）

### 1.1 Pooling by asset class and portfolio weight distance（2026-07-03·组合优化系列 #10）

214 期货品种、多层 IS/OOS（5/10/20 年入样×1/5 年出样、随机子样 50 品种）实证：**按资产类别 pooling 收益序列**做 forecast 权重拟合，在多数切分下显著优于全池 pooling/不 pooling/按权重距离聚类（如 10y/5y 切分 asset-class 1.066 vs all-pooled 0.570）；方法论间取平均（blend of unpooled/all/asset-class 权重）=稳健性正道但常被弱腿拖累。配方面：SR 收缩 0.5+相关性收缩 0.75+分层聚类 ~6 簇+40 年 EWM SR 估计+**「纳入每条规则的相反面、只选正 SR 版本」防隐式拟合**+方法论选择本身=「meta implicit fitting」须平均化或事前冻结。

### 1.2 Rolling/EW estimates yes or no（2026-06-29·诚实负发布）

EW/滚动窗 SR 估计（5/10/20/30 年 span）对比全历史估计用于优化：**多切分下无显著增益**（多数 p 值不显著）——作者明言「即使无正结果也发布研究」。与我方诚实负文化同构（futures-cta 臂 0/16→0/16→0/2 三连负在案）。

### 1.3 第五书《The Art and Science of Trading》公告（2026-09-04·2026-12-01 出版）

「半自动交易」框架=信号可自由（含直觉），**仓位/成本/风险管理/执行一律规则化**（科学护栏包住交易方法）；最简趋势规则示例=「价格涨了还是跌了」。对我方=全系统化架构的社区镜像对照件（我方无自由裁量腿，护栏=REGIME_GUARD+成本+退出铁律）。

## 二、harvest 登记与裁定（采集≠入册）

1. **方法论参照卡（C 级·未来组合构建面）**：①「规则相反面入样、只取正 SR」防隐式拟合装置——未来任何合成/权重面 prereg 可冻结条款；②方法论选择=meta 拟合面，解=跨方法论权重平均或事前冻结（与我方 T-27 五法锦标赛 prereg 冻结纪律收敛，零新动作）；③资产类别 pooling 优于全池——若未来在册员规模扩张至跨类多池，权重拟合面按类 pooling 的外部先例。
2. **pysystemtrade 指针（C 级常设）**：开源期货回测/交易框架——futures-cta 臂现 parked（3 连诚实负），**无新外部机制证据不 re-queue**（其规则族=trend/carry 与我方 CTA_P1/P2 同族）；若臂重启，该库=借力律候选基础设施，登记不下载不启动（P1 数据扩容署名律）。
3. 诚实负发布文化=独立佐证，零动作。
4. **无新候选族**：Carver 面=期货组合优化方法论，非我方现役 ETF corps 域内新机制；最简趋势规则=在册 #19-23/#25 族变体叙事，反重复律不另立。

## 三、funnel 双列（O-1721 报告律·本片）

| 面 | 收割数 | 过闸数 |
|---|---|---|
| 源首捕获 | 1（qoppac·3 帖含 2 篇全文） | 0（无新族无采纳） |
| 方法论参照卡 | 3（相反面入样/meta 拟合平均化/类 pooling） | 0（登记不采纳） |
| 常设指针 | 2（pysystemtrade 库/标签化档案定向拉取道） | 0 |

**harvested != passed**：本片零采纳零注册零引擎改动零跑批。

## 四、下步指针

- wave-6 face-a 余源待扫：SSRN 学术扫/CrossRef（Lesmond 指针承 digests §三）/Alpha Architect/QuantConnect/米筐/优矿/券商金工研报——每片 1-2 面，死面诚实记录。
- qoppac 后续片=标签定向（portfolio optimization 系列余帖），排片归 T-47 机会道。
- 集思录 category-5 feed 增量=常态 digest 直通道（本窗 08:41 对照零新件已留痕）。
