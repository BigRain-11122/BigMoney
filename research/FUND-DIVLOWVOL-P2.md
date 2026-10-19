# FUND-DIVLOWVOL-P2 预注册【DRAFT-NOT-FROZEN·r1038 开批票】· 红利低波族复活批（盈利质量过滤强化+参数邻域扫描+出场轴优化）

> **状态=草案**：本件 r1038 开立（O-20261019-2230 CEO 直令同轮开动面）；**§2 探针四元组/完备门/D6 probe/种子注册/禁向闸=r1039 冻结窗跑齐后 commit 冻结**；冻结前禁烧；§7/§8 占位纪律（写数字即造假）。
> 模板=`research/PREREG_TEMPLATE.md`（T-02 6/7）；判据权威=`research/BACKTEST_SCIENCE.md` v2＋共享库 `scripts/science_gates.py`（禁手抄判线）。
> **CEO 判负线复活授权（O-20261019-2230-bm-b §二.1·三件律：本授权+新预注册+新证据）**：承 FUND-DIVLOWVOL-P1 判决（0.89 vs 基准 1.0025·DSR 0.675·results/fund_divlowvol_p1/fund_divlowvol_p1_results.json 在册），新证据三腿=①盈利质量过滤强化（eligibility np_ttm/np_annual+quality_faces 盈利质量面——P1 未用）②参数邻域扫描（Sobol/邻域格·判负面主判据邻域稳健性检验）③出场轴优化（出场轴显式门三选一显式声明·P1=②持有到底，P2 出场轴=r1039 冻结窗设计定稿）。防运气门不拆（CEO 令原文：技能线/DSR/PBO/种子登记/预注册冻结全照旧）。
> 血统：FUND-DIVLOWVOL-P1.md（股票横截面月频族·bm-b r610 冻结·N_eff 2,002 池烧）＋ CEO 研究导向律合规（红利低波=A 股原生主流风格打法·形式化非国外框架筛国内打法）。

## §0 批件身份【跑前·冻结窗定稿】
- 批名/批号：**FUND-DIVLOWVOL-P2**（批内格数 N_eff=冻结窗定稿：judged cells×成本 face＋K null 族——扩容即买单）。
- 认领（F-04 先行）：**本件=r1038 开批票**（O-20261019-2230 §二「bm-b/bm-c＝池单元领烧」）；冻结窗前补 fleet/inbox/ MSG 声明（r1039 首动作）；跑批开批执行票=冻结 commit 后按链式开票律另立。
- 部门归属：dept:策略（族规格）＋研究（judgment 面）。
- 算力预算：长活入池（runnable_pool·池单元领烧·O-20261019-2230 §二·workers_plan 冻结窗定稿·CEO 10% 余量律）。

## §0.5 禁开方向硬闸【冻结窗跑闸】
- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/FUND-DIVLOWVOL-P2.md`（rc0 放行·fail-closed）。
- **复活例外申报（O-20261019-2230 CEO 授权面）**：例外类型=**new_data**（盈利质量过滤面：eligibility.csv np_ttm/ttm_ok 11,647 行＋data/fund_history_export/quality_faces.parquet——P1 判负时未入判据面）＋**new_mechanism**（出场轴优化=原否证未覆盖的机制面：P1=纯持有到底出场，P2 显式出场轴设计+参数邻域扫描=原否证未检验的稳健性维度）。CEO 授权=O-20261019-2230-bm-b §二.1 原文在案。

## §1 α 机制段【D6·承 P1＋质量腿】
- 机制勾选：**风险溢价**（主·承 P1 verbatim 论证）＋**行为偏差**（辅·承 P1 verbatim）；**新增质量腿论证**：盈利质量过滤（TTM 净利为正且盈利质量面过线）剔除「高股息=价值陷阱」伪成员——红利 carry 的现金流确定性主张只在盈利可持续成员上成立，质量过滤=把「股息率排序」从「价值陷阱收集器」矫正为「现金流溢价收集器」——由 P2 burn 读数检验。
- 散户凭什么赢【M0.2】：承 P1 verbatim（制度/容量面：Top-N 等权月频·¥1M 账户容量无限）。
- 同族相关性准入【D6】：probe 冻结窗跑（headline 日收益 vs 在册成员+同批全格 max|corr|≤0.7 fail-closed；**姊妹族披露预置**：FUND-DIVLOWVOL-P1 本族前代=0.8039 价值族 corr 前置披露面照 P1 §1 注记纪律）。
- M1 t 面申报【必填】：`science_gates.t_from_sharpe` 派生＋`m1_t_value_gate`（t≥2.0）冻结窗接线。
- M3 闭合族对号：family_key=**fund_divlowvol_stock_xs**（P1 已入册=**在册闭合族**——本批=P2 复活批按「新证据增量」声明通道（O-20261025-1105）+CEO 复活授权面；delta 声明=①②③三腿，跑前写死）。

## §2 数据与面板【r1038 数据可达性审计实证（本窗已跑）＋冻结窗补齐】
**r1038 审计结论（results/_r1038bmb_stock_domain_audit.json 在案）：本地四面齐备·零 TRANSFER 硬依赖（p1c 对齐面除外·冻结窗裁定）**
| 面 | 路径 | r1038 实测 | 状态 |
|---|---|---|---|
| 分红事件 | `data/fund_history_export/div_events_faces.parquet` | 54,494 行/5,124 符号/1991-04-03→2026-10-23/mtime 2026-10-17（T-154 转移件 sha256 在册） | ✅ LOCAL |
| 盈利质量 | `data/fund_history_export/quality_faces.parquet` | 在位（r1038 实测存在；行数/字段=冻结窗探针补录） | ✅ LOCAL |
| 资格/质量过滤 | `data/fundamental/eligibility.csv` | 11,647 行·列面 code/name/np_annual/np_interim/np_ttm/ttm_ok/r1_loss/r2_st/eligible | ✅ LOCAL |
| 个股日线 | `data/astock_daily/per/`（T-87 采集器·bm-b 车道） | 面板 complete·cutoff≥2026-10-19（astock_daily_update_status 22:22 实测） | ✅ LOCAL（本地重建主路） |
| p1c_stock 冻结面板 | bm-a 宿主（T-139 冻结件） | **不在本地**——对齐需求=冻结窗裁定：本地重建（astock_daily per 面）主路 vs TRANSFER 对齐件 | ⚠️ 冻结窗裁定 |
- **数据锚面定义四元组【G-ANCHOR-FACE】**：每个数字探针锚冻结窗逐锚补齐（面路径+加载函数+起算窗+预热窗）；探针-锚同面断言 fail-closed。
- **evidence_cutoff（D2 前向锁定）**：冻结窗定稿（候选=2026-10-19 或 P1 同锚 2026-09-22——**新批新锚原则默认 2026-10-19**·cutoff_meta 必带）。
- 数据完备门：冻结窗跑（NaN/停牌/政体系列漂移对账/拆分断点普查=承 P1 §2 门族）。

## §3 方法学【冻结窗定稿·三腿规格预置】
- 信号（承 P1 月频横截面 Top-N 等权再平衡骨架）＋**腿①盈利质量过滤**：资格面=eligibility（eligible+ttm_ok+np_ttm>0）∩ quality_faces 过线（参数冻结窗写死）；**腿②参数邻域扫描**：主判格参数邻域网格（Top-N/波动窗/股息窗参数域·Sobol 或邻域格·计 N_eff 依扩容买单律）；**腿③出场轴**：出场轴显式门三选一（①策略自有出场②持有到底声明+runner 显式禁用引擎缺省出场栈③template_default 按设计测）——**本批出场轴选型=r1039 冻结窗定稿**（候选=P1 hold-through 对照+自有出场邻域）；缺省栈双通道逐键申报+出场原因普查第二件门（CENSUS_BLOCK_SHARE=0.20 承 P1 §0.6）。
- null 对照：K=冻结窗定稿（same-mask 随机段族·seed 带=科学种子带律·`seed_admit_gate` rc0 先行+SEED_REGISTRY 登记）。
- 成本口径：V2（ADV20 三层滑点+1%ADV 帽）×2 face 恒开；**CN-C7 往返成本 bp 申报**：股票面按 `knowledge/rules.py fee_schedule_for` 前缀路由（买边/卖边+印花税仅卖边 5bp+过户费双边 0.1bp·¥5 最低佣金临界名义 ¥20,000 档位必附）。
- 账本：finalize `science_gates.append_ledger`（dict schema 唯一）。

## §4 判据【冻结窗写死·共享库禁手抄】
- G1' v2=`science_gates.g1_prime_v2`（skill_line_v2 数据驱动·bootstrap CI 下界>0·F6 双口径）；G2=`science_gates.g2_registration_v2`（DSR≥0.95·家族 PBO≤0.25）；M1 t≥2.0；阶段×风格面（O-20261019-2230 §二.4 组合族批归其本批·本批=族级判决面）。
- 防运气门全保留（CEO 令原文「防运气门不拆」：技能线/DSR/PBO/种子登记/预注册冻结照旧）。

## §5 跑前预测【冻结窗写死·≥3 条+极端日先验】
（冻结窗定稿——占位纪律：写数字即造假）

## §6 产物
- runner：`scripts/fund_divlowvol_p2_backtest.py`（新·承 P1 runner 骨架 import 复用律）；结果件：`results/fund_divlowvol_p2/`（顶层 `science_gates.cutoff_meta` 必带）；本件 §7/§8 回填。

## §7 跑后实证【跑前占位】

## §8 批后复盘【跑前占位】
