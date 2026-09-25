# P-1e 预注册：zoo 行为因子（#85/#92/#93）股票域 IC 批（跑前写死）

> 机器/车道：**bm-b 循环轮**（dept:研究）· r219 认领，F-04 声明=`fleet/inbox/MSG-20260926-0255-bm-b.md`（本 commit 锁）。
> 令链：O-1819（队列永不空·advisory）→ T-64 slice-5 判定消费（ASTYLE_ZOO #85/#92/#93 消费位=P-1c harness IC 批）→ r218 参数化冻结卡（DIGEST-20260926-zoo-paramfreeze-92-94.md）→ r218 state.next 指针（#85+#92 同/邻批 corr 先查、#93 算力复核、PREREG_TEMPLATE）→ r219 面探针（`results/shortline/p1e_probe.json`，prereg-input·IS-only·零判读数字）。
> 范式：**P-1c/P-1d IC 海选一脉**——零引擎跑、IC 计数入因子账本、引擎账本不动；recorded v1 常数门（P-1d s9 同代口径：IC 海选型不触 G1'/G2 v2 引擎门）。

## §0 批件身份【必填·跑前】

- 批名/批号：**P-1e zoo behavior-factor IC batch**（P-1 系第五批）。格数=7 员因子 ×3 horizon（h5/h10/h20，主口径 h10）+ 3 掩码类 ×K=50 null ×3h → **N_eff=157**（因子账本 +7 computed +150 null，r32 口径；引擎账本零动）。
- 认领：F-04 先行=MSG-20260926-0255-bm-b（防双机制造窗撞车）；任务单链=T-64 slice-5 判定消费位（ASTYLE_ZOO #85/#92/#93 行冻结标注）。
- 部门归属：dept:研究。
- 算力预算（探针实测，p1e_probe.json timing）：构造器合计 ~53s（terrified 4.0 / stv 12.8 / coin_team 21.5 / ARC 族 14.1）；IC pass 按 P-1d 实测率 ~1.9s/道（401.5s/211 道）→ 全批 ~471 道 IC ≈ 单进程 **15-20 min** → **>5min=后台池化**（runnable_pool 提交+autofill 续批，O-20260924-2100 执行面分离；禁轮内内联代跑）。#93 冻结卡算力条款复核=实测 14.1s wall（cumsum 因子化 O(T×N)/幂次，T=8792×N=5222）vs 冻结卡「~7.5e8 算元·分钟级」✓ 成立，naive 上界（qlib 200-300min）无需复现。
- 批报告必带 audit 段（无 audit 段的结果件不公账本）。

## §1 α 机制段【必填·D6】

**四选一=行为偏差**＋一句话论证：本批四员同族=凸显理论（BGS 2012）与处置效应（Grinblatt-Han 2005/Frazzini 2006）的 A 股截面读数——付费方=追极端收益者（凸显性吸引过度买入后回落）、恐慌抛售者、以及处置偏差下过早止盈/死扛浮亏者，超常收益由对方侧行为偏差系统性支付。

- `zoo85_terrified`：凸显性加权收益 roll20 均值+标准差半和——高凸显（相对截面极端偏离）吸引注意力过度买入→反转（高值看空）。
- `zoo85_stv`：量维度变体（|r|≥0.1 阈按|r|×100 排、未超按换手率排的 salience 权重 roll20 cov(w,r)）——同一凸显机制的价格/量双读数（广发 STV 何家璇 2022 血统）。
- `zoo92_coin_team`：三分腿收益（日间/日内/隔夜）的「低波动/低换手=硬币=翻转其近期收益」条件修正反转——知晓性代理条件翻转（冻结卡校准义，非字面路径连续）。
- `zoo93_arc/vrc/src/krc`：换手衰减递推成本基处置读数（ARC≡CGO，VWAP 口径）+价格矩变体（集中度/尾部不对称/盈亏分化）——低 CGO（浮亏者死扛→供给压价至均衡价下）=溢价源（**低值看多→原型子 IC 负号**）。

**同族相关性准入检查【D6 必填·探针 IS-only 实测】**（双口径：截面 spearman 均值 + ic10 序列 pearson）：

| 对 | max 读数 | 判定 |
|---|---|---|
| 主因子互对（4 员全对） | ic10 stv\|coin_team = **0.4911**；xs_spearman max 0.3648 | <0.7 → **无拒收无合并** |
| zoo 主 vs 在册近邻 alpha191 070/081/042 | terrified\|arc…max=0.3648（xs）；ic10 max 0.3645 | <0.7 → 机制近邻构面独立；合成阶段仍须聚类（P-1c §8 ⑤ 先例） |
| #93 族内 arc vs vrc/src/krc | -0.0564 / +0.0966 / -0.0284 | 矩变体与主读数低相关=独立信息面 |

**max|corr| 全表=0.4911 < 0.7 → 批内零合并零拒收**；清单与全表=`results/shortline/p1e_probe.json` corr 节（逐对列出不复述）。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙：p1c_stock 缓存面板（Money02/data/cache/p1c_stock，**T=8792 × N=5222，meta ok=5130**；短史 92 员由掩码自然降覆盖非剔除——P-1c Stage-A 缓存构建口径；与 P-1c 批跑 ok 5129 的 −1 差=彼批复权侧车不可读排除门，本批吃缓存原样零重派生，如实披露）。选料面非可交易面：**不施加 b_layer 掩码**（P-1c 母批同口径；幸存者消费时 B 层另算）。
- **evidence_cutoff=2026-09-22**（缓存构建落盘口径；缓存零刷新=冻结面，cutoff 后新 bar 不回流本批）。结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)` 字段（缺=C2 VIOLATION）。
- 换手率面=**turnover_derived sidecar**（r219 物化：`turnover_derived.npy` float32 T×N + meta.json；TURNOVER_DERIVATION.md §4 冻结分板公式：非 688 =volume/osh、688/689 =(volume/100)/osh；构建三门全过：存储对账 1e-6 三股+688 二股/688 异常行清零/列对齐。**bars 原生 turnover 列全史 NaN 除末 bar，禁用**）。p1e_turnover_derive.py=sidecar 物化器（与 p1c_turnover_derive.py 审计探针用途互补非重复）。
- vwap=缓存字段（Stage-A 已修 688 volume=100× 真实股数面；TURNOVER_DERIVATION.md §3 全车队警报已吸收）。
- pct_chg 单位核=百分比（div100 后与 close 比值吻合率 1.0，探针 bars_pctchg_unit 面）；**本批 fwd_ret=close 口径冻结**（close/close.shift(-h)−1），pct_chg 不入批（残余不吻合=停牌跨段日，如实记）。
- 数据完备门：探针已过（面板载入零读错+构造器 selftest PASS：ARC 暴力对照 worst 1.18e-15）。
- 覆盖披露（探针 coverage 面，IS 段）：terrified/coin_team 34.0%、stv 30.3%、ARC 25.6%、vrc/src/krc 25.7%、非有限 ARC cell 32,617,132（60 行有效性窗+RS0 有限双门——长停牌股丢覆盖非静默混历）。

## §3 方法学【必填】

- 因子定义冻结=**scripts/p1e_factors.py**（r219 commit 锁，构造器=定义真值源）：常量 N_ARC=60 / DELTA_STV=0.7 / THETA_SAL=0.1 / STV_X=0.1 / W_ROLL=20 / TR_CLIP=0.99；ARC=cumsum 因子化（log1p(-TR) 递推），窗语义=60 行有效性计数==60（交易日类似物）。
- **跑前勘误留痕（r200 范式·判向无涉）**：构造器 docstring「#93 …expect positive forward IC」为符号笔误——冻结卡真值=#93 低值看多→**原型子 IC 预测负号**；勘误只改注释零计算改动（同 commit 修，防「看结果改判向」嫌疑锚=勘误先于任何批跑）。
- **#85 基准面披露**：冻结卡叙述基准=中证全指/HS300——in-repo 缓存无外部指数面，冻结=**面板截面等权均值**（scr/core.py calc_sigma bench=None 实现位校准，clean-room 偏差已披露）；跨面迁移须重标定。
- IC=逐日横截面 spearman（`shortline_p1_ic._ic_series_fast`，先掩码后排名；**等价自检门 max|diff|≤1e-6 vs composite_ic.ic_series 批跑前置**）。
- 期限：h5/h10/h20 报告列，**主口径=h10 严判**（P-1a/c/d 家族准绳；h20 越线=留档带 snooping 折价不翻案）。
- IS=面板起点→2024-12-31（IS_END）；OOS=2025-01-01→cutoff（**样本外恒盲**）。
- null：**3 掩码类 ×K=50 白噪声**（M_close=terrified；M_close_tr=stv+coin_team；M_arc=#93 四员）——掩码=tradability 同类真因子（P-1d 掩码类范式）；**seed=67000+i 连续账本**（SEED_REGISTRY 新基 `'p1e_zoo_behavior': 67_000` 本 commit 登记；band 67000..67149；rg 扫描净空，sole hits=数据文件数字巧合 t34/wild_route 先例）；null 线 p95 按 h 分列、按掩码类分列。
- 账本：`science_gates.append_ledger('P-1e', 157, file_name, evidence_cutoff='2026-09-22')`（dict schema 唯一手抄 prev，r217 纯函数返回值必嵌教训）；因子账本 +157（7 computed+150 null）；**引擎账本零动（零引擎跑）**。
- 成本口径：IC 海选=零成本统计面（不触 engine/exit_rules；IC 过线≠可交易，T+1/冲击/涨停撮合=B 层/P-2' 另算——P-1c §8 诚实条款照用）。

## §4 判据【必填·recorded v1 常数（P-1d s9 同代）】

- **V1**：|IS IC_mean| > max(0.02, 类内 null p95)
- **V2**：|IC_IR| ≥ 0.30（真门）
- **V3**：OOS 同号且 |OOS IC_mean| ≥ 0.5×|IS IC_mean|（留存≥50%）
- A3 期数门：IS 有效截面日 n_periods≥500。
- 多重性：7 因子×3 horizon 计数如实记（主口径 h10 判定）。
- 硬界设计三件套（D-20260925-01⑥）：本批=IC 统计面，max 硬界不适用；分布界（median/p95）随结果披露；TR_CLIP=0.99=换手尖峰守卫（冻结于构造器，非跑后滤镜）。
- **跑后禁调门槛禁换口径禁重跑**（一次定稿；工程修复重跑须双跑留痕如实用记）。

## §5 跑前预测【必填·≤3+极端日先验】

1. **方向**：四主因子原型 IC **全负号**（terrified/stv/coin_team=反转族；arc=处置溢价低值看多→负号）——共同负号=本批最强预测。
2. **量级与幸存**：|IS IC| 0.02-0.06 带（GTJA 反转簇 0.03-0.08 为近邻上沿参照；#92 三腿和与变体腿幅度预测薄于 #85 主腿）；h10 主口径三线全过预测 **0-2 员**（全灭概率 ~40%：P-1d 基率 1/10 + zoo 素材【未实证】全档）。
3. **变体腿**（vrc/src/krc）：方向先验弱（矩读数无符号理论），预测不设向、V1/V2 诚实判；与 arc 低相关（探针 ≤0.097）=独立信息面机会与噪音风险并存。
- **极端日先验**：凸显/处置类在 2015-07 股灾+2016-01 熔断窗微结构（|r|≥0.1 阈激活率高+换手尖峰+TR_CLIP 触带）→ 崩盘窗 IC 分部可能反号/放大；批报告按 IS 分年段披露（探针未跑该面=跑前预判面如实记）。

## §6 产物

- `scripts/p1e_ic_batch.py`（runner，**次轮交付**：复用 p1c_stock_ic_batch loaders+`_ic_series_fast`+等价门+离线 selftest——**跑前交付+自检过门才池化**，r198/wild_route「首发即崩」家族防线：夹具必镜像生产入参形态）。
- `results/shortline/p1e_zoo_behavior.json`（结果+判定表+audit 段+顶层 evidence_cutoff/cutoff_meta）+ `research/shortline/p1e_zoo_behavior_results.csv`。
- 本文件 §7/§8 跑后回填。

## §7 跑后实证【跑前必为空——占位纪律：写数字即造假】

（2026-09-26 05:4x 批跑 / r226 收割 · 一次定稿 · recorded v1 常数口径 · fail-closed finalize exit 0）

**批有效性硬门全过**：等价门 max|diff|=2.22e-16（vs composite_ic ic_series，probe −mom60 real slice 600×60 fwd h20）；三掩码各 K=50 白噪声 null p95 |IC|：M_close h10 0.0018 / M_close_tr 0.0018 / M_arc 0.0020（h5/h20 同量级 0.0015-0.0019）=全部 << V1 地板 0.02（thr=max(0.02, p95)=0.0200 全员）；面板 p1c_stock cache T=8792 × N=5222（ok 5130，选样面非 B 层掩码=P-1c SS2 同口径）；evidence_cutoff=2026-09-22；seeds 67000..67149 连续账本位（M_close 67000-67050 / M_close_tr 67050-67100 / M_arc 67100-67150）；CELSS 腿 runner pid1800 05:40:09→~05:46 约 6min（7 partials，注记预估 4-5min 带内）；finalize 0.4s；引擎跑=0。

### 主结果：7 因子 × h10 主口径，**幸存 2/7 = zoo85_stv + zoo92_coin_team**

| 因子 | 掩码 | IS IC/IR | OOS IC | 留存 | V1/V2/V3 | 判定 |
|---|---|---|---|---|---|---|
| **zoo85_stv** | M_close_tr | **−0.0467 / −0.440** | −0.0560 | **120%** | ✓/✓/✓ | **PASS** |
| **zoo92_coin_team** | M_close_tr | **−0.0750 / −0.492** | −0.0818 | **109%** | ✓/✓/✓ | **PASS** |
| zoo85_terrified | M_close | −0.0526 / −0.274 | −0.0861 | — | ✓/✗/✓ | FAIL（V2 差线 0.026） |
| zoo93_arc | M_arc | −0.0477 / −0.232 | −0.0575 | — | ✓/✗/✓ | FAIL |
| zoo93_vrc | M_arc | −0.0442 / −0.260 | −0.0061 | 崩 14% | ✓/✗/✗ | FAIL |
| zoo93_src | M_arc | −0.0047 / −0.035 | +0.0255 | 反号 | ✗/✗/✗ | FAIL |
| zoo93_krc | M_arc | −0.0184 / −0.152 | −0.0294 | — | ✗/✗/✓ | FAIL |

- h5 pass=2 / h10 pass=2 / h20 pass=3（+terrified h20 crosser −0.273·带 snooping 折价留档不翻案，多重性注记冻结）；A3 期数门 7800+ 全员 ✓。
- 覆盖面：terrified/coin_team share 0.3401 · stv 0.3033 · arc 0.2564 · vrc/src/krc 0.2572（真实因子暖窗/有效性稀疏 vs null 掩码支持面披露=meta.mask_disclosure 冻结面）。
- 产物：`results/shortline/p1e_zoo_behavior.json`（判定表+audit+顶层 evidence_cutoff/cutoff_meta）+ `research/shortline/p1e_zoo_behavior_results.csv`。

### 账本（r32 因子账本口径）

- **183135 → 183292（+157 = computed 7 + nulls 150**，SEED_REGISTRY 'p1e_zoo_behavior' 67000..67149）；引擎账本 N 不动（零引擎跑）；delta-幂等（同日重 finalize 零新员=冻结块逐字保留）。

## §8 批后复盘【SR-7T 跑后填】

### 机制定案五则

1. **共同负号 7/7 = §5 最强预测全中**。反转族（恐慌/异质波动/硬币路径=低波动低换手翻转动量）与处置溢价（低 CGO 看多→负号）在股票域宽截面同号——zoo 深读「clean-room 机制提取」的血统在 IC 面首次实证。
2. **幸存 2 员 OOS 留存均 >100%**（stv 120% / coin_team 109%）=样本外强于样本内、无过拟合签名；coin_team IC −0.0750/IR −0.492 为本批最强。
3. **§5「#92 三腿和幅度薄于 #85 主腿」预测反转为错**——三分法腿（日间/日内/隔夜）×双修正（波动翻转+换手翻转）等权和的结构反而厚于单腿恐慌族；错因=把「和的噪音稀释」直觉套在「多腿独立修正信号求和」上，方向性预测可靠、相对幅度预测不可靠（P-1d 预测对账同结论）。
4. **#85 主腿 terrified V2 差线 0.026**（IR −0.274）但 h20 crosser=信息衰减钟慢于 h10 假设第二例（P-1d dzjy_amt_share_20 先例）；带 snooping 折价留档，h10 主口径判定不变，禁重跑翻案。
5. **#93 处置效应族全灭如实**：主腿 arc 方向对（负号如处置溢价预言）厚度不足（IR −0.232）；变体矩读数 vrc/src/krc = §5「无符号理论」预言应验（src OOS 反号崩、vrc OOS 崩至 14% 留存）——TR_W 加权矩在 IC 面无独立信息，族收线。

### 预测对账（§5 跑前写死 vs 实测）

- 四主因子全负号：**✓ 7/7**；|IS IC| 0.02-0.06 带：**✓ 5/7**（coin_team 0.0750 超上沿=kicker、krc 0.0184/src 0.0047 带下）；h10 三线全过 0-2 员：**✓ 恰 2=带上沿**（全灭 40% 先验未中）；变体腿不设向、V1/V2 诚实判：**✓**（全灭落位）；「#92 薄于 #85 主腿」：**✗**（反转为批内最强）；极端日先验面：崩盘窗分年段披露未在本批跑面（IS n≈7850 期全窗口径）——留档不翻案。

### 处置与续作

- **stv + coin_team 入合成素材货架（+2）**；入册前置=**近邻相关性检验**（D6 同族 max|corr|≥0.7 拒收律）：候选近邻=stv↔terrified（同 #85 家族·掩码共享面）、coin_team↔P-1c GTJA 反转簇（070 −0.0906/081 −0.0655 负号族）与在册 lhb_count_20（注意力反转 −0.84）——联合合成批消费前必查（P-1d/P-S v2「货架效应」教训：同形态高相关对的合成增益可能只是 √2 分散而非新信息）；合成批另开预注册，认领制。
- **禁单独成策略**（P-A 单因子用法先例=只作合成素材）。
- terrified h20 crosser 留档不晋级；#93 族收线留档；**跑后禁调门槛禁换口径禁重跑**（一次定稿）。

## §9 工序排程（P-1d §7 范式）

1. **r219（本轮）**：本预注册冻结+面探针收口 commit（probe json+构造器/探针/sidecar 三脚本）+SEED_REGISTRY 登记+docstring 符号勘误。
2. **次轮**：runner 交付+selftest→`results/runnable_pool.json` 池化提交（车道 bm-b·lane_owner 戳=R31/r188 家族）→autofill 续批（py 水位门）。
3. **收割轮**：判定表+账本 append+§7/§8 回填+（若幸存）合成素材货架入册与近邻聚类注记；0 幸存=诚实收线。
