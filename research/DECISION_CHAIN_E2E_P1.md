# DECISION_CHAIN_E2E_P1 预注册（T-90 · CEO 直令 O-20260927-0758「决策链条最重要·先判温度偏好再派策略·然后去回测」·四臂全链端到端回测证）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> 血统=DECISION_CHAIN.md v1.0 五环链正典（环①温度计=REGIME_GUARD v3·环③路由=T34_EARLY_SIGNAL CONF/LADDER 冻结配置·环④席位=T-33 roster v1）＋T-22 虚拟时间点 harness 同构。**本批=CEO「然后去回测」的落点：整链 vs 单策略 vs 被动的机器验证。**

## §0 批件身份【跑前】

- 批名 / 批号：DECISION_CHAIN_E2E_P1（决策链四臂端到端回测批）。**批内格数（N_eff）=5,522**＝新增包络臂 2（B 单策略臂 + D 六员等权臂）× 2,761 起点（legacy 1,255 + deep 1,506）——包络格计数（T-34 §0 先例：包络/包络叠加格计账，成员曲线格反重复不计）。**A1/A2 臂=T34_EARLY_SIGNAL 已计已测面（5,522 格已在 T-34 账）**：本批逐字重派生（G-REPRO 位级复现门）不重计——反重复计数纪律（T-34 §0 dprobe 先例）；成员引擎曲线格=T-22 已计 16,566 格血统（Stage A 曲线面重派生，零重计）。扩容即买单：臂/起点集/窗口族任何扩容按新格数入账。
- 认领：T-2026-09-27-90 claimed bm-b r310（CEO 即时工单=认领与开动同轮·O-1730·本预注册冻结=开动交付物）；F-04 先行=MSG-20260927-0816-bm-b-decision-chain-e2e（fleet/inbox/ 防双机在制窗口声明）。
- 部门归属：dept:研究+策略（票面 owner=研究部 harness 复用 + 组合与资金部席位权重重放；本机 bm-b r310 执）。
- 算力预算：Stage A 成员曲线=**本地复用优先**（results/t34/curves_*.jsonl 机本地 checkpoint 在位且位级校验过→零重跑；缺件则 t22/t34 原语重派生 16,566 格 ≈ 80-110min @12 workers BelowNormal 分离批 R41）；Stage B 包络组合=纯向量化 <5min/臂。>10min 面一律分离后台入 results/runnable_pool.json，轮不内联代跑；批报告必带 audit 段（无 audit 段不入账本）。

## §1 α 机制段【D6——无机制段=批不受理】

- [x] **结构性行为机制（政体持续性下的条件部署）**：整链主张=市场政体呈持续性分段（bear/chop/bull 政体自相关），政体条件化部署（GREEN 集中进攻席位/ORANGE 震荡军分散/RED 现金避险）捕获分段持续性红利；**代价支付者=换防摩擦**（政体切换日整书换手×单边费率）与**假信号鞭打成本**（状态误报→错配段部署）——故「链值不值」必须实测（CEO「然后去回测」逐字）。环②偏好面=缺口诚实标注（v4 评估项另批预注册，本批路由只用环①温度计——DECISION_CHAIN.md §一 逐字）。
- D6 同族披露：本批**零新交易员函数**（成员=在册 6 员注册配置纯重放）；四臂共享同一成员书（A/B/D 臂间相关性=构造性，臂间对照为同书受控比较，成员级 corr 门已在册不重跑）；包络臂层面以**臂间日收益逐对 corr**（全窗）作披露列（A1-A2 构造性极高预期 >0.99、B-D 中高、A-D 路由分化面如实）。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：双轴逐字复用 T-34 §2 冻结面——legacy=core48 面板（evidence_cutoff=**2026-09-24**·跑前探针=面板末日 48 员一致）；deep=T-18 增长成员面板（2013-06-17 起·manifest PASS·cutoff=**2026-09-22**）；**binding cutoff=2026-09-22**（deep 面）；cutoff 后新 bar 锁定不回流本批；结果 JSON 顶层带 science_gates.cutoff_meta("2026-09-22")（缺字段=VIOLATION）。
- 数据完备门（不过即 VOID 中止零产数）：
  - **G-CENSUS**（r105 律）：冻结 cutoff 下重枚举起点集逐位等于 T-22 finalize 记录 {legacy: 1,255, deep: 1,506}（源=results/t22_virtual_timepoints.json 实读，禁手抄）；
  - **G-ANCHOR**：6 员锚定门全过（T-22 run 门同款）；
  - **G-V3**（两腿）：legacy 轴 v3 import-replay（live.paper.v3_state_series 血统·T-34 §2 同源）截断 2026-09-23 窗口状态计数逐位等于校准批记录 GREEN=664/YELLOW=772/ORANGE=35/RED=161（源=results/regime_calibration_v3.json state_counts 实读）；且 2026-09-24 单日 replay 态=results/regime_state.json asof 2026-09-24 态（ORANGE）实读对账（两源禁手抄，断言双源一致）；
  - **G-REPRO**（本批核心完整性门）：A1/A2 臂 12m beat-passive 率+最差起点 dd+换防均值必须**位级等于** T-34 verdict 冻结读数（legacy 0.4296/0.4659·deep 0.3942/0.4304·dd −0.1249/−0.1041·换防 48.3→52.74/17.66→23.63；源=results/t34_early_signal_verdict.json 实读）——不等即本批管线漂移 VOID；
  - **G-MANIFEST**：t18 manifest verdict==PASS 且 48 员（_load_axis_prices 内建断言）。
- 政体真值源诚实边界：legacy 轴=REGIME_GUARD v3 四态重放（真链环①）；deep 轴 v3 仅覆盖 2020+→**诚实降级 T-22 冻结 3-way proxy**（510300 vs MA200·T-34 §3 逐字先例·disclosed proxy 非第二真值源）——deep 轴链=「代理温度链」次级披露面，**主判读=legacy 轴**。

## §3 方法学【冻结】

- **四臂定义（全部冻结·零新搜索）**：
  - **A1=整链确认线路由臂**：T-34 CONF 臂逐字（v3 状态序列→军团路由映射冻结：GREEN→attack={COMPOSITE-CE-01}·YELLOW/ORANGE→chop={CE-02, DROUGHT, ENGULF, NEEDLE, VOLATILITY}·RED→defense=∅→100% 现金；T-33 roster v1 冻结分配）；
  - **A2=整链+半档梯臂**：T-34 LADDER 臂逐字（A1+C1 前置快线半档·MA20>MA60 连续 P=5 点火·非对称熄灭·attack=0.5 混合权重·T+1 因果·T34 §3 全参数零改动）——「半档梯 A/B 面」即 A2−A1（STYLE_CORPS §4.5 条款兑现）；
  - **B=最佳单一策略不换臂**：COMPOSITE-CE-01 全窗满仓单持（24m 双轴唯一过线员·票面钦定），引擎 T+1/成本同款，零路由零换仓（除成员自身信号进出）；
  - **C=被动基线**：T-22/T-34 同款同窗 EW buy&hold（起点日已上市成员等额·零再平衡）；
  - **D=六员等权不换臂**：在册 6 员 1/6 静态等权混合·全窗不路由（唯一再平衡=漂移回锚如实计费）。
- **席位空缺诚实标注（O-0758/DECISION_CHAIN 逐字）**：进攻军在册 0 员（STYLE_CORPS v1.1）——A1/A2 的 GREEN 段 attack 席位=T-33 roster v1 的 CE-01 单席冻结重放＋**席位空缺旗**（现役进攻军 0 员的当值事实与本批历史重放席位的分歧如实入 §7 披露行）；进攻军入册后全链完整版复跑=队列面（票面 honest boundary 逐字）。
- **包络构造（T-34 §3 逐字复用·零重实现）**：军种日收益=成员引擎曲线日收益 EW；env_ret(t)=Σ_c w_c(t)·r_c(t) − rebalance_cost(t)；rebalance_cost=单边费率 × Σ_c|w_c(t)−w_c(t−1)|，单边费率=science_gates.COST_X2_RATE/2（运行时派生禁手抄）；T 收盘决策→T+1 开盘生效（shift(1) 赋权·无未来数据）；起点日初始建仓不计费（同向保守诚实让分）。
- **窗口族**：{6m=126, 12m=252, 24m=504}，每起点 24m 一段切 6m/12m 片（P-5 切片法）；**主判窗=12m**（T-34 J1 同窗·换防摩擦显性化窗）；partial 窗如实标记，主读=完整窗子集。
- **政体分段（披露维度·非门）**：T-22 §3 冻结 3-way proxy（bear/chop/bull+na）逐字——全臂×段 beat 率与臂间对照单列披露（供 MARKET_STAGE_TABLE.md 行级消费与断环定位）。
- **null 对照**：对照=臂间受控比较（A1 vs B/D）+被动基线 C（A/B 设计固有对照，T-34 §3 先例无随机 null）；bootstrap：beat 率 95% CI=二项 bootstrap B=2000，seed 基=**20260929**（t34 族 one-step：t34=20260928；runner 跑前 rg 全 repo 零命中证+登记 science_gates.SEED_REGISTRY 再跑，顺序律）。
- **成本口径**：成员曲线=V1 legacy 引擎面 base（13bp 系·T-22/T-34 同源）；包络再平衡=上述单边率；×2 生存面不入本批（x2 面另批·T-34 §3 先例）。
- **账本**：finalize 步 science_gates.append_ledger(batch_name="DECISION_CHAIN_E2E_P1", batch_trials=实际包络格数 5,522, file_name, evidence_cutoff="2026-09-22")——禁手抄 prev。

## §4 判据【跑前写死·禁看结果调线·全部跑前冻结】

- **J-CHAIN（主判·legacy 轴 12m 完整窗）——「不能单策略打所有市场」机器验证**：
  - J-C1（链 vs 最佳单体）：A1 vs B beat 率 95% bootstrap CI **下界 > 0.50**；
  - J-C2（链 vs 静态等权=路由价值隔离）：A1 vs D beat 率 CI 下界 > 0.50；
  - J-C3（链 vs 被动）：A1 vs C beat 率 CI 下界 > 0.50（六员书基线能力面）；
  - J-C4（红线）：A1/A2/B/D 四臂最差起点 12m 回撤均 ≥ **−0.35**（P-5/T-22/T-34 冻结红线）；
  - **链赢判读=J-C1∧J-C2∧J-C3（CI 下界口径·点估计并行披露）∧J-C4**；任一不过=**链不赢诚实报+断环定位（§下方）**。J-C1 单过而 J-C2 不过=路由无增值面（链赢但赢在成员书非路由）——如实分读禁合并叙事。
- **J-LADDER（半档梯 A/B 面·STYLE_CORPS §4.5 条款兑现）**：J-L1=A2−A1 12m beat 提升 >0 且双轴同号（T-34 J1 同构复验）；J-L2=A2 最差起点 dd ≥ −0.35；PASS→ENABLED candidate 面维持（启用仍走 T-33 d3 spec 冻结+11-01 月界·本批零接线）；FAIL→诚实不用（O-2030 逐字）。
- **断环定位（链不赢时必产·四环量化表）**：①温度环=v3 序列 vs 3-way proxy 分段分歧率+分歧窗 A1 表现归因；②路由环=A1 vs D 逐段差（同书受控差=路由净效应）；③摩擦环=A1 换防次数×单边费率年化摩擦占毛收益份额+无摩擦反事实 A1'（零再平衡费面）对照差；④席位环=GREEN 段窗份额+GREEN 段 A1/A2 vs B 差（进攻席位空缺的机会成本面）。全环量化入 §7，禁叙事替代数字。
- **D7 四必报（每臂×轴×窗）**：OOS 笔数（窗内换防次数）/覆盖年数/独立政体窗数（分段桶数）/CI 宽度。25td 间隔子采样 beat 率=重叠窗稳健性披露列。
- 诚实边界：PROSPECT 22 员与进攻军新席不入本批（观察仓/未入册零部署）；环②偏好面缺口如实标注；本批零注册零 paper 接线零路由 spec 变更。

## §5 跑前预测【写死于跑前·≥3 条·含极端日先验】

1. **G-REPRO 位级复现**（确定性管线，置信最高）：A1/A2 全读数=t34 verdict 冻结值逐位（0.4296/0.4659/0.3942/0.4304·dd −0.1249/−0.1041·换防 48.3/52.74/17.66/23.63）。
2. **A1 vs D（路由价值）点估计 [0.00, +0.08]、CI 下界 [0.42, 0.55]**：legacy 窗 GREEN 664 日（40.7%）链集中进攻席 vs D 恒等权；RED 161 日链现金避险 vs D 满仓扛跌——方向先验正、幅度受 YELLOW→chop 保守路由稀释；**J-C2 是最可能不过线的判**（T-34 已证 CONF 臂 12m beat-passive 仅 0.4296=成员书 12m 基线弱，路由增量若 <2pp 即 CI 下界压线）。
3. **A1 vs B（vs CE-01 单体）点估计 [+0.02, +0.10]、CI 下界 [0.46, 0.56]**：B 全窗满仓扛 RED 段（CE-01 熊段 0.595 弱于现金 0.0 回撤面）；链 RED→现金避 161 日熊段=主增益源；GREEN 段 B=链 attack 席同员（席位重合→增益主要来自 RED 段）。
4. **A1 vs C（vs 被动）≈T-34 CONF 读数带 [0.40, 0.47]**（同一臂——C 对照在 T-34 已测，本批复现面）。
5. **摩擦环读数**：A1 换防均值 ~48 次/12m 窗（T-34 实测 48.3）×单边 ~13bp×换手率——年化摩擦占毛收益 [3%, 12%] 带内；无摩擦反事实差 [0.3pp, 1.5pp]/年。
6. **极端日先验（三件套(c)）**：窗内潜在极端微观结构日=2024-09-24/10-08（政策脉冲·单日大幅高开→GREEN/YELLOW 状态日翻转→链全书换手单点摩擦尖峰）、2025-04-07（外生缺口→RED 触发日）、2026-01-19（D-C 批实证极端溢价日）；影响路径=①状态翻转日换手费率尖峰入摩擦账（单日 rebalance_cost 可达平常日 10-50 倍）②dd 尾部（牛熊切换 12m 窗最差起点 dd 逼近红线面）③分段桶边界翻转——边缘窗如实入 na/边界披露禁调段定义迎合。判据面=整窗读数与 dd（非单点 max 检测线），极端日经整窗路径进入读数=机制内化无豁免路径。

## §6 产物

- script：scripts/decision_chain_e2e.py（run/status/selftest 子命令；Stage A/B import-face 复用 t34_early_signal+t22_virtual_timepoints 枚举/装载/锚门/包络原语，禁重写；selftest hermetic 离线夹具 r116 律+B7b 契约腿 r297 律——下游消费键集 ⊆ 构造键集断言）。
- 产物：results/decision_chain_e2e.json（顶层 evidence_cutoff+cutoff_meta+audit 段+四臂×双轴×窗全表+J-C1..C4/J-L1..L2 读数+断环四环量化表+corr 披露+D7 四字段）+ research/shortline/decision_chain_e2e_results.csv（小件入 git）+ 本文件 §7/§8 回填 + MARKET_STAGE_TABLE.md 行级刷新消费面。
- 下游：月度四件套「链条健康」节（当值态+换军事件+断环扫描+偏好面进度）消费本批基线；STYLE_CORPS §4.5 接线注维持（启用走 T-33 d3 另批）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（finalize 于收割轮回填：G 门读数+四臂全表+J 判读+断环表+预测对账+账本行）

## §8 批后复盘【必填·s7-T】

（一次定稿；预测对账；门禁链损耗账 results/gate_attrition.json 追加一行；回执入轮报告+CODELY.md 行级追加；链赢/链不赢断环定案呈 GM）
