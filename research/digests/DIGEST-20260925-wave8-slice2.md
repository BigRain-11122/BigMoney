# DIGEST-20260925 · wave-8 slice-2（O-1721 常态链 · bm-b r171）

> 执行人：bm-b（OS iteration loop R171 · T-51 wave-8 slice-2 · face (b) Wilmott 标题雷达作者论文开放通道追查）
> 性质：内部研究用途，不构成采纳建议；一切外部内容未经我方门禁复验不得作为采纳依据；无登录、无绕墙、串行步速（R109 律）。
> 票据：T-2026-09-25-51 progress_r171 认领锁 commit a0937363（10:52:59 origin 在册，r170 claim-lock-first 律）；face (a) Bouchaud 趋势线= bm-a slice-1（b7a690f2 已交付），本片零重叠（反重复）。

## 〇、通道实况（fetch 记账 10 次外呼：arXiv 4 + CrossRef 4 + S2 1 + SSRN 1 + tandfonline 1 + UZH 1，含 301 重定向跟随）

- **R124 学术梯第三例确认**：Semantic Scholar API 首探即 429（无鉴别限流），当场按 R124 预案转 CrossRef——备胎轮换律第三次实弹（BM-A R124/R149 两例在先）。
- arXiv API 全通（http→https 301 一律跟随）；CrossRef API 4/4 全 200 零失败。**arXiv 语法坑**：`au:Wolf_M` 被解析为精确短语 "Wolf M"＝0 命中（须用 au:Vecer 类姓氏裸词或 all: 检索）。
- 诚实失败行：SSRN 摘要页（papers.ssrn.com）= 请求中止（bot 阻断）；tandfonline QF 2010 摘要页 = 403（付费墙）；UZH Wolf 出版列表页 = 部分内容（只回出 Bernoulli 2022 正文片段）。

## 一、Vecer max-drawdown hedging（风控线参照）——主源双件在册【registry 级验证】

- Wilmott 线索原题《Preventing portfolio losses by hedging maximum drawdown》(J. Vecer)：CrossRef 精确题名查询 **0 直接命中** → **维持 title-level UNVERIFIED**（大概率 Wilmott Magazine 专栏体，开放注册表不可见——与 bm-a slice-1 对 Wilmott hit-rate 线索的 0 命中判定同构）。
- **学术主源线已锚定**（CrossRef 注册级验证：题名/ venue / DOI / 作者对——正文未读，付费墙）：
  1. Pospisil, L. & Vecer, J. (2008). **"PDE methods for maximum drawdown"**. The Journal of Computational Finance. DOI 10.21314/jcf.2008.177
  2. Pospisil, L. & Vecer, J. (2010). **"Portfolio sensitivity to changes in the maximum and the maximum drawdown"**. Quantitative Finance. DOI 10.1080/14697680903008751
- 邻接发现（arXiv 开放全文面）：Sadoghi, A. & Vecer, J. (2015). "Optimum Liquidation Problem Associated with the Poisson Cluster Process". arXiv:1507.06514 (q-fin)——泊松簇过程下的最优清算（执行面邻接，非 drawdown 主题）。
- 消费路由（登记不采纳）：**风控线/防守军**——FUNDAMENTAL_BLEND_V2 已登记 wave-6 卡 vol-targeting+drawdown-limits（L38）的条件面参照；dd-limits wrapper 若开变体批须先过 G1'/G2/D6 门链+预注册，本片零采纳零引擎。
- 诚实边界：两主源正文未读（JCF/QF 均付费墙），内容性主张零转述；本片只交付注册级事实（谁/何刊/何年/何 DOI）。

## 二、Wolf resampling-vs-shrinkage（组合层稳健估计参照）——线索正主一发命中【registry 级验证】

- **精确主源**：Wolf, M. (2004). **"Resampling vs. Shrinkage for Benchmarked Managers"**. SSRN working paper. DOI 10.2139/ssrn.567785（题名+作者+年份 CrossRef 验证；SSRN 摘要正文被 bot 阻断未读——诚实失败行在 §〇）。
- **Ledoit-Wolf 收缩谱系全景**（CrossRef 注册级扫描，全部 registry-verified；正文未读）：
  - Ledoit & Wolf (2012). Nonlinear shrinkage estimation of large-dimensional covariance matrices. Annals of Statistics 40(3). DOI 10.1214/12-aos989
  - Ledoit & Wolf (2017). Nonlinear Shrinkage of the Covariance Matrix for Portfolio Selection: Markowitz Meets Goldilocks. Review of Financial Studies 30(12). DOI 10.1093/rfs/hhx052（SSRN 2383361）
  - Ledoit & Wolf (2020). Analytical nonlinear shrinkage of large-dimensional covariance matrices. Annals of Statistics. DOI 10.1214/19-aos1921
  - Ledoit & Wolf (2021). Shrinkage estimation of large covariance matrices: Keep it simple, statistician? J. Multivariate Anal. DOI 10.1016/j.jmva.2021.104796
  - Ledoit & Wolf (2022). Quadratic shrinkage for large covariance matrices. Bernoulli 28(3):1519–1547. DOI 10.3150/20-bej1315（UZH 页面片段独立确认卷期页码）
- **量纲诚实检查（量纲级非传输级·R118 律）**：LW 大维渐近的适用域是 n/p→临界（样本≈维数）；我方 B_MAXDIV 面=core48（48 资产 × 数百观测日，n/p≈0.1）**不在大维临界域**——收缩对本司组合面的价值=协方差良态化/降噪卫生（避免病态逆），非「大维奇迹」；任何采纳=预注册 A/B 变体批（样本协方差 vs shrunk 协方差喂 B_MAXDIV 同一管线）过门链后才算数，本片零采纳。
- 消费路由：**T-28 J4 组合层跨期稳健 / B_MAXDIV 10-01 接线**的方法论参照面（ PROFIT_MODEL_MAP 约束②正源补强候选）；方法论引用=借力不引数据流（digest lane 合法），无新数据源入引擎。

## 三、Lehle intraday optimisation（执行面）——开放通道诚实死面【title-level UNVERIFIED 维持】

- 线索原题《Rigorous optimisation of intraday trading》(C.-A. Lehle，Wilmott 雷达 B 级)：CrossRef 双查（作者+题名两路）**0 相关命中**；arXiv all:Lehle 25 件全扫**零金融相关**。
- **同名异人警示（诚实护栏）**：arXiv 命中的 Lehle 均非该作者——Katrin Lehle（天体物理 TNG-Cluster 星系团模拟）与 Bernd Lehle（physics.data-an：强噪声下 Langevin 时间序列漂移/扩散提取，PRE 83:021113 2011 / PRE 97:012113 2018）。后者方法论（测量噪声下提取真实信号参数）与我方信号处理面有抽象邻接，但**与 Wilmott 线索零同源，禁混同引用**。
- 判定：维持 title-level UNVERIFIED（Wilmott Magazine 专栏体推断，注册表不可见）；下一波候选通道=Wilmott/Wiley 期刊 TOC 面（IJTAF 邻接）人工浏览，登记入 wave-9 待扫清单。

## 四、漏斗与消费路由（funnel 双列·诚实账）

| 面 | harvested（登记级） | gate-passed（过门链） |
|---|---|---|
| Vecer drawdown 对冲线 | 2 主源（JCF 2008+QF 2010）+1 arXiv 邻接 | 0（正文未读/付费墙，零转述） |
| Wolf resampling-vs-shrinkage | 1 正主（SSRN 567785）+ LW 谱系 5 件 | 0（A/B 变体批未开） |
| Lehle intraday | 0（开放通道死面） | 0 |

- 本片零引擎、零新数据源、零 token 成本外呼 10 次；三线索两活一死，死面如实记账（R149「诚实＞完备」律）。
- 反重复自检：与 bm-a slice-1（Bouchaud 趋势线=进攻军 T-33 供给面）零重叠；本片两活线均走**防守/组合稳健**消费面，属 O-0857 作战图两约束面的正交补强，非重建（既有 registered 卡 L38 dd-limits/L28? 的参照源补强，非新机制）。
- 下步指针：若 dd-limits wrapper 或 B_MAXDIV 协方差 A/B 任一面立项，须从 PREREG_TEMPLATE.md 起草+science_gates 共享库判线+冻结 commit（R99 律）后运行；本 digest 的 registry 事实即引用底账。
