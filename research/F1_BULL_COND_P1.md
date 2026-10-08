# F1-BULL-COND-P1 预注册（T-2026-10-08-177 leg-2 slice-2 · O-20261007-2215 §二「阶段条件化是不同命题」判决批）

> 冻结纪律：本件 commit=跑前冻结；跑后只许回填 §7/§8，禁改判据禁重跑（PREREG_TEMPLATE verbatim）。
> 判别器标签恒冻结 v1.0（results/regime5_labels/REGIME5-2026-09-30.json·阈值指纹=REGIME5_LABELER_V1 selftest 哈希）——本批零改标签阈值（r871 验证批主门判负在案：BULL 态差 +9.94bp/日量级对但三面显著性全败·标签修订只能走 O-2215 修订窗另批预注册，本批消费的是冻结 v1.0 标签面如实）；CEO 令 §二 verbatim：「阶段条件化是不同命题，但同样过意义门+成本压测，禁止因 CEO 需求降科学门」——本批零门降。

## §0 批件身份【跑前】

- 批名/批号：`F1-BULL-COND-P1`（批内格数 N_eff=**1,009**＝9 judged cells（L∈{60,120,250}×topk∈{1,2,3}）+ 1,000 BULL 同掩码随机选员 null；x2/x3 成本压测=披露列不计 N，CN_TREND 先例）。
- 认领：F-04 先行——fleet/inbox/MSG-2026-10-09-0350-bma-f1-bull-cond-p1.md 声明（本窗随冻结同推）；任务单引用=T-2026-10-08-177-P1（bm-a claimed·leg-2 slice-2）·CEO 令=O-20261007-2215 §二/§三 @bm-a ②；候选链=r898 external_scan_slice1 rank1 + r890/r898 准入链（无条件形态 REJECT BAN-01 零烧在案·f1_admission_gate.bm-a.json）。
- 部门归属：dept:研究（牛市进攻供给线第二专精员候选判决面）。
- 算力预算：numpy 向量化轻批（9 cells×3,289 标签日循环+1,000 null 复制，预计秒级-分钟级·REGIME5-VALIDATION-P1 40.2s 同族先例）；<5min=轮内直跑合法；批报告带 audit 段。零池面零池写（轻批不入 runnable_pool）。
- 出场轴显式门（O-20261001-1108）声明：**①策略自有出场**——REGIME-5 标签翻离 BULL 即全仓清空（regime-window 出场· dismantling 成本计入最后一在市日净收益·冻结约定）+ 窗内 top-k 集合变化即换仓（rank-fallback 换仓）；无引擎缺省出场栈依赖、非持有到底、非 template_default。

## §0.5 禁开方向硬闸【跑前】

- `python Tools/banned_direction_gate.py --prereg research/F1_BULL_COND_P1.md` 退出 0=放行（跑前实跑留痕于轮报告）。
- 命中编号：**BAN-01**（ETF 横截面动量·本批 §1 诚实陈述「ETF 横截面动量轮动」必命中）；另预防性引用 **BAN-09**（风格延续语义族——本批「强者恒强」机制陈述若命中其 pattern 同由本例外覆盖）。
- 例外类型：`new_mechanism`
- **原否证不可能看见的东西**：BULL 态窗口隔离——BAN-01 原否证（31 只 ETF 周频横截面动量·全史混合态样本·年化 −7.65%）与宽基趋势择时否证（MA200/20-60 同向·全窗混合态）均在**全历史混合态**上测量，从未在 REGIME-5 BULL 标签子窗（全史 201 日/24 窗）内**隔离测量**条件化形态：非 BULL 日强制空仓的截面动量在原否证的设计空间外（原批全部持仓跨态混合、无条件翻面结构）；CEO O-20261007-2215 §二裁定「阶段条件化是不同命题」+ CJoE 2024 外源独立证据（A 股因子动量利润集中于牛市侧·r898 external_scan_slice1 锚）为该隔离面提供机制主张。例外面诚实边界：r871 验证批已实测 BULL 态 t+1 漂移 +9.94bp/日量级对但显著性三面全败（n=59 主窗）——本批测的是**轮动选择信号**在 BULL 窗内是否超越同窗被动/随机基线，非标签显著性复诉。

## §1 α 机制段【D6】

- [x] **行为偏差**：追涨/锚定×羊群——BULL 态内信息扩散缓慢与注意力稀缺使近 L 日相对强者（ETF 横截面动量轮动·top-k 持有）获得延续性买压；付出代价方=窗内过早止盈的处置效应持有者与锚定逆势者。外源锚：CJoE 2024（A 股因子动量利润集中在牛市侧·unverified external hypothesis——验证独立归本方门禁链）；内证锚：MOM 族无条件形态 0/4920 判负在案——**本批主张的不是无条件截面动量复活，而是「BULL 窗隔离」这一原否证未见过的条件化机制面**。
- **散户凭什么赢【§1.2】**：**制度+行为**——日线公开量价零信息劣势零速度竞赛；ETF 容量无限；制度面散户零委托约束可在 BULL 确认窗自由切换进攻袖（机构委托契约锚定防守袖不能自由轮动·REGIME5_VALIDATION_P1 §1.2 同律引用）。涉机构已验证结论引用：无（BULL 态条件化 ETF 轮动=O-20261007-2215 CEO 原生方向令新立，无机构正典结论可引——如实零引用非硬凑）。
- **同族相关性准入检查【D6】**：in-runner D6 面（cn_kline_pattern_p1 d6_block 同款机械）——逐 judged cell 全日历净收益序列（3,289 标签日·非 BULL 日=0）对在册 6 CE 成员（ew6 canon member_run 日收益）逐对 |corr| + 批内两两 |corr|（披露列）；**≥0.7 vs 在册成员=拒收**。家族碰撞面预检：r890 探针已实测**无条件超集形态** vs CTA_P1 max|corr|=0.0344（f1_ctap1_corr_probe.bm-a.json·9 代表格全列）——条件化形态持仓日 ⊂ 无条件形态持仓日，与 CTA_P1（期货连续时序趋势·全日历持仓）重叠严格更窄，碰撞风险上界不劣于已测值；CTA_P1 纸盘试用期非在册交易员（REG6 六成员=准入门对象），其探针读数=advisory 引用列。D6 预期：本策略 ~94% 日空仓，与任何连续持仓成员日收益相关结构上趋零；数值以批报告 D6 表机读为准。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：**O-1555 冻结五员** {510300, 510050, 510500, 512100, 588000}（CEO 令冻结面·扩池=无）。
- **数据锚面定义四元组【G-ANCHOR-FACE·每个探针锚必带】**：
  - ①五员日线面板：`data/daily/sh<code>.csv` ②加载=`pd.read_csv` 直读截断 date≤cutoff（runner=f1_bull_cond_p1.load_panel·非引擎 load_core 池面）③起算=各员自有首 bar（510300=2012-05-28·510050=2005-02-23·510500=2013-03-15·512100=2016-11-04·588000=2020-11-16·本窗机读）④预热=mom_L 需 L+1 bar+vol60 需 60 bar→首 BULL 窗 2014-07-30 时 510300/510050/510500 已全预热（L=250 亦足）；512100/588000 晚入伍按 alive-only 逐日判定（eligible=三面 finite：mom_L/vol60/ret_next）。行数锚（截断前→后）：510300 3,489→3,449?（机读 audit 段落如实）·尾行截断后恒 2026-09-30（D2 锁盒断言）。
  - ②冻结标签面：`results/regime5_labels/REGIME5-2026-09-30.json`（cutoff 2026-09-30·3,289 标签·契约 date/state 两键）；加载=直读 JSON `labels[]`（r587 anti-transcribe 零重贴）；raw 日标签直读（N_CONF=1 面=r871 校准 argmin·防抖层属消费端 bm-c 矩阵修订窗未消费面，本批消费文件面 verbatim）。
  - ③主日历=标签日历（3,289 日·2013-03-21→2026-09-30）——条件收益 t→t+1 的 t+1 即下一标签日（与 REGIME5-VALIDATION-P1 §3 同约定）。
- **探针-锚同面断言**：runner 探针实载路径与上述锚声明逐位比对（labels cutoff==CUTOFF 断言+面板尾行==CUTOFF 断言+五员列名断言）——一面不相等=配置错配 VOID（fail-closed 拒烧·报「面错配」非「数据腐坏」）。
- 窗口与 **evidence_cutoff=2026-09-30**（=标签件 cutoff·面板一律截断到 cutoff·D2 前向锁盒：cutoff 后新 bar（10-08 已在文件内）锁定不得回流本批·runner 截断断言+audit 披露截断行数）；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)` 字段。
- 数据完备门（不过门禁跑批）：标签件在位且 cutoff==面板尾行日期；K 检查=全史 3,289 标签日 ≥1,000 律 ✓·BULL 子面 201 日/24 窗（条件批小样本面如实：F6 双口径门与 M1 t 面按 201 期间数如实计算·n<30 entries 格=trade gate 结构性判负如实报）。
- 探针种子选位律（D-20261004-02②）：null 种子基=**94_200**（94_001..94_999 净袋·SEED_REGISTRY 实测 94_x int 占用仅 94_100·r899 机读）——1,000 复制经 numpy `SeedSequence(94_200).spawn(1000)` 单基派生**禁顺爬**；基点已登记 `science_gates.SEED_REGISTRY["f1_bull_cond_p1_null_base"]=94_200` 于本冻结 commit。

## §3 方法学【冻结】

- 信号定义：mom_{i,t}=close_{i,t}/close_{i,t−L}−1（成员自有 bar 序 shift(L)·L∈{60,120,250}·r890 探针同式）；eligible(i,t)=mom_L/vol60/ret_next 三面 finite；target=top min(k,n_eligible) by mom 降序（k∈{1,2,3}）；权重=入选集内 1/vol60 归一。
- **条件化与出场（冻结）**：日 t 标签（收盘量价→t 日标签可用）==BULL 才允许持仓；条件收益=t→t+1 收盘收益（零未来数据·r871 同约定）；窗内 target **集合**不变则权重冻结（无逐日 vol 漂移换仓）；集合变化=换仓事件（rank-fallback）；标签翻离 BULL=窗口结束全仓清空。
- 成本（冻结约定）：换手事件计费=入场（0→w）+换仓（|Δw|）+清仓 dismantling（清仓成本计最后一在市日净收益）；cost=**13.041bp/边 ×换手额**（COST_X1 repo 冻结常量·V1 legacy 家族锚=与 r890 探针/r871 验证批/无条件判负面同口径可比）；压测面 x2/x3=披露列（CEO §二「成本压测」面）。
- 往返成本 bp 申报【CN-C7】：ETF=**26.082 bp/往返**（面 A `knowledge/cost_spec.py` 派生恒等·13.041×2）；单笔名义额档位注记=¥5 最低佣金临界 ¥20,000（五员宽基 ETF 流动性面档位风险低如实注记）。
- null 对照（K=1,000 同掩码随机 null）：逐窗 k~U{1,2,3}、窗内全程 eligible 成员均匀随机选 k_eff 只、入场逆 vol60 权重冻结持窗、同入场/清仓成本约定——隔离「动量排序选择信号」（skill_line null 面=批自有 null 族·mu/sigma 机读）；无引擎调用。被动基线=**同掩码条件化 510300**（BULL t 日持有 510300·零成本·passive anchor；+0.10 边际要求由 skill_line 结构承载·r898 诚实先验 verbatim「轮动须击败同窗 max(passive+0.10, null 线)非绝对收益」）。
- 账本：`science_gates.append_ledger(batch_name="F1-BULL-COND-P1", batch_trials=1009, file_name="results/regime5_bull_scan/F1-BULL-COND-2026-09-30.json", evidence_cutoff="2026-09-30")`（dict schema 唯一禁手抄 prev；重跑面=redo 检测批名已在链→batch_cells=0 无自回声（r253 单计数律）+跳 append）。
- 闭合族对号声明【M3】：family_key=`f1_bull_cond_momentum`——`science_gates.CLOSED_FAMILIES` 实测零该键（r899 机读：cta_futures_p1/cn_combo_five_family/wild_route_s1/factor_blend/t28_spm_first/microcap_2024_crash/lowamp_daily_xs/lowamp_deep_xs/g2_slot_mon_p2_xs 九键无 f1 键）=open 照跑；交叉注记：cn_combo_five_family（REV-TILT/DIV-LOWVOL-ROT/REGIME-POLICY/CORE-SATELLITE/DDCTL 配置结构族）≠本批（BULL 窗隔离截面动量·机制面不同·CEO §二「不同命题」裁定）；BAN-01 禁开面由 §0.5 new_mechanism 例外承载。
- **新因子 t 面申报【M1】**：策略面无直接 IC t——`science_gates.t_from_sharpe(SR_ann, n_periods=201)` 派生面（判据=`science_gates.m1_t_value_gate` t≥3.0 Harvey 门槛）；n=201 在市期间数如实（M1_MIN_PERIODS≥30 ✓）；缺面=missing_input 拒收非放行。

## §4 判据【跑前写死·禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=1009, n_trades, n_entries, null_pool=批自有, passive_override=同窗被动)`**：在市口径 Sharpe（BULL t→t+1 净收益 201 日流·mean/std(ddof=1)×√252·cells/nulls/passive 三面同式同口径）> skill_line_v2（**batch-own null_pool + passive_override=条件化 510300 同窗 Sharpe**·P4_EXT_TILT/REPO_CALENDAR_P2 双 additive 面首次同用）**且**平稳 bootstrap CI 下界>0 **且** F6 双口径（n_entries=逐成员开仓计数·n_trades=逐成员平仓计数·entries_ok 为准·min 30）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始在市收益跑·n_trials=skill_line n_eff·cn_kline 同例）**且** 家族 PBO≤0.25（`screening/pbo.py cscv_pbo` CSCV 8 块·9 格在市净收益 201×9 阵）；缺输入=诚实拒收。
- **M1 t 面**：`m1_t_value_gate(t_from_sharpe(SR,201))` t≥3.0；**D6 拒收线**：逐 cell vs REG6 max|corr|≥0.7=该 cell 拒收。
- **批注册判决（冻结）**：任一 cell 全链过（G1' pass_v2 ∧ M1 pass ∧ G2 eligible_v2 ∧ D6 无拒收）=家族有注册资格候选（注册另走注册件+月界）；全 cell 不过=本批判负如实（预注册结构性预期：n=201 在市日+24 窗的 t 面与 entries 面均紧——见 §5 预测②③）。
- 保留历史描述性条款（批级披露·不替代 v2 门）：年化>0、OOS 双正（pre2020/2020+ 两半披露面）、回撤≥−35%、成本压测 x2/x3 逐 cell 披露、全起点分布（24 窗逐窗净贡献 best/worst/p25/中位/p75 + 两半子窗——条件批「起点」=入场窗·§1.3 多起点律的诚实适配面如实申报）。
- 硬界设计三件套【D-20261025-01①】：本批无数据腐坏检测判线（N/A 如实）——max 单日 |r| 为披露列非判线；极端日先验=§5 第 4 条（2015 气泡顶簇/2025 冲击窗在市日单列披露面）。

## §5 跑前预测【写死于跑前·≥3 条+极端日先验】

1. **entries/结构面**：每 cell n_entries 预计 24×k+换仓加入（top-1 格 24-34 风险面：L=60 短窗内排名翻转偶发；top-2/3 格 48-72+）——**top-1 格 entries<30 结构性 trade-gate 判负为诚实预期结果非事故**；n_in 恒 201（flat_bull=0 预期·panel 完备）。
2. **收益面**：x1 在市 Sharpe 预计 **−0.5~+1.5 区间**（五宽基高同涨跌·窗内动量排序区分度有限·追高 588000/512100 集中格波动放大）；相对无条件形态（全史 ann −2.18%~+3.91%·Sharpe 0.1-0.16）条件化不必然改善风险调整后读数——**G1' line 预期全败为主读数**（诚实先验：被动项大概率主导线位）。
3. **skill_line/门面**：被动面（条件化 510300 同窗）Sharpe 预计 **1.0~1.8**（全史 BULL 漂移 +14.3bp/日·窗内 vol ~1.2-1.5%）；null 族 mu 预计 0.8~1.5（随机选五宽基同掩码继承 BULL β漂移）·sigma 0.15~0.35 → null 项=mu+σ×√(2·ln 810k)≈mu+5.2σ 预计 **1.8~3.3**；skill_line 预计 **1.9~3.5**——**无 cell 过线为基线预期**；M1 t=SR×√(201/252)=0.893×SR → t≥3.0 需 SR≥3.36（几乎不可及·如实）。
4. **极端日先验**：在市窗含 2015-04/05/06 气泡顶簇（510300 单日 ±3-5%·588000 未入伍）与 2025-07/08/09 冲击窗（512100/588000 单日 ±4-8% 可能）；top-1 集中格单日净收益尾部 |r| 预计可达 ±5-8%——max 单日披露列如实记录非判线；若 2015 簇极端日主导某 cell 窗净贡献=单列披露禁粉饰。
5. **换仓面**：24 窗内 top-k 集合翻转事件预计 0-15 次/批（L 慢变·窗短）；换手总额换算成本预计 <1.5% 全史（入场+清仓 24×2×13.041bp 支配·窗内翻转稀疏）。

## §6 产物

- runner=`scripts/f1_bull_cond_p1.py`（run/selftest 子命令·冻结后实现·确定性幂等：nulls 全种子化、redo=批名在链检测+batch_cells=0 无自回声+attrition 自有行替换；selftest=面板/标签/掩码/成本约定合成 fixture+种子带+skill_line 插件面+g2 拒缺输入 6 腿离线自检）。
- 交付：`results/regime5_bull_scan/F1-BULL-COND-2026-09-30.json`（顶层 evidence_cutoff+cutoff_meta+audit 段+9 cell 全表[x1/x2/x3·entries/trades/turnover·窗分布·两半子窗]+null 族+被动面+D6 表+PBO+逐 cell G1'/M1/DSR/G2+verdict+trials_ledger）；§7/§8 本件回填。
- 消费面：判负→BULL 供给扫描线收口（CEO §二命题以实数闭卷）；任何 cell 全链过→注册件+纸盘接线另批（月界面）。

## §7 跑后实证【跑前为空——占位纪律：写数字即造假】

## §8 批后复盘【跑后回填·s7-T】

- 跑前冻结=本件 commit（冻结后禁改判据；回填限 §7/§8）。
