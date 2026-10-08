# REGIME5-VALIDATION-P1 预注册（T-2026-10-08-177 slice-2 · O-20261007-2215 @bm-a ① 验证批）

> 冻结纪律：本件 commit=跑前冻结；跑后只许回填 §7/§8，禁改判据禁重跑（PREREG_TEMPLATE verbatim）。
> 判别器规则恒冻结于 research/REGIME5_LABELER_V1.md v1.0（阈值指纹=selftest t01 哈希）——本批**零改判别器阈值**（标签禁拟合结果）；本批校准对象=消费端防抖层 N_CONF（O-2215 §一.3 明文「校准归 bm-a 判别器验证批」）+阶段差收益测量。

## §0 批件身份【跑前】

- 批名/批号：REGIME5-VALIDATION-P1（批内格数=1,010＝Leg A 阶段差 5 格 + Leg B N_CONF 取值集 5 格 + 随机标签 null 1,000 复制；全部计入 N_eff）。
- 认领：F-04 先行——fleet/inbox/MSG-2026-10-08-08xx-bma-regime5-validation-p1.md 声明（本窗随冻结同推）；任务单引用=T-2026-10-08-177-P1（bm-a claimed·slice-2）·CEO 令=O-20261007-2215 §一（O-20261007-2215-bm-c.md 本地件）。
- 部门归属：dept:研究（判别器验证=测量面）。
- 算力预算：单机 numpy 纯向量化轻批（1,000 null 复制×3,289 标签日置换＝秒级-分钟级）；<10min=轮内直跑合法；批报告带 audit 段。
- 出场轴显式门（O-20261001-1108）声明：本批=**测量/校准批非策略判决批**——零持仓零入场零出场零引擎调用（出场轴三选一 N/A 如实声明）；下游消费面（bm-c 矩阵+在册袖面）的出场轴归各在册冻结件，本批不触碰。

## §0.5 禁开方向硬闸【跑前】

- `python Tools/banned_direction_gate.py --prereg research/REGIME5_VALIDATION_P1.md` 退出 0=放行（跑前实跑留痕于轮报告）；预判零命中（REGIME-5 阶段判别+风格路由=O-2215 CEO 新方向令，非 BANNED_DIRECTIONS 九方向任何一族——判别器面向指数量价结构非选股/择时信号族）。

## §1 α 机制段【D6】

- **行为偏差**【主选】：指数级 regime 漂移=群体行为周期（BULL 追涨自我强化/BEAR 恐慌出清/GRIND 阴跌观望/CHOP 多空平衡）——由全体市场参与者共同付出代价（趋势期追高者抬轿、崩溃期恐慌者斩仓），日线公开量价（价距 MA200+量能扩张 z+广度代理）可测，无速度/数据劣势；SUPPORT 态=制度干预脉冲（救市天量+强收盘指纹·国家队/政策资金付出代价）并入行为面同测。
- **散户凭什么赢【§1.2】**：**制度**——本决策维度（风格-阶段路由）上机构受委托契约/仓位纪律/风格锚定约束**不能自由轮动**（熊市防守员不能清仓、牛市进攻员不能切防守），散户零委托约束可按确认翻面自由切换；叠加无信息劣势（日线公开数据·无速度竞赛·ETF 容量无限）。涉机构已验证结论引用：无（regime-风格矩阵路由=O-20261007-2215 CEO 原生方向令新立，无机构正典结论可引——如实零引用非硬凑）。
- **同族相关性准入检查【D6】**：**N/A 如实声明**——本批零新策略函数入册（下游=bm-c 冻结矩阵 v1.0 消费既有在册袖面；随机标签 null=测量对照件非候选）；在册交易员相关性检查对象（新函数）不存在。若未来矩阵路由出策略入册，彼时按 sleeve-tag 先例过 max|corr|≥0.7 拒收门。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：单品种 510300 沪深300ETF（O-2215 §一 指数代表锚·CEO 判据方向 verbatim 面即 510300）。
- **数据锚面定义四元组【G-ANCHOR-FACE·每个探针锚必带】**：
  - ①日线面板：`data/daily/sh510300.csv` ②加载=`scripts.regime5_labeler.load_panel`（判别器同源加载器·冻结件·禁另写）③起算 2012-05-28 ④预热=MA200+z120d+60 日高点窗→首有效标签日 2013-03-21（实测锚）；探针=3,488 行·尾行 2026-09-30（本窗实测）。
  - ②冻结标签面：`results/regime5_labels/REGIME5-2026-09-30.json`（判别器 v1.0 全史回放产物·cutoff 2026-09-30·3,289 标签·契约三键）；加载=直读 JSON `labels[]`；起算=首标签 2013-03-21；无额外预热（标签已含全部预热后置）。
  - ③消费权重面：bm-c 冻结矩阵 v1.0 `research/REGIME_STYLE_MATRIX_V1.md` §二权重表——加载=`scripts.regime_style_matrix.py` import（冻结引擎·零重实现）；Σ|Δw(X→Y)| 逐对机器派生。
- **探针-锚同面断言**：runner 探针实载路径与上述锚声明逐位比对——一面不相等=配置错配 VOID（fail-closed 拒烧·报「面错配」非「数据腐坏」）。
- 窗口与 **evidence_cutoff=2026-09-30**（=标签件 cutoff=面板尾 bar 日·前向锁盒 D2：cutoff 后新 bar 不得回流本批）；结果 JSON 顶层必须带 `science_gates.cutoff_meta(cutoff)`。
- 数据完备门：标签件存在且 cutoff==面板尾行日期（不等=拒跑）；K 检查=全史 3,289 标签日 ≥1,000 律 ✓·主验证窗 2020-01-02→cutoff 实测约 1,6xx 交易日 ≥1,000 律 ✓（runner 机读确报）。
- 探针种子选位律（D-20261004-02②）：null 种子基=**94_100**（94_001..94_999 净袋·SEED_REGISTRY 实测零占用）——1,000 复制经 numpy `SeedSequence(94_100).spawn(1000)` 单基派生**禁顺爬**（顺爬 94_100+999 越入 95_000+ = N1 阶梯实撞红线）；基点先登记 `science_gates.SEED_REGISTRY["REGIME5_VALIDATION_P1_NULL_BASE"]=94_100` 于本冻结 commit。

## §3 方法学【冻结】

- 信号定义：**冻结 v1.0 标签直读**（r587 anti-transcribe：机读 labels 件零重贴）+消费端防抖层（N_CONF 连续确认·首标签 bootstrap·REGIME_STYLE_MATRIX_V1 §三律）。滞后规则：日 t 收盘量价→日 t 标签可用→条件收益=**t→t+1 收盘价收益**（next-day close-to-close·零未来数据：标签输入全部为 ≤t 收盘信息）。
- **Leg A 阶段差收益**（主验证窗 2020-01-02→cutoff+全史披露面）：每态 s 条件次日均收益 d_s＝mean(r_{t+1}|state_t=s)−mean(r_{t+1}|窗内全标签日)；显著性双机器面=(a)置换 null 1,000 复制（窗内标签日**逐态日数保全**的随机重排·同防抖层）经验双侧 p=rank(|d_s|)/1001；(b)块 bootstrap 20 交易日块 2,000 抽 95% CI。
- **Leg B N_CONF 校准**（全史 2013-03-21→cutoff）：候选 N∈{1,2,3,5,8}（N=1=无防抖裸标签）；逐 N 机读=确认翻面数 F(N)·错态日数 W(N)·翻面过渡成本 C(N)=Σ_flips Σ|Δw_matrix(X→Y)|×2×COST_X1 bp（COST_X1=13.041bp/边·rev_osc_stock_p1 冻结常量 import·双边×2 保守）·错态机会成本 O(N)=Σ_wrong-days |d_conf−d_raw|（全史态差·Leg A 全史面机读）；**L(N)=C(N)+O(N)·N_CONF\*=argmin L(N)**；缺省 3 确认律=L(3)≤1.10×min L(N) 则 3 维持，否则 N_CONF\* 旗标呈报（矩阵修订窗律内换装·O-2215 消费端）。
- **Leg C 过渡成本吃得过判据**：net(N_CONF\*)=Σ_conf-days d_conf − C(N_CONF\*)（全史·收益小数单位）>0=PASS（O-2215 §一.3「翻面净收益须吃得过过渡成本」verbatim 判据）。
- null 对照：Leg A 置换 null 1,000 复制（上述·种子基 94_100 spawn）；无被动基线（单品种条件差测量·被动=无条件均值本身已入 d_s 定义）。
- 成本口径：**V1 legacy（13.041bp/边）**——历史锚点复现恒用 V1 双轨防漂移；往返成本 bp 申报（CN-C7）：ETF=**26.082 bp/往返**（面 A `knowledge/cost_spec.py` 派生恒等）；单笔名义额档位注记=¥5 最低佣金临界 ¥20,000（本批无单笔模拟·成本面仅翻面过渡包络）。
- 账本：`science_gates.append_ledger(batch_name="REGIME5-VALIDATION-P1", batch_trials=1010, file_name="results/regime5_validation/REGIME5-VALIDATION-2026-09-30.json", evidence_cutoff="2026-09-30")`（dict schema 唯一禁手抄 prev；guard 前持久化=r509 律）。
- 闭合族对号声明【M3】：family_key=`regime_labeler_validation`——`science_gates.CLOSED_FAMILIES` 实测零 regime 键（本窗机读）=open 照跑。
- **新因子 t 面申报【M1】**：Leg A 逐态直接 t=d_s/(sd_s/√n_s)（条件收益直接面·非 Sharpe 派生）全列披露；判据=`science_gates.m1_t_value_gate`（t≥3.0 Harvey 多重检验门槛）**仅施于方向性主张两态**（BULL/BEAR·主门见 §4），描述态（CHOP/GRIND/SUPPORT）t 面披露不设门。

## §4 判据【跑前写死·禁看结果调线】

- **主门（方向性·冻结）**：BULL d_s>0 **且** BEAR d_s<0（主验证窗 2020-01-02→cutoff），各自：置换 null p<0.05（双侧）**且**块 bootstrap 95% CI 不含 0 **且** M1 直接 t≥3.0——三面全过=REGIME-5 标签面判据成立；任一态三面任一败=该态判据不成立如实报（禁调标签阈值——阈值修订只能走 O-2215 修订窗另批预注册）。
- 描述面（无门·全列披露）：CHOP/GRIND/SUPPORT 三态 d_s+null p+CI+t；SUPPORT 态样本量小（全史 102 日·2020 后窗内更少）=小样本面如实（CI 宽披露禁粉饰）。
- **Leg B/Leg C 判据（冻结）**：N_CONF\* 按 §3 L(N) argmin 机读；net(N_CONF\*)>0=吃得过 PASS；两者结果全表披露（5 候选行全列·禁只报最优）。
- 保留描述性条款（批级披露）：G1'/G2 注册门**N/A 如实声明**（本批零策略函数入册·注册门对象不存在；下游袖面注册归各在册件自身门禁）；skill_line_v2 读数=轮报告披露行（判线共享库 import 机读·禁手抄）。
- 硬界设计三件套【D-20260925-01①】：本批判线=分布界口径（条件均值+块 bootstrap CI 主责）非裸 max；极端日豁免单列=2015-07 救市簇/2016-01 熔断/2024-09-24 政策脉冲（§5 先验）命中日单列披露非整批判负；跑前极端日先验=§5 第 4 条。

## §5 跑前预测【写死于跑前】

1. **BULL 态差**（2020→cutoff）：正号·量级 +3~+15 bp/日（牛市漂移高于无条件·2019-2021 与 2024H2 簇贡献）；**BEAR 态差**：负号·量级 −15~−40 bp/日（2022-2024 长熊+2025-2026 深熊簇）。
2. **N_CONF 翻面数**：N=1 裸标签全史翻面数十至百余（SUPPORT 脉冲窗高频）；N=3 确认翻面预计 15~45 次（~1-3 次/年）；N=8 骤降至 <15（滞后过度）。
3. **过渡成本吃得过**：C(3) 全史累计包络预计 <1%（<10 次确认翻面×~60bp/次量级）——BEAR 躲避单态差×780 全史日即数倍于成本；net(3)>0 预期 PASS·N_CONF\*=3 或 5 预期（SUPPORT 高频抖动使 N=1/2 L(N) 抬升）。
4. **极端日先验**（块设计 20 日块吸收）：2015-06/07 崩盘-救市簇（BEAR+SUPPORT 密集·510300 涨停锁价日 Δr1=461.6bp 正典在册）·2016-01 熔断四日·2024-09-24 政策脉冲（BULL onset 候选+SUPPORT 前奏）·2025 关税冲击窗——命中日单列披露豁免面（§4 三件套 (b)）。
5. **描述态**：GRIND 小负（阴跌漂移）；CHOP 近零；SUPPORT 正号但 n 小（CI 宽·全史 102 日·主验证窗内 n 未定数如实机读）。

## §6 产物

- runner=`scripts/regime5_validation.py`（run/selftest 子命令·冻结后实现·确定性幂等；selftest=锚面断言+同面断言+账本拒双 append 腿）。
- 交付：`results/regime5_validation/REGIME5-VALIDATION-2026-09-30.json`（顶层 evidence_cutoff+cutoff_meta+audit 段+五态差全表+N_CONF 五行全表+null 分布摘要+net/cost 面）；§7/§8 本件回填。
- 消费面：bm-c `regime_style_matrix.py`（awaiting_upstream→标签面已在位·本批后 N_CONF 校准值落 MATRIX run 消费）·O-2215 判据回访 10-21。

## §7 跑后实证【跑前为空·占位纪律：写数字即造假】

（占位·run 后机械回填：五态差+三面显著性全表+N_CONF 五行表+N_CONF\*+net/cost+预测对账+audit。）

## §8 批后复盘【必填·s7-T】

（占位·run 后回填：预测对账+门禁链损耗账 `results/gate_attrition.json` 追加一行+skill_line_v2 当批读数+全起点分布（本批窗口=全史 2013 起+2020 主窗双面即多起点披露·滚动 3/5 年窗最差补测面声明）+试验量归因（1,010 格一句话）+宝藏/方法论捕获问+回执入轮报告。）

- **跑前冻结=本件 commit**（冻结后要改判据（回填限 §7/§8）。
