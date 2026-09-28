# DECISION_CHAIN_V3_TOURNAMENT 预注册（T-101 · CEO 直令 O-20260928-1506 链锦标赛快速迭代令「要快速的迭代方法……一整个决策链条去尝试，先判断市场热度，风格，题材等，然后才是仓位，技术指标什么的……科学思考 理性执行」）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> **节拍=DECISION_CHAIN.md v1.2 §4.7 锦标赛版本批**（K 假设一预注册并行烧·T-27 先例）；**预先承诺姿态（最强反 dredging）**：本批三臂假设在 **v2（T-95·DECISION-CHAIN-V2-P1）verdict 落地前**冻结——物理事实：冻结时点 results/runnable_pool.json 条目 DECISION-CHAIN-V2-P1 status=**waiting**（排位 W1/W2-JUDGE done + W3-JUDGE 在飞 + W4-JUDGE waiting 之后）；看到 v2 结果再设计=弱姿态禁用（票面 PRE-COMMITMENT LAW 逐字）。
> 血统=v2 预注册（research/DECISION_CHAIN_V2_PREREG.md·含 §9 a1/a2/a4/a5 修正案全谱）+v1（DECISION_CHAIN_E2E_P1·a9ed12ff+r318 LANDED chain_win=否）+MARKET_CLOCK_COMBO L1/L2/L5 正典面+t18_deep_manifest core48 正典 48 员+T-27 五法锦标赛跨臂校正先例。

## §0 批件身份【跑前】

- 批名 / 批号：DECISION_CHAIN_V3_TOURNAMENT（决策链 v3 锦标赛三臂批：H1 STYLE-TILT / H2 THEME-SATELLITE / H3 MINIMAL-CHAIN CONTROL）。**批内新格数（N_eff）=16,566**＝三臂各 {base,x2}×2,761 起点（legacy 1,255+deep 1,506·T-22/T-34 冻结起点集逐字）。**B/C/D 臂=v1 已计已测面逐字复用零重计**（v1 N_eff 16,566 已含；G-REPRO-v1 门=位级复现冻结读数=T-34 §0 反重复先例·管线完整性门非重测）。跨臂校正面：K=3 机制假设臂×{6m,12m,24m}×{base,x2}——终裁 DSR/PBO 按批内臂数与系列版本数（v1.1+v2+v3 批）联合校正（§4）。
- 认领：T-2026-09-28-101 owner=**bm-c**（claim 61ca275a 2026-09-28 15:16·CEO 令票=认领与开动同轮 O-20260924-1730）；本预注册=owner 亲执（无侧支）。
- 部门归属：dept:策略（链规格）+研究（judgment 面）+组合与资金部（ladder/cash-leg 复核）。
- 算力预算：Stage-A 全 checkpoint 复用（v2 §0 同款：t34 曲线档+REV-OSC 袖序列 a4/a5 双路门+GC001 面板+热度复合件=零重派生）；Stage-B 三臂包络纯向量化（T-90 血统·每臂 <5min 量级）；烧位=**v2 finalize 后队列衔接**（票面「immediately after v2 finalize」逐字——池条目 status=waiting 排位=DECISION-CHAIN-V2-P1 之后，池序列化零死轮）；>10min 面分离入池（O-2100 执行面分离律）。

## §1 α 机制段【D6——每臂一个环级机制假设·零自由参数搜索】

- **H1 STYLE-TILT（环② v4-lite 重引入·风格比价权倾斜）**：机制=「大小盘+成长价值两组比价信号（core48 既有面零新管道）以 ≤10% 卫星预算权倾斜进 v2 链」——LS 腿 5%：r60(512100 中证1000) vs r60(510300 沪深300) 比价，胜者腿得 5%；GV 腿 5%：r60(159915 创业板) vs r60(512800 银行) 比价，胜者腿得 5%；其余 90%=v2 面逐字（六员 EW 核心×N=5 阶梯+REV-OSC 熊袖+repo 现金腿）。切换=N=5 日确认滞回（与 v2 阶梯同款确认语义·T 收盘确认→T+1 生效·shift(1) 因果）。**机制假设：风格动量携带政体持续性奖赏（style momentum carries regime-persistent reward that pure temperature routing misses）**——v1 尸检杀的是日级成员路由（73% 日分歧），本臂检验的是**慢频风格偏好**（60 日窗·5 日确认≈月频级切换）是否为独立信息源。代价支付者=倾斜腿切换摩擦（确认滞回压制频次）+卫星分仓的机会成本。
- **H2 THEME-SATELLITE（题材卫星·板块谱系动量门）**：机制=「MARKET_CLOCK_COMBO L2 板块谱系动量（core48 ETF 板块面 r20 排名·L2 正典 import 禁重实现）选 top-1 板块 ETF 以 ≤10% 卫星权重入 v2 链」——卫星宇宙=L2 正典板块分类面（宽基/债券/黄金/QDII/科创条目按 L2 分类剔除·仅板块类 ETF 参选）；top-1 判定=r20 谱系排名（L2 canon 逐字）；切换=N=5 日确认滞回（**v0 成本病防线逐字**：时钟组合 v0 判负 0/228·成本拖累 7.8%/年——迟滞门就是为防此复发而设）；其余 90%=v2 面逐字。**机制假设：题材/板块轮动携带等权核心错过的截面 α（theme/sector rotation adds cross-sectional alpha the equal-weight core misses）**。代价支付者=卫星切换摩擦+单一板块集中度风险。
- **H3 MINIMAL-CHAIN CONTROL（最小链证伪对照臂）**：机制=「v2 面**剥袖**：六员 EW 核心×N=5 确认阶梯+repo 现金腿，**零袖零叠加零路由**」——最小可行链=核心+阶梯+现金腿三件套（RED20/YELLOW65/ORANGE50/GREEN80·满热 95 档热度窗内·v2 §3 ② 逐字含 a1 修正）。**机制假设（基线）：若 H1/H2 打不过 H3，则风格/题材面零增值=诚实报**；副读数=H3 vs A-v2（v2 落地后）隔离 REV-OSC 熊袖贡献（v2 §5 预测袖≈零/小负——本臂使其可测）。诚实注记：H1/H2 vs H3 的差=**袖+叠加联合面**（H1/H2 含袖、H3 不含）——分解链=H1−A-v2=纯风格叠加（v2 落地后可减）、A-v2−H3=纯袖、H3−D=纯阶梯（与 J-C2 同族）。
- D6 同族披露：三臂共享同一成员书与同一 v2 底座（臂间=受控比较）；零新交易员函数；风格对与板块成员=core48 正典 48 员内选取（§2），零新数据管道。

## §2 数据与面板【跑前探针事实】

- **core48 正典 48 员**：results/shortline/t18_deep_manifest.json members 逐字（48 员全清单在册）——**风格对在册性已验**：510300（大小盘·大盘腿）/512100（小盘腿）/159915（成长腿）/512800（价值腿）四员全部在册；**H2 板块参选面=L2 正典板块分类 import**（runner 建设期从 MARKET_CLOCK_COMBO L2 机制件装载·分类映射禁重造；板块分类覆盖 census 入 §7 披露）。
- 宇宙/起点集/成员曲线/袖序列/现金腿/热度面：**v2 §2 逐字复用**——legacy=core48 面板（cutoff 2026-09-24）+deep=T-18 增长面板（2013-06-17 起）；**binding cutoff=2026-09-22**；cutoff 后新 bar 不回流；t34 曲线 checkpoint（{base,x2}·G-ANCHOR 六员锚）；REV-OSC 袖=a4/a5 双路门（重放优先·工件漂移回退·fail-closed）；GC001 现金腿（T-88 s3 面板·年化/252·缺日 ffill）；热度复合=market_clock import（数据窗外 GREEN 恒 0.80 降级披露）。政体真值源=REGIME_GUARD v3 双轴两腿门（legacy 主判/deep 降级 proxy 披露·v2 §2 语义逐字）。
- **风格/板块面数据完备门（本批新增 G-STYLE/G-THEME）**：G-STYLE=四风格腿 {510300,512100,159915,512800} 各自 r60 可算窗覆盖率 census（起点集窗内全序列可得=PASS·部分可得=降级披露非 VOID）；G-THEME=L2 板块参选面 r20 谱系可算窗 census 同法。涨停家数/炸板率/连板高度采集器=**缺位如实披露列入供给队列**（O-1506 §三.2 逐字——本批不用不编造；偏好面 v4 正典建设另线）。
- 数据完备门族（任一不过即 VOID 中止零产数）：G-CENSUS（{1255,1506}）+G-ANCHOR（6 员）+G-V3 两腿+G-MANIFEST（t18 PASS 48 员）+G-REPRO-v1（B/C/D 位级）+G-REPRO-REV（袖 stats 位级·a5 双路）+G-HEAT（覆盖窗 census）+**G-STYLE+G-THEME（本批新增）**。

## §3 方法学【冻结】

- **六臂总设计**：A 位=三臂并列（A-H1/A-H2/A-H3）+共享对照 B/C/D（v1 §3 逐字：B=COMPOSITE-CE-01 全窗满仓单持·C=被动 EW·D=六员等权不换）——**版本可比性=全臂共享 v1/v2 同款对照与同网格**。
- **A-H1 = v2 面逐字（§3 v2 A 臂全五腿：六员 1/6 恒权+N=5 确认阶梯+REV-OSC 熊袖 RED 激活占帽全额+GC001 现金腿+阶梯切换日回锚计费）+ 风格倾斜叠加**：叠加构造=每日（仅确认翻转日重算·滞回门内零交易）LS 腿 5% 给 r60 胜者、GV 腿 5% 给 r60 胜者；叠加腿收益=对应 ETF close-to-close 日收益（T+1 生效律同阶梯）；叠加再平衡成本=单边率×Σ|Δw|（COST_X2_RATE/2 运行时派生禁手抄）·确认翻转日一次性计费；**叠加腿独立于阶梯帽**（阶梯帽管 v2 面 90% 主体·叠加 10% 恒满——机制注记：叠加面不受政体缩放=风格假设的强检验姿态，RED 态叠加仍 10% 持仓，政体防御由 v2 面 90% 承担）。
- **A-H2 = v2 面逐字 + 题材卫星叠加**：每日（仅确认翻转日重算）top-1 板块 ETF 得 10%；N=5 确认滞回（v0 成本防线）；计费同 H1；卫星面独立于阶梯帽同 H1 姿态。
- **A-H3 = v2 面剥袖**：六员 EW×阶梯+现金腿（RED 态 20% 帽内=六员核心缩放·80% 现金腿 accrual——无袖：RED 态 20% 帽内全额为六员核心缩放面）；其余语义逐字 v2。
- 窗口族 {6m=126·12m=252·24m=504}（主判窗=12m）+faces {base·x2}+政体分段 3-way proxy 披露维度——全 v2 §3 逐字。
- **本批无随机 null**（臂间受控比较先例 v1 §3/v2 §3 同款）；bootstrap beat 率 95% CI=二项 percentile B=2000；**seed=`decision_chain_v3_tournament`=20291000**（SEED_REGISTRY 本 commit 同步登记；带回避已证：20283000..20290500=trial/mass/chain-v2 带满·20261001=chain-v1·20261002..20261030=t11_negday 带回避·20291000=带外净位 rg --no-ignore 全 repo 零 SEED 用例命中证 2026-09-28 15:2x）。
- 账本：finalize 步 science_gates.append_ledger(batch_name="DECISION_CHAIN_V3_TOURNAMENT", batch_trials=16,566, file_name, evidence_cutoff="2026-09-22")——禁手抄 prev。
- 反重复披露（票面 anti-dup 逐字）：T-95 v2 在飞面零触碰（本批=v3 候选集·v2 absorbed as lineage）；MARKET_CLOCK_COMBO v0 verdict（0/228·成本拖累 7.8%/年）=证据输入非重建（H2 迟滞门即其教训）；T-74 谱系/L2 面+market_regime v3 序列复用；v1 网格已消费不重跑（B/C/D G-REPRO 位级门）。

## §4 判据【跑前写死·禁看结果调线·与 v1/v2 完全同口径】

- **J-CHAIN（主判·legacy 轴 12m 完整窗·A 位=逐臂）**——判线逐字 v1/v2：
  - J-C1（链 vs 最佳单体）：A-臂 vs B beat 率 95% bootstrap CI **下界 > 0.50**；
  - J-C2（链 vs 静态等权）：A-臂 vs D beat 率 CI 下界 > 0.50；
  - J-C3（链 vs 被动）：A-臂 vs C beat 率 CI 下界 > 0.50；
  - J-C4（红线）：全臂最差起点 12m 回撤 ≥ **−0.35**；
  - 臂赢判读=J-C1∧J-C2∧J-C3∧J-C4；任一不过=该臂不赢诚实报。
- **J-TARGET（序列级主判据·O-20260927-0809 §二冻结口径逐字）**：A-臂 pooled beat 率 > B 臂同面读数（逐轴×窗×面）且 A-臂最差起点回撤 ≥ −0.10；两级读数分开披露禁合并。
- **J-TOUR（锦标赛裁定·本批新增·T-27 五法锦标赛先例）**：①逐臂 J 线读数并列披露；②**证伪门逐字（票面）**：H1/H2 任一臂打不过 H3（pooled beat 率点估计与 CI 下界双双 ≤ H3 同面读数）=该机制假设判负如实报；③**跨臂多重校正**：三臂联合的 DSR 按批内总 N_eff 折减、PBO 三臂面板、预期假阳性率=E[FP] 如实披露；④胜者规则预冻结=J 全过且 J-TOUR 校正后仍立的唯一臂入册候选（多臂同过=并列入册·纸盘接线走 10-01 月界非本批）；⑤零臂过=锦标赛判负·断环定位照产·v4 触发器评估照 O-0809 §四.5。
- **四环复定位（逐臂）**：环①=确认切换频率；环②=叠加腿切换次数+摩擦份额+零费反事实（A′ 同 v2 §4 语义）；环③=卫星/倾斜腿成本归因；环④=GREEN 段窗份额+进攻席位空缺（0 员如实）。全环量化入 §7 禁叙事替代数字。
- **D7 四必报（每臂×轴×窗）**：OOS 笔数/覆盖年数/独立政体窗数/CI 宽度；25td 子采样披露列。
- 反 dredging 三闸：①迭代数入 N_eff（系列 v1.1+v2+本批·版本批=K=3 臂联合校正如实注记）；②机制假设=§1 三条逐臂；③禁看当版结果改当版（本批改动只面向 v4；**v2 verdict 落地前冻结姿态=三闸最强面**）。
- 诚实边界：胜者=只入册候选（票面「winner = candidate registration only, paper wiring goes through month boundary」逐字）；judged 重放面 vs 活面分歧披露同 v2；本批零注册零 paper 接线。

## §5 跑前预测【写死于跑前·≥3 条·含极端日先验】

1. **H1 风格倾斜**：A 股风格动量文献面（小盘 2023-2024 微盘崩塌前强势→2024 红利/大盘切换）=政体持续但急变窗密集——N=5 确认+60 日窗≈月频切换 [每年 2-6 次/腿]；叠加腿贡献点估计 [−1pp, +3pp]/年（宽带=风格信号在 core48 面上的历史强度未探=如实宽带）；**J-C1 单过概率 [15%, 45%]**。
2. **H2 题材卫星**：v0 时钟组合 0/228 判负（成本拖累 7.8%/年）+迟滞门修复后预期换手降 ~80%——卫星贡献点估计 [−2pp, +2pp]/年（v0 判负先验压上界·迟滞修复为正贡献源）；J-C1 单过概率 [10%, 40%]。
3. **H3 最小链**：阶梯+核心+现金（无袖）——RED 段防御与 v2 同面（袖预期≈零）→H3 与 A-v2 读数差预期 [−0.5pp, +0.5pp]（袖贡献带·v2 §5.5 同源）；**H3 vs H1/H2 证伪门=大概率 H1/H2 不显著超越 H3（概率 [55%, 80%]）**——若命中=风格/题材零增值诚实报（CEO falsification 姿态的预期主流）。
4. **最差起点 dd**：三臂均 ≈ v2 阶梯压缩带 [−0.22, −0.12]（H3 同面·H1/H2 叠加 10% 独立于帽→dd 上浮 [0, +2pp]）；J-TARGET −0.10 线大概率不达（v2 §5.4 同源 [10%, 35%] 过线概率）。
5. **极端日先验（三件套(c)同款窗）**：2024-09-24/10-08 政策脉冲=风格/题材腿同向高开（叠加腿满 10% 持仓敞口·整窗路径入读数无豁免）；2025-04-07 外生缺口=卫星/倾斜腿 T+1 确认滞后；2026-01-19 D-C 极端溢价日入整窗。判据面=整窗读数与 dd 非单点检测线。
6. **G-REPRO 族（确定性·置信最高）**：B/C/D 位级=v1 冻结读数；袖 stats 位级=judged 冻结读数。

## §6 产物

- script：scripts/decision_chain_v3_tournament.py（run/status/selftest 子命令；**import-face 复用**=decision_chain_v2 全部原语（阶梯/袖双路门/现金腿/热度复合/checkpoint 装载）+t34/t22 枚举锚门+MARKET_CLOCK L2 板块谱系件+core48 r60/r20 比价面（t18 manifest 48 员内·纯 pandas 派生零新管道）——禁重实现；selftest hermetic 离线夹具 r116 律+B7b 契约腿 r297 律）。
- 产物：results/decision_chain_v3_tournament.json（顶层 evidence_cutoff+cutoff_meta+audit 段+六臂×双轴×窗全表+J-C1..C4/J-TARGET/J-TOUR 逐臂读数+跨臂校正面+四环复定位表+叠加/袖/现金腿归因列+corr 披露+D7 四字段）+research/shortline/decision_chain_v3_results.csv（小件入 git）+本文件 §7/§8 回填+research/DECISION_CHAIN_LEDGER.md v3 行 verdict 翻面。
- 下游：月度四件套「链条健康」节消费；CEO 呈报=s4（结果一出立刻报·含 J-TOUR 证伪门与四环复定位·负也照报）；v4 触发器评估（本批断环定位+进攻军席位+偏好面 v4 正典+温度计校准修订）。
- 烧位：池条目 DECISION-CHAIN-V3-TOURNAMENT（waiting·排位=DECISION-CHAIN-V2-P1 之后）；v2 finalize → 本批 ready-flip 衔接零死轮。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（finalize 于收割轮回填：G 门读数+六臂全表+J-C/J-TARGET/J-TOUR 逐臂判读+四环复定位+叠加/袖归因+预测对账+账本行）

## §8 批后复盘【必填·s7-T】

（一次定稿；预测对账；门禁链损耗账 results/gate_attrition.json 追加一行；回执入轮报告+CODELY.md 行级追加；锦标赛裁定+证伪门定案呈 GM/CEO）
