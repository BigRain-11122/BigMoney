# DIGEST-20260926-zoo-paramfreeze-92-94 · zoo #92/#93/#94 深读参数化冻结（bm-b r218 · T-64 下窗指针② · any-machine 条款）

> 执行人：bm-b（OS iteration loop r218 · state r217 下窗指针「zoo #92/#93/#94 deep-read parameterization」·开工前 fetch 核 origin 零撞车（R176 律）：同窗仅 bm-a R203 close（T-70/autofill 面，零 zoo 交集）。
> 性质：参数化冻结记录，登记≠采纳；**本片零跑批零引擎零账本**，funnel 过闸数维持 0；冻结产物=ASTYLE_ZOO.md #92/#93/#94 三行构造列改写（通道级→冻结级）。
> 纪律：QuantsPlaybook 无 license=代码结构性禁抄，只做机制叙述提取+clean-room；外呼全串行 2.5s+（R109）；trees API 权威清单（R216 律：README 链接陈旧禁直信）。

## 〇、通道实况（~9 外呼全串行 · 诚实失败行）

- **trees API ?recursive=1 = 2742 entries·truncated=False**（与 r216 完全一致·库存稳定）。
- **gh-proxy.com 前缀恒活**：5 件全 200（球队硬币 8.5MB / 筹码分布 8.8MB / 特征分布择时 397KB / 系列之二 5.2MB / checkpoint 392KB）——CJK 路径 percent-encode 配方照旧。
- **FactorZoo 独立仓 hugo2046/FactorZoo = 404 假面**：license API 404 + trees API 404——**实现位实为 notebook 同目录 vendored 副本**（`B-因子构建类/个股动量效应的识别及球队硬币因子/FactorZoo/SportBetting.py`，树内 6 entries 含 __pycache__）。通道律新例：**社区库深读定参须先扫 notebook 同目录 vendored 源，独立仓 404≠实现不存在**。
- **QuantsPlaybook 全库零 LICENSE 文件**（树内 LICENSE* 扫描空）——禁抄码律维持实证。
- 系列=三件主读+系列之二边界核+bt_func.py+SportBetting.py 两实现位件，提取=code cells 全量（L1 确定性·temp 留存不入 git=禁抄码边界纪律）。

## 一、质量门/AI 污染扫描（六要素+复现诚实度差距面）

三件均真人复现叙述特征：精确研报引用+公式表+人类学习痕迹自述（系列之二 cell 1「最开始我的理解是…后面发现华创习惯使用HMA」）+实现偏离自注（球队硬币 get_coins_team 注释「研报中多为…意外收获是…」）；无占位码/零互动模板/方法学空洞三红旗。**质量门 PASS（B+ 通道·登记级）**；宣称数字照旧零采信【未实证】。

## 二、#92 球队硬币 `path_continuity_mom` 冻结（构造校准+三处实现偏离）

- **构造校准（深读核心价值）**：r216 判定摘要的「路径连续性」为叙事层；实现层=**可知性代理条件翻转修正反转**——三腿收益三分法（日间 close/close_{t−1}、日内 close/open、隔夜 open_t/close_{t−1}），每腿双修正：①波动翻转（σ<截面均值=硬币→翻转 rolling20 均值μ）、②换手翻转（ΔTR<截面均值→翻转当日腿收益再 rolling20 均值）；腿修正=0.5×(①+②)；coin_team=三腿等权和；coin_team_f=自由流通换手版。
- **实现↔研报偏离三处（冻结披露）**：a) 月末采样 vs 逐日 rolling20（采实现版=日频适配 IC 批）；b) 隔夜腿研报=隔夜距离|隔夜收益−截面均值|为底、实现=裸隔夜收益——**距离变换方法在库已定义未接线**（r204「helper 已 import 未上调用点」的外源镜像例，跨库同病）；c) standalone overnight_f 腿与 revise 合成腿 ΔTR 错位（t−1/t−2 vs t/t−1，以 coin_team_f 实际消费的合成路径为准）。
- 符号=反转向（低值看多）；VolatilityMomentum=族内变体（仅低波动侧翻转·另一侧置空）。
- 数据面：日线 OHLC+换手率原生（#85 STV 腿同源）；自由流通换手率=潜在缺位批前核。

## 三、#93 处置效应 CGO `disposition_cgo` 冻结（算力重条款履行）

- **ARC ≡ CGO 代数证实**：归一换手衰减权重下 ARC=Σ TR_W×(P_t−P_{t−k})/P_t 与 (P_t−RP_t)/P_t 恒等（RP=Σ TR_W×P_{t−k} 参考价）——广发 27 号「筹码」读数与 Grinblatt-Han CGO 同估计机械，r216 并入注记深读实证成立；P=成交均价（VWAP）口径、close=经典变体；分母=现价非成本（「相对资本收益」口径注记）。
- 冻结参数：窗 n=60 交易日（默认）；存活权重 ATR_{t−k}=TR_{t−k}×∏(1−TR_j)；矩读数 VRC/SRC/KRC=TR_W 加权方差/偏度/峰度；陈浩 CYQ 面=三角分布 triang(low,high,峰@均价)/均匀分布+decay=TR×Coeff（**Coeff=1**）+获利盘 CYQK_C/活动筹码 ASR/成本重心 CKDW/相对位置 PRP；研报公式记号笔误（求和号内 n 因子）以语义为准。
- **算力预估（票面条款履行）**：O(60)/股·日；全史 5,000 股×~2,500 日≈7.5×10⁸ 简单算元=numpy 向量化分钟级；naive 上界=notebook 自述 qlib 因子生成 200-300min；批前 P-1d 5,222 股面板实测复核入 prereg。

## 四、#94 LHB 机构特征分布择时 `lhb_inst_dist_timing` 冻结

- IS_NetBuy=机构席位逐席(买−卖)日总和；IS_NetBuy_S=/沪深300 当日成交额；HMA(30)/HMA(100) 双均线；信号=两端做多（(fast>slow∧fast>0∧slow>0)∨(fast<slow∧fast<0∧slow<0)）·目标仓位 0.9·不满足=平仓空仓——**「做空中间」=研报叙述非实现**（netbuy_cross 实现位证实=纯多两端+空仓中段）；V 型分布=前瞻 10 日窗实证面。
- 系列边界：系列之二=量能指标（AMA5/AMA100·√型分布·bimodal_distribution_strategy·skopt 贝叶斯调参）=另一主题不入本行。
- 数据面前置核（batch 前）：LHB 席位明细是否含机构席位逐席买卖金额；仅汇总面=数据面缺位如实降级。

## 五、遗留与移交

- **#86 ICU 均线仍通道级**（参数化待深读冻结）——open-to-any 单写者；#90 AO 构造分歧二选一（TradingView SMA(H+L) vs 研报 SMA(H−L)）随 T-34 快线池评估一并定。
- P-1c IC 批指针：#85+#92 同批或相邻批（corr≥0.7 合并条款先查）→ #93 相邻批（算力实测复核）→ 新 prereg 从 PREREG_TEMPLATE.md 起草（§1 α 机制段四选一+同族 max|corr| 拒收门+共享库判线禁手抄）。
- #94=择时族低优先（T-34 快线候选池·冻结已毕可评·LHB 席位数据面前置核）。
- 通道律候选（GM 审阅）：「notebook 同目录 vendored 实现位优先于独立仓假设」入 RESEARCH_MECHANISM 通道注记。
