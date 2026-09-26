# DIGEST 2026-09-26 wave-10 深读位#1：Anytime-Valid Referee for LLM Factor-Mining Agents（2609.27051 全文裁定）
> T-2026-09-26-76 wave-10 face (e) 深读收位 · bm-b r266 · O-1721 外源常态链 · RESEARCH_MECHANISM §外源深读
> 单作者:bm-b；深读对象=arXiv 2609.27051v1（Qu/Chen/Wang, DeepGrounding+AlphaAvatar, 2026-09-22, 37p）全文（abs 页+HTML 全文双取，零登记墙零付费）。
> 杠杆律执行：r260 素材级登记标注 UNVERIFIED-until-deep-read → 本轮深读完成=裁定面正式化；**采纳零接触**（消费路由=science_gates 方法论面，任何落地=新 prereg）。

## §一 判定与映射

| 面 | 内容 |
|---|---|
| 判定 | **A 级方法论线索·深读完成**（r260 判定维持+细节全核）；对我司=evaluation/science-gates 既有族（T-63/T-02/science_gates 链）**第三方实证补强**，非新族 |
| 论文命题 | 「Propose, Don't Judge」/governed self-evolution：agent（脚本/bandit/LLM）只许提议，**冻结统计裁判**独占判定；裁判=agent 不可触碰的 trust kernel（下注尺寸+评分数据+假设宇宙+append-only 决策日志+成本计） |
| 与我司同构 | prereg 冻结 commit=「冻结宇宙」；science_gates 共享判据库=「冻结裁判」；OOS 恒盲=「仅提交后数据」；禁跑到达标为止+判据禁看结果改阈值=反 optional stopping/multiplicity——同构面全对齐 |

## §二 核心配方提取（可迁移分面，全部 UNVERIFIED→已核细节，采纳仍须 prereg）

1. **e-process 逐日下注**：W_t=∏(1+λ_s·X_s)，X=提交后逐日 rank-IC，λ 可预测（aGRAPA plug-in 上限 φ=0.8 无破产界）；test supermartingale→Ville 不等式：任意停时读数 P(sup W≥1/α)≤α。等待期信息下界 T≈ln(N_v/(kα))·2σ²/μ²（σ=0.12 日 IC 噪声下 δ 级因子≈1434 天，**没有更好 bettor 能缩短**——cap 只在阈值附近损失 5%）。
2. **AR(1) 白化**：下注对象 X̃_t=X_t−ρ̂_t·X_{t-1}（收缩截断估计）。论文自曝关键数：裸流在 ρ=0.2/0.4 下假承认 6.0%/15.4%（vs 名义 5%）——**正 IC 冲击后的条件均值>0 使裸流下注被 AR 噪声欺骗**；白化后恢复 1.8/2.0/2.4%。边际零假设只有测量级保证（白化条件零假设可证、边际不可证）。
3. **在线 e-BH 承认**：冻结宇宙 N_v=2000 槽/epoch，γ_c=w_v/N_v，k 次承认门槛=N_v/(kα)（首承认=40,000）；FDR≤α 于**任意停时+任意候选间依赖**，承认不撤销；近重复提交只烧 proposer 槽位不破界（重提交=+0 假承认，攻击性 hidden-retry 只能从泄漏裁判榨出 +0.027/提交）。
4. **e-detector 退休**：对「存活零假设 E[X̃|G]≥δ_t」反向下注、每日重启求和 M_t=ΣW^(j)；ARL 保证 E[τ_A]≥A*（A*=1260），中位延迟 204-322 天；stake=对「全衰减到零」设计替代的 Kelly（不可拟合健康漂移——拟合则 M≈t 线性爬升=全员误报）。
5. **δ=2c·TO/κ 经济门槛**：κ̄=0.018=**市场常数**（E[gross]/E[IC] 平均口径；逐 sleeve 估计会翻转 shelving 决策——首版逐 sleeve 估计把 77% 波动率 sleeve 错误 shelve）；**各族 break-even 差一个数量级**（value 0.010 / liquidity 0.012 / vol 0.017 / momentum 0.031 / 短反转 0.074）→ 单一 δ=0.015 是信号质量地板非经济门槛（论文自曝）。
6. **执行中性**（Prop.2）：裁判永不见账本；账本可从决策日志零成本重算（540 cells 录一次、重 book 零成本，220 LLM cells 复现逐字节）。

## §三 对我司法制的实证 receipts

- **谁判=假承认数，proposer 不能弥补**：冻结裁判 synthetic 假承认 0.00/提交（全种子），三种泄漏裁判（偷看 t 检验/自适应门槛/无门）0.26–0.85/提交、controller 换谁都一样；真实 CSI-500 十年 11.7/campaign vs 泄漏 86–196（5-11×）。**=我司「判据冻结/禁看结果改阈值/禁跑到达标为止」的外部 A 级实证**（CEO 元哲学「实战出真知」的学术同源版：谁主张漂亮都没用、门的完整性才决定假发现）。
- **Prop.1 四条件 vs 我司四律**：(i)λ 可预测↔prereg 冻结 commit；(ii)仅提交后数据↔OOS 恒盲；(iii)epoch 内宇宙冻结↔种子登记+冻结批产物；(iv)无 foretelling↔禁未来数据。逐条已满足。**缺口面**：我司纸盘监控逐轮读数（T-24 月度 hr 门/x2-watch F3 逐轮爬读）=固定冻结窗上的高频读取=anytime-valid 升级候选面（非违约：门值本身冻结，但逐轮读数的多重偷看面在 Ville 口径下才正式有界）。
- **视界教训（§8.7）**：日频 IC 证书结构性认证不了慢因子（动量 IC 0.001@1d→0.009@63d，跨 δ 无望），且 e-BH 高门槛偏爱「日统计最强」族=净经济最差族（短反转 break-even 0.074）；修复=**认证所交易的视界，非日频**。→ 我司 G1'v2 按族固定窗（h10/h20/60d）=该正解形态的第三方验证；未来若做日频 e-face，禁做唯一门。
- **等待换算律**（对 PROSPECT→INTERN 6 月窗）：T∝2σ²/μ² 我司 blend 级流 σ 远小于单因子日 IC 的 0.12 → 等待大幅缩短=现行 6 月窗合法；但若未来做单因子日 IC 级流水线，δ 级边缘=1434 天结构性地长，6 月窗偏短——先验校准指针留档。
- **LLM 角色边界**：LLM proposer 产率胜脚本（6/6 设定）、平 bandit、唯一增量=自写诊断探针（3/6 可评族显著降干预 regret、3/6 无差异、**从不更糟**；探针永不入统计检验=零多重性成本）。→ J13 本地 LLM 车道角色边界判词：提议+诊断面，判官面永归冻结 science_gates；探针面（LLM 写一次性诊断脚本）=未来可选车道，观测池。

## §四 采纳边界（杠杆律尽调面）

- 样本=单市场 CSI 500、四起点年共享大部分数据、无 walk-forward 外 held-out；LLM 臂=重放非保证实例（训练覆盖窗=Prop.1(iv) 失效面，论文自曝）；组合层=测量仪器非策略（alpha t<1 全组、无借券费、卖空假设无清单、κ̄ 全样本估计=in-sample 输入、DSR 只折 108 组不折构造搜索=自曝低估）。
- **消费路由冻结**：science_gates 方法论面。任何 e-value 伴随读数/e-detector 退休面/per-family δ 经济门槛面落地=从 research/PREREG_TEMPLATE.md 起草+D6 机制段四选一+同族相关性门。本轮**零采纳零接线零引擎零台账**。
- 具体候选（未来 prereg 起点，按性价比排序）：①纸盘 sleeve e-value 伴随读数面（不动冻结门、加列只读）；②per-family δ=2c·TO/κ 经济门槛律（新 prereg 阈值设计警示面——单 δ 跨族=数量级错配，论文 break-even 表直接可引）；③factor-sleeve 层 e-detector 退休面（T-34 fast-line 池消费面候选）。

## §五 funnel（双列照报）

- 本片：深读收位 **1/1**（素材级→深读级）；采纳 **0**；新族 0（evaluation/science-gates 既有族方法论补强）；引擎/批/台账零接触。
- 引用级注册链：r260 素材登记 → 本 digest 深读裁定 → 采纳冻结待未来 prereg。

## §六 续作指针

- face (a) jisilu run-9/hibor run-5/guorn run-3+jin-gong 节后 verify=09-28 周一开窗（date-gated）。
- 10-01 月首 trio（science_audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门自动激活。
- e-value 面若开做：先 per-family δ 表（§二-5 的 break-even 口径=PREREG_TEMPLATE α 机制段素材）再起草，禁直接搬 0.015。
