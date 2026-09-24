# REGIME_ENFORCE_WIRING 预注册 · T-2026-09-24-21（跑前冻结）

> 批类=**执行保真验收批（tool-validation·风控+交易 lane）**——零 α 主张、零试验格、`ledger_trials_added=0`（PAPER_GUARD_DUAL_RAIL T-20 / CASH_LEG T-09 / cost_v2_gates 同源先例）。本件冻结于实现之前；跑后只许回填 §7 占位，禁改判据。
> 权威链：CEO 令 **O-20260924-1325**（REGIME_GUARD v3 enforce 提案=批准实装，三条件随行）→ 提案原文 `research/ENFORCE_PROPOSAL_REGIME_GUARD_V3.md` → 票面 T-2026-09-24-21 → 本件。
> 认领：F-04 MSG-20260924-1345-bm-b-claim-T21 先行 + 票据 claimed @ commit 53ce2ec（r98）。

## §0 批件身份

- 批名/批号：REGIME_ENFORCE_WIRING / 0 试验格（验收门 G0-G5 为判定门非统计门；不产生 N_eff——注册面零触碰）。
- 部门归属：dept:风控（防线立法执行面）+交易（paper 记账面消费）。
- 截止纪律（O-1325 条件 2 票面绑定）：**实现完成于 2026-10-01 前**；滑期=与 T-20 同步升级 GM 做月界选择（节点自决权不含改月界）。
- 算力预算：v3 窗口重放（build_bench+维度序列+state_replay）秒级 + paper 六员生产跑 ~分钟级 + 合成 fixture 验收 ≈ **<3min，轮内可完成**；批报告带 audit 段。

## §1 α 机制段【N/A 声明——防线执行面非信号面】

四选一均不适用：本批不产生任何新信号/策略函数/因子，只把**已校准过门的 REGIME_GUARD v3 状态机**（T-10 全弧：v3 三门 PASS）接入前向纸盘记账，属防线响应矩阵的执行层接线。**D6 同族相关性准入：N/A**——零新策略函数；在册 6 员评估语义仅记账面变化，注册证据零触碰（G1 硬门）。

## §2 必随披露（O-1325 条件 3 逐字随票）

**G2 低统计力注记（REGIME_GUARD_VALIDATION_V3 §4.2 小样本标注条款原文触发）**：ORANGE 回合数=1（main=1 < 8）——G2 为机械 PASS，橙级误报率 0.0% 系单回合样本，统计力不足；本 PASS 判定不因小样本回撤，但提案裁决必须知情此点。**本注记逐字随票、随本预注册、随法文件 enforcement-state 节**；10-31 首月包必报 v3-enforced 纸盘增量 vs shadow 增量（诚实双轨）；月度裁决窗直至 2026-10-02（7 天否决窗延续）。

## §3 冻结设计【核心——实现轮逐字执行】

### 3.1 旗标机制（live/paper.py 加性）

- `regime_guard_context(mode)` 加性扩展：mode=`enforce` 自本批起为**合法态**，需同时满足三重门：
  1. `results/regime_enforce_approved.json` 在位（本批交付件：`calibration_pass=true`（引 results/regime_calibration_v3.json v3 三门 PASS）+ `gm_approval=true`（引 O-20260924-1325）+ `active_from="2026-10-01"` + 本注记 verbatim）；
  2. **日期门**：`ENFORCE_ACTIVE_FROM = "2026-10-01"`（硬常量，O-1325 条件 2 月界锁）——该日前任何 enforce 请求=诚实降级 shadow + gate_note（禁月中切换）；该日（含）起 enforce 语义激活；
  3. 环境变量 `BIGMONEY_REGIME_GUARD` 默认 shadow 不变——他机/无环境=零行为变化。
- 现「批准件在位也拒」的双拒语义由本批正式取代（O-1325=票面签名件即「separate signed item」的签名生效）。

### 3.2 v3 状态源（复用禁重建）

- paper 窗口逐日 v3 状态=**import `scripts/regime_calibration` 原语现场重放**：`build_bench()` → `bench_dim_series()`/`breadth_series()` → `raw_series(level_fn=raw_level_v3)` → `state_replay(resolver=resolve_state_v3)`——与校准批同一冻结种子（WINDOW_START 前最后一日 init，prereg V3 §1.2 逐字），**bit 一致性由 G2 门硬验**；禁缓存禁另建状态存储（活数据每跑现算，秒级）。

### 3.3 响应矩阵语义（paper 域映射，REGIME_GUARD §1 原文）

窗口内语义切换点**唯一**=`ENFORCE_ACTIVE_FROM`：该日前日期=legacy 语义（**禁追溯改写**——确定性重算每跑一致）；该日（含）起（且 enforce 三重门全开时）应用：

- **ORANGE/RED 日=停开新仓**：入场信号被掩蔽（引擎 `fill_guard` 买拒单语义逐字复用 P4-B2：pending 丢弃不重试；卖顺延/退出机零触碰——「红不强平既有仓」原文）；
- **YELLOW 日=新仓名义 ×0.5 + 禁加仓**（paper 域无加仓路径=单次入场制，如实注记）；
- **RED 日新资金全额现金停泊=paper 域结构性惰性**（INITIAL_CASH 固定、无新增资金流——该条款归实盘执行闸门，如实披露非本批实现面）；
- **A 轨铁律**：`anchor_gate` 永不接收任何掩蔽/旗标（T-20 A 轨同款）；hr.py、firm/traders 注册字段零触碰；x2 看护注册期种子恒 legacy。

### 3.4 双轨记录（提案过渡期条款：并行留痕 1 个月）

paper JSON `regime_guard` 块加性升级：`{mode, active, gate_note, v3_state_tail（窗口末 N 日状态）, enforced:{active_from, days_enforced, entries_blocked, entries_halved}, shadow_ref:{state,asof}（v1 live 现值）}`——自激活日起 enforced 计数器与 shadow 参照并行留痕；10-31 月度包读取此块出「v3-enforced vs shadow 增量」必报件。

### 3.5 live 探测器 DARK 部件（O-1325 条件 1 后半）

- `scripts/market_regime.py` probe **维持 v1 shadow 零耦合**（本批对 probe 运行路径零改动）；「v3 切换部件」=3.2 重放通路（交付即 DARK）；probe 实切 v3=**GM 交付后复核**独立动作，非本批运行时效果。

### 3.6 法文件接线（T2·7 天否决窗续至 2026-10-02）

- `firm/risk/REGIME_GUARD.md` 增 **enforcement-state 节**：批准链（O-1325）、激活门（10-01 月界+T-20 同落）、响应矩阵 paper 域映射、§2 注记 verbatim、10-31 必报条款；iron_rules 指针括注同步；science_audit C6 指纹联动核验（阈值零改动预期——THRESHOLDS 字典不动，C6 应保持绿，如红则修联动面非阈值）。

## §4 数据与成本口径

- 面板：core48 `data/daily` + 510300 日历（live/paper.load_core 与 market_regime 现行面）；v3 重放输入=活数据照常增长（生产 accrual 面）。
- **evidence_cutoff=2026-09-23**（前向锁盒 D2；验收对照 JSON 顶层 `science_gates.cutoff_meta` 键）。
- 成本口径：V1 legacy FeeSchedule（13bp）零触碰（铁律）；掩蔽与 CostPatch 正交（x2 滚动腿语义不变）。

## §5 跑前预测（实现轮对照，禁跑后改）

1. 激活首日=2026-10-01 后首个 paper 跑；9 月残月窗（09-23→09-30）enforce 请求=诚实降级 shadow，`entries_blocked=0`（日期门未开）。
2. G2 一致性门=paper 侧重放与校准批重放在重叠日期 **bit-exact**（同一代码路径同一种子）。
3. 激活后首窗内（若无危机）`days_enforced` 主要为 YELLOW（v3 校准读数：ORANGE/RED 合计 12.01% 史占比，2026-09 时点=ORANGE 1 状态日）；`entries_blocked` 期望 0-个位数。
4. 全部验收门（G0-G5）首跑全绿的置信度 ~70%（加性接线的典型风险=合成 fixture 时钟注入面与 x2 块字段交互——G3/G4 若红按坑律修实现禁改判据）。

## §6 占位纪律

§7 跑前为空；跑后回填。**写数字即造假**（PA_LHB §6 坑律）。

## §7 实现与验收留痕（跑后回填）

（空）

## §8 复盘条款

- 实现轮=本件逐字执行；任一门红=修实现禁改判据；滑期=与 T-20 同步 defer+升级 GM（O-1325 条件 2）。
- 他机禁自启 enforce 接线（MSG-1305-ALL 在效）；本批产物落账=票据 done+result_ref。
## §7 实现与验收留痕（跑后回填）

**实现轮=r99（bm-b，2026-09-24）——全弧一次定稿，G0-G5 全 PASS。**

- **引擎加性件**（engine/backtester.py，O-2250 加性铁律）：`entry_size_scale`（date-indexed Series，执行日名义乘子，作用于 sizing 基数之后/成本 v2 ADV 帽之前；缺失日=1.0；clip[0,1]——响应矩阵只减半不加杠杆）+ `fill_guard_buy_dropped` 计数器（任何 fill_guard 在场时 metrics 增键，None 路径永不发射）+ `scaled_entries`（scale<1 成交计数）。legacy 逐字节不变实证=G1a noop 等价（全 1 scale/全 True 守卫=行为与基线全同）+ G1b 生产双跑字段级奇偶。
- **paper 接线**（live/paper.py）：`_load_approval`/`v3_state_series`（§3.2 import-replay：build_bench→bench_dim_series→breadth_series→raw_series(raw_level_v3)→state_replay(resolve_state_v3)，冻结种子，无缓存）/`_enforce_mask`（决策日状态门控次一执行日：buy_fillable(E)=state(E-1)∉{ORANGE,RED}；scale(E)=0.5 iff state(E-1)=YELLOW；**执行日 ≥ ENFORCE_ACTIVE_FROM 才适用=月界前窗口日期恒 legacy 禁追溯改写**；首行无先决=不拦）/`regime_guard_context` 三重门（批准件完整性硬拒→enforce 合法态；**T-05 双拒语义正式取代**）/`update_trader` 双轨块（enforced 计数器+shadow_ref+gate_note）/main 降级路径（窗口末日 < 日期门=纯 legacy 调用+块记录降级注记）。
- **批准件交付**：results/regime_enforce_approved.json（calibration_pass 引 v3 三门 PASS+gm_approval 引 O-20260924-1325+active_from=2026-10-01+**§2 注记逐字**+co-landing 声明+反事实证据链）。
- **S6 请求通道接线**：iteration_prompt.txt live.paper 步改「先设 `$env:BIGMONEY_REGIME_GUARD='enforce'` 再跑」——三机经 git 同享同一请求+同一批准件+同一日期门=语义确定性（防他机无请求→paper JSON 掩蔽/未掩蔽互相覆写漂移）；日期门未开期该请求被诚实降级=零行为变化（G4 实证）。
- **法文件**：REGIME_GUARD.md §6 enforcement-state（批准链/注记逐字/激活门/响应矩阵映射/A 轨/双轨/C6 七条）；iron_rules.md 指针括注同步（数值零改动）。
- **验收**（scripts/regime_enforce_gates.py → results/regime_enforce_gates.json，verdict=PASS）：G0 smoke 23/23；G1a 引擎加性旗标六断言（确定性/全1无操作/全真无操作/键只增/半缩咬合 qty 490.82=981.65/2/买拒计数）；G1b shadow 生产双跑字段级奇偶（ex 墙钟 updated）；**G2 v3 重放 bit 一致**（1632 日窗口全量重放 vs 校准批记录：GREEN 664/YELLOW 772/ORANGE 35/RED 161 逐位、init 2019-12-31 在位、tail=2026-09-23）；G3 掩蔽语义 fixture 七断言；G4 降级路径真数据实弹（env=enforce 全跑：6 员块全降级、days_enforced=0/entries_blocked=0、窗口指标与 shadow 跑逐字段一致、退出码 0）；G5 A 轨（anchor/cost_x2 块跨模式逐字段相同+结构断言 mask 只达 paper_run）；收尾恢复 shadow 正典文件。
- **C6 联动核验**：science_audit run 6/6 OK（阈值零改动预期兑现，C6 绿）。
- **x2 腿口径裁定（如实披露）**：cost_x2_check 维持 legacy 语义帧——x2 看护对照的注册期种子恒 legacy（§3.3 A 轨行），滚动腿同帧对照才保 probation 信号效度；enforce 掩蔽只落 paper_run 记账面。T-20（bm-a 在制）B 轨按其预注册另行接规则守卫腿，两轴正交、各自披露。
- **坑三条（入册）**：⑴ PS 双引号内 `$env:VAR` 被 PowerShell 变量展开吞名（python -c 内联坑族新变体：变量展开型，非转义型）——**含 `$` 的内联 python 一律临时件**；⑵ noop 等价断言必须剔除加性披露键（scaled_entries/fill_guard_buy_dropped 是「旗标在场即增键」的设计行为，整 dict 比较必假红——判据=行为等价非键集等价）；⑶ qty 粒度 round(,2) 决定半缩断言容差 0.01（1e-9 必假红，J18 自洽坑族新例）。G1a/G2 首跑红=门 fixture 实现层，按「修实现禁改判据」修复后四跑全绿。
