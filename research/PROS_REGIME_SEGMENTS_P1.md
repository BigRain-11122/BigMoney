# PROS_REGIME_SEGMENTS_P1 预注册（T-89 slice-1 · CEO 令 O-20260927-0752「市场阶段适配统计令」·六员分段表已由令内实测提取·本批补 PROSPECT 22 员分段缺口）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> 血统=T22_VIRTUAL_TIMEPOINTS.md（2026-09-24 冻结件）·harness=scripts/t22_virtual_timepoints.py 血统复用；判据 0.70 线+分段定义与 T-22 逐字相同（票面指定 identical）。

## §0 批件身份【跑前】

- 批名 / 批号：PROS_REGIME_SEGMENTS_P1（PROSPECT 22 员政体分段统计批）。**批内格数＝每格计入 N_eff**：一格=一个（起点 × 员 × 成本面）引擎跑（窗口切片取自同一次跑，不另计格）；被动基准窗=每起点一格（P-5/T-22 记账先例）。预估：legacy 轴 1,255 起点 × 22 员 × 1 面 = 27,610 格 + 1,255 被动窗；deep 轴 1,506 起点 × 22 员 = 33,132 格 + 1,506 被动窗（listed≥24 门=T-22 §7 实测口径）；全批预期 ~63,503 格。扩容即买单：窗口族/成本面/起点集/成员集任何扩容按新格数入账。
- 认领：T-2026-09-26-89 claimed bm-b r309（CEO 即时工单=认领与开动同轮·O-1730）；F-04 先行=MSG-20260927-0757-bm-b-prospect-regime-segments（fleet/inbox/ 防双机在制窗口声明）。
- 部门归属：dept:研究+数据（CEO 令统计面·票 owner bm-b）。
- 算力预算：~63.5k 格 @T-22 实测烧速（15,060 格 20-30min @20-25 workers）≈ 2-4 小时 → **>10min 批分离后台+跨轮 checkpoint（R41）**；>5min 算力批按 S3 纪律入 results/runnable_pool.json 提交后返回，轮专注预注册/判定/接线；批报告必带 audit 段（finalize 步 compute_audit 实跑采样回填——无 audit 段不入账本）。

## §1 α 机制段【D6——无机制段=批不受理】

- [x] **本批=已注册候选（PROSPECT level 22 员）政体分段分布复检，非新 α 主张**（P-5/T-22 先例体裁）：22 员（PROS-ANTS/ANTS-CE/BBS/BBS-CE/DOJI/DOJI-CE/DUCK/DUCK-CE/HAM/HAM-CE/IBB/IBB-CE/IMM/IMM-CE/MCB/MCB-CE/OVB/OVB-CE/RSRS-CE/TMU/TMU-CE/VOB-CE）机制主张与 G1'/G2 注册锚定已在 firm/hr TRADERS_DIR 注册件+anchor 面在册（results/prospect_paper/PROS-*.json 22/22 anchor_ok=true）；本批零新策略函数、零参数改动、零新搜索（票面 "pure replay of registered candidate configs"），机制论证引用在册注册件不重复。四选一归属：各员各异（见各自注册件），本批不引入新机制主张。
- 同族相关性准入检查【D6】：零新函数入批 → 无新 corr 对。**变体对重叠披露**：11 族 × (-01, -CE-01) 双变体 + RSRS-CE/VOB-CE 单员 → 同族双变体非独立样本（族内参数变体共享 α 主张），pooled 读数必须按「22 员口径」与「11+2 族口径」双列披露；段读数主表按员逐列（供 MARKET_STAGE_TABLE.md 行级消费），禁把变体对当独立证据双计。批内日收益 corr 全对以本批产物 sleeve-tag 口径实测入 §7（>0.7 对=同族冗余披露非拒收——本批非注册批；晋升消费面（t24_prospect_promotion 第三腿）按员读数天然免疫族内双计）。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：legacy 轴=core48（2020-01-02 锚定全量面板，46-48 员 listed-at-start 逐起点实测）；deep 轴=T-18 增长成员面板（2013-06-17 起·GA-GF 门全过 r101·GF 已由 T-19 stage-3 解除·adjusted_view date-join）——两轴均与 T-22 §2 逐字相同。
- 窗口与 evidence_cutoff（前向锁盒 D2）：legacy 轴 cutoff=**2026-09-24**（跑前探针实测=面板末日·48 员全一致·2026-09-27 探针落定）；deep 轴 cutoff=**2026-09-22**（T-18 manifest 冻结口径·T-22 同源·探针复现一致）；cutoff 后新 bar 锁定不回流本批；结果 JSON 顶层带 science_gates.cutoff_meta(cutoff)（finalize 步写入，缺字段=VIOLATION）。
- 数据完备门（不过门禁跑批）：①两轴面板可载+legacy 末日=cutoff；②22/22 员 anchor_gate 全 PASS（锚定漂移=批作废 exit 3，T-22/P-5 契约；锚源=results/prospect_paper/PROS-*.json anchor 面构造性字节对账）；③起点枚举与 T-22 实测一致（legacy 1,255 / deep eligible 1,506）——不符即先探针定谳禁开跑。

## §3 方法学【冻结】

- 信号定义：22 员在册注册配置（firm/hr TRADERS_DIR PROS-*.json 件内 signal params + exit_overrides）纯重放；信号构建/滞后规则=live/paper SIGNAL_BUILDERS 同源（T-22 §3 契约：信号日→次日执行，engine T+1，禁未来数据）；参数零改动。
- 起点枚举（全枚举·无抽样·无 seed）：pos ∈ [WARMUP_TD=252, len−W6M]，且 listed(pos) ≥ MIN_LISTED=24（T-22 §3 冻结口径 identical）。窗口族 {6m=126, 12m=252} td（票面 base face 判读窗）+ 24m=504 免费切片披露面（同引擎跑权益曲线切片，不另计格——T-22 先例）；partial 窗如实打 partial 旗，主判读用全窗子集并行披露。
- 政体分段（**与 T-22 §3 逐字相同**·披露维度·非门）：510300 收盘 vs MA200 三态代理——bear=close<MA200；chop=close≥MA200 且 MA200≤其 20bar 前值；bull=close≥MA200 且 MA200 升；MA200/前值无效期=na（诚实桶）。本代理为披露用 PROXY，与 REGIME_GUARD v3 重放（2020+ 专有）不同源，不参与任何门判。
- null 对照：被动基准=EW buy&hold of listed-at-start members（同窗等额）——beat-line 即 null 比较（P-5/T-22 先例体裁，分布复检非 IC 批，无随机 null 抽样）；全枚举确定性 → seed N/A。
- 成本口径：base 面=**V1 legacy 13bp×2 压测**（T-22 §3 同口径·注册候选 anchor 同源）；x2 面票面未指定=**不跑**（注册 anchor 已有 x2_full_sharpe 单点面在册，省 63.5k 格算力；若 G2/晋升消费面需要 x2 分段另行预注册扩容）。
- 账本：finalize 步 science_gates.append_ledger(batch_name, batch_trials=实际格数, file_name, evidence_cutoff)——禁手抄 prev；shard 逐格 checkpoint（results/pros_segs/cells_{axis}_{shard}.jsonl·机本地·gitignore），跨机最终聚合走 finalize 产物（小 JSON+CSV），大文件不入 git（TRANSFER 律）。

## §4 判据【跑前写死·禁看结果调线】

- 主判（T-22 §4 冻结口径 identical·票面指定 0.70 线）：**每员每轴 primary 窗（6m base）beat_rate ≥ 0.70 且 min_dd ≥ −0.35**（beat=同窗引擎收益>同窗被动收益）；12m/24m 为并行披露面。**本批=统计面非门面**：主判读数直接供 t24_prospect_promotion 第三腿（beat_rate_6m≥0.70）与 MARKET_STAGE_TABLE.md 行级消费——FAIL 即晋升腿如实判负，无降级动作（PROSPECT 非在册员，观察仓零改写）。
- 政体分段：bear/chop/bull（+na）各段 beat_rate/min_dd 单列披露（22 员×2 轴×段全列）；**角色读出**（CEO 令派工项：per-member role readout）：段画像→军团归属判读（bear 段专才=防空军向；chop 段专才=震荡军向；bull 段专才=进攻军向；全段均衡=全天候向）——读出=描述性判读随数字披露，禁叙事替代数字；与 O-2012 军团制/T-33 军种面衔接（进攻军 0 员缺口的数据面：若 bull 段出现≥0.70 员=进攻军席位候选如实标注，入队仍走供给线纪律）。
- D7 四必报（每员×轴×窗）：OOS 笔数（窗内 trades）/覆盖年数（起点跨度）/独立政体窗数（分段桶数）/CI 宽度（beat 数二项 bootstrap 95% CI，B=2000，冻结）。
- 诚实边界（T-22 §4 承袭）：PROSPECT 22 员=注册候选后选样 → 本批是分布证据**非新样本外**；相邻窗重叠（连续起点 6m 窗重叠 ~80%）→ 有效 n < 格数，CI 报有效 n（25td 间隔子采样重算 beat_rate 作稳健性披露）；变体对族内双计边界（§1）；真前向证据恒=观察纸面管道（t24）。
- 本批**不跑 G1'/G2 注册门**（零新成员；再注册须另行预注册）。

## §5 跑前预测【写死于跑前·≥3 条·含极端日先验】

1. **pooled beat 率落 [0.42, 0.68]**：T-22 在册 6 员实测 legacy pooled 0.578 / deep 0.4812 为锚带；PROSPECT 22 员虽过 G1'/G2 注册门但**未经 beat 线预筛**（T-22 分片未跑=promotion 第三腿 0/22 零行根因），防御/短 K 线形态族为主体 → 预测多数员不过 0.70 线；若 >5 员过线即与 T-22 在册员分布显著背离，须查口径差异（起点集/被动基准/成本面三查）。
2. **分段方向 bear>bull 复现**（O-1600/T-22 同向）：bull 段（deep 轴含 2020 牛起点）PROSPECT 防御族崩塌预期 0.2-0.4；bear 段 0.55-0.70；chop 段居中 0.5-0.7。若某员 bull 段≥0.70 且 n≥30 → 进攻军席位候选（预测：≤2 员，RSRS-CE/VOB-CE 类趋势族概率最高）。
3. **变体对段画像同向**：-01 与 -CE-01 同族双变体段读数方向一致（共享 α 主张）——若同族变体段方向背离 >20pp，即族内参数变体实质分化，如实披露并入族口径读数注记。
4. **极端日先验（三件套(c)）**：面板窗 2020+ 内潜在极端微观结构日=2024-09-24/10-08（政策脉冲单日大幅高开）、2025-04-07（外生缺口）、2026-01-19（D-C 批实证极端溢价日）——本批判据面=整窗 beat 率与 min_dd（非单点 max 检测线），极端日影响路径=①整窗 dd 尾部（牛熊切换窗 min_dd 可能逼近 −0.35 线）②三态代理段边界翻转（极端日后 MA200 相对面切换→分段桶边缘归属敏感）→ 段桶边缘窗如实入 na/边界披露，禁调段定义迎合。

## §6 产物

- script：scripts/prospect_regime_segments.py（run/status/selftest 子命令；T-22 harness 血统复用=import 面复用 t22_virtual_timepoints.py 引擎/装载/账本函数零重实现，成员注入面=level=PROSPECT 注册配置重放；selftest hermetic 离线夹具 r116 律）。
- 产物：机本地逐格 checkpoint=results/pros_segs/cells_{axis}_{shard}.jsonl+done 标记（gitignore）；finalize（收割轮）=results/prospect_regime_segments.json（顶层 evidence_cutoff+cutoff_meta+audit 段+22 员×2 轴×段全表+族口径双列+D7 四字段+corr 全对）+ research/shortline/prospect_regime_segments_results.csv（小件入 git）＋本文件 §7 回填。
- 下游（票 slice-2/slice-3 另行）：research/MARKET_STAGE_TABLE.md 常设件行级消费本批 §7 数字；进攻军席位供给提速评估提案面（GM 署名前禁动队列）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（finalize 于收割轮回填：主判读数表+分段表+D7+预测对账+账本行）

## §8 批后复盘【必填·s7-T】

（一次定稿；预测对账；门禁链损耗账 results/gate_attrition.json 追加一行；回执入轮报告+CODELY.md 行级追加）

## §9 零跑修正案：legacy census 门 1,255→1,256（bm-b r313 · 建批前探针定谳 · 零格已烧合法窗）

- **触发**：r313 slice-1b 建批第一步探针（results/_r313bmb_prospect_probe.py+json）实测 legacy 轴面板（冻结 cutoff **2026-09-24**）枚举起点 **1,256** vs §2③ 转录自 t22 记录的 **1,255** 门——§2 内在张力探针定谳：cutoff 09-23→09-24 扩一 bar 使枚举上界恰 +1 起点（listed 46-48 全程 ≥ MIN_LISTED=24，资格过滤无拦截，探针 listed_uniform [46,47,48] 实证）；deep 轴 1,506 ✓=t22 记录、双轴 panel_end ✓（09-24/09-22）、22 员名册逐字 ✓、anchor 22/22 ✓ 零偏。
- **修正**：§2③ legacy 门 1,255→**1,256**；§0 legacy 格数 27,610→**27,632**（全批预期 ~63,503→**~63,525** 格，被动窗 1,255→1,256+1,506）；runner G-CENSUS 门=新值 1,256 **且**=t22 记录 1,255+1 交叉对账（对账基线披露面保留）；+1 起点=面板扩展合法面（最鲜 6m 窗入批，2026-03→09-24）。
- **反 dredging 合规**：修正时点零格已烧（runner 未建、checkpoint 零行、零包络格）＝非结果驱动，纯探针/数据面驱动（r251/r280 零跑修正先例·DECISION_CHAIN s9.2 同窗）；判据语义零触碰（0.70 线/分段定义/成本面/被动基准原文不动）。
- **append-only 留痕**：§2③ 原文「1,255」字样不删（起草面=t22 记录转录事实留痕）；本节为 §2③ 行的合法修正记录；runner 冻结面=本修正后版本（r313 冻结 commit 先于任何整片格烧，R99 律）。
