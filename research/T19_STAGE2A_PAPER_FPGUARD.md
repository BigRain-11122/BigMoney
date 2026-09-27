# T-19 STAGE-2A 纸盘前向保护预注册 · consolidation forward-protection guard（跑前冻结）

- 票：T-2026-09-24-19 stage-2a（claimed bm-c r48；stage-1/-2b/-2c 已闭，本件=票面最后一未开面）
- 令链：O-20260924-1325 §二（选项 a guard 式先行批准 + 「前向保护范围必须含边界面，由 stage-2a 前向保护件承接，与 T-20 落地后接力时序不变」）→ T-20 全闭环（bm-a R107·MSG-20260924-1320 边界裁定：T-20 面 EXCLUDES 折算断点保护、bm-c stage-2a 在 T-20 落地后接力）→ 本件=接力件
- 截止律：T-20 spec deadline 条款（2026-10-01 月界前完成、首完整月 10 月自首 bar 起带保护运行、禁月中语义切换）；本件落地窗=2026-09-28（周一），月界前 3 天裕量

## §0 批件身份

| 项 | 值 |
|---|---|
| 批件 | T19_STAGE2A_PAPER_FPGUARD v1.0 |
| 类型 | 工程执行保真面（非 judged 批、非信号面） |
| 载体 | scripts/t19_paper_guard.py（新）+ live/paper.py 加法接线 |
| 数据面 | data/consolidation/registry.json（21 事件/19 员·bit-exact 冻结件·只读消费） |
| 域 | live/paper.py 纸盘前向面（6 在册交易员 paper_run + cost_x2_check rolling 腿）；anchor_gate/x2 注册种子/登记册本体零触碰 |
| 域界注记 | REV-OSC/SYSTEM-V1 活面 harness（个股 qfq 日线域）不在本件范围——登记册=ETF 份额折算域，个股送转股为另一机制且个股面板已 qfq 复权，如实划界 |

## §1 α 机制段【N/A 声明——执行保真面非信号面】

本件零策略信号改动、零判据线改动、零锚点改动；α 机制四选一=N/A（T-20 PAPER_GUARD_DUAL_RAIL §1 同款声明）。

## §2 冻结契约【核心语义——跑前写死】

1. **C1 买入掩码（no-trade 面）**：登记册逐事件 (sym, date) → 买入掩码该格=False（P4-B2 逐字：buy=False 执行日→pending 单 DROPPED）。构造于 prices_full 联合索引（build_guard 同构），全 True 默认；事件日不在该成员面板索引（停牌/非交易日）=跳过并计入 diag（禁盲写）。
2. **C2 卖出面**：**UNTOUCHED**（明确冻结的负决定）。理由：P4-B2 卖出延后语义不能移除断点跳空——延后期间仓位按断点日收盘估值，幻影照常入账；断点跳空的真移除=选项 b 调整面板（O-1325 §二 b 缓议，待 GM 裁）。s5 边界面由 C3 披露承接。
3. **C3 边界面披露（s5 语义修正随行·boundary-inclusive）**：对纸盘窗口逐位置/逐平仓单做越界判定——开仓日 ≤ 事件日 ≤ 估值/平仓日（**两端均含**；s5 实证=断点当日收盘退出承载 8/10 幻影行，边界排除式掩码必漏此形）。命中→forward_guard.consolidation 披露行（sym/event_date/implied_ratio_approx/pct_observed/amplitude_class/position_entry_date/entry-to-event bars）。开仓日导出律=price_index[-(hold_days+1)]（hold_days 自首成交逐 bar +1·含延滞日·引擎零触碰推导）；平仓单 entry=exit_index−hold_days。**reporting-only：marks +0、账本 +0、判据零改**（T-20 deliverable-4 血统）。
4. **C4 组合律**：买入腿=T-20 buy AND T-19 buy（paper_run 内 T-21 regime 再 AND——AND 可交换，三面共存）；卖出腿=T-20 sell **同一对象原样透传**。组合点=live/paper.py __main__ 单点（build_guard 后、update_trader 前）；update_trader/paper_run 签名零改动（披露块=函数内 lazy import 加法块）。
5. **C5 铁律继承**：anchor_gate 永不收任何掩码；x2 注册种子 legacy 只读；登记册 D2 锁盒（本面只读，8 条 pending-announcement 事件的改分类=数据道 stage-2 面，非本面）；engine/exit_rules.py 零触碰；每跑 fresh 构造（T-20 同律：无缓存、登记册新事件自动进下一跑）。

## §3 数据与成本口径

- 面板=live/paper.py prices_full（load_core 原面）；成本模型/仓位/出场优先级零触碰。
- 掩码列=登记册成员 ∩ 面板宇宙（缺列跳过计入 diag）；掩码 reindex 后缺行 fillna(True)（paper_run 既有语义）。
- registry 元数据进 diag：events_total / events_in_universe / buy_blocked_days / skipped_non_panel。

## §4 验收门（跑前写死·全绿=完成）

- **G1 合成掩码精确性**：合成面板+合成登记册→掩码恰在事件 (成员,日) 格 False、他处 True；非登记册成员恒 True；非面板日禁写。
- **G2 实数据零漂移**：真登记册最新事件 2026-07-07 < 6 交易员纸盘窗起点（created 09-23+）→ 掩码在全部纸盘窗 all-True；组合守卫==T-20 守卫（buy 逐格相等、sell 同一对象）；events_in_window=0。
- **G3 边界披露四形**（合成）：held-through（entry<D<mark）✓ 标记；断点日平仓（entry<D==exit，s5 8/10 形）✓ 标记；断点前平仓（exit<D）✗ 不标；断点后开仓（D<entry）✗ 不标。
- **G4 组合恒等**：composed.buy == t20.buy & t19.buy；composed.sell is t20.sell。
- **G5 接线零侵入断言**：update_trader/paper_run 签名 diff=0；anchor_gate 调用点 diff=0；selftest 全绿（live.paper selftest + 本件 selftest）。
- **G6 实弹接线跑**：S6 链 live.paper 实跑→6 员 state 含 forward_guard.consolidation 块（enabled=true、events_in_window_n=0、crossing_rows=[]）、其余面与接线前一致（加法键唯一差异）。

## §5 跑前预测（写死于实现前）

- P1：当前真登记册（21 事件全 ≤2026-07-07）对 6 员纸盘窗（≥2026-09-23）零命中→G2 零漂移必过；consolidation 披露块空行集。
- P2：未来登记册追加窗内事件后（数据道 stage-2 追加面），下一跑自动生效：该日买单 DROP + crossing_rows 出行（fresh-per-run 结构保证，合成测试证形）。
- P3：本件不改变任何 10-31 判据口径；首完整月保护自首 bar 在位（月界条款满足）。

## §6 批件纪律

prereg 先冻（本件）→ 同 commit 实现冻结；selftest 离线密闭；负结果如实；月界（10-01）前完成；禁改 T-20/T-21 已冻语义。

## §7 跑后实证【实现轮回填】

- **实现轮**：bm-c r129（2026-09-28 03:5x·月界前 3 天裕量内）。
- **载体**：scripts/t19_paper_guard.py（build_consol_buy_mask / compose_fill_guard / crossing_rows / selftest）+ live/paper.py 两处加法（__main__ 组合点 + update_trader 披露块）。
- **G1-G4 selftest 4/4 PASS**（合成掩码精确性=事件格恰 False·非面板日/非面板员跳过计数；边界四形=held-through✓/断点日平仓✓（s5 8/10 形）/断点前平仓✗/断点后开仓✗；组合恒等=sell 同一对象透传）。
- **G2 实数据零漂移 PASS**：真登记册最新事件 2026-07-07 < 最早纸盘窗 2026-09-23（6 员 created 实读）→ 掩码全窗 all-True，组合守卫==T-20 守卫。
- **G5 接线零侵入 PASS**：update_trader/paper_run 签名 diff=0；anchor_gate 调用点零改动；live.paper selftest 全绿（anchor 6/6 含）+ 全仓 smoke 25/25。
- **G6 实弹接线跑**：本轮无新 bar（09-25=中秋节休市·面板 cutoff 09-24）→ live.paper 未触发，G6 眼下顺延至首新 bar 轮（今日 15:30 后/次轮）跑——零漂移语义下预期=6 员 state 仅多 forward_guard.consolidation 加法块（events_in_window_n=0/crossing_rows=[]）。跑后在此行补 G6 判定。
- 预测对账：P1 零漂移=G2 已证；P2 future 生效=合成证形+fresh-per-run 结构；P3 判据零改=码面 diff 断言（无判据文件触碰）。


## §8 批后复盘

（跑后填）
