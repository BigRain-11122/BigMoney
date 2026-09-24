# T22_VIRTUAL_TIMEPOINTS 预注册（T-22 · CEO 令 O-20260924-1532 + GM 派工 O-20260924-1730 §三.1 分片接管）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。

## §0 批件身份【跑前】

- 批名 / 批号：T22_VIRTUAL_TIMEPOINTS（虚拟时间点滚动全起点大验证）。**批内格数＝每格计入 N_eff**：一格=一个（起点 × 交易员 × 成本面）引擎跑（窗口切片取自同一次跑，不另计格）；被动基准窗=每起点一格（P-5 记账先例）。预估：legacy 轴 1,255 起点 × 6 员 × 2 面 = 15,060 格 + 1,255 被动窗；deep 轴起点数以枚举实数为准（~2.8k 起 → ~33.6k 格 + ~2.8k 被动窗）；全批预期 4.9 万+ 格（票面 "expect 10k+ scale cells" 达标）。扩容即买单：窗口族/成本面/起点集任何扩容按新格数入账。
- 认领：F-04 先行——MSG-20260924-1745-bm-c-t22-shard-takeover（bm-c 分片接管声明：bm-b 认领在册但心跳停滞 15:45 起 80min+，O-1730 §一.5 健康机接管条款）＋票 T-2026-09-24-22 note 同步；bm-b 恢复后按 checkpoint 归队续跑（本批 checkpoint=cells_*.jsonl 逐格键）。
- 部门归属：dept:研究+数据（票 owner dept=研究部+数据部；执行=bm-c）。
- 算力预算：legacy 轴 ~15k 格 @worker_cap()（floor(32×0.8)=25，RAM 守卫 min(cap, free/0.5GB) 实取 ~20-25 workers）BelowNormal 池（O-1136）≈ 20-30 分钟；deep 轴下轮起（~33.6k 格 ≈ 40-60 分钟）；>10min 批已后台化+跨轮 checkpoint（R41）；批报告必带 audit 段（finalize 步以 compute_audit 实跑采样回填——无 audit 段不入账本）。

## §1 α 机制段【D6——无机制段=批不受理】

- [x] **本批=在册 6 员鲁棒性分布复检，非新 α 主张**（P-5/P-5B 先例体裁）：6 员（COMPOSITE-CE-02/ENGULF-CE-01/NEEDLE-DE-01/VOLATILITY-CE-01/DROUGHT-CE-01/CE-02 系在册 paper 级全员）机制主张与 G2 注册档案已在册（STRATEGY_LIBRARY.md v1.0＋各员注册件），本批零新策略函数、零参数改动，机制论证引用在册档案不重复。四选一归属：各员各异（风险溢价/行为偏差为主，见在册档案）；本批不引入新机制主张。
- 同族相关性准入检查【D6】：零新函数入批 → 无新 corr 对；6 员间日收益 corr 以 P-5B sleeve-tag 口径在册（全员 <0.7，注册档可查）；本批不动成员集。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：core48（legacy 轴=2020-01-02 锚定全量面板，46-48 员 listed-at-start 逐起点实测）；deep 轴=T-18 增长成员面板（2013-06-17 起·Money02/data/cache/t18_deep_panel·GA-GF 门全过 r101，GF 硬门已由 T-19 stage-3（r59·O-1310 s3 probe-replicated SATISFIED）解除，adjusted_view 21 因子可 date-join）。
- 窗口与 evidence_cutoff（前向锁盒 D2）：legacy 轴 cutoff=**2026-09-23**（面板末日·今晨 daily 已收）；deep 轴 cutoff=**2026-09-22**（t18 manifest 冻结口径）；cutoff 后新 bar 锁定不回流本批；结果 JSON 顶层带 science_gates.cutoff_meta(cutoff)（finalize 步写入，缺字段=VIOLATION）。
- 数据完备门（不过门禁跑批）：①面板可载+末日=cutoff；②6/6 员 anchor_gate 全 PASS（锚定漂移=批作废 exit 3，P-5 契约）；③起点枚举≥100（legacy 实测 1,255）。

## §3 方法学【冻结】

- 信号定义：在册 entry builders（SIGNAL_BUILDERS 全面板因果构建·warmup 用过去收盘）+ 在册 exit_overrides（ExitPatch）；参数零改动。滞后规则：信号日→次日执行（engine T+1 契约，禁未来数据）。
- 起点枚举（全枚举·无抽样·无 seed）：pos ∈ [WARMUP_TD=252, len−W6M]，且 listed(pos) ≥ MIN_LISTED=24（P-5 s2 口径）。窗口族 {6m=126, 12m=252, 24m=504} td；每格跑一次 24m 引擎跑，6m/12m 切片取自同一权益曲线（P-5 先例）；partial 窗（不足整窗）如实打 partial 旗，主判读用全窗子集并行披露。
- null 对照：**被动基准=EW buy&hold of listed-at-start members（同窗等额）**——beat-line 即 null 比较（P-5/P-5B 先例体裁，本批为分布复检非 IC 批，无随机 null 抽样）；全枚举确定性 → seed N/A（如后续加随机 null 另登记 SEED_REGISTRY）。
- 成本口径：base 面=**V1 legacy 13bp×2 压测**（P-5 同口径）；x2 面=CostPatch(2)（成本乘子=2·ce_transfer/combined_exit/lowchurn 屏 G2-proven 用法；COST_X2_RATE=0.0026082=记录口径率非乘子）〔**2026-09-24 17:3x 工程勘误（跑前冻结件透明修正·判据零触碰）**：首跑 x2 面误传 CostPatch(COST_X2_RATE)=0.26% 成本乘子（近零成本）——被「x2 收益>base」异常捕获于 ledger 前；该 7,530 格全数作废改名 invalid_cells_legacy_x2_c1_costbug.jsonl 隔离（不入账不进 finalize 读取面），x2 面以正典乘子重跑为唯一产数跑（r55 P-A1 run#1/run#2 双跑留痕同律）；base 面 7,530 格无 CostPatch 不受影响〕；双面并行跑，x2=生存门（P-6/G2 口径「×2 存活」）。
- 政体分段（披露维度·非门）：510300 收盘 vs MA200 三态代理——bear=close<MA200；chop=close≥MA200 且 MA200≤其 20bar 前值；bull=close≥MA200 且 MA200 升；MA200/前值无效期=na（诚实桶）。**本代理为披露用 PROXY，与 REGIME_GUARD v3 重放（2020+ 专有）不同源，不参与任何门判。**
- 账本：finalize 步 science_gates.append_ledger(batch_name, batch_trials=实际格数, file_name, evidence_cutoff)——禁手抄 prev；shard 逐格 checkpoint（results/t22/cells_*.jsonl·机本地·gitignore），跨机最终聚合走 finalize 产物（小 JSON+CSV），大文件不入 git（TRANSFER 律）。

## §4 判据【跑前写死·禁看结果调线】

- 主判（P-5/P-5B 冻结口径·票面指定）：**每员每面每窗 beat_rate ≥ 0.70 且 min_dd ≥ −0.35**（beat=同窗引擎收益>同窗被动收益）。primary 读数=**base 面 6m 窗**；12m/24m 与 x2 面为并行披露面。x2 面=生存门：任一员在 x2 面跌破 beat/ dd 线即在批报告标 x2-fail（不影响 base 主判，但入 T-28 稳定盈利定稿的减分项）。
- 政体分段：bear/chop/bull（+na）各段 beat_rate/min_dd 单列披露；**政体依赖发现（P-5B 6/6 FAIL pooled 0.6067）的对账假设**：分段读数与全段 pooled 的背离方向如实披露。
- D7 四必报（每员×面×窗）：OOS 笔数（窗内 trades）/覆盖年数（起点跨度）/独立政体窗数（分段桶数）/CI 宽度（beat 数二项 bootstrap 95% CI，B=2000，冻结）。
- 本批**不跑 G1'/G2 注册门**（零新成员；再注册须另行预注册）；本批 FAIL 不触发在册员降级（月审/10-31 首检线不动）——本批=分布证据供 T-28 定稿与月审消费。
- 诚实边界（P-5 承袭）：6 员在册后选样 → 本批是鲁棒性分布复检**非新样本外**；相邻窗重叠（全枚举连续起点 6m 窗重叠 ~80%）→ 有效 n < 格数，CI 报有效 n（相邻去相关：25td 间隔子采样重算 beat_rate 作稳健性披露）；2025+ 窗读数带 OOS 折扣注记；真前向证据恒=paper 管道。

## §5 跑前预测【写死于跑前·≥3 条】

1. base 6m pooled beat_rate 落 [0.55, 0.70]：P-5B K=50 实测 0.6067，全枚举加入牛段密集起点后大概率仍低于 0.70 线（政体依赖发现在全量上重现有余）→ 预测多数员单员不过 0.70 线。
2. 分段方向：bear 段 beat_rate 高于 bull 段（防御型技能在弱政体跑赢被动=O-1600 切片同向发现）；chop 段最弱（双向摩擦）。
3. x2 面 6m beat_rate 相对 base 退化 <10pp（在册员低换手设计）；若 >10pp 即成本敏感红旗如实入报告。
4. legacy 轴 ORANGE 窗（2025+，即 paper 同窗）beat_rate 为全批最高分段（O-1600 初答 5/6 正收益同源预期）。

## §6 产物

- script：scripts/t22_virtual_timepoints.py（selftest 10/10 离线+24 格实弹 smoke 双验证过；run/status/selftest 子命令）。
- 产物：机本地逐格 checkpoint=results/t22/cells_{axis}_{face}_{shard}.jsonl+done 标记+logs/（gitignore）；finalize（收割轮）=results/t22_virtual_timepoints.json（顶层 evidence_cutoff+cutoff_meta+audit 段）+ research/shortline/ 聚合 CSV（小件入 git）＋本文件 §7 回填。
- 分片声明：bm-c=legacy 全轴（shard c1·pos [0,1255)·双面）先行（票 deliverable-5 legacy 控制批无 GF 依赖可先跑）→deep 轴 d-c1（pos [0,1400)）次之；bm-a 若接手=deep 轴剩余分片；bm-b 恢复按 checkpoint 归队（任意分片皆可，键去重幂等）。

## 跑前勘误（2026-09-24 17:4x · bm-a fix-forward · J18 实现修正判据零改动 · commit 随本块冻结）

- **Erratum-1（x2 面）**：§3「x2 面=CostPatch(COST_X2_RATE=0.0026082)」勘误为 **CostPatch(2.0)**。CostPatch 契约=**乘子**（G2 先例：ce_transfer L168/combined_exit_screen L184 皆 `CostPatch(2)`；science_gates 注释原文「mult」）；COST_X2_RATE=压测后单边费率常数（13bp 全套×2≈0.0026082）非乘子。原实现把费率常数当乘子=全部费字段×0.0026（近零费）=压测面反向成超廉价面，污染 §4「x2 生存门」。**bm-c 机已跑的 x2 面 cells 全部作废须重跑**（base 面不受影响；重跑法=删 results/t22/cells_legacy_x2_c1.jsonl 后 `run --axis legacy --shard c1 --faces x2`）。selftest 新增 S5b 方向门（断言 stressed commission==2×base）防回归。
- **Erratum-2（深轴装载缺失）**：runner `_init_worker`/`cmd_run` 原恒载 legacy 面板（axis 参数被忽略）→ 补 `_load_axis_prices(axis)`：deep=T-18 面板窗（manifest 冻结）+T-19 adjusted view 19 只（GF 法：return 面修正）+amount 列按 live/paper.py L135 回退律合成（volume×close，在册 6 员 entry builder 零消费，披露代理）+twin 面字符串日期 to_datetime 归一。深轴实弹探针（dprobe，12 cells）全 PASS：panel 2013-06-17→2026-09-22。
- **事实披露（判据不动，呈 GM 裁定）**：MIN_LISTED=24（§3 冻结·P-5 口径）下深轴 eligible=**1,506**、首起点=**2020-01-02**——T-18 面板 2013-2019 段（约 7 年，含 2015 股灾/2018 熊，深史主轴的立身段）全被 listed≥24 排除，深腿≈legacy 窗的孪生面复检。若 GM 欲兑现 O-1532「深史海量」意图，须另开预注册增订（MIN_LISTED=5=T-18 panel_start 同款下限的子网格，判据同 §4）——**未裁前本批按冻结口径跑 2020+ 段**。
- **撞车史披露**：bm-a r82 曾独立交付同名 prereg/runner 变体（commit 17:32:23，晚于 bm-c 17:23:51）→ 按 fleet/README §4 后到让路+GM 17:35 reconciliation 裁定 superseded（备份 quant/.codely-cli/t22-bm-a-wip-20260924/），bm-a 归并正典：本勘误三件（Erratum-1/2+探针）+d-a1 分片执行即归并动作。bm-b r105（17:29:47/17:33:25）同窗另交付 P-5C 变体批并已发 leg L（16,289 cells，PID 10380）——与正典 T22 legacy c1 重复烧算，**呈 GM 裁定**（bm-a 不裁）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（finalize 轮回填：per 员×面×窗 beat_rate/min_dd/CI、分段表、D7 四字段、与 §5 预测逐条对账、trial 总数与账本 delta。）

## §8 批后复盘【必填·s7-T】

（收割轮回填。）
