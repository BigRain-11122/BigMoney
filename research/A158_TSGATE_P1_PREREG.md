# A158-TSGATE-P1 预注册 —— Alpha158 因子库「时序分位门」普查+分诊批（B2 备货·GM 供料件落地）

> 模板=research/PREREG_TEMPLATE.md 结构镜像（§0-§8）；批型=**判别力探针/供应普查**（gate_census→gate_verify 血统），**非策略回测批**——G1'v2/G2v2 机械面不适用（无策略收益序列），判读线=gate_verify 三控判线逐字镜像（见 §4 声明）；跑前 commit 冻结；跑后只回填 §7/§8，要改判据要重跑。
> 供料源=GM 供料件 STANDBY_POOL_SUPPLY_B2_B4.md §B2（O-1815①+O-1820 三验预填：可判负假设✓/消费面指名✓/判负处置预案✓）；上游=Alpha158 普查判负终态（157/158 因子 |ICIR|<0.09 于 ETF/基金截面·research/ALPHA158_CENSUS_CN_ETF.md）——**本批假设=截面判负的是「截面选基」用法，同族因子改做单标的时序分位门对前瞻收益/政体态有判别力**（同族换用法路线·与截面判负互为独立假设、不互相翻案）。
> 统摄律：BACKTEST_SCIENCE.md v2 + COMPUTE_AUDIT.md 批件纪律 + O-1820(3) consumer_plan 必填 + pit-95/r431 decidable 掩码律 + r433 同门换用法律（择时用法 9/10 判负教训随附）。

## §0 批件身份。【跑前】

- 批名/批号：**A158-TSGATE-P1**（Alpha158 时序分位门·wave-1 普查+分诊）。非试验账本批（marks +0·SEED +0·无策略曲线）；算力=本地 CPU 确定性普查（估单机串行 ~6min·workers 并行 ~1-2min·零 token 零网络）。
- 认领：lane-free（B2 供料件指定·lane_owner=null=任何健康机可烧）；入池条目=results/runnable_pool.json `A158-TSGATE-P1`（consumer_plan 必填律）。
- 部门归属：dept:研究（判别力普查面·T-101 v4 供料线）。
- **consumer_plan（O-1820(3)）**：PASS 门→gate_verify 式独立复核资格（下一关）→T-101 v4 政体门候选臂库；PARTIAL 门→C1 情绪/政体门输入特征清单（gate_verify PARTIAL 降格先例）；FAIL=该因子时序门用法关线（合法产出）。次级消费：T-74 L5 仓位阶梯特征面。
- 意义审计：①可判负假设（门判别力 OOS 净差不显著=关线）②指名消费面（上文）③判负处置预案（FAIL=关线照报·PARTIAL=降格输入特征）——三验全过。

## §1 伪 α 机制段。【四选一+D6】

- **[x] 行为偏差**（主）——**风险源价**（辅）：单标的自身 252 日分位极端态=过度反应/恐慌态识别面——「超跌反弹」（MBAlib 空头抑制语料·W10 §1 血统）vs「急跌不接飞刀」（r433 择时教训）**族内方向矛盾在册=条件化门价值主张而非方向宣称**；代价支付者=极端态逆势接刀者/恐慌跟随者；截面用法判负（ICIR<0.09 全族）≠时序用法判别力——两用法独立假设独立判决。
- **D6 同族相关性准入（邻接披露·本批为普查面无注册轴）**：已知邻接族逐门披露列——①`ROC20_q10` 门=census ROC20_q10=W10 MOM 探针同构（r228 锚：510300 open=374/decidable=3,344/首可判 bar-idx==139）=**跨血统锚门**（本批复算须逐位复现，作 fail-closed 锚）；②RSV30/RSV60 低分位门 vs census `RSV60_low<0.2`（构造不同：自身分位 vs 绝对 0.2——同族近邻披露）；③A158 `VSTD20`=**成交量**标准差比（Std($volume,20)/($volume+1e-12)）≠census `VSTD20_q20`（价格波动分位）——**命名撞车诚实声明**（两构造不同·结果表按 A158 定义）；④MAD60（MA 距离）不在 A158 库（A158 对应面=MA60 均值比）——无重叠如实注记。
- 消费面邻接披露：W8 TSTATE 轴（mad60/rsv60 试用语法面）与本批 C1 输入特征面=**不同消费面**（同门换用法判例 r433 随附：择时用法 9/10 判负·bear 段接刀风险预注册在案）。

## §2 数据与面板。【跑前探针事实·G-ANCHOR-FACE 四元组律】

- 宇宙/池：**全面板 data/daily/*.csv（bm-a 本地 ETF/基金面板·1,724 码·≥500 bars 入样·MIN_BARS=500 gate_verify 逐字）**；五员冻结宇宙（O-1555）{510300,510050,510500,512100,588000}=落地性次级描述面（O-1531④）。
- **evidence_cutoff=2026-09-22（P-5C 冻结口径 binding）**：面板一律先截断到 cutoff（截断后 510300=3,483 行·2012-05-28→2026-09-22）；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层 `science_gates.cutoff_meta("2026-09-22")`（C2 缺字段=VIOLATION）。
- **因子库=Alpha158 静态特征库 qlib-verbatim 移植**（源=qlib/contrib/data/loader.py get_feature_config 逐字公式·pandas 实现）：kbar 9（KMID/KLEN/KMID2/KUP/KUP2/KLOW/KLOW2/KSFT/KSFT2）+ price 3（OPEN0/HIGH0/LOW0·**VWAP0 剔除=面板无 $vwap 字段·census err=1 血统如实**）+ rolling 29 算子×窗 {5,10,20,30,60}=145 → **157 因子**。滚动算子 min_periods=1（qlib 语义）；Slope/Rsquare/Resi=闭式滚动 OLS（qlib rolling_slope/rsquare/resi 语义镜像·rsquare 滚动 std≈0 置 NaN 守卫）；IdxMax/IdxMin=滑动窗 argmax/argmin+1（qlib 语义）；Rank=窗内百分位（qlib percentileofscore 语义·pandas rolling.rank(pct=True)）。
- **门定义（冻结）**：每因子两侧——低分位门 `f < f.rolling(252, min_periods=120).quantile(0.10)`；高分位门 `f > f.rolling(252, min_periods=120).quantile(0.90)`→**314 门**。decidable 掩码=f.notna() ∧ qref.notna()（pit-95/r431 坑律：底层面值 notna 派生·禁 map({False→x}) NaN 归桶）；预热窗（252/min_periods=120）gate-closed 诚实。
- **前瞻收益**：h=20（消费面=v4 政体门 20 日族·gate_verify 同口径），`fwd = close.shift(-21)/close.shift(-1) − 1`（信号日收盘信息集·T+1 次日收盘买·持有 20 日·无未来数据）。
- 数据锚面四元组（每数据锚必带）：**510300 锚**=（①data/daily/sh510300.csv ②pd.read_csv 直读 ③全史起算 2012-05-28 ④预热窗 252/min_periods=120→ROC20_q10 门首可判 bar-idx==139）——r228 探针事实逐位对账锚（open 374/decidable 3,344）。
- 数据完备门（fail-closed，不过即 VOID 拒烧）：**G-PANEL**（csv 数≥1,500·五员全在位）+ **G-CUTOFF**（截断后五员末行≤2026-09-22·510300 截断行数==3,483）+ **G-ANCHOR-ROC20**（510300 ROC20_q10：decidable==3,344 ∧ open==374 ∧ 首可判 bar-idx==139·r228 探针逐位锚）+ **G-FACTORS**（157 因子全序列非全 NaN·每因子≥1 工具 decidable≥500）——runner 探针与锚**强制同面断言**（探针加载路径与锚声明路径逐位比对·一面不相符=配置错配 VOID 拒烧）。

## §3 方法论。【冻结】

- 判别力统计（gate_verify 逐字镜像·IS/OOS 双段）：分段 IS≤2016-12-31 / OOS≥2017-01-01；每工具每段门事件≥15（MIN_EV=15）；门内/门外 20 日前瞻均差=diff；**diff_net=diff−0.10% 往返成本**（ETF 保守值）；**不重叠控制= stride-20 双组内抽稀**（thin(pin)/thin(pout)→diff_net_thin）；每工具每段 t=Welch 双样本。**桶定义（B2 冻结·pit-95/r431 严口径）**：in 桶=open∧decidable∧fwd 有效；out 桶=（¬open）∧decidable∧fwd 有效——两桶均 AND decidable 掩码（严于 gate_verify 原 out 桶（原=~mask 含预热窗日）·差异如实披露·锚门掩码计数 374/3,344 不受桶定义影响）。
- 聚合（每门）：全面板 per-inst 中位 diff_net（IS/OOS）+正份额 pos_share（OOS）+中位 t（IS/OOS）+中位 diff_net_thin（OOS）+ |t|>2 工具占比；五员次级面逐员读数表。
- **判读线（跑前写死·gate_verify 逐字）**：`PASS = OOS med diff_net>0 ∧ pos_share≥0.55 ∧ IS med diff_net>0`；`PARTIAL = OOS med diff_net>0`；`FAIL = else`；`N/A = OOS n_inst<30`。分层闸语义=普查→候选资格分诊，**非策略宣称**（PASS 仅获 gate_verify 式独立复核资格）。
- **多重检验税披露（O-2245 精神）**：N_gates=314·E[FP]=0.05×314=15.7 门量级预期假阳——PASS 门升格 v4 候选前必过独立复核面（D6 邻接审计+独立 OOS 复核），普查面零注册效力。
- 幂等：结果件在位=refuse 重跑（refuse-if-exists 守卫）；确定性双跑字节恒等（selftest 腿·唯一运行时元数据=generated/elapsed 独立段）；checkpoint=per-shard jsonl 断点续跑（跨机 kill 复活律）。
- 账本：非试验账本批（无策略 trial）——**不 append trials_ledger**（census/verify 先例）；N_gates=314+判读线如上披露。

## §4 判据。【跑前写死】

- 本批判据=§3 gate_verify 三控判线（IS/OOS+成本+不重叠）逐字冻结——**G1'v2/G2v2 不适用声明**：本批无策略收益序列/无 trade 流（探针批型），机械套用=类别错配；判读线等价强度=OOS 盲段+成本+不重叠三控（与 gate_verify 同门同线，可比性=本批设计目标）。
- 描述条款（批级披露不替代判线）：OOS 正份额/中位 t/五员逐员读数/IS-OOS 反号门单列（gate_verify PARTIAL 族先例：2017 前后机制漂移如实注记）。
- 硬界设计三件套 (c)：本批无策略 max 线——**极端日先验面**=七极端微观结构日（2015-07 股灾/2016-01 熔断/2024-02 微盘崩/2024-09-24·09-30 政策脉冲/2025-04-07 外生缺口/2026-01-19 极端量日）门态披露列（各门在七日的开/关态随结果表披露·r228 探针七日八维态先例）。

## §5 跑前预测。【写死于跑前·≥3 条】

1. **跨血统锚复现（确定性·非预测）**：510300 ROC20_q10 门 open==374/decidable==3,344/首可判 bar-idx==139（r228 探针同 cutoff 同构造逐位复现；不符=fail-closed VOID）。
2. **PASS 门数 ∈ [0, 25]**（314 门·E[FP]≈15.7 假阳量级+真信号族（RSV/ROC 动量超卖族 20 日正信号在册）→模态结局=低个位真信号+十余假阳噪声面=PASS 门全部待独立复核方可升格）；**PASS+PARTIAL 合计 ≤ 60**（census 20 门仅 4 族正先例→判别力稀疏预期）。
3. **RSV 族低分位门方向先验**：RSV30/RSV60_q10 OOS med diff_net>0（census RSV60_low<0.2 PASS+RSV30 PASS 血统同向·门内样本收窄致 N/A 可能如实）。
4. **多数门=FAIL**（~254+/314）：截面判负族时序门用法大面积平塌=合法关线产出（关 157 因子时序门用法省未来臂）。
5. **极端日先验**：RSV/ROC 低分位门在 2015-07-27/2025-04-07 开窗（r228 MOM 锚同族·超卖态极端日聚集）；高分位量能门（VSUMP/VSUMD high）在 2024-09-24/09-30 政策脉冲开窗——门态逐日披露验证。

## §6 产物

- runner：`scripts/a158_tsgate_probe.py`（subcommands：run[--shard k --shards n --workers N]/finalize/status/selftest；`__main__` 守卫=Windows mp 坑律；selftest=hermetic 合成面：①因子公式锚腿（KMID/RSV/ROC/STD 数值断言）②门构造腿（分位边界/decidable 掩码 NaN 伪影禁用·pit-95）③统计腿（IS/OOS 切分/cost/stride-20 thin/verdict 四态合成数据断言）④确定性双跑字节恒等腿（r297 律·generated/elapsed 独立段比对）⑤G-ANCHOR-ROC20 实数据锚腿（510300 三元组逐位）⑥refuse-if-exists 幂等腿）。
- 产物：`results/a158_tsgate_p1.json`（顶层 cutoff_meta+prereg 块+314 门 IS/OOS 聚合+verdicts+五员次级表+极端日门态披露+audit 段）+ `research/A158_TSGATE_P1.md`（可读供应面：判定表+PASS/PARTIAL 候选清单+诚实注记）+ checkpoint `results/a158_tsgate_p1/`（gitignored·per-shard jsonl 断点续跑）。
- 池路由：入池 `A158-TSGATE-P1`（lane_owner=null·lane-free·workers_plan=shard 内 worker_cap 并行 BelowNormal·O-2130 多核律）；>5min 串行估计=池批面（autofill 续烧）；finalize=烧后合并腿（lane 任意健康机·per W-SCREEN 先例）。

## §7 跑后实证。【2026-09-29 17:2x 回填·判决面 owner 一次定稿·bm-a r438】

- **漏斗全链**：面板 1,724 csv → 截断 cutoff 后 ≥500 bars 入样 **1,013 工具**（711 跳过全=min_bars·新基不足·gate_verify 同律·零因子错误=157 因子 pandas 移植全面板零异常）→ 314 门 → **PASS 48 / PARTIAL 142 / FAIL 117 / N/A 7**（N/A=OOS 工具<30 的极窄门）。
- **§5 预测对账**：①锚门逐位复现 ✓（in-run fail-closed 双形态·3344/374/139）；②PASS=48 vs 预测带 [0,25]=**MISS 如实**——根因=SUMD/SUMP/SUMN 三元组构造恒等（SUMP+SUMN=1·SUMD=2SUMP−1）+VSUMD/VSUMP/VSUMN 同构+CNT 族+5/10/20/30 窗高相关→**有效独立族数 ≪314**，中位判线在关联簇内成片通过（E[FP]=15.7 仅解释约 1/3·48 PASS 全部须经独立复核面收束）；③RSV 低分位方向命中（RSV30_q10 OOS +0.53%/RSV60_q10 OOS +0.65% 双正）但 IS 反号→**PARTIAL**（与 gate_verify MAD60/ROC20 PARTIAL 同族处置·2017 线机制漂移族）；④FAIL=117 vs 预测 ~254+=MISS（同②关联族推涨 PARTIAL/PASS 所致·FAIL 占比 37% 非多数如实）；⑤极端日门态披露落盘（2015-07-27 n_open=90·RSV5_q10/ROC5_q90 等开窗·全 314 门×7 日态在 results JSON）。
- **消费面主发现（v4 政体门候选队列）**：**STD20_q90**（OOS 中位 +1.07%·正份额 0.74·五员次级面 5/5 全正 +0.3%~+1.7%·不重叠 +0.93%）与 **RSQR20_q90**（趋势强度高位=趋势延续面·OOS +0.93%·五员 4/5 正）=头两号独立复核候选；STD10_q90（OOS +1.26%）次之。量能 RSI 族（VSUMP/VSUMN/VSUMD 窗 10/20/30）与方向计数族（CNTD/CNTN/CNTP）=关联簇成片 PASS·簇内代表待 D6 审计后取一。
- **跨面诚实注记（判定不互借律）**：**ROC20_q10（=W10 MOM 同构门）在本 B2 政体门普查面上 FAIL**（OOS −0.15%·IS +1.03% 反号）——W10 试用语法面=另一消费面独立冻结（W8 TSTATE 同族降格后依法开波先例），本面读数不借判 W10 面、W10 面亦不借本面；读数如实入档供 v4 政体门面参详。
- **面板卫生发现**：五员在面板内**双名双件**（510300.csv 与 sh510300.csv 并存·史长不同·n_in 173 vs 254）——主判定面按工具计数如实双计（无去重宣称）·五员次级表双列披露；后续维护链对账项（去重决策归数据道另行裁定·本批零改动）。
- **锚门复现**：G-ANCHOR-ROC20 in-run+finalize 双过（预注册 §5.1）。

## §8 批后复盘。【同窗回填·bm-a r438】

- **消费面指名回执**：T-101 v4 政体门候选库=48 PASS 门入独立复核队列（下一关=gate_verify 式独立 OOS 复核+D6 邻接审计·簇内 SUMD/SUMP/SUMN 与 VSUM* 族各取代表前禁整簇入册）；C1 输入特征清单=142 PARTIAL 门（RSV30/RSV60_q10 在列·与 gate_verify RSV 绝对门 PASS2 读数并存=同族两面如实）；T-74 L5=STD/RSQR 高位门族特征面。
- **关线清单**：117 FAIL 门=该因子该侧时序门用法关线（合法产出·与截面判负互为独立假设·不互相翻案）。
- **独立复核队列指针**：48 PASS → 下批 `GATE-RECHECK-A158`（gate_verify 纪律独立复核·冻结后烧）=v4 政体门臂候选唯一升格通道。
- **轮报告/CODELY.md 同轮回执**：bm-a r438（本批=供给底线破口响应·板空常供律例行供料·B2 备货件闭环：prereg 冻结→runner→池条目→autofill 17:20 点火 1724/1724→finalize 同轮全落地）。
- **账本**：非试验账本批（marks +0·SEED +0·无策略 trial·不 append trials_ledger——census/verify 先例）；N_gates=314·E[FP]=15.7 已披露；evidence_cutoff=2026-09-22 顶层在位（C2 键合规）。
