# G2_SLOT_MON_P2 预注册【§9 冻结窗·stage-2 注册级判决面：G2 矿供线月频翻译层 2 面短名单全量判决（core48 ETF 消费面·G2 线首个正发现的后继判面）】

> **FROZEN v1.0（2026-10-03 bm-a r648 冻结窗）**：本件 commit 冻结先于任何 P2 run（R99 律）；冻结窗探针 **PASS 6/6**（results/_r648bma_p2_probe.json·L1 短名单恒等 {old_032,best_016}·L2 vendor HEAD==a770825+roster freeze sha16 `7ce1e81d019eba3d` 恒等·L3 种子带 [20570000,20570060) 撞带扫描零命中·L4 core48 面板 48 csv 全覆盖截断线·L5 父批 IC 锚逐值在位·L6 双面 volume_price 类 BAN 继承零命中）；种子带 `g2_slot_mon_p2_nulls=20570000` 同冻结窗落锄（science_gates.SEED_REGISTRY·带 [20570000,20570060)·与 mon_p1 基座 20560000 净距 10000·撞带扫描零命中）。冻结后禁改 §0–§6 判据面；跑后只回填 §7/§8。**本批=r647 G2_SLOT_MON_P1 §8 链级裁定的直接后继**：census 提名 2/47（old_032 稳过+best_016 marginal），本批=对短名单做**注册级全判据链判决**（MON_P1 §4 提名线原文「stage-2 判面须独立 §9 冻结后按 science_gates.g1_prime_v2/g2_registration_v2 共享库全判据链走（判线禁手抄·缺输入=诚实拒收）」——本件即该 §9）。
>
> 众链承继：O-20260930-1132（G2 矿供规范化）→ G2_OVERLAP_CENSUS_P2（126 NEW-FACE 法位 §8 下片）→ 周频三批族位收口（OLD 0/41·STOCK 0/14·TAIL 0/71）→ 尾段合并普查收口（G2_SLOT_TAIL_P1 r644·全链 0/126）→ 月频低换手翻译分解（G2_SLOT_MON_P1 r647·**2/47 存活=G2 线首个正发现**：成本主杀答案 32/47 月频 x2 转正 vs 周频 0/126 全灭）→ **本件=短名单注册级判决**（判决≠注册：注册资格=g2_registration_v2 全过·判决面诚实三态）。
> 部门 dept:研究（G2 矿供线·judgment 面收口）；dept:工程（vendor 接线继承受 g2_slot_mon_p1 单源）；lane=单机短批 in-round 合法（O-2100 先例·census 同窗 20.2s 量级×2 面+60 null+族矩阵 CSCV·预算上限 300s）。
> 认领（O-04 先例）：开工声明双机在到窗互不可见防撞车——fleet/inbox/ **MSG-2026-10-04-0005**；任务票 **T-2026-10-03-164-P1**（bm-a 开票同轮认领·O-1730 即时律·fetch 实核 origin max=T-163 @23:5x）。

## §0 批件身份【必填·跑前】

- 批名/批号：**G2_SLOT_MON_P2**。类别=**stage-2 注册级判决面**（MON_P1 §4 冻结提名线的独立 §9 判面·2 面短名单全量判决）——本批**有判决宣称资格、有注册资格判定面、零纸盘资格宣称**（纸盘入册=hr.py 晋升管线按 g2 verdict 文件读取·本批不越权）；判决三态=judged-negative / eligible-for-registration（g2_registration_v2 全过）/ consumption-blocked（律 A 出场普查 >20% 或数据门败）。
- 判决面（2 cell-faces × 2 成本面）：**old_032**（old 族·volume_price 类·父批 IC +0.027954=月频 null p95 1.64×·x2 全窗 +13.29% vs EW48·beat 0.7667）+ **best_016**（tail 族·volume_price 类·父批 IC +0.017731·x2 +8.47%·beat 0.6667 marginal 提名）；成本面 x1=13.041bp/边主测量+**x2=26.082bp/边判决面**（REV-OSC 族 sleeve 先例口径·rev_osc_stock_p1 同律）。
- 批内行数：**N_rows=124**（2 面 blend 腿+60 null 袖+60 null 袖 IC 面+2 面族矩阵复算〔old 族 18 面+tail 族 27 面月频 x2 blend 矩阵=PBO CSCV 输入〕）；ledger 记账试验总数 N=**124**（BATCH_CELLS 申报面=2 judged cell-faces+60 nulls=62·DSR n_trials 用 g1_prime_v2 skill_line n_eff 派生·REV-OSC r281 先例 n_eff_override 口径；RETAIL_QUANT_TRACK 预算归属：<100 单批免归因线·62+62 矩阵复算如实入账）。
- 算力预算：实测预估 **60-180s 单进程**（2 面月频 blend≈父批 20.2s×2/47·60 null 袖≈父批 null 腿×3·族矩阵 45 面复算≈父批 leg ii 量级）；**预算上限 300s**（O-1901 ①-iii·超限合法停如实披露）；批报告必带 audit 段。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸（冻结窗已过）：`python Tools/banned_direction_gate.py --prereg research/G2_SLOT_MON_P2.md` → 退出 0=放行（fail-closed·冻结 commit 内回执）。
- 人工预读结论：**零命中预期**——双面=vendor 量价交互类横截面因子（成交额/成交量结构面），消费面=48 ETF 月频 Top-16 等权袖；禁向九方向无一涉及（本批无横截面动量/反转构造〔因子值非价格动量序〕、无单名择时、无 BAN-04 类构造、无水温前置、无个股确认前置、无市值/价格因子输入、无缓冲带、无风格延续）；BAN 类继承零命中（短名单双面均 volume_price 类·probe L6 实证）；本节不复述禁向词面（机器闸为准·r483 清洗律）。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·M02 双件门】

- **出场轴=②持有到底（ALWAYS-ON hold-through·月频排名轮换版）**：成员**只因月频横截面排序轮换离场**（再平衡日落出当月 Top-16=唯一出场·与父批 census 机件逐字同面），**无价格类出场**（无止盈/无止损/无衰减踢出/无亏损时限/无持有上限）。
- **执行载体=blend 近似腿（非 engine 判决路径）·如实降级披露**：本批判决面=REV-OSC 族 sleeve 先例口径（rev_osc_stock_p1 同族——sleeve 判决面走科学门库不走 engine 出场栈；FUND 族双通道逐键申报对 engine 路径批为法定件、对本 sleeve 面为**N/A 如实声明**：engine/ 零触碰·runner 断言零 engine import·出场=月频排名轮换唯一·构造性无缺省出场栈可泄漏）。律 A 出场原因普查等效腿：**runner 逐笔记录每次月度换仓出场原因=rank-rotation 唯一合法 reason**，任何非 rank-rotation 出场占比 >20%（CENSUS_BLOCK_SHARE=0.20 跑前写死）→ verdict=consumption-blocked——census 机件下该普查腿为构造性恒等断言（census 腿无第二出场路径），仍逐笔落盘以全判面同构。
- T+1 执行与成本模型：blend 腿 T+1 镜像（e=g+1）与 x1/x2 成本面=父批冻结机件恒等继承（census 近似腿·非 engine T+1 正典——注册后进入 paper 的执行面归 hr.py 晋升管线重测·本批不宣称）。

## §1 α 机制段【必填·D6·四选一】

- 机制勾选：**[x] 行为偏差（主）+ [x] 微观结构（辅）**——与三先例+父批同文继承（vendor 量价引擎横截面：成交额/成交量结构载荷知情资金趋向的可靠分信息·彩票偏好/叙事追逐面反向）。**本批不重新主张机制**（判的是父批提名面的注册资格——机制主张以 burn 读数检验不以此段宣称为准）。
- **数学化陈述【§1.2·D-20260930-41 必填】**：¥1,000,000 级账户在 48 ETF 面月频 Top-16 等权=容量无限、月频再平衡执行压力近零；不重跑机构结论（横截面量价因子有效性衰减=公开文献常识面引用）；例外三问=本账户独有约束成立（场内 ETF 直接持有·真实成本·月频持有 21 交易日视界）。
- **同族相关性准入检查【必填·D6·冻结】**：**入池前 probe 已核**（父批 §1 执行载体 d6_numeric.json——old_032 vs 在册六员 max|corr|=0.3532·best_016=0.3442〔父批 §7 实测·全对 <0.7〕）；**本批再核双面 vs 在册六员逐对落盘**（REG6 日收益序列·P2 §3 腿 iv）——**max|corr| ≥ 0.7 → 该面 verdict=judged-negative（并族拒收·非点火门=判决门）**；双面间互对如实披露（同引擎血缘预期高聚·两面判面独立非互斥）。
- M1 t 面【必填申报】：`science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面（逐面 x1 headline）；判据=`science_gates.m1_t_value_gate`（Harvey/Liu/Zhu 门槛 **t≥3.0**·claim_class=new_strategy）。
- M3 闭合族对号【必填】：family_key=**g2_slot_mon_p2_xs**（新键·science_gates.CLOSED_FAMILIES 在册键零命中=open 照跑；g2_slot_* 系全部为 census 判负族=与父批周频判负线同门不同面·互不沿用判决——本批判的是月频口径存活面）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/面板：**core48 在册白名单 48 员**（knowledge/panel_gate.INSERVICE_WHITELIST·sha16 `abf3d43b9ca13ea5`·RW-4 冻结）；固定四元组：`data/daily/<code>.csv`（code 含交易所前缀）·raw `pd.read_csv` 直读；窗自 2020-01-02；**evidence_cutoff=2026-09-22**（**与父批 MON_P1 同窗**——截断线由 read_csv 截断保证 D2 前向锁盒；探针事实（r648 leg4）：48 csv 全覆盖 ≥cutoff·union 尾 bar=2026-09-30〔面板已推进至国庆前末 bar·新 bar 不回流=截断线内排除·如实披露〕）。
- **vendor 引擎锚**（G-ANCHOR 同例）：toolstack/repos/ml-quant-trading·HEAD==`a770825f841504e41581f057b4d94160e6a50c2e`（r644/r647 探针恒等实证·probe L2 复验）；LEGACY_REGISTRY import·torch 2.11.0+cu128 **CPU 路**（GPU 不用）。
- **roster 冻结**：**2 烧面**（census 提名短名单·probe L1 恒等断言 {old_032, best_016}·族与类标签自父批原样继承〔old/tail 族·volume_price 类〕·BAN 继承零命中 probe L6）。
- **mask 定义**：六字段全 notna 且 volume>0 且 amount>0（+上市前行 mask）；vwap=amount/volume——与父批逐字同面。
- **族矩阵（PBO 输入面·冻结）**：old_032 面=old 族富集子池 18 面月频 x2 blend 全窗日收益矩阵；best_016 面=tail 族富集子池 27 面同构——**同族 PBO=CSCV 判面**（screening/pbo.cscv_pbo·g25_retro 同族矩阵先例·REV-OSC r281 全记录口径）；族矩阵面=P2 runner 从父批冻结 roster（sha16 `7ce1e81d019eba3d`）确定性重算（同窗同机件·父批 leg ii 镜像复算=确定性交叉核验腿）。
- 数据准备门（不过门跳越·fail-closed）：①48 员 csv 全在位全覆盖 ②vendor HEAD==装基 ③roster/短名单 sha 恒等 ④种子带 disjoint ⑤父批 IC 锚逐值在位（probe L5）。

## §3 方法学【必填·冻结·与 G2_SLOT_MON_P1 §3 同构继承+注册级判面增量】

- **面计算（冻结）**：每面 `LEGACY_REGISTRY[f](panel)` → [T,N] masked 因子张量（torch CPU·float32；vendor 算子语义零重写零重实现——vendor 单源 import 禁改 vendor 件）。
- **腿 (i) fwd-5d rank-IC**（继承+父批恒等交叉核验）：逐日横截面 Spearman vs 5 交易日前瞻收益；**重测 ic5_mean 必须与父批锚逐值恒等（容差 1e-6）**——漂移=机械故障 fail-closed（probe L5 锚：old_032=+0.027954·best_016=+0.017731）。
- **腿 (ii) 月频 Top-16 blend 袖（判决面）**：与父批逐字同构（g=每月首个交易日·e=g+1·Top-16 等权·换仓成本 sum|dw|×cost_side·x1/x2 双成本面）；统计面增量（注册级）：全窗 Sharpe（年化 √252）/全窗收益/maxDD/滚动 126td beat-rate（步长 21·T-22 镜像）/政体分段描述披露（510300 t22 3-way proxy·**描述面非硬门**——月频族 81 起点枚举密度下 12m per-start 政体分段计数不足 50 门阈=r633 G-SEG 密度错配教训先核不移植；分段计数+分段收益如实落盘·任一政体段负贡献如实披露）。
- **腿 (iii) null 对照（月频口径·注册级扩容）**：**60 same-mask 月频随机袖**（`rng([20570000, k])` 子流律·K=60·父批 K=20 的注册判面扩容——DSR/g1 判读 null 池加深）；null 带=月频随机选基的 ①|mean IC| 分布 ②x2 beat-rate/EW48 超额分布（双基准同父批口径）。
- **腿 (iv) D6 数值面**：双面 x1/x2 blend 日收益 vs **REG6 在册六员全部成员**日收益逐对 |corr| 落盘（判决门 ≥0.7=并族拒收）+双面互对披露。
- **腿 (v) 注册级判据链（本批核心增量·REV-OSC sleeve 先例口径）**：逐面（headline=x1 面）——
  - **G1' v2**：`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=62, pool="core48", n_trades, n_entries, null_pool=P2 null 池, passive_override=EW48 同窗 Sharpe)`（判线禁手抄·库内读 skill_line_v2+stationary-bootstrap CI+F6 双交易门）；
  - **x2 survival**：x2 面全窗 Sharpe > 0（x2 成本面生存·REV-OSC 同律）；
  - **M1**：`t_from_sharpe` → `m1_t_value_gate`（t≥3.0）；
  - **DSR**：`deflated_sharpe_ratio(returns, n_trials=g1["skill_line"]["n_eff"])`（REV-OSC r281 口径）；
  - **PBO**：同族矩阵 CSCV（old 族 18 面/tail 族 27 面·`screening/pbo.cscv_pbo` 全记录→pbo_verdict 带宽）；
  - **G2 注册资格**：`science_gates.g2_registration_v2(g1_pass, dsr, pbo)`（DSR≥0.95+PBO≤0.25·缺输入=诚实拒收）；
  - **面级 verdict 三态**：全过=**eligible-for-registration**（注册执行=hr.py 晋升管线月界面·本批只判不册）；任一判据败=judged-negative（如实落盘败项）；出场普查 >20% 或数据门败=consumption-blocked。
- **账本（冻结）**：finalize 步 `science_gates.append_ledger(batch_name="G2_SLOT_MON_P2", batch_trials=124, file_name="results/g2_slot_mon_p2/g2_slot_mon_p2_verdict.json", evidence_cutoff="2026-09-22")`（dict schema 唯一·禁手抄 prev）。
- **确定性**：批 JSON 零墙钟字段；selftest=双跑字节恒等（mini 管线·真面板）+短名单/cutoff/mask/种子带/成本单源/父批 IC 锚/月频时点计数/出场原因普查断言诸腿。

## §4 判据【必填·跑前写死，禁看结果调线】

- **面级判决线（冻结·全过才 eligible）**：①G1' v2 pass（g1_prime_v2 库判）；②x2 survival（x2 Sharpe>0）；③M1 t≥3.0；④DSR≥0.95（g2_registration_v2 内）；⑤同族 PBO≤0.25（g2_registration_v2 内）；⑥D6 vs 在册六员 max|corr|<0.7；⑦出场普查 rank-rotation 占比 ≥80%（=非 rank 出场 ≤20%）；⑧预算内完成（<300s·超限=合法停非判负）。
- **双面独立判决**：任一面判负不影响另一面（cell 级判决·REV-OSC 族 cell 先例）；**old_032=primary headline**（父批稳过面）·best_016=secondary（marginal 提名·预期判负风险高如实预注册）。
- **零翻案律**：本批判负=月频翻译层该面注册资格判负（G2 线该 cell 闭环）；本批不构成父批周频三批判负线的翻案面（口径独立·同 MON_P1 §4）。
- **判线 v2 当批读数回执**：本批=注册级判面·g1_prime_v2/g2_registration_v2 消费面如实落盘（各门读数入结果 JSON gates 段·禁手抄）。
- **硬界设计三件套【D-20260925-01①】**：数据腐坏检测=面板六字段 notna 计数+日期单调+重叠零容忍（门=冻结窗探针复验）；max 硬界=批预算 300s；极端日先验入 §5(c)。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- (a) **old_032 面判面**：G1'/M1/DSR 预期**过线边缘**（父批 x1 全窗 +15.49% 年化·Sharpe 预期 ~0.7-1.0 区间·t 值依赖有效月 ~79-81 个再平衡——t≥3.0 门槛预期边缘过或边缘败·honest 预注册不押方向）；x2 survival 预期过（x2 +13.29% 年化>0）；PBO old 族 18 面矩阵预期 **0.30-0.60**（族内月频面同源高聚·PBO≤0.25 门槛预期**难达**=最可能判负项——若过=真异质面强证据）。
- (b) **best_016 面判面**：预期**判负**（marginal 提名·父批 x2 +8.47% 年化·Sharpe 预期 ~0.4-0.7·t≥3.0 大概率败·PBO tail 族 27 面矩阵同聚预期 0.35-0.65 判负——如实预注册）。
- (c) **极端日先验**：2024-09-30/10-08 级单日 ±8-10%（涨停簇日·mask 无涨跌停价列不 mask·如实披露）+2020-02-03 疫情首日；月频腿簇日暴露 ~81 次换仓·描述披露非判据。
- (d) **null 带**：月频 null x2 beat-rate 均值预期 0.00-0.30（K=60 比父批 K=20 估计更稳·带中心与父批 §7 实测一致 ~0.1-0.2 附近·漂移大=袖构造异常先查）。
- (e) **D6 双面互对**：old_032 vs best_016 |corr| 预期 **≥0.7**（同引擎血缘量价交互类·同月频时点面同 Top-16 构造=高聚先验·如实披露非判项〔判项=vs 在册六员〕）。
- (f) **族矩阵复算确定性**：45 面族矩阵复算 blend 收益 vs 父批 leg ii 实测预期逐值恒等（容差 1e-9·同机件同窗——漂移=机械故障 fail-closed）。

## §6 产物

- runner=`scripts/g2_slot_mon_p2.py`（**待建·冻结后**；结构=scripts/g2_slot_mon_p1.py 同构适配：roster=2 面短名单·nulls K=60·注册级判据链腿 v〔g1_prime_v2/m1/DSR/PBO-CSCV/g2_registration_v2〕·族矩阵复算 45 面·selftest 子命令=短名单/cutoff/种子带/父批 IC 锚/成本单源/确定性双跑字节恒等/出场原因普查断言诸腿）。
- probe=`results/_r648bma_p2_probe.py`（已建已跑·**PASS 6/6**·冻结窗先例事实件）。
- 结果：`results/g2_slot_mon_p2/g2_slot_mon_p2_verdict.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+gates 段〔g1_prime_v2/x2/m1/dsr/pbo/g2 逐门读数〕+face_verdicts+exit_census+d6_numeric.json+ic_by_face.csv+族矩阵矩阵落盘）。
- 本文件 §7/§8 回填；轮报告回执。

## §7 跑后实证【2026-10-04 bm-a r649 回填·判据面零改动】

- **判决：双面 judged-negative（G2 月频翻译层注册资格判负·零翻案律关线）**。failed_lines 两面同构={g1_prime_v2, m1_t_value, dsr}；其余判据线全过：x2 生存（old_032 0.6499 / best_016 0.4108 均>0）·同族 PBO（old 0.1857 / tail 0.1286 均≤0.25）·出场普查（846/332 出场 100% rank-rotation·other_share=0.0·构造性断言与逐笔日志双证）·D6 vs 在册六员（0.3537/0.3497 均<0.7）。
- **三败线读数（headline=x1）**：G1' v2 线=**0.8208**（null_term 主导：60 袖月频随机池 mu=0.3094+sigma=0.099×√(2·ln 622,651)；passive_term=0.5006 被覆盖）——old_032 Sharpe 0.76<0.8208（距线 0.06）·best_016 0.4527<0.8208；CI 下界两面均非正；M1 t=1.911/1.151（hurdle 3.0）；DSR=0.002393/0.000147（n_trials=622,651=全局账本口径）。
- **§5 预测对账（零移线）**：(a) PBO 预测 0.30-0.60 **未中**（实测 0.1857/0.1286——族矩阵聚类度低于预期，如实记录预测偏差；老_032 G1'/M1/DSR「边缘」预测=实测明确败）；(b) best_016 判负预测**命中**；(d) null x2 beat-rate 均值 0.2569∈预测带 [0.00,0.30] **命中**；(e) 双面互对 |corr|=0.8849/0.8845≥0.7 **命中**（同引擎血缘高聚先验）；(f) 45 面族矩阵复算 vs 父批 leg ii **45/45 恒等零漂移**（4dp 舍入后 1e-9）。
- **null 带（K=60 扩容）**：|mean IC| p95=0.014715（父批 K=20=0.017049——池加深 p95 下移，月频判读线更稳）；极端日实证=2024-09-30 +12.43%/2024-10-08 +11.20%（预测 §5(c) 涨停簇日精确命中）+2024-09-27 +7.94%。
- **政体分段（描述面）**：old_032 bull/chop/bear 三段全胜 EW48（na 段 0.1541 vs 0.1888 如实负披露）；best_016 bull 段负（0.5728 vs 0.6913）余段胜——描述披露非判项。
- **执行面**：elapsed=46.3s（预算帽 300s 内）；selftest 10/10（含双跑字节恒等+零 engine 载体断言）；禁向闸 ADMIT（r648 冻结窗+本窗双回执）；账本 622,589→**622,713**（+124 冻结申报面）；产物=verdict JSON+d6_numeric+ic_by_face.csv+族矩阵双 CSV（results/g2_slot_mon_p2/）。

## §8 批后复盘【s7-T】

- **新方法判定：有 1 条→方法论资产卡已 append**（knowledge/METHODOLOGY_ASSETS.md）——月频口径 null 池自校准读数（随机袖 Sharpe mu≈0.31=宇宙窗内漂移面，月频批判线必须用同口径 null 池而非全局 collector；K=20→60 深化使 |IC| p95 下移 0.0170→0.0147）+父批矩阵复算恒等 tripwire 范式（同机件同窗重算 4dp 恒等断言=机械故障 fail-closed 闸，45/45 实证）。
- **新宝藏判定：无**（负判决面；无新正发现入册——TREASURE_REGISTRY 本批零 append，判定行留本件）。
- **老问题关线：G2 月频翻译层真关线**——周频三批 0/126（OLD/STOCK/TAIL）→月频翻译 2/47 提名→注册级 **0/2**：G2 矿供线全链判决闭环（零翻案律；月频翻译层无注册资格面）。判负结构=三败线全部由全局账本 n_eff=622,651 多重检验校正驱动（线 0.8208/DSR 门槛结构性高），非面本身月频口径不健康（x2 生存/PBO/出场/D6 四面全过）。
- **与 O-1058 注册改革的关系**：O-20260930-1058 已立法认知「DSR≥0.95 全局账本执行口径结构性不可达」并以批内 BH FDR 替代（W14+ REEVAL 面生效）；本批判据面冻结于 g2_registration_v2（W13 前波次保持冻结判据律）→按冻结判据执行负判决，非判据错配申诉（零翻案双锁）。G2 线后继如再开新判面（如再翻译层），须新 §9 冻结+按当值判据库。
