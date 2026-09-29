# T-101-V4-A7-PRESCREEN 预注册（臂级分件冻结·A7 流动性政体信号轴+防御倾斜政体门臂·廉价初筛面）

> 依据：PREREG_TEMPLATE.md · BACKTEST_SCIENCE.md v2 · BACKTEST_PLAN.md 三铁律 · TRIAL_LABOR_LAW §2 两段制 · DECISION_CHAIN v1.2 §四.7 锦标赛节拍（臂级分件冻结合法窗·r433 A2 先例）· r433 教训律（同门换用法反向证伪律+政体门臂 D6 按 beta 同源族预声明处理）
> 供给触发：compute_audit supply_gap/supply_floor 三连 FLAG（池 ready=1<3）· T-102 v0.2 定稿 §五 A7 行（r432）· r433/r434 next 指针（A2 线 LINE_CLOSE 后下一 bm-a 可做臂）
> 血统：T-102 v0.2 §五 A7＝lane-1 v4 自提——B4a「extreme markets 最优」政体条件化学术旁证（MOP 2012 TSM 58 品种）+ REPO 期限梯 carry 已过 G1（INNOVATION-QUOTA-W1 3/4 G2-eligible·bm-c r182）；国内性=交易所逆回购利率=A 股原生流动性压力计（2013-06 钱荒/2015-02 春节前 53.44 实证在册·CEO 研究导向律：国内打法优先立项）

## §0 批件身份

- 批名：**T-101-V4-A7-PRESCREEN**（A7 流动性政体防御门臂·廉价初筛面）；批内格数＝**10**（2 门 × 5 员；null 对照面 K=200/格如实另计披露，不膨胀策略格）；
- 认领：F-04 先行＝`fleet/inbox/MSG-20260929-1535-bma-t101v4-a7-prescreen.md`；任务板引用＝T-101（v4 版本批新代）；§五臂表行引用＝A7；
- 部门归属：dept:研究（链条研究线）；
- 算力预算：分钟级单进程 pandas（≤3min），不入池；批报告带 audit 段（脚本 stdout 自带时长/行数）；
- 车道：**bm-a**（REPO 期限梯面板 data/repo_daily＝bm-a 车道采集件〔T-88 s3·r328 bm-a 接线·update_repo.py 车道护栏=仅 bm-a〕+ ETF 五员面板 data/daily 均本机在位；全 A 面板不触碰）；
- 语法查重：TRIAL_GRAMMAR_LEDGER 全表已核（rg repo|liq|GC00|流动 零命中）——W1-W8 tstate/census 轴全为价量面语法；REPO-CALENDAR-P1/P2（bm-c r182）＝**现金腿日历期限摆动**语法（carry 优化），本批 A7＝**权益风险开闭政体门**用法（门级择时），语法面与机制面均不同。

## §1 α 机制段（D6）

- [x] **机制**：流动性挤压强制去杠杆——交易所/银行间流动性收紧（逆回购利率尖峰）时，杠杆持有者与面对赎回的机构被迫先卖最流动资产（五员宽基 ETF＝最流动层）→压力窗负漂移；防御门在压力窗降权益敞口避开强制卖出级联。国内原生锚：2013-06 钱荒（上证数周 −14%）/2015-02 春节前（GC001 53.44）＝A股原生流动性危机史；学术旁证＝B4a TSM「extreme markets 最优」（压力态可判别→政体门有时效面）；
- **门定义（冻结·圆数无寻优）**：信号面=GC001（交易所隔夜逆回购·最活络期限）收盘年化利率 `close`；
  - **门 L1（水平门）**：`GC001.close > 5.00`（年化%）→ 压力态 → risk-off；≤5.00 → risk-on；除 2011-05-13 面板首日前 NaN→risk-on；
  - **门 L2（z-score 门）**：`z = (close − rolling120.mean()) / rolling120.std(ddof=1)`，`z > 3.0` → risk-off；预热 120 bar 内 NaN→risk-on（利率长期下行面 2011 中枢 ~4-6%→2024-26 中枢 ~1.5-2%，z 门自适应世代漂移）；
  - 执行（T+1 保守代理·O-1132）：信号日 t 收盘算门→t+1 开盘执行；pos(t)=gate(t−1) 滞后一日全仓门控（risk-on=满仓该员·risk-off=现金腿 0%）；现金腿 0%（REPO-CALENDAR carry 不并入本门——分族 D6 见下）；
- **同族相关性准入检查（D6·预声明处理 per r433 教训律）**：
  - **主判定面（臂表 A7 行点名）**：A7 门策略日收益 vs **REPO-CALENDAR 现金腿 carry 族**——proxy=GC001 日 carry（close/252 日息）与 GC001 日利率变动两列实算 max|corr|；判线 max|corr|≥0.7 拒收恒在；预期=结构性近零（权益日波动 ~1.5% vs 现金腿 carry 日息 ~0.008%），实测证伪/证实如实入 §7；
  - **预声明（r433 律）**：稀疏防御门 vs 自身 B&H 无条件 corr 结构性高（门开 ~95% 时段≈主载 beta）——**该面非同族重复证据面**，如实披露不作拒收线；存活格升格门=**CORRSOURCE 式 alpha 分解预承诺**（leg1 OOS α HAC t≥2·leg2 真实超额>同掩码位移 null p95·t101_v4_a2_corrsource.py 模板），未过分解不入全量判决面；
  - 双门互 corr（L1 vs L2 每员 1 对）：跑后 §7 实测。

## §2 数据与面板

- 权益宇宙：五员冻结宇宙 O-1555＝{510300, 510050, 510500, 512100, 588000}；**数据锚面定义四元组（G-ANCHOR-FACE）**：`data/daily/sh<码>.csv`＋`pd.read_csv`（raw 直读）＋文件首行起算（510300 实际 2012-05-28）＋信号预热 120 bar（L2）；588000 上市 2020-11 短窗如实披露；
- 信号面板：`data/repo_daily/GC001.csv`（G-ANCHOR-FACE 第二成员·同四元组法：raw 直读·2011-05-13 首·close=年化%口径·T-88 采集件 spec=research/shortline/REPO_PANEL.md）；信号日历=GC001 自有交易日历；权益执行日=各员自身日历（信号按日历日前向填充到权益面板=最近信号日 gate 值·跨日历缺口如实披露）；
- evidence_cutoff（D2 前向锁盒）＝**2026-09-28**（双面板尾行实测同日）；cutoff 后新 bar 锁定不得回流；结果 JSON 顶层必带 `science_gates.cutoff_meta(evidence_cutoff)`；
- 探针-锚同面断言：runner 实载路径=声明路径逐位比对，一面不等=配置错配 VOID；
- 数据完备门：5 员 csv 全在位且尾行=2026-09-28＋GC001 尾行=2026-09-28（缺一=fail-closed 拒烧）；
- 利率带健全性：0<close<200（T-88 采集律同值·2015-02-10 53.44 真春节前钱荒在带内）。

## §3 方法学

- 执行（T+1 保守代理）：risk-off 信号日 t 收盘→t+1 开盘出（-0.05%）；risk-on 回归日 t 收盘→t+1 开盘入（-0.05%）；持有日收益=close/close−1；现金腿 0%；
- 成本口径：**0.1% 往返**（0.05%/腿·A2 同值）；
- 分段（判读恒带）：bear/bull/chop 三态=510300 close vs MA200 与 MA200 60d 斜率（A2 同法）；
- null 对照：**同掩码循环位移 null**（掩码 np.roll·保持门开/关天数与持续期结构），K=200/格，seed 基=**20309000**（SEED_REGISTRY 新键 `t101_v4_a7_scrnull`·108-key 清点零冲突 2026-09-29 15:2x 后落）；
- **初筛存活判据（跑前冻结·triage 非 G1' 降级——全量判决面 G1' v2/G2 恒在）**：① OOS（2017-01-01 起）净年化超额 vs 同窗 B&H >0 ② OOS **entries≥15**（=risk-off 压力段计数·每段独立证据单元·A2 同线）③ 全期最大回撤≥−35%（描述条款）④ 门策略 OOS Sharpe > null Sharpe 中位（同掩码对照）；
- 账本：`science_gates.append_ledger("T-101-V4-A7-PRESCREEN", 10, "t101_v4_a7_prescreen.json", evidence_cutoff="2026-09-28")` 返回值**嵌入 out["trials_ledger"] 后再 json.dump**（坑律 112：返回值丢弃=账本块零落地簿记盲区律·C 修模板 t101_v4_a2_corrsource.py L160）。

## §4 判据

- 本批（初筛面）：§3 冻结 4 条存活判据（triage）；存活者→**升格门两连**：先 CORRSOURCE 式 alpha 分解子批（§1 预承诺）→ 过者才入全量判决面={6m,12m,24m} 虚拟起点窗×成本 ×2 压测×分段×双 nulls+G1' v2（science_gates.g1_prime_v2 共享库禁手抄）+G2（g2_registration_v2：DSR≥0.95+PBO≤0.25 CSCV 8 块·DSR n_trials=活链头跨波不重置）；
- 判负处置（预先承诺）：初筛判负臂=**线关闭**如实入 §7 与 gate_attrition 损耗账，禁换参数再跑（同语法重跑禁令同源）；entries<15 判负=「OOS 证据面太薄」如实分类（非机制证伪·与超额≤0 判负分列）；政体依赖性如实入面不粉饰；
- 预期假阳性披露：10 格初筛+后续网格，跨波累计 N_eff 照 TRIAL_LABOR_LAW §4 不重置（链头 340,655 活读）。

## §5 跑前预测（写死于跑前）

1. **门 L1（水平门）OOS 事件面极薄**：2016 后交易所 GC001>5% 仅孤立年末尖峰（流动性宽松世代·2013-06 式钱荒绝迹）→ 预测 OOS entries ≪15 → **按冻结判据②判负（证据面薄·非机制证伪）**；IS（2012-2016）含 2013-06 钱荒+2015 压力段→IS 面避损为正（门本职=该政体）；
2. **门 L2（z3 门）良性季节尖峰鞭打**：低利率世代月末/季末尖峰（中枢 1.6% 时 3-4%=3σ+ 但非危机）→ 预测 entries 10-30 过②线，但 whipsaw 成本拖累 → **OOS 超额≈负或近零 → 按判据①判负**；
3. **总预测：A7 臂大概率本面即终局（双门全灭）**——若成立=快速关线省全量判决烧批（TRIAL §2 快速回测律的正产出形态）；若任一门存活→升格门 alpha 分解（预承诺）而非直接入册；
4. **分段**：避损集中于 bear/chop 段（压力段与 bear 丛聚）；D6 vs carry 族=结构性近零预期（§1）；
5. **诚实注记**：本门真正的盈利史（2013-06 型钱荒）在 IS 窗——若 L1 判负主因=entries 薄，机制未证伪仅 OOS 乏证据，如实分类禁粉饰为「机制无效」。

## §6 产物

- script：`scripts/t101_v4_a7_prescreen.py`（t101_v4_a2_prescreen.py 模板+lesson-112 账本嵌入）；
- results JSON：`results/t101_v4_a7_prescreen.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+trials_ledger）；CSV：`results/t101_v4_a7_prescreen.csv`；
- 本件 §7/§8 回填；gate_attrition.bm-a.json 追加一行（第 72 条·entries 列表名 r248 律）。

## §7 跑后实证【待回填】

## §8 批后复盘【待回填】
