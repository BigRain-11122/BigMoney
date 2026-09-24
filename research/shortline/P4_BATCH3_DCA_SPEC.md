# P-4 批三 SPEC：死扛族 #14 补仓摊薄（分批建仓）引擎支持评估与批测设计 · 先 spec 后实现

> 令链：CEO O-20260923-1705（风格动物园）→ zoo #14「新写（需引擎分批建仓支持评估——先 spec 后实现）」→ 认领 MSG-20260925-0335-bm-b（F-04 先行）。
> 本件性质：**spec 一次定稿**（r138 bm-b）。引擎代码本轮零改动；实现+批测=后续独立票+预注册（本件 §6 rails 即未来 prereg 骨架，按 `research/PREREG_TEMPLATE.md` 冻结后才能开跑）。
> 铁律适配：`engine/exit_rules.py` 退出优先级/T+1/成本模型零触碰（分批=纯入场侧扩展）；engine additive iron rule（新旗标默认关=legacy 路径字节恒等，T-03/T-09/T-21 先例）；红线框架内（单票≤10%/总仓≤80%/−8% 止损照走——zoo §三头部注记「不扛到毁灭」）。

## §0 批件身份

- 批名：P4-B3-DCA（死扛族 #14 补仓摊薄）；本件=spec，批跑另开预注册 `P4_BATCH3.md`。
- 认领：bm-b loop round 138（MSG-20260925-0335）；部门归属：dept:研究（风格族研究）+dept:工程（引擎支持评估）。
- 前批状态：P-4 批①（bm-b r35，诚实 0 候选+sleeve2）、批②/2A、P4_QUEUE mini 皆 done——批③为 zoo P-4 队列唯一未开工项。

## §1 引擎能力评估（结论：现引擎**不能**分批建仓；缺口=入场侧三处，均为加法式可扩展）

实证（`engine/backtester.py` r138 现行版逐点）：

1. **双重封锁加仓**：执行环 `if sym in positions: continue`（pending 入场执行段）＋ 队列环 `if sym in positions or sym in pending_entries: continue`（收盘信号段）——持仓期间同 symbol 一律禁再买。单次全仓入场是构造性行为，非参数可调。
2. **ExitState 无分批账本**：单一 `cost_price`/`quantity`；分层仅存在于**退出侧**（`close_fraction` 分档减仓+`tier_reached`）。入场侧无 tranche 记账面。
3. **持仓与 T+1 无碍**：加仓=纯买入，不触 `hold_days==0` 当日禁卖守卫（仓位已 aging）；`max_positions` 槽位按名计数（非资本），加仓不占新槽。分批扩展与 T+1/槽位语义零冲突。
4. **成本与滑点面天然兼容**：legacy 13bp 与 cost_v2（ADV20 三层+1% 帽）均按「每次执行」计——每档加仓=一次独立执行，ADV 帽逐档生效，无需改成本模型。
5. **退出语义读 `cost_price`**（`engine/exit_rules.py` evaluate）：`pnl` 对 cost_price 相对计；止损=`trailing_stop_price>0 ? trailing : cost_price×(1−8%)`。**分批的正确记账=加仓后 `cost_price := VWAP`，退出机制零改动即自然继承**——−8% 止损恒活、止盈分档与 trailing 全部按新均价语义运行（止损线随摊薄下移的固有代价见 §3 披露）。

**结论**：分批建仓=入场侧加法式扩展（新可选参数+新记账规则），与既有六层 additive 旗标（T-03/T-09/T-20/T-21/D5/P4-B2 fill_guard）同构，工程可行性与隔离性俱佳；无需触碰任何退出逻辑。

## §2 加法式扩展设计（冻结——实现票照此施工，J18 修实现禁改判据同律适用）

新可选参数 `staged_entry`（`run_backtest(..., staged_entry=None)`；**None=legacy 路径字节恒等**）：

- `grid_fracs`：资本分割元组，如 `(0.40, 0.30, 0.30)`；**引擎硬断言 `sum ≤ 1.0`**——名预算=legacy 单发的同一 `target_value`（sizing_mode/entry_size_scale/cost_v2 链原样前置计算后，按 fracs 切档）。分批≠加码：名总敞口上限与单发恒等（红线 §3-a 的构造性保证）。
- `add_triggers`：对**首档成交价**的下跌触发档，如 `(0.0, -0.05, -0.10)`；首档=正常入场信号；第 k 档未成交且 `close ≤ first_fill×(1+trigger_k)` 时**收盘排队、次日 open 执行**（与入场信号同 T→T+1 因果，零未来数据；首档成交前不设触发）。`max_adds = len(grid_fracs)−1`（封顶补仓次数=构造性硬帽）。
- **加仓成交记账（逐条冻结）**：`quantity += add_qty`；`cost_price := (旧cost×旧qty + px×add_qty)/(旧qty+add_qty)`（VWAP）；`high_watermark` 自首档起连续 max **不重置**（trailing 语义不变、偏保守）；`trailing_stop_price` **不重置**（未激活则初始止损随 VWAP 自动下移；已激活则维持已锁线）；`hold_days`/`tier_reached` 不变；每档加仓=独立执行（fill_guard buy 拒=该档排队单丢弃计数、触发档为水平态可再排，fill_guard 先例语义；cost_v2 ADV 帽逐档）。
- **新指标键（仅旗标 ON 时出现，G5 键集纪律）**：`num_adds_filled`/`num_adds_dropped`/`avg_cost_first`/`avg_cost_end`/`adds_per_entry`。
- **自检硬门（实现票验收）**：①旗标关=对拍 legacy 字节恒等（同种子全量跑 diff）；②VWAP 记账=手工合成 3 档例逐分核对；③触发因果=截断对拍（close 序列截断后触发集不变）；④红线断言=fracs 超 1.0 必须报错拒跑。

## §3 红线合规映射（zoo §三纪律化框架逐条）

- **a. 单票≤10%**：`grid_fracs` 是同一 10% 预算的**预分割**（sum≤1.0 硬断言），名总敞口上限=legacy 单发恒等——摊薄只是把同一笔钱分时投入，不加码。
- **b. 总仓≤80%**：`max_positions`/`position_size_pct` 机制原样，零变化。
- **c. −8% 止损照走**：P2 止损对 VWAP 恒活（§1-5），任何时点价格≤VWAP×0.92 即全清；**诚实披露**：每成交一档，止损线机械下移（这是摊薄的定义性代价，非规则漏洞）——「不扛到毁灭」由三重构造保证：max_adds 封顶＋预算预分割（总敞口≤10%）＋止损恒活。
- **d. T+1/退出优先级/成本模型**：零触碰（§1-3/§1-4；exit_rules.py 不改一行）。

## §4 α 机制段（未来批 prereg §1 四选一预填：**行为偏差**）

- 论证：超跌触发日的恐慌卖压（处置效应+损失厌恶踩踏）使 ETF 短端价格偏离均衡；网格分批承接的对手方=被迫止损者与非信息驱动抛售者，承接方赚取行为补偿。
- **本批真问题（机制级对照，族内首例）**：P-4 批一已判深水锚定 full-shot=接飞刀（full −0.267/OOS −1.003）＋#17 定投式被判「引擎语义退化≡月度动量轮动」→ **入场工程（分批摊薄）是否足以翻转同一超跌信号族的判负**——staged vs single-shot 同触发配对对照，批的存活判据首先是「判读」而非「注册」。
- 诚实反方：下刀尾险（趋势下跌政体中 −8% 止损必咬合；加仓=向下跌方向集中敞口）——跑前预测必须在 prereg §5 写死此先验。

## §5 D6 同族相关性准入（未来批必跑）

- 最近亲族=oversold_bounce（PROS-OVB-CE-01 sleeve2）与批一超跌 sleeve；若 staged 变体与其日收益 `max|corr|≥0.7` → 按 D6 拒收**注册面**（对照判读面不因此失效——批的知识产出=「分批是否改判」，注册仅是附带可能）。数值与逐对清单在 prereg §1 跑前落死。

## §6 未来批 rails 骨架（常数随 prereg 冻结日复核，禁手抄判线）

- 宇宙 core48；面板截断 evidence_cutoff=prereg 冻结日面板现值（前向锁盒 D2；结果 JSON 顶层 `science_gates.cutoff_meta` 必带）；OOS 2025+ 恒盲；成本=V1 legacy 13bp＋×2 压测（P-4 族先例线）；双退出制 default | CE。
- 网格：2 个超跌触发 × 2 入场制（staged | single-shot 基线）× 2 退出 = 8 格 ×(1×+×2)；随机 null n=50 新 seed 基（`science_gates.SEED_REGISTRY` 先登记）；锚定 6 员硬门；门禁=`science_gates.g1_prime_v2/g2_registration_v2` 共享库（i 线 0.3521/vi 0.4004 在册记录线）；账本 `append_ledger`。
- 单格对（staged vs 单发同触发同退出）为**主判读面**：ΔSharpe/Δ回撤/止损咬合率三列必报；G1' 过线者才进 G2/DSR/PBO 面。
- 实现票面：engine `staged_entry` 旗标+§2 自检四门 → `scripts/p4_batch3_dca.py`（batch2a 范式）→ prereg `P4_BATCH3.md` 冻结 commit → 开跑（>5min 走 runnable_pool，轮内禁内联代跑）。

## §7 状态与指针

- zoo #14 状态翻面：新写 → **spec 已落（本件）**；实现+批测待认领（独立票+prereg 冻结律）。
- 预测节（prereg §5）与跑后对账（§7/§8）归未来批件，本件不预写数字（占位纪律）。
- 回执：r138 轮报告＋CODELY.md 行级追加；认领 MSG 本件头。
