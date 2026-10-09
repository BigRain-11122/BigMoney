# PARKING-P1 预注册（空仓停泊腿·三臂对照）· O-20261009-1105-bm-a §三派单 · dept:研究

> 权威：research/BACKTEST_SCIENCE.md v2＋BACKTEST_PLAN.md 三铁律＋COMPUTE_AUDIT.md；CEO 直令 O-20261009-1105（「不做期权，可转债可以作为空仓期的补充，国债也可以，你们自行科学决策设计」）。
> 本件=跑前冻结件：跑后只许回填 §7 占位节，禁改判据禁重跑（一次定稿）。

## §0 批件身份【必填·跑前】

- 批名/批号：**PARKING-P1**（空仓停泊腿三臂对照批）；**批内格数=24**（4 判 instrument × 6 duration 档，每格计入 N_eff，扩容即买单）。
- 认领：F-04 先行——fleet/inbox/MSG-2026-10-09-1205-bma-parking-p1-claim.md（本件冻结 commit 同窗）；任务引用=O-20261009-1105-bm-a §三 @bm-a 派单（due ≤10-14 12:00）。
- 部门归属：dept:研究（停泊域首批判决批；消费面=O-1105 §四 10-21 回访+10-31 月考停泊增益面）。
- 算力预算：纯面板数学（6 面板 read_csv+stint 切片+K200 null 抽样）——预估 **<3 min 单核**，不入池（<5min 短批豁免）；批报告必带 audit 段（无 audit 段的结果件不入账本）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/PARKING_P1_PREREG.md`（冻结 commit 前实跑，exit 0 放行；exit 1=不受理 fail-closed）。
- 预判：九方向登记表无「现金停泊/债券 carry」面（BANNED_DIRECTIONS 九族=趋势/因子类已证伪方向）——预期零命中；命中则按 BAN-__ 编号+new_data/new_mechanism 例外三问补写，未补=不受理。

## §1 α 机制段【必填·D6——无机制段=批不受理】

四选一：**[x] 风险溢价**——停泊工具在空仓窗内承接**久期/信用/票息风险溢价**（arm A=国债久期溢价+票息；arm B=转债信用溢价+股性期权费+下修博弈补偿），由**债券发行人票息与转债发行人权益稀释**付出代价；空仓现金躺平=零承接=零溢价，承接与不承接的差=停泊 pickup 的机制来源。

**散户凭什么赢【§1.2·必填】**：**制度**（五选）——交易所账户零门槛停泊通道（国债/转债/货币 ETF 100 股手起、T+0 资金可用性），¥1M 体量对面板日成交 ¥31-266 亿=零市场冲击；本批主张**不是对机构的信息优势**，是「自家空仓现金 vs 自家停泊」的**自比收益**（无外部对手方要求）；涉机构已验证结论（现金管理/债券 carry=常识面）——RETAIL_QUANT_TRACK §三引用面：本账户独有约束=空仓窗由主策略出场结构决定（机构无此约束）、本市场未验证=散户可投 ETF 形态的 as-traded 面测量、样本外新数据=无新主张；三问内答=引用不自跑。

**同族相关性准入检查【必填·D6】**：runner 批内计算 4 判 instrument 日收益序列 vs **在册 6 员**（COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-CE-01、VOLATILITY-CE-01）＋同批全部格＋K200 null 的 `max|corr|`（日收益口径，sleeve-tag 先例）：`max|corr| ≥ 0.7 → 拒收`（诚实披露数值；新机制主张另开预注册）。
- **argmax 预期＝无**（跨资产类新域；利率政体共因子为唯一相通面——arm A/B 与在册股票域 6 员的相关预期 <0.3；511380 转债股性面与股票域共因子最高、预测带见 §5.6）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- **宇宙/池（声明口径）**：6 员停泊面板，核名全过（data/basic/etf_list.csv 权威名）：
  - **arm A 国债臂**：511010 国债ETF国泰 / 511090 30年国债ETF鹏扬 / 511260 十年国债ETF国泰
  - **arm B 可转债臂**：511380 可转债ETF博时（核名过=启用；ETF 形态）
  - **arm C 基线**：511880 银华日利ETF / 511990 华宝添益ETF（货币 ETF）＋纯现金（0% by construction）
  - **arm B-直池（双低池）腿=数据就绪门 honest-gated**：O-1105 命令「直接可转债双低池（集思录 feed 已在采）」——仓内实况=集思录面 T-60 s1/s2 探针验通（cb_face_probes.json）但**日面板采集器未建**（data/ 下无 jsl 面板）；B-直池腿**不进本批冻结格集**，待 bm-b 素材扫描（≤10-16）+采集器建面后**另开子批预注册**（诚实披露，禁无数据烧格）。
- **数据锚面定义四元组【G-ANCHOR-FACE·每个数字探针锚必填】**（探针=results/_r912bma_parking_probe.json·r913 机读锚）：
  - 6 ETF 面板：`data/daily/sh<code>.csv` + **raw pd.read_csv 直读截断**（非引擎 load_core 池面）+ 各员首 bar 起算 + **预热窗=0**（stint 数学无指标预热）：511010（3,273 行·2013-04-09→2026-09-22）/511090（797 行·2023-06-13→）/511260（2,204 行·2017-08-24→）/511380（1,570 行·2020-04-07→）/511880（3,266 行·2013-04-18→）/511990（3,273 行·2013-04-09→）。
  - repo 现金基线：`data/repo_daily/GC001.csv` + raw pd.read_csv 直读截断 + 2011-05-13 起算 + 预热窗=0（3741 行·→2026-10-08，**截断到 evidence_cutoff**）。
  - 熊/阴跌段面（§4 Face 4）：`data/daily/sh510300.csv` + raw pd.read_csv 直读截断 + 2012-05-28 起算 + **MA200 预热窗=200 bar**（首有效第 200 bar）。
- **探针-锚同面断言**：runner 探针实载路径与上述声明逐位比对——一面不相等=面错配 VOID（fail-closed 拒烧，报「面错配」非「数据腐坏」）。
- **evidence_cutoff（前向锁盒 D2）=2026-09-22**：全面板截断到 cutoff（GC001/510300 更鲜=截断；511 面板尾 bar 恰=2026-09-22 探针实证）；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必须带 `science_gates.cutoff_meta(cutoff)` 字段（缺=science_audit C2 VIOLATION）。
- **数据完备门**：6 ETF 面板尾 bar=2026-09-22（探针实证）＋GC001 覆盖 ≥511010 全史窗（2013-04-09>2011-05-13 ✓）——不过门禁跑批。
- **as-traded 面偏差诚实声明（本批最大测量面）**：6 ETF 面板=as-traded 价（分红除息未复权）——**实测收益低估真收益**（国债 ETF 分红流 ~1%/yr、货币 ETF 分红流 ~2%/yr 实证带：511880 13.4y 价幅仅 +0.33%/yr vs 货基真收益 ~2-3%/yr）→ ①判 instrument 对 repo 基线的 pickup **被低估**（against-arms 偏差=fail-closed 方向 ✓ 主门保守）；②null 族 μ 同源低估（技能线偏松，如实披露）。**主门（Face 1 成对 t）在保守方向成立**=过门结论加强、不过门结论=「as-traded 面无法证实 pickup」数据债裁定（另开复权面板后重判），禁把保守面不过门改写为「停泊无价值」。
- **探针种子选位律**：本批 null 族种子=**94_300**（94_001..94_999 净袋·D-20261004-02②；与在册 94_100/94_200 不撞），冻结 commit 同窗登记 `science_gates.SEED_REGISTRY`；带闸探针簇保留簇 95_000..95_003 零接触。

## §3 方法学【必填】

- **stint 定义（冻结）**：stint=(entry 日, duration d)——entry 日收盘买入、entry+d 交易日收盘卖出（持有到底，窗内无中途操作）；duration 档=**{5, 10, 20, 40, 60, 120} td**（6 档）；entry 步进=**每 5 td 全普查**（确定性、无抽样；每格 stint 数=⌊(有效行数−d)/5⌋，逐格披露）。
- **成本口径**：**V1 legacy 面 A**——ETF 往返 **26.082bp**（面 A 恒等，CN-C7 单一可比数=单边 bp×2）；成本施加=entry+exit 两边全计入判 pickup；**×2/×3 压测**=52.164/78.246bp 往返（压测面照 O-1105 三铁律 1）。
- **基线三形态（冻结）**：
  - **C2 repo 现金代理（主基线）**：日 carry=GC001 close（年化%）/250（交易日口径）；诚实注记=GC001 周五占款 3 日历日未建模（代理 5/250=0.02 > 真 7/365=0.0192 → 代理**略高于**真 repo 收益 → against-arms 方向 ✓）；可用性=T+1 晨（比 ETF T+0 慢一腿，如实标注=「随叫随到」对比面）。
  - **C1 货币 ETF 实测面（次基线·披露）**：511880/511990 as-traded 收益（偏差声明见 §2——低估 ~2%/yr，**禁作主门基线**=假放行陷阱，仅披露）。
  - **C0 纯现金（参考）**：0%（O-1105「纯现金躺平」形态；成本敏感面=对 C0 的 pickup 须先付往返成本）。
- **pickup 定义（冻结）**：stint pickup u_s = [P_X(exit)/P_X(entry) − 1] − carryRepo(entry→exit 同窗累积) − cost_rt(stress 档)；主门 stress=×1（26.082bp），成本压测面=×2/×3；对 C0 pickup = [P_X(exit)/P_X(entry) − 1] − 26.082bp×stress。
- **null 对照（停泊域自有 null 池·O-1105「不挪用趋势域尺子」）**：**K=200** masked 随机 (entry, duration∈6 档) stint 于 **511880**（C-money 典型员），逐 stint 算同式 pickup 年化 Sharpe（`mean_u/σ_u×√(250/d)`），池成 {coverage:{mu, sigma, n_values=200}, source="PARKING_P1 own null family (511880 random-entry stints vs repo proxy)"}——**seed=94_300**（跑前登记 SEED_REGISTRY）＋被动基线=批自 passive（`passive_override`=511880 全史窗活算年化 Sharpe vs repo 代理——REPO_CALENDAR_P2 律·禁手抄）；技能线=`science_gates.skill_line_v2(batch_cells=24, null_pool=批自族, passive_override=…)`（**不挪用 core48 池**）。
- **滞后规则**：信号面零滞后（stint 数学无信号）；GC001 close 当日可得=当日 carry 入账无前视（收盘后利率已知）。
- **账本**：`science_gates.append_ledger(batch_name="PARKING-P1", batch_trials=24, file_name="results/parking_p1.json", evidence_cutoff="2026-09-22")`（dict schema 唯一，禁手抄 prev）。
- **闭合族对号声明【M3】**：本批 family_key=**parking_cash_leg**——`science_gates.CLOSED_FAMILIES` 十键无此族（cta_futures_p1/cn_combo_five_family/wild_route_s1/factor_blend/t28_spm_first/microcap_2024_crash/lowamp_daily_xs/lowamp_deep_xs/g2_slot_mon_p2_xs）→ **open 照跑**；跑前 `closed_family_check` 实跑留 rc。
- **出场轴显式声明【O-20261001-1108 必填三选一】**：**② 持有到底声明**——stint=entry→entry+d 持有到底、窗内零操作；runner=纯面板模拟**无引擎参与**（引擎缺省出场栈结构性缺席=显式禁用面）；接线路的出场轴（过门后）=① 策略自有出场（主信号回场日退出·exit-to-asset 特性——bm-c 设计件 ≤10-16，O-1105 §三），**本批不测不判接线路出场**。

## §4 判据【跑前写死·共享库禁手抄】

- **Face 1 主门=成对 pickup t 检验（O-1105「A/B 必须打过 C」零假设校准·逐格）**：per (X, d) 格——(a) mean pickup > 0；**(b) `science_gates.m1_t_value_gate` t ≥ 3.0**（Harvey/Liu/Zhu 多重检验门槛·共享库）；(c) `science_gates.bootstrap_ci_sharpe`(pickup 序列) CI 下界 > 0；三条全过=格 PASS（批报告逐列披露 t/CI/mean 全输入）。C0 面（纯现金）成本压测=×2 档 net mean > 0（O-1105 成本压测纪律）。
- **Face 2 注册面=G1' v2+G2 v2（Face 1 幸存格才触发·逐 instrument）**：`science_gates.g1_prime_v2(sharpe_full=pickup 日序列年化 Sharpe, returns=pickup 序列, batch_cells=24, null_pool=批自族, passive_override=511880 活算)` ——skill_line_v2=max(passive+0.10, μ_null+σ_null·√(2·ln N_eff))·全输入逐列披露；**NaN-safe=nan-aware 统计**（r442 坑律）；G2=`science_gates.g2_registration_v2(g1_pass, dsr=deflated_sharpe_ratio(原始 pickup), pbo=screening/pbo.py CSCV 8 块·族=本批 24 格)`（DSR≥0.95·PBO≤0.25·缺输入=诚实拒收）。
- **Face 3 安稳钱红线（O-1105 三铁律 2·逐格）**：within-stint 最大回撤 **p95 红线**——arm A（511010/511090/511260）≥ **−3.0%**、arm B（511380）≥ **−6.0%**（预注册定值）；**硬尾帽**——单 stint 净值谷底 A: > −10.0% / B: > −15.0%（击穿=该格红线 FAIL 单列披露）；arm B-ETF 形态的强赎/退市/债底破位硬过滤=ETF 管理人层面（直池腿另批承载显式过滤——§2 gated 腿注记）。
- **Face 4 空仓段面读数（O-20260926-1355 矩阵挂钩·必披非门）**：熊/阴跌日集=510300 close<MA200（仓内 canonical 熊代理·SIG Top10 同闸）；entry 日 ∈ 熊集的 stint 子集 pickup 单列读数（arm A/B 空仓高发段增益=停泊腿的矩阵挂钩消费面）。
- **随叫随到流动性门（O-1105 三铁律 1·逐 instrument）**：面板全史 median daily amount ≥ **¥50,000,000**（¥1M 停泊单 ≤2% 日成交占比；etf_list 快照日额 511010~53亿/511090~33亿/511260~31亿/511380~51亿/511880~266亿/511990~110亿——预判 6/6 过）；回场延迟声明=ETF 卖出资金当日可用（T+0 交易可用/T+1 取现）——零交易日回场延迟，成本=退出腿冲击吸收于 26.082bp×stress。
- **不冒新险（O-1105 三铁律 3·批级声明）**：停泊袖预算独立（最高 100% 空仓现金、零杠杆零保证金）；99% stint 损失下限逐臂披露；接线时=独立袖车道（marks 非试验账本 +0 族·PROS-* 白名单范式）、停泊亏损不传导主策略（接线约束，过门后 bm-c 工程腿执行）。
- 描述性条款（批级披露）：全窗年化>0；OOS 双正（窗中点分段）；袖全窗最大回撤 ≥−35%；**as-traded 偏差面注记恒附**（§2 声明）。

## §5 跑前预测【写死·跑后对账】

1. **arm A pickup 量级**：511010/511260 vs repo 代理全窗 pickup ≈ **+0.3%~+2.0%/yr**（国债票息+久期溢价超隔夜 repo ~0.5-1.5%/yr·as-traded 分红低估 ~1%/yr 抵减后）；511090（30Y 久期）pickup 均值同带但 **σ 大 3-5×**——t 值=量级/σ 预测 511090 **不过 t≥3.0**（长端波动吃掉显著性）。
2. **arm B pickup 量级**：511380 vs repo ≈ **−2%~+4%/yr 宽带**（转债信用+股性双源·2021-2024 转债熊段深负、2024-09 后正）——**t≥3.0 过线与否不预设立场**；60/120td 档 p95 红线 **预测击穿风险高**（2021H2-2024H1 熊段 60td 窗内回撤 −8~−15% 实证带·§5.5 极端日先验）。
3. **duration 边际**：短档（5/10td）**预测全灭成本面**——对 C0 pickup=carry(5~10td ≈ 2-8bp) − 26.082bp×1 = **负**（往返成本吃掉短停泊）；**最小可行停泊档预测 ≥40td**（carry 累积 ≥ 成本）；对 C2（repo 基线·成本对称消零+仅付 26.082bp×1）短档存活概率高于 C0 面。
4. **极端日先验（硬界设计三件套 c·D-20260925-01①）**：①**2022-11~2023-01 理财赎回潮债灾**——511090 型 30Y 面单日 −1.5%~−2.5% 连环、60td 窗回撤 −5%~−9%→**511090 p95 红线 −3.0% 预测 FAIL**（honest：30Y 端「安稳钱」语义本就紧）；②**2024-09-24 政策组合拳债跌**——长端单日 −0.8%~−1.2%；③**2021H2-2024H1 转债熊**（511380 价幅 14.86→9.57=−35% 全史）——120td 档窗内 −6% 击穿预测出现于该段；④**2016-01 熔断+2015-07 救市**——arm A 债面彼时为避险资产正 pickup（股债跷跷板）。
5. **null 族形态**：511880 随机 stint pickup Sharpe μ_null 预测 **−0.5~−1.5**（as-traded 分红低估 ~2%/yr 直接入 μ）、σ_null 预测 **0.8~2.0**（短档 stint 噪声大）；技能线 null 项预测被动项（511880 活算 +0.10 面）不主导——**Face 2 技能线大概率被动项主导**，如实披露。
6. **D6 argmax 预测**：511380 vs 在册股票域 6 员 corr 峰值 **0.3-0.6**（转债股性共因子）<0.7 拒收线；arm A 三员 <0.15。全预测带跑后对账（对/部分/错逐条）。

## §6 产物【跑前声明】

- scripts/parking_p1.py（gates/run/selftest 三态子命令·探针先行纪律；探针-锚同面断言内置；audit 段嵌批内）
- results/parking_p1.json（顶层 evidence_cutoff=2026-09-22＋audit 段＋verdicts 逐格＋null_pool 全输入＋passives＋D6 corr 清单＋§5 预测对账块＋prereg_sha256_at_run）
- research/parking_p1_results.csv（全列）＋本件 §7 回填

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（占位——本节跑后回填，一次定稿）

## §8 批后复盘【必填·s7-T】

- 预测对账（对/部分/错逐条）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线当批读数披露；
- 回执入轮报告＋CODELY.md 行级追加；**过门接线**：注册件带 evidence_cutoff＋exit-to-asset 工程腿（bm-c ≤10-16 设计件消费本批 verdict）＋10-21 回访首读数＋10-31 月考停泊增益面；不过门=诚实判负收线（复活条件=复权面板数据债清偿后另开预注册）。
- **全起点分布【§1.3 必填】**：stint 全普查=全起点面（每格全部 entry 位披露 p25/中位/p75/最好/最坏——非抽样天然满足）；滚动 3/5 年窗最差档单列。
- **试验量归因【§1.4 必填】**：本批新增 24 格（O-1105 CEO 直令派单·停泊域首判决批·月考消费面在册——预算正当性=命令件）；30 天窗 RETAIL_QUANT_TRACK §四闸记账。
- **宝藏捕获律收口步**：判决 finalize 时问「本批有无新宝藏/新方法？」有→knowledge/TREASURE_REGISTRY.md 出入记录+METHODOLOGY_ASSETS.md 方法论卡 append。
