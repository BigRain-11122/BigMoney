# QUEUE_BANDIT 预注册：批队列老虎机排程器 v1（UCB1 over gate_attrition，L1 确定性决策支持件）

- **批号**：QUEUE_BANDIT（batch-queue bandit scheduler v1）
- **车道**：bm-a 研究部（认领 MSG-20260924-0910，dept:研究）
- **日期**：2026-09-24 09:1x（跑前冻结）
- **性质**：**决策支持件非试验批**——零引擎跑、零因子 IC、零网络；ledger_trials_added=0（corr-watch R36「记录格复现+监控类零 N_eff 入账」先例）；不入试验账本、无 V1/V2/V3 门（无假设检验对象）；本件只冻结「算法+数据源+奖励口径」三样，防事后调参。
- **动机**（R61 RD-Agent digest 定位）：playbook §6 车道排队现状=定性人择；RD-Agent(Q) 的方向选择机械化 = 其框架里我方 OS 循环唯一真缺环。轻量移植=UCB1（Auer et al. 2002）多臂老虎机 over 批族（arm=批次家族车道）历史回报，服务 O-1819「队列永不清空」：队列见底时按 UCB1 序取下一车道起草预注册，替代「凭记忆挑」。

## §0 范围与边界（冻结）

1. **数据源单源**：`results/gate_attrition.json`（science_audit C4 损耗账，2026-09-24 03:03 首建，s7-T 批后复盘必填）——**不含**台账建账前的历史批次（P-4 批二/G2_FOLK/P-A/P-1c 等约 30 批均在 CODELY/轮账本但不在 C4 台账）。**诚实限制**：v1 有效拉取数=台账条目数（首跑 6），未试臂=纯探索序；价值随 s7-T 纪律自然累积。台账前历史回填=v2 候选（须逐批转录核验，本批不做）。
2. **advisory-only**：排程器输出=车道排序+候选登记，**不自动发起任何批**；一切批照旧走预注册+认领；P1 署名门（现金腿/日线双腿门票/Optuna/负面事件库/期货扩容/regime enforce）与 GM/CEO 重审项（REGIME_GUARD v3 拧法）**只标记不越权**。
3. **测量批处理**：P-5/P-5B/corr-watch/science_audit 类纯审计测量不占臂位（非车道候选）；但 EW6/IV6 类「组合验证测量」是真实车道产出（validated=true），按所属臂计拉取。
4. 零改任何在制面：不碰 STRATEGY_LIBRARY 判定、不碰账本、不碰门禁。

## §1 臂分类学（arm taxonomy，冻结）

臂=批次家族车道（按入场/构造 DNA 归族，与动物园/STRATEGY_LIBRARY 口径对齐）：

| arm | 族义 | 台账内已有拉取 |
|---|---|---|
| portfolio-construction | 组合构建/风险预算/相关性监控 | EW6, IV6 |
| synthesis-crosslib | 因子跨库小 K 合成 | XSTOCK_SYNTH（PASS 收线 r114，账本 60074） |
| patterns-confirmation | K 线形态/民间确认构造 | （G2_FOLK 等先于台账） |
| event-attention-factors | LHB/大宗/两融/热度/资金流事件注意力因子批 | （P-A/P-1d 先于台账） |
| trend-timeseries | 趋势/动量/状态族 | （NSP1/G2_NSP1 先于台账） |
| stock-pool-tilt | 股票池 B 层长多倾斜/因子→策略转化 | P4_EXT_TILT |
| futures-cta | 期货 CTA | CTA_P1, CTA_P2_NOAU |
| pairs-cointegration | 配对协整 | p4-pairs |
| low-freq-asset | 低频低成本品种族 | （LFC 先于台账） |
| regime-defense | 行情防线校准 | （T-05 先于台账） |

- **批名→臂映射（冻结 dict）**：EW6-portfolio-validation→portfolio-construction；IV6-portfolio-riskbudget→portfolio-construction；p4-pairs→pairs-cointegration；P4_EXT_TILT→stock-pool-tilt；CTA_P1→futures-cta；CTA_P2_NOAU→futures-cta。**未知批名→unmapped 桶**（输出警告，不算臂不排序；新臂命名=预注册修订，禁静默自扩）。

## §2 奖励口径（rubric，冻结）

- **r=1.0**：批产出≥1 个耐久正结果——交易员注册 / 组合 validated=true / 因子 V1∧V2∧V3 全过 / G1'-v2 过线员≥1；
- **r=0.5**：批产出仅 Tier-2 证据（G1' 候选/观察名单/袖珍池，未过下游门）；
- **r=0.0**：全灭/eliminated/validated=false；
- 实现按 gates 字段机械判：`validated==true` 或 `g1_passers≥1` 或 `survivors_g1_prime_v2≥1` → 1.0；`eliminated≥1 且无上述` → 0.0；其余（缺字段）→ 按 eliminated==0 且无正结果 → 0.0 并在输出披露字段缺失。**禁人工读数裁量**：判据必须在代码里可复算。
- 奖励按「批」计不按「员」计（一臂一拉取=一批；一批量级差异由 cells_ledger_delta 在输出披露但不入奖励——防大格批主导）。

## §3 UCB1 算法（冻结）

- `score(a) = Q(a) + c·sqrt(ln N / n(a))`，`c=√2`（Auer 2002 原版常数），N=已映射拉取总数，Q=臂均值奖励，n=臂拉取数；
- **n=0 臂=UCB=+∞ → 探索优先**（忠实 UCB1 语义：未试臂排最前）；输出层给两个序：`ucb1_policy_order`（未试臂在前、试过臂按 score 降序）与 `exploit_ranking`（仅试过臂按 score）；
- 平手 tiebreak=§1 表序（冻结，禁跑后换序）；
- 输出逐臂：n_pulls/mean_reward/ucb1_score/status（untried/exploit）/last_batch/ts。

## §4 候选登记（candidate registry，冻结状态位）

每臂挂具体候选批 + 状态位：`open`（可认领）/ `gated-P1`（须署名）/ `claimed`（他机在飞）/ `closed`（已收线）/ `blocked-source`（源阻断）/ `pending-GM/CEO`（重审中）。首跑登记（跑前写死）：

- portfolio-construction：open=（FL 前向窗口=2026-12 自然到期件、月度 corr-watch W3=10-01 例行）；gated-P1=现金腿（exit-to-asset 引擎特性+逆回购停泊）。
- synthesis-crosslib：**closed=XSTOCK_SYNTH（PASS 收线 r109 跑/r114 回填：IS IC 0.1078/IR 1.03/OOS 留存 0.895，账本 60074）**；臂下次素材按 SS8 多重性条款（gdhs 季频解冻或新库）另开预注册。
- patterns-confirmation：closed（A 层穷尽 R42；振荡/背离双判定律）。
- event-attention-factors：**closed=Alpha158 真缺口 7 族 B 类批（bm-b r121 finalize：一次试验 0/5 主格 FAIL，prereg §0 多重性律收线；账本 +65=60547；V1 0.02 地板杀 4/5+V2 0.30 墙杀 5/5=IS 量级主死因；复活须新预注册+新机制论证）**、open=资金流 mf_main_net_5/10/20 前向采集器+短窗 IC 参照批（R58·120d 源顶披露条款·面板 source-blocked 中）；blocked-source=P-B 板块热度（clist 腿阻断 ~13h+）。
- trend-timeseries：closed（NSP1/G2_NSP1/CTA 三判；复活须另开预注册+期货扩容=P1）。
- stock-pool-tilt：closed（P4_BATCH2 0/19+P4_EXT_TILT 0/5 摩擦墙判定律）。
- futures-cta：closed（CTA_P1/NOAU 双判；降杠杆变体/分合约 roll 平移=另开预注册）。
- pairs-cointegration：closed（P4_PAIRS；双腿对冲/日内粒度=P1）。
- low-freq-asset：closed（LFC）。
- regime-defense：pending-GM/CEO（v1/v2 校准双 FAIL 停线条款，证据包在案）。
- 工程类候选（不占臂，单列）：J13 v2 盲测资格预检（工程部·须预注册）、Optuna（gated-P1）、负面事件库消费（gated-P1）、日线双腿门票（gated-P1）。

## §5 产物与验证

- `scripts/bandit_queue.py`（`run`/`selftest` 两子命令）；`results/bandit_queue.json`：顶层 `evidence_cutoff`（=science_gates.cutoff_meta 字符串值，C2 合法键；输入台账批件截止≤2026-09-23）+ arms 排序 + candidates 登记 + unmapped 警告 + audit 段（`ledger_trials_added: 0`）。
- selftest（离线、合成台账，禁读活数据）：①奖励 rubric 四分支（1.0/0.5/0.0/缺字段披露）；②UCB1 数学单点复算（手工算值比对）；③未试臂探索优先序；④真实批名映射 6/6；⑤未知批名→unmapped 不崩；⑥tiebreak 表序；⑦evidence_cutoff 顶层键存在且为字符串；⑧候选状态位枚举合法。全过=门。
- 首跑判据：run exit 0、JSON 良构、臂覆盖台账 6 拉取无 unmapped、portfolio-construction exploit_ranking 居首（Q=1.0 数学必然）。

## §6 跑前预测（写死于跑前）

1. 6 拉取全映射零 unmapped（映射表按台账批名逐一写死）；
2. exploit_ranking 首位=portfolio-construction（Q=1.0/n=2，唯一正奖励臂）；
3. 未试臂=6 个（synthesis-crosslib/patterns-confirmation/event-attention-factors/trend-timeseries/low-freq-asset/regime-defense；§1 表 10 臂−4 试过臂 portfolio/pairs/stock-pool-tilt/futures-cta），UCB1 policy 序=6 未试臂全部先于任何试过臂；
4. Q=0 试过臂 score：pairs/stock-pool-tilt（n=1）≈√2·sqrt(ln6/1)≈1.34>futures-cta（n=2）≈0.95>portfolio（2.34 首位不变）；
5. candidates 登记与 §4 逐行一致。

## §7 跑后实证（2026-09-24 09:11 首跑，run exit 0 / selftest 8/8 PASS）

- 拉取映射：6/6 全映射，unmapped=0（预测 1 ✓）；
- exploit_ranking：**portfolio-construction Q=1.00/n=2/UCB1=2.3386 居首**（预测 2 ✓）；
- 未试臂 6 个探索优先序（预测 3 ✓）：synthesis-crosslib→patterns-confirmation→event-attention-factors→trend-timeseries→low-freq-asset→regime-defense，全部先于试过臂；
- 试过臂 score 实测：stock-pool-tilt/pairs（n=1）=1.8930（表序 tiebreak：stock-pool-tilt 先）> futures-cta（n=2）=1.3386——**预测 4=部分对**：序（n=1>n=2、portfolio 首位）全对，但手算值漏乘 c=√2（预测写 1.34/0.95，正确值 1.893/1.339；1.34 实为 sqrt(ln6) 的中间量误当终值），**手算 UCB1 对照必须带 c 因子全程**（坑入 §8）；
- 候选登记与 §4 逐行一致（预测 5 ✓）；evidence_cutoff='2026-09-23' 顶层字符串键在位（C2 合同 ✓）。

## §8 批后复盘（s7-T：决策支持件零 N_eff，损耗账不追加行）

- 预测对账：4 对 + 1 部分对（预测 4 手算值误差）+ 0 错——本件无门禁翻案权（无 V1/V2/V3），唯一硬判据=selftest 8/8+首跑三判据全过（已过）；
- **首读数定案**：v1 排程器落地即读数=「组合车道是台账期唯一正奖励臂（Q=1.0），UCB1 忠实语义下 6 未试臂探索优先、portfolio 其次」——即队列见底时按 explore 序取未试臂起草预注册、portfolio 类例行件（corr-watch 月更）照常走；advisory-only 边界不变，P1/GM-CEO 门不越权；
- 价值随 s7-T 台账自然累积（台账 2026-09-24 03:03 首建，前置历史批不入账=已知限）；XSTOCK_SYNTH 落账后自动入 synthesis-crosslib 臂；
- **坑（手算对照类，泛化）**：预注册预测段里的手算数字必须完整走公式全程（c 因子勿中途丢），写中间量当终值=预测段污染（本件序未受影响纯属运气：各臂 c 同乘不改变序）——若未来换 arm-wise c 或加权 UCB，此类手算误差会翻序；
- 消费方：轮循环 S2 认领参考（队列见底时读 results/bandit_queue.json 取序）；显示接线归 bm-c 车道决策（本轮不接）。
