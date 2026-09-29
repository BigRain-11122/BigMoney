# T-101-V4-A12-PREDCOND 预注册（五员 vol/风险条件化连续仓位面首测·非选择非择时）

> 血统：A11 §8 下游指针兑现（「输入特征路线残余去向=**预测器/条件化面**（vol/风险条件化·非选择非择时），若未来立项须新 prereg+D6 先行论证」——本批即该指名路线首测）+ r444 state next(a)。A2/A9/A10/A11 四子线已证伪=门/因子特征源的**二值择时（A2/A9）、门态连续权重（A10）、横截面 top-k 选择（A11）**三用法；本批=**原始已实现波动率源的连续条件化用法**首测——结构性新面：条件子不是门态不是特征排序，是 σ20 已实现波动率本身；功能形不是 0/1 全进全出（A2/A9）不是门态均值权重（A10 C2）不是成员选择（A11），是**暴露水平连续条件化（c_vtar）+ 成分连续条件化（c_volinv）+ 双腿交互（c_vtar_volinv）**。
> 状态：**FROZEN——冻结于跑前·2026-09-29 20:2x·bm-a r445（起草机同轮一次冻结·A9/A10/A11 臂线批先例：一次冻结即烧）**。本冻结 commit 同窗含 SEED_REGISTRY 两键注册（20316000/20316500 三步律过：两新基 vs 全现存值零碰撞·带 20316xxx 代码面 rg 空·首元素 0.1802/0.6239 互异·在册仅两对注册律前 legacy dup [20260923/48000] 历史冻结零触碰）+runner+MSG-2016 声明。

## §0 批件身份【必填·跑前】

- 批名：**T-101-V4-A12-PREDCOND**·批内格数：**12**（宇宙 2 × 条件子 3 × 成本 2）；null 对照 K=200/格·另计不膨胀策略数。本批=**试验判决批**（入 trials_ledger，batch_trials=12）。
- 认领：F-04 先行=MSG-20260929-2016-bm-a-ALL（fleet/inbox/·开工声明）；任务板引用=臂表 A12 位（A 系列惯例=臂表行即工单·r441/r442/r443 同法·无新票）。
- 部门归属：dept:研究（链条研究线·T-101 v4 政体门臂 A12 位）。
- 算力预算：est <3 min 单进程（2 宇宙条件化回测 + 2,400 随机条件化 null + 双 nulls B=2000/P=2000 ×12 + PBO CSCV 2×6 配置 + A10/A9/A11 三源 D6 复算）——trivial compute in-round 合法（O-2100·A11 141.3s 同族先例）；worker 数 1；批报告必带 audit 段。
- 车道：**bm-a**（五员面板 data/daily in-repo·fv/a10/a11 三机器件本机全在·r441/r442/r443 同车道延续）。
- 语法查重/防重跑：vol/风险条件化连续仓位用法=**未被消费面**——attrition 71 行全查零命中（A2/A9=单门二值择时已关·A10=门态连续权重已关·A11=横截面选择已关·MA200 二值分段=tpl.regime_segment 描述面非策略面）；W9 AMP GATE/VOL 条件率面=bm-b 个股短线波（不同宇宙不同车道·邻接披露）；Moreira-Muir vol-managed portfolios=国外学术机制参考件（CEO 2026-09-28 1522 导向律：机制参考非方向盘——本批立项权源=**在仓判决链指名残余面**非外源框架）；同语法重跑须新 prereg（本冻结 commit=防重跑锚）。

**§0-X 条件化组合器形态【冻结·禁搜参·全冻死】**：
- **宇宙**：U5=冻结五员 O-1555={510300, 510050, 510500, 512100, 588000}（主面）；U4={510300, 510050, 510500, 512100}（深度腿——512100 上市 2016-11 使 U4 共同窗 ~9.8 年 vs U5 ~5.8 年·两腿分格独立判）。
- **窗口**：master=成员日期交集；σ20 预热 20d（全 master 面计算 σ20 后切窗·窗首即有 21 个 σ20 观测）；跑前探针锚（@2026-09-28 面板）：U5 master 2020-11-16..2026-09-28 n=1,424→窗 2020-12-14 起 n_eff=1,404；U4 master 2016-11-04..2026-09-28 n=2,405→窗 2016-12-02 起 n_eff=2,385。**门/因子可判性零依赖**（条件子=σ20 只需 20d）=窗口比 A11 深（U4 2016-12 vs A11 2017-05；U5 2020-12 vs A11 2021-05）——含 2018 bear 全程+2020-02 熔断窗（U4）。
- **条件子（三面·冻结定义·零参数搜索）**：
  - **c_vtar**（暴露水平条件化）：w_exp,t = clip(TVOL_t / σ_ew20,t, 0, 1)；σ_ew20=EW 袖日收益 20d 滚动 std（ddof=1）；TVOL_t=σ_ew20 序列 trailing 252d 滚动中位（min_periods=63·NaN→w_exp=1.0 满暴露默认·窗首 ~63d 占比披露）；成员权重=1/n 恒等权。再平衡日 t 用数据 ≤t 计算信号，w_raw,t 落位、w_eff=w_raw.shift(1)（T+1 开盘代理）。
  - **c_volinv**（成分条件化）：w_i,t = (1/σ_i20,t) / Σ_j(1/σ_j20,t)，Σw=1 **恒满仓**（零择时成分·A11 同构隔离设计）；σ_i20=成员自身 20d 滚动 std（下界 clip 1e-8 防御）。
  - **c_vtar_volinv**（双腿交互）：w_i,t = w_exp,t × (1/σ_i20,t)/Σ(1/σ_j20,t)——水平×成分双条件化。
- **再平衡**：stride-20（rebal_idx=arange(0,n,20)·gate_verify/A11 同律再平衡日历）；再平衡间权重恒定。
- **禁搜参声明**：条件子三面/stride-20/σ 窗 20d/TVOL 窗 252d(63 min)/等权/成本二档=全冻结；无任何阈值、窗长、加权指数搜索。

## §1 α 机制段【必填·D6】

四选一：**[x] 风险溢价**——两条子腿同族：①**c_vtar=波动率管理暴露**（vol-managed exposure）：波动率聚簇下恒仓持有者承受回撤复利（高波态单位暴露的后续收益被波聚簇侵蚀），条件化暴露在同等平均暴露下削减高波段回撤深度——由谁付出代价=恒仓被动持有者在波峰段的多余暴露（Moreira-Muir 2017 机制参考件·国外框架=参考非方向盘·本批立项权源=在仓判决链 A11 §8 指名）；②**c_volinv=低波风险溢价倾斜**：A 股宽基高波指数（512100/588000 型）由彩票偏好流长期支付负向风险溢价，低波成分长期存活者溢价——由谁付出代价=追逐高波弹性的彩票偏好资金流。**本批反向锚=A11 实证**（U4 f_c2 高波 tilt=唯一正超额面 +10.4%/×2 +8.3%=高波员确有超额读数）——若 c_volinv 判负=A11 镜像证据互证高波溢价面成立·若 c_volinv 过线=低波溢价面独立存活——**双向都可判负·双向都有信息**。
- 若条件化组合器全量风险调整表现不过批自**随机条件化** null 池 → 条件化袖面判负，输入特征路线残余去向=纯预测器（forecast）面。

**同族相关性准入检查【D6·跑前预声明】**：
- **vs 宇宙成员 B&H**：c_volinv/c_vtar_volinv 恒满仓格与高波员 B&H corr≥0.7 结构高发主预期（恒满仓持有同类资产定义性同源·A11 判例 0.80-0.97）——预声明：其独立信息含量=条件化差分，由批自随机条件化 null 池隔离测量；max|corr|≥0.7 仍按 D6 律 REJECT（注册资格面·不阻断科学判决线）。
- **vs A10 16 格**（门态连续权重线·同连续暴露功能形不同信号源）：runner 经 a10 模块 import 复算 pairwise max|corr|≥0.7 → REJECT（门态与 σ20 信号源不同·低 corr 主预期·判读面）。
- **vs A9 单门 9 格**（fv 机器件复算）：同上 REJECT 律。
- **vs A11 24 格**（横截面选择线·**本批最邻接闭面**）：runner 经 a11 模块 import 复算 24 格日收益 pairwise——**c_volinv vs A11 f_c2 格高 |corr| 风险预声明**（高波 tilt 镜像同源·符号相反映射同一信息=信息冗余非新信息·|corr| 判线照算）。
- 批内 12 格 |corr| 矩阵逐格落 JSON（披露不 kill·r231 先例）；vs 在册六员 D6 绑定门=s4 intake 切片 defer 注记（paper_export 无日序列·r434/A10/A11 同法）。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙成员同 §0-X；数据锚四元组（G-ANCHOR-FACE）=`data/daily/sh<码>.csv` + `tpl.load_panel` 单源（cutoff 截断+尾行断言内建·探针-锚同面断言=A11 同法）。
- **冻结行数锚（@2026-09-28·r231 同表·A10/A11 同锚）**：510300=3,486 / 510050=5,251 / 510500=3,289 / 512100=2,405 / 588000=1,425；尾行一律 2026-09-28（runner 断言·fv.ANCHOR_ROWS 逐字）。
- **共同可判窗**（§0-X 探针锚）：U5=2020-12-14 起 n_eff=1,404（~70 再平衡）；U4=2016-12-02 起 n_eff=2,385（~119 再平衡）。**IS 面（<2017-01-01）结构性近空**：U4≈21d / U5=0——G1' 判据面不受影响（全期 Sharpe+skill line+trade gate），OOS 超额面=全窗即 OOS 如实记（A11 同构披露）。
- **evidence_cutoff=2026-09-28**（D2 前向锁·A10/A11 同面）；cutoff 后新 bar 不回流；结果 JSON 顶层必带 `science_gates.cutoff_meta`。

## §3 方法学【必填】

- **执行机器零重实现（import 单源）**：`t101_v4_a2_prescreen`（tpl：load_panel/regime_segment/sharpe/ann_ret/max_drawdown/position_series/daily_returns）；`t101_v4_a158_fv`（fv：dual_nulls/window_grid/WINDOWS/GATES17/ANCHOR_ROWS/CELLS9/g_p1_check/g_accept_check）；`t101_v4_a10_regimecombo`（a10：combo_position/combo_returns/COST_RATE/COST_RATE_X2/TRADE_EVENT_DW/CELLS16/C1_FAMILY——A10 格 D6 复算源）；`t101_v4_a11_xselect`（a11：build_universe_face/cell_weights/xsection_returns/CELLS24/FEATURES/TOPK——A11 格 D6 复算源）；`science_gates`（sg：g1_prime_v2/g2_registration_v2/deflated_sharpe_ratio/append_ledger/SEED_REGISTRY）；`screening.pbo.cscv_pbo`（CSCV 8 块冻结）。
- **条件化连续权重回测语义（本批新面·冻结定义·A11 连续权重口径扩展）**：再平衡日 t 条件子计算（数据 ≤t）→w_raw,t（成员×暴露权重矩阵）；生效 w_eff,t=w_raw,{t-1}（T+1 开盘代理·shift 语义）；日收益 r_t = Σᵢ w_eff,i,t × r_i,t − Σᵢ|w_eff,i,t − w_eff,i,{t-1}| × cost_rate（首效日 |Δw|=建仓成本·A11 xsection_returns 口径）。
- **成本口径（A10/A11 保守冻结逐字）**：cost_rate=0.001/单位 |Δw|（0.1% 往返/满换手=0/1 门控口径 2 倍保守面）；×2 压测腿=0.002。SPLIT=2017-01-01（IS 近空披露见 §2）。
- **trade/entries 口径（G1 双口径·A11 冻结同值）**：trade event=Σᵢ|Δw_eff,i,t|≥0.10 的交易日数（TRADE_EVENT_DW=0.10）；n_entries=OOS（≥SPLIT）trade events；entries_ok=≥15（tpl.MIN_OOS_ENTRIES 同值）。
- **随机条件化 null（批自 null 族池·本批核心对照）**：K=200/格·每 null=同再平衡日历上以**同形随机条件化**替换条件子输出（c_vtar 格→w_exp~U(0,1)/再平衡日·EW 成分；c_volinv 格→成分~Dirichlet(1,…,1)·暴露 1 恒满仓；c_vtar_volinv 格→双腿皆随机）→同构造同成本回测——隔离测量「条件子携带的信息 vs 同形随机条件化」；seed 基=`SEED_REGISTRY["t101_v4_a12_predcond_scrnull"]`=**20316000**（rng([20316000, cell_idx])·本批注册）；2,400 null Sharpe 全收=批自 null 族池（**nan-safe 统计 r442 律**：有效集统计+nan_excluded 计数披露）。
- **双 nulls（W1 `_dual_nulls` 语义逐字）**：块自助 B=2000·block=20 circular（均值 CI）；符号翻转 P=2000（双侧 p）；seed=[`SEED_REGISTRY["t101_v4_a12_predcond_unc"]`=**20316500**, cell_idx]·cell_idx=冻结 12 格表序。
- **虚拟起点窗网格（三窗·描述面恒带）**：{6m=126, 12m=252, 24m=504}；起点=每交易日 p∈[窗首+1, n−w]（W1 同径日频起点·重叠窗如实披露）；每窗策略收益 vs **同宇宙 EW-B&H 同窗收益**（EW 合成指数=(1+r_ew).cumprod() 披露构造）；段=起点日 510300 MA200 政体（bear/bull/chop·tpl.regime_segment 逐字）。
- **G1' v2（共享库禁手抄）**：`sg.g1_prime_v2(sharpe_full, returns_full, batch_cells=12, n_trades, n_entries, null_pool=批自 null 族池, passive_override=同宇宙 EW-B&H 同窗 Sharpe)`——skill line N_eff=ledger 活头+12 数目驱动。
- **DSR**：`sg.deflated_sharpe_ratio(returns_full, n_trials=本批 append 后活头)`（跨波不重置·禁 dsr_from_stats 充数）。
- **G2 注册资格 v2（共享库）**：`sg.g2_registration_v2(g1_pass, dsr, pbo)`。**PBO 族面（跑前冻结）**：族=每宇宙「本批已试配置全网格」=3 条件子×2 成本=**6 配置**（薄族噪声如实披露·A11 12 配置族对照）；两宇宙分族判（cscv_pbo 8 块）。
- 分段恒带：bear/bull/chop OOS 逐段年化（≥30 日段才计）。
- 账本：`sg.append_ledger("T-101-V4-A12-PREDCOND", 12, "t101_v4_a12_predcond.json", evidence_cutoff="2026-09-28")`（finalize 时落·线性·**返回值必落 out["trials_ledger"] 键 r442 律**）。

## §4 判据【必填·跑前写死，禁看结果调线】

**FV-PASS（注册候选资格）= 五条合取（全量判决面）**：
1. **G1' v2 pass**（skill line+bootstrap CI 下界>0+trade 门 entries_ok——共享库逐条）；
2. **DSR ≥ 0.95**（原始收益 deflated_sharpe_ratio·n_trials=append 后活头）；
3. **成本 ×2 压测**：OOS 超额（vs 同宇宙 EW-B&H·0.2% 往返口径）> 0（x1 格读冻结 x2 双胞胎格·A11 同法）；
4. **G2 eligible_v2**（G1∧DSR∧PBO≤0.25·共享库）；
5. **D6-ACCEPT**（§1 四面 max|corr|<0.7·预声明结构同源论证不豁免判线）。
- FV-PASS 格→s4 intake 切片（D6 绑定门对在册六员→STRATEGY_LIBRARY+纸盘按 W10 §s4 律）；FV-FAIL 格→条件化袖面子线关面如实入 §7+attrition（禁换参重跑）；零 FV-PASS=「五员宇宙 vol/风险条件化连续仓位用法判负」合法判决照报不粉饰。
- 多重检验税披露：n_wave=12 判格·E[FP]=0.05×12=**0.60**；N_eff 累计照 TRIAL_LABOR_LAW §4 跨波不重置（活头实读·344,080→344,092）。
- 描述条款恒带（非判线）：全期 maxdd≥−35% 地板·政体依赖性·entries 数·窗深与 IS 近空。

## §5 跑前预测【必填·写死于跑前】

1. **c_volinv U4 负超额主预期**（A11 镜像反向锚）：U4 高波员（512100）系 A11 f_c2 唯一正超额面的载体（+10.4% 高波 tilt）——低波条件化系统性减持高波员=镜像减持超额载体→OOS 超额负主预期；U5 同构（588000 载体）。**该腿=双向信息腿**：判负=A11 高波溢价镜像互证成立；过线=低波溢价独立存活证据。
2. **c_vtar 崩避面小正超额可能但难过线**：U4 窗含 2018 bear 全程+2020-02 熔断+2022 bear（σ20 峰值段暴露收缩=崩避机制窗）→OOS 超额小正可能；但 stride-20 滞后（崩后进·崩中不避·极端日本身不被避开——见第 5 条）+0.1%|Δw| 成本吃掉大部分；skill line≈1.2-1.6（N_eff≈344k·批自 null μ/σ 待实测）下 G1' 全灭主预期。
3. **c_volinf trade events 偏薄风险**：低波权重漂移慢→多数再平衡 Σ|Δw|<0.10→U5 腿（~70 再平衡）entries_ok≥15 边缘风险·U4 腿（~119 再平衡）过门主预期；c_vtar/c_vtar_volinv 腿暴露摆动大→entries 过门主预期。
4. **D6 主预期**：c_vtar vs A10 格低 corr（信号源不同·σ20 vs 门态）；**c_volinv vs A11 f_c2 格 |corr|≥0.7 REJECT 高发主预期**（高波 tilt 镜像同源·符号相反=同一信息不冗余豁免·|corr| 判线照算）；c_vtar_volinv 双继承。
5. **极端日先验（硬界设计三件套 (c)）**：U4 窗内极端日=2018-02/2018-10 崩盘簇、2020-02-03 熔断日（510300 单日 −7%+）、2024-09-24/25 熔涨簇（单日 +8%/+9%）、2025-04 关税窗（如有·面板内）；σ20 在这些日簇后飙升→c_vtar 暴露收缩滞后 1-20d（T+1+stride）——**极端日本身不被避开**（机制的真实收益窗=崩后低吸段非崩中避损段·如实披露机制边界）；描述面 max 单日 |r| 读数预期与被动同量级（无日内杠杆）。
6. **总判**：0/12 FV_PASS 主预期→vol/风险条件化袖面判负；输入特征路线残余去向=纯预测器（forecast·walk-forward 面）供下游另批——判决照报不粉饰。

## §6 产物

- 结果：`results/t101_v4_a12_predcond.json`（顶层 evidence_cutoff+cutoff_meta+audit 段+12 判格全量+null 池统计+D6 四面+PBO 族面+三窗/分段描述面+批内 12×12 矩阵）
- 轮报告回执 + `results/gate_attrition.bm-a.json` 追加行（entries 列表消费面 r248 律）+ 臂表 A12 行（research/DECISION_CHAIN_BENCHMARKS.md §5）

## §7 跑后实证【跑后一次定稿·2026-09-29 20:4x·bm-a r445·61.0s】

- **判决：FV_PASS 0/12（12 D6-REJECT）——vol/风险条件化袖面判负**。跑前预测六条兑现五条半：①c_volinv 双宇宙 OOS 超额全负（U5 −2.04%/−2.25%·U4 −0.74%/−0.92%·×2 稳健）=**A11 镜像反向锚实证闭环**（f_c2 高波 tilt +10.4% ↔ c_volinv −2.0% 同一信息两符号·低波条件化=镜像减持高波溢价载体·双向信息腿判决=高波溢价面互证成立而低波面无独立存活）；②c_vtar 双宇宙 OOS 超额小正（U5 +0.86%/×2 +0.65%·U4 +0.29%/×2 +0.08%·方向一致量级递减）=崩避倾斜存在但远低于注册线；③c_volinf/c_volinv entries_ok 双腿全过（35-98 events·§5.3 薄事件风险未兑现·预测半错如实记）；④D6 12/12 REJECT 主导面=vs_a11（max 0.847-0.933·c_vtar 最高对=U4|f_c2|top2 0.8958；vs_bh 0.57-0.83·512100 0.832 最高）=§1 预声明「恒持同类资产 beta 定义性同源」兑现——注册资格面关（独立信息含量=条件化差分由 null 池隔离=最高格仅 ~1.1σ 于 null 中位）；⑤极端日/maxdd 描述面=**0/12 击穿 −35% 地板**（对照 A11 恒满仓 top-k 20/24 击穿·最深 −60%——暴露条件化结构性压回撤深度=本批唯一正面描述性发现）；⑥总判 0/12 兑现。
- **真实 skill line=1.0889**（null_term 主导：μ_null=0.2390·σ_null=0.1683·N_eff=346,282·批自随机条件化 null 池 2,400 抽零 NaN；passive_term=0.4787）；批内最高格 U5|c_vtar|x1 Sharpe 0.4316=线位 40%——无边缘格判负干净（E[FP]=0.60 名义·实收 0）。DSR top=U4|c_vtar|x1 0.001（34.6 万折减）。bootstrap CI 全负下界（top 格 CI95 −0.46~+1.05）。
- **PBO 族面**：U5=0.1714（<0.25 合格带·但 G1/DSR 先灭无注册面意义）·U4=0.4286（6 配置薄族噪声披露兑现）。
- **N_eff 账**：346,270→346,282（+12 线性·ledger 活头实读=他机在飞烧批已推至 34.6 万·跨波不重置律生效·A11 时点 344,080 与本批间 +2,190=bm-b W10 screen 等他机批）。
- **结论链**：输入特征路线五子线态=A2/A9/A10（择时三态）+A11（横截面选择）+**A12（vol/风险条件化连续仓位·本批）全谱判负**——门/因子特征源在五员宇宙的三种用法（二值择时/选择/条件化）+原始波动率源条件化用法全部关闭；**残余去向=纯预测器（forecast·walk-forward 面）**，若未来立项须新 prereg+D6 先行论证（预测器面=特征→收益预测的条件期望建模·非仓位映射·与已闭三用法功能形不同）。

## §8 批后复盘【必填·s7-T】

- **跑前预测质量**：六条五兑现一半错（③c_volinv 薄事件风险未兑现=预测保守面·entries 45/69 全过）——机制先验与实证一致；本批零修正零重跑（selftest 腿 3/4/8 stride-20 口径错冻结前自检抓到=工程接线错在冻结前修复·判据面零触碰·r251/r280 先例族合法窗内）。
- **邻接披露发现（A10/A11 双 null seed 面）**：fv.dual_nulls 语义逐字但基=模块内置 fv 键 20313500——A10/A11 runner 直调继承 fv 基而其 prereg/元数据声明批自键（20314500/20315500）=**声明与实跑基不符**（统计有效性零损：dual nulls CI/p 为 seed 任意统计面·判决不依赖具体 seed）；A12 起正法=runner 显式 rebind fv.UNC_BASE 至批自键使声明=实跑真值（本批已行·JSON `unc_base_wiring` 字段留痕）。
- **血统注记**：W11 berth（bm-c r237 同窗落地）=STD 二值门 TRIAL 波面（个股车道）与本批连续 σ 条件化（ETF 五员臂线）=同源信息不同用法不同车道——A9 已判 STD 门二值择时负·本批判连续条件化负=「同族换用法」双向关闭在册。
- **下游指针**：条件化面残存正面描述性发现=c_vtar 回撤压制面（0/12 击穿地板 vs A11 恒满仓 20/24）——不入注册资格面（Sharpe 线下），若未来风险预算类立项（如 SPM 风险平价线）可作输入注记非策略宣称；输入特征路线到此全谱收线，**下一立项面=纯预测器（forecast）或转出 T-101 v4 线**（须 CEO/GM 派单或 TRIAL_LABOR 常设线供给）。
