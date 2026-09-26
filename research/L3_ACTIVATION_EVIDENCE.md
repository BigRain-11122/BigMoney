# L3-ACTIVATION-EVIDENCE 预注册 · T-81 slice-2 激活表证据化 · O-20260926-1342 §三（CEO 直令）

> 跑前冻结件。跑后只许回填 §7；禁改判据（改=新版本号+CEO 判据线程序）。
> 语义=**读数派生面**（零新回测零新搜索零新成员）：T-74 市场时钟 L3 袖激活表由设计直觉表（MARKET_CLOCK_COMBO s0 v1.0 SLEEVE_TABLE）升格为画像证据驱动表（O-1342 §三原令）；证据源=T-81 slice-1 已发放 17 卡（results/strategy_scorecard.json profile_cards，prereg=PROFILE_CARDS_P1 v1.0.1）。
> 账本政策：`append_ledger('L3-ACTIVATION-EVIDENCE', 0, ...)` **+0**（读数面非试验，slice-1 范式）。

## §0 身份与范围

- 载体=`scripts/market_clock_call.py` 扩展（L3 面）；产物=`results/market_clock/l3_activation_table.json`（八格全表）+ CALL 面 `active_sleeves` 改证据驱动输出。
- 八格=4 政体 × 2 热度（GREEN/YELLOW/ORANGE/RED × COOL/HOT），格键 `STATExHEAT` 与画像卡 `heat_cells` 逐字对齐。

## §1 袖→证据成员映射（申报制·全既有件引用·禁新编）

| 袖 | 证据成员卡 | 依据（既有件） |
|---|---|---|
| offense 趋势/动量袖 | AGGR-OFFENSE、AGGR-CONC-TOP2、AGGR-REGIME | T-56 进攻实验室家族=唯一进攻构造在册账户；STYLE_CORPS §3 进攻军 0 员在册如实披露 |
| grid 网格袖 | （无成员） | T-78 grid_sleeve_p1 0/5 生存者判负=族证伪，结构性不激活 |
| mean_reversion 均值回归区间袖 | VOLATILITY-CE-01 | 震荡专家双面印证（PROFILE_CARDS §7）；t22 震荡段全 PASS=STYLE_CORPS §5 震荡军段门禁证据 |
| satellite 游资题材小卫星 | （无成员） | T-57 野路子 0 存活者（判负），结构性不激活 |
| divlowvol 红利低波底仓 | （无成员） | CN-DIV-LOWVOL-ROT 批在飞（R250 冻结未跑），结构性不激活（in-flight） |
| airdefense_cash 防空军现金腿 | 结构性现金（非回测面）+ 策略腿成员=COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01 | STYLE_CORPS §3 防空军主力名册（地量/金针/阳包阴/复合系）；现金腿按构造激活不主张证据 |

- 映射覆盖披露：B_MAXDIV=军内分散法（MSG-1958 角色调整）非袖成员；ALLOC 族=配置构造面非袖成员——两者不进袖映射（基准/构造面如实排除）。
- 无成员袖（grid/satellite/divlowvol）=结构性状态标签（FALSIFIED / NO_SURVIVORS / IN_FLIGHT），全格不激活，不因格证据翻转。

## §2 判据线（跑前冻结·FROZEN）

1. **格级证据门**：袖在某格 evidence-activated ⇔ ∃成员卡 `heat_cells[格].verdict == PASS`（格级证据=该状态分样本来证，O-1342 §一.3）；证据矩阵=6 袖×8 格全量呈报（含设计未提名袖的格证据读数，仅披露不激活）。
2. **激活交集律**：`activated`（CALL/表内激活位）=设计提名（SLEEVE_TABLE 该格袖集）∩ 证据门（§2.1）——证据门只降级不添袖（路由切换=11-01 月界目标，STYLE_CORPS §7 过渡纪律）；证据-PASS 而设计未提名的袖=表内披露行非激活行。
3. **fail-closed 降级**（O-1342 §一.4 + PROFILE_CARDS §3.5）：提名袖成员格无证据（缺格/NO_EVIDENCE）=NOT_ACTIVATED_NO_EVIDENCE；成员格有证但全 DEAD_ZONE=NOT_ACTIVATED_DEAD；证据面缺席（profile_cards 不可读）=全部**证据门袖** NOT_ACTIVATED_EVIDENCE_FACE_MISSING（§2.4 结构现金腿不在此列，按构造律保留）。
4. **RED 行构造律**：现金腿=STRUCTURAL_CASH（按构造激活，L5 帽 20% 不破）；策略腿成员 RED 格证据=NO_EVIDENCE（窗内零 RED 日）→ 策略腿 NOT_ACTIVATED_NO_EVIDENCE；RED 行禁题材卫星沿用。
5. **设计表保留**：SLEEVE_TABLE 设计基线逐字保留于产物 `design_sleeves` 字段（升格非删表，追溯面）。
6. **L1/L2/L5 零改动**：政体/热度/板块/仓位阶梯面不动（O-1342 只令 L3）。
7. 自洽门：证据驱动表内每格成员计数与 profile_cards 原始 verdict 逐字恒等（产物自带 per-member verdict 快照，禁中间改写）。

## §3 跑前预测（写死于跑前）

1. 当前格 ORANGE_COOL（2026-09-24）→ 证据驱动激活集=空（ORANGE 零日构造性 NO_EVIDENCE），CALL 首读=「零袖激活 fail-closed」诚实页。
2. GREEN_COOL：offense ACTIVATED（3/3 PASS）；grid FALSIFIED。
3. GREEN_HOT：offense ACTIVATED（OFFENSE/REGIME PASS，CONC-TOP2 DEAD）；satellite NO_SURVIVORS。
4. YELLOW_*：mean_reversion ACTIVATED（VOLATILITY 两格 PASS）；grid FALSIFIED。
5. RED_*：现金腿 STRUCTURAL；四策略腿成员 NO_EVIDENCE。
6. 全表 8 格无任何全格激活主张（万金油禁令，O-1342 §一.3）。

## §4 产物

- `scripts/market_clock_call.py`：SLEEVE_EVIDENCE_MAP（§1 冻结映射）+`_l3_evidence_table()`+CALL 面接线+selftest 合成夹具腿。
- `results/market_clock/l3_activation_table.json`：八格×袖全表（design_sleeves/members/per-cell verdicts/status + meta=evidence_cutoff/prereg sha16/来源 batch）。
- CALL-*.md/JSON：`active_sleeves`=证据驱动（激活袖串行+不激活诚实行），`l3_evidence` 结构面入 JSON。
- 正典升版：MARKET_CLOCK_COMBO v1.2（§1 L3 行证据驱动注记，CEO 令 O-1342 §三=立法依据）。
- 轮报告回执+T-81 progress 行+CODELY.md（如有坑律）。

## §5 跑后实证（跑后回填·一次定稿）

- 发放：八格全表落 `results/market_clock/l3_activation_table.json`（meta evidence_cutoff=2026-09-24，source=PROFILE-CARDS-P1/T-81，prereg sha16=58b6cd8bab36a805）；CALL 面 active_sleeves 证据驱动 4 行（当前格 ORANGE_COOL）；selftest 8/8；幂等复跑字节恒等（sha16 4c68e3f130e0b372 两跑一致）。
- 预测对账（§3 五条全中）：①ORANGE_COOL 零激活 fail-closed=对（grid FALSIFIED+mean_reversion NO_EVIDENCE+divlowvol IN_FLIGHT 三行+零袖汇总行）；②GREENxCOOL offense ACTIVATED 3/3 PASS=对；③GREENxHOT offense ACTIVATED 2/3（CONC-TOP2 DEAD_ZONE 如实携带）=对；④YELLOW 两格 mean_reversion ACTIVATED（VOLATILITY PASS）+grid FALSIFIED=对；⑤RED 两格现金腿 STRUCTURAL_CASH+策略腿成员全 NO_EVIDENCE（RED 零日）+卫星禁令沿用=对。
- 附加读数（表内披露非激活行）：airdefense_cash 策略腿成员在 GREEN/YELLOW 格有证（bear 专家跨州 PASS）但设计未提名=披露行非激活行（激活交集律 §2.2 生效）；mean_reversion 在 GREENxCOOL 有证未提名同披露。
- 万金油面：全表 8 格无一袖全格激活主张；三无成员袖（grid/satellite/divlowvol）结构标签全表恒定不因格翻转。
- 正典升版：MARKET_CLOCK_COMBO v1.2（§1 L3 证据化注记+变更记录）；CALL canon 字段随升。
- slice-3 指针：四必报分层（CI 宽度/独立窗计数按状态分层入判据）+ 月界 11-01 路由切换呈报面（STYLE_CORPS §7 过渡纪律）。


## 变更记录

- v1.1 (2026-09-26 R265 bm-b)：divlowvol 结构标签状态刷新——IN_FLIGHT「runner pending」→JUDGED_NEGATIVE（CN-DIV-LOWVOL-ROT 0/4 G1'v2 判负 bm-a R252 实况）+状态面引用改指 strategy_scorecard.json landing_hooks（LANDING_HOOKS_P1 §2.2 契约首例）。**状态读数更新非判据变更**：§2 判线（证据门×提名交集×无成员袖全格不激活不因格证据翻转）零改动；§7 跑后实证中的 IN_FLIGHT 字样=当时历史实况留档不改。
- v1.0 (2026-09-26 R255 bm-b)：跑前冻结（O-1342 §三激活表证据化；判线全冻结于跑前）。
