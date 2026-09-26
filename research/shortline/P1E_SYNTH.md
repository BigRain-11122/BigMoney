# P1E_SYNTH 预注册：zoo 幸存双员联合合成（zoo_pair_2 = zoo85_stv + zoo92_coin_team，日频 IC 层）· 跑前写死

> 机器/车道：**bm-b 循环轮**（dept:研究）· r229 认领，F-04 声明=`fleet/inbox/MSG-20260926-0644-bm-b.md`（本 commit 锁）。
> 令链：O-1819（队列永不空·advisory）→ T-64 slice-5 判定消费位 → P1E_ZOO_BEHAVIOR_IC.md（r219 冻结/r226 finalize·§8 处置「stv+coin_team 入合成素材货架（+2）·联合合成批消费前必查近邻相关·合成批另开预注册，认领制·禁单独成策略」）→ P1E_NEIGHBOR_CORR_CHECK.md（r227 冻结/r228 收割 verdict=**pass**·max|corr|=0.4829<0.7·§5 PASS 面授予独立列资格且**本检零授权**）→ r228 state.next 指针①（开放池认领候选）。
> 范式：**PS2_SYNTH（K=2 强偶转正）+ XSTOCK_SYNTH（股票域跨库小 K 合成）一脉**——因子层 IC 批：零引擎跑（引擎账本 N 不动）、IC 计数入因子账本、零策略级注册比较；recorded v1 常数门（P-1e/P-1d s9 同代口径：IC 海选型不触 G1'/G2 v2 引擎门）。
> **零授权声明（前置）**：邻检（P1E_NEIGHBOR_CORR_CHECK）按其 §5 只授「独立列资格」零授权——本批科学资格完全来自本预注册自身的跑前冻结；素材消费的正当性由本批判据承担，不由上游批件继承。

## §0 批件身份【必填·跑前】

- 批名/批号：**P1E_SYNTH**（P-1e 幸存者联合合成批）。格数 N_eff = **1 primary + 21 nullA + 50 nullB = 72**（+2 条件报告列：h5/h20 仅当 primary 过 V1 后补，snooping 折价标签）；引擎账本零动。
- 认领：F-04 先行=MSG-20260926-0644-bm-b（防双机在制窗撞车）；任务链=P-1e 母批 §8 处置条款+STRATEGY_LIBRARY §四 Zoo 行（SATISFIFIED booking「合成批另开预注册」注记）——本批非 P1 级新方向（P-1 系股票截面 IC 家族既有管线延续，O-1620 域授权范围），无需新署名任务单（PS2/XSTOCK 先例=MSG+prereg commit 即锁）。
- 部门归属：dept:研究（playbook §6 P-2 型合成线·股票域）。
- 算力预算（母批探针实测外推）：7 员面板构造合计 ~53s（p1e_probe.json timing）+ IC pass ~1.9s/道（P-1d 实测率）×72 道 ≈ 137s + nullB 50 组双面板生成+掩码+z+合成 ~4-7s/组 ≈ 200-350s → 单进程 **~8-12 min** → **>5min=后台池化**（runnable_pool 提交+autofill 续批，O-20260924-2100 执行面分离；禁轮内内联代跑）。批报告必带 audit 段（无 audit 段的结果件不入账本）。

## §1 α 机制段【必填·D6】

**四选一=行为偏差**＋一句话论证：母批 §1 机制段整族继承——凸显理论（BGS 2012）与知晓性条件修正（coin-team 路径动量）的股票截面联合读数；付费方=追极端收益者（stv 面）与低波动/低换手惯性持有者（coin_team 面），两腿同属反转族负号机制（母批共同负号 7/7 实证）；**联合合成的科学主张=跨凸显/知晓两亚机制去冗余后仍有增量 IR（XLIB 机制定案 #1「IR 增材料刻度」的直接检验）**——由行为偏差的持续存在支付。

**同族相关性准入检查【D6 必填·全部为已冻结读数，零新探针】**（双口径：截面 spearman 均值 F1 + ic10 序列 pearson F2）：

| 对 | 读数（冻结源） | 判定 |
|---|---|---|
| **primary 互对 stv↔coin_team** | F1 0.3648 / F2 0.4911（r219 探针 `results/shortline/p1e_probe.json`） | <0.7 → **双员独立列、零合并**；<0.5 亦低于 XSTOCK 聚类阈 → 联合不属同簇代表制而为真双列合成 |
| coin_team↔alpha191_070 | .2584/.3837（r228 邻检判定面） | <0.7 → 与 GTJA 反转簇机制近邻但独立 |
| coin_team↔alpha191_081 | .2028/.3459（同上） | <0.7 → 同上 |
| coin_team↔lhb_count_20 | .2302/**.4829**（同上·判定面 max） | <0.7 → 注意力族独立 |
| stv↔terrified | .3365/.4384（同上） | <0.7 → #85 家族内主腿/变体不合并 |
| stv↔lhb_count_20 | F2 **0.519**（同上·advisory 面） | **仅披露不拒收**（邻检 §4 条款）——合成批聚类信息面注记：若未来跨库批与 lhb_count_20 同池，须按 XSTOCK §1 聚类条款复验 |

- 判定面 max|corr|=**0.4829 < 0.7 → 素材准入**（规格=P1E_NEIGHBOR_CORR_CHECK.md·结果=results/shortline/p1e_neighbor_corr.json·r228 收割一次定读）。
- **本批为因子层合成，无策略级注册比较**（策略转化须另开预注册先过 D6 逐对名单+股票域成本模型，XSTOCK §1 逐字条款）；批内同族冗余由 nullA 全枚举承担（见 §3）。

## §2 数据与面板【必填·跑前事实，全部继承母批冻结面】

- 宇宙/面板：**p1c_stock 缓存面板**（Money02/data/cache/p1c_stock，T=8792×N=5222，meta ok=5130；缓存零刷新=冻结面；选料面非可交易面：不施加 b_layer 掩码——母批/P-1c 同口径；幸存者消费时 B 层另算）。
- **evidence_cutoff=2026-09-22**（缓存构建落盘口径；cutoff 后新 bar（09-24 起）不回流本批）。结果 JSON 顶层必带 `science_gates.cutoff_meta('2026-09-22')` 字段（缺=C2 VIOLATION）。
- 换手率面=turnover_derived sidecar（r219 物化，TURNOVER_DERIVATION.md §4 冻结分板公式）；vwap=缓存字段（Stage-A 688 修正已内建）；pct_chg 不入批（母批 §2 同款，fwd_ret=close 口径）。
- IS=面板起点→2024-12-31（composite_ic.IS_END）；OOS=2025-01-01→cutoff（**样本外恒盲**）；**h10 主口径**（家族准绳），h5/h20=过门后报告列。
- 掩码（母批 §3 冻结类，逐员沿用）：terrified=M_close；stv/coin_team=M_close_tr；arc/vrc/src/krc=M_arc——掩码=tradability 同类真因子（P-1d 范式）。
- 数据完备门（不过门禁跑批）：①面板载入零读错（母批已证）②p1e_factors 构造器 selftest PASS（冻结构造器自带门）③runner 复现锚（§3 确定性锚，母批记录逐位复现）④A3 期数门 IS n≥500。**零新探针**：本批全部跑前输入读数已冻结于母批 §1/§7 与邻检件，禁重探禁改写。

## §3 方法学【必填·冻结】

- **主配方 primary=zoo_pair_2**：两员各按母批记录 IS IC 符号定向（**冻结常数：7/7 员负号→全员 orient=−1**，母批 §7 表：terrified −0.0526/stv −0.0467/coin_team −0.0750/arc −0.0477/vrc −0.0442/src −0.0047/krc −0.0184），逐日横截面 z 化（composite_ic 同款语义，min 5 只有效），**等权均值 min_valid=2**（K=2=min(3,K)，PS2 §2 同款）。
- 面板=7 员全池单一实现重算（`p1e_factors` 冻结构造器+母批 loaders 复用，零新构造逻辑）；IC=逐日横截面 spearman（`shortline_p1_ic._ic_series_fast`，先掩码后排名；**等价自检门 max|diff|≤1e-6 vs composite_ic.ic_series 批跑前置**）。
- **nullA（21 对全枚举·同偏同秤）**：母批 7 员池 C(7,2)=21 对全部同配方（各员自身掩码、定向、z、等权 min_valid=2）→ 21 个 IS |IC| 的 p95。**枚举优于抽样**（零抽样噪声）；primary 自身在 21 对之内=同偏同秤诚实（P-2/PS2 先例条款）。nullA 回答的问题=「母批判据选出的幸存对」是否有胜过「同池任意双员对」的选择边际。
- **nullB（50 组 K=2 白噪声·matched-null）**：draw i=0..49，两员噪声面板 seed=67200+2i / 67200+2i+1（**新基 'p1e_synth_null_b'=67200 本 commit 登记 SEED_REGISTRY**；带 67200..67299，registry+rg 全扫净空——rg 命中皆 results 件回测数字巧合，t34/wild_route 先例）；每员 M_close_tr 掩码（primary 掩码类）→ z → 按自身 IS IC 符号定向（P-2「定向即偏差」matched 处理）→ 等权 min_valid=2 → 50 个 IS |IC| p95。
- 账本：`science_gates.append_ledger('P1E_SYNTH', 72, file_name, evidence_cutoff='2026-09-22')`（dict schema 唯一，**prev 读点=链上 ledger 读现值**——XSTOCK 链上读数律，禁手抄）；因子账本 +72（+2 条件报告列）；引擎账本零动。
- 成本口径：IC 海选=零成本统计面（IC 过线≠可交易；T+1/冲击/涨停撮合=B 层/策略级转化批另算——P-1c §8 诚实条款照用）。
- **跑前勘误适用条款（r200 范式·零计算改动）**：p1e_factors docstring #93 符号笔误已于母批同 commit 勘误，本批继承冻结版零触碰。

## §4 判据【必填·recorded v1 常数（母批/P-1d s9 同代）】

- **V1**：|IS IC_h10(primary)| > max(0.02 地板, nullA_p95, nullB_p95)
- **V2**：|IS IC_IR| ≥ 0.30（真门）
- **V3**：OOS 同号 且 |OOS IC| ≥ 0.5×|IS IC|（留存≥50%）
- A3 期数门：IS 有效截面日 n_periods≥500。
- **PASS = V1∧V2∧V3∧A3 四门全过**（h10 唯一门控期限）；过 V1 后补 h5/h20 primary 报告列（+2 计数，snooping 折价标签，非门控）。
- 硬界设计三件套（D-20260925-01①）：本批=IC 统计面，max 硬界不适用（母批 §4 同款）；分布界（median/p95/null 带）随结果全量披露；TR_CLIP=0.99 换手尖峰守卫已冻结于构造器。
- **跑后禁调门槛禁换口径禁重跑**（一次定稿；工程修复重跑须双跑留痕如实用记）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

1. **复现锚全过**（同缓存同代码路径，母批 §7 记录 4 位小数逐位复现 within 5e-5）——高置信。
2. **primary IS |IC| ∈ [0.055, 0.080]**：两员 0.0467/0.0750 等权 z 均值基线 ≈0.061，互相关 F2 0.4911 的联合阻尼与截面分散化小幅修正（PS2/XSTOCK OOS 端增益模式参照）。
3. **nullA p95 ∈ [0.058, 0.095]**：强货架带风险直系——6/7 员 |IS IC|≥0.018、5/7≥0.044，coin_team 配 terrified/arc/vrc 类组合基线 (0.075+0.044~0.053)/2≈0.060-0.064；PS2 教训=K=2 带随强员密度升（K=6 0.0785→K=2 0.0957），21 对小池 p95≈次高对。
4. **nullB p95 ∈ [0.0008, 0.0030]**：母批 M_close_tr 单面板 p95 0.0018，K=2 均值再收敛。
5. **V2 IR ∈ [0.50, 0.80]**：成员 0.440/0.492+corr 0.49 分散化增益（XLIB IR 增主张的正面读数面）——**V2 预计不再是绑定约束，绑定约束移向 V1 vs 抬高的 nullA 带**（XSTOCK §5 同款预判结构）。
6. **V3 留存 ∈ [90%, 130%]**：成员 OOS 留存 120%/109% 同族同号。
7. **主判 PASS 概率 25-45%**：primary 须为 21 对 top-1 且对次高有余量（PS2 死于 rank 3/28 同形风险）；**若 FAIL 预计死于 V1**（货架效应）。
8. **极端日先验**（硬界三件套 (c)）：本批=IC 统计面无 max 硬界适用；2015-07 股灾+2016-01 熔断窗凸显阈值激活率高+换手尖峰（母批 §5 同款先验）→ 联合 IC 的 IS 分年段稳定性为跑时披露面（跑前未跑该面=如实记，禁跑后加门）。

## §6 产物

- `scripts/p1e_synth.py`（runner，**次轮 r230 交付**：gates/run/selftest 子命令；复用 p1e_ic_batch loaders+p1e_factors 冻结构造器+_ic_series_fast+PS2/XSTOCK 合成与 null 结构，零新科学逻辑；**跑前交付+自检过门才池化**——r198/wild_route「首发即崩」家族防线：夹具必镜像生产入参形态 r157/r221 律）；自检锚：①等价门 ≤1e-6 ②配方单调锚（合成 IC≈+1，1e-9）③**确定性锚 VOID 级**：7 员 IS/OOS IC 对母批 §7 记录复现 within 5e-5 ④nullA 21 对全有限 ⑤nullB 50 组全有限 ⑥z 语义对齐（zpop 继承 px 列，J7 对齐坑族第 4 例防线）。
- `results/shortline/p1e_synth.json`（判定表+null 带全量+audit 段+顶层 evidence_cutoff/cutoff_meta）+ `research/shortline/p1e_synth_results.csv`。
- 本文件 §7/§8 跑后回填。

## §7 跑后实证【跑前必为空——占位纪律：写数字即造假】

（收割轮一次定稿回填；工程修复重跑须双跑留痕如实记。）

（2026-09-26 07:47 批跑（runner pid17616·autofill 07:04:04 发射·elapsed 2586.9s）/ r231 bm-b 收割 finalize exit 0 · 一次定稿 · recorded v1 常数口径）

**主判 FAIL（V1 货架效应·§8 FAIL 分支收线）**：primary（zoo85_stv+zoo92_coin_team）IS IC **0.0700** / IR 0.552 / OOS 0.0816（同号·留存 **116.6%**）；V1 线=max(0.02, **nullA_p95 0.0762**, nullB_p95 0.0019)=**0.0762** → 0.0700<0.0762 差 0.0062 判负；**rank 5/21**（4 对在其上：terrified+coin_team 0.0822 / coin_team+vrc 0.0762 / terrified+vrc 0.0758 等——非 top-1·§5-7「PS2 rank 3/28 同形风险」应验）；V2 0.552≥0.30 ✓·V3 116.6%≥50% ✓·A3 IS n=8011≥500 ✓——**四门面 V1 单点死亡**（「若 FAIL 预计死于 V1」预判精确命中）。

**硬门全过**：等价门 max|diff|=2.22e-16 ✓；确定性锚 7 员 IS/OOS IC 对母批 §7 记录 Δ=0.0（within 5e-5·VOID 级）✓；nullA 21 对全有限（band 0.0153–0.0822）✓；nullB 50 组全有限（p95 0.0019 / p50 0.0009·matched M_close_tr 白噪声带·母批同量级）✓；结果件顶层 evidence_cutoff=2026-09-22 + science_gates.cutoff_meta 双键在位（C2 合法键）✓。

**FAIL 分支处置（§8 判前写死照执）**：「联合增益」主张收缩——批池顶部对（terrified+coin_team 0.0822）≠primary=**封闭线观察记录·禁直接采信**（PS2 §7 同款）；zoo 材料维持**单因子用法**（母批 §8 禁单独成策略条款照携）；未来消费面=跨库合成批素材库扩容（xstock 线·另开预注册）。

**预测对账（§5 八条）**：①复现锚全过=对 ②primary IS|IC| 0.0700∈[0.055,0.080]=对 ③nullA p95 0.0762∈[0.058,0.095]=对 ④nullB p95 0.0019∈[0.0008,0.0030]=对 ⑤V2 IR 0.552∈[0.50,0.80] 且绑定约束=V1 非 V2=对 ⑥V3 留存 116.6%∈[90%,130%]=对 ⑦FAIL 死于 V1·非 top-1=对（货架效应命中）⑧极端日 IS 分年段稳定性=未在本批跑面·如实记留档不翻案（母批同款）。**7 对 + 1 如实记**。

**账本**：184754 → 184826（**+72**·V1 fail→+0 条件报告列；引擎账本 N 零动·零引擎跑）；prev 读点=r231 修复后 canonical `ledger_head()`（窄面 `_chain_head_total` 183292 漏嵌套目录 results/wild_route/=链分叉 184754 真头·修复先于 finalize 落地·selftest 19 检全过含 2 新检）；损耗账 `results/gate_attrition.json` +1 行（kind=measurement·cells_ledger_delta=72·ledger_total_after=184826）。

**audit**：elapsed 2586.9s（§0 预算 8-12min 的 ~4x·如实披露——179 IC 道×T8792 面实测率高于探针外推）；workers=1 单进程（O-20260923-1738）·RAM 守卫未触发（可用 11.3GB>6GB 线）·finalize 0.5s；audit 段已入结果件。

## §8 批后复盘【SR-7T 跑后填】· 分支处置判前写死

- **PASS 分支**：zoo_pair_2 取得「策略级转化候补资格」注记——**零注册零授权**：策略级转化（G1' v2 共享库门+股票域成本模型 P4_BATCH2 先例+B 层 3517 宇宙过滤+T+1）**另开预注册**；STRATEGY_LIBRARY §四 Zoo 行收割轮更新（读数规格/结果双指针）。
- **FAIL 分支（货架效应收线）**：「联合增益」主张收缩为「批池任意双强员对即可达同等 IC」——zoo 材料保持**单因子用法**（母批 §8 禁单独成策略条款照携）；材料未来消费面=跨库合成批素材库扩容（xstock 线，另开预注册）；顶部对（若非 primary）=封闭线观察记录**禁直接采信**（PS2 §7 同款条款）。
- 预测对账（§5 八条逐条对/部分/错）+门禁链损耗账（`results/gate_attrition.json` 追加一行：kind=measurement，cells_ledger_delta=72/74，ledger_total_after=当批链上现值）+当批判线读数（V1 地板/nullA/nullB 三带数字）全量披露。
- 回执入轮报告+CODELY.md 行级追加（若注册新员——本批构造上零注册——则注册件带 evidence_cutoff+接线+smoke 锚定门复跑）。

## §9 工序排程（P-1e §9 范式）

1. **r229（本轮）**：本预注册冻结+F-04 MSG+SEED_REGISTRY 'p1e_synth_null_b'=67200 登记（本 commit）。
2. **次轮 r230**：runner 交付+selftest 全过→`results/runnable_pool.json` 池化提交（lane bm-b·lane_owner 戳 R31/r188 律）→autofill 续批（py 水位门）。
3. **收割轮**：finalize fail-closed（append_ledger 返回值必嵌 r217 律）+判定表+§7/§8 回填+STRATEGY_LIBRARY Zoo 行按分支更新+0 幸存=诚实收线。
