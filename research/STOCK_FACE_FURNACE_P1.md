# STOCK_FACE_FURNACE_P1 预注册 · 股票面三族淬炼炉（T-2026-10-01-139-P1 akshare 面 · bm-b 车道）

> 令源：CEO 直令 O-2026-10-01-1035-bm-a（原话「股票呢？不要光走ETF」）· 票：T-2026-10-01-139-P1（immediate·status=open·lane 注记 akshare face=bm-b collector host；p1c_stock 面=GM 会话车道互不重叠）· CEO 即时律=认领与开动同轮。
> 面性质：**淬炼勘探面**（REFINE_BENCH_LAW v1.0 + LOWAMP-FURNACE-20260930-P1 先例范式）——零判决宣称、零注册宣称；发现窗选优偏差照律注记；产出=显著带清单直入千人试用期**股票语法**（首批股票面候选供给）+ REV-OSC 淬炼对照面。ETF 面结论**只作设计输入**，零判决外推、零判据挪用（票面 execution laws 逐字）。
> 批号格数：REV 121 + LOWAMP 144 + MOM 16 = **281 格**（枚举面，无随机参数抽取）· 每格双 nulls（sign-flip 2000 + block bootstrap 2000，验证窗日序列）· 每格双成本面 {x1, x2}。

## §0.5 禁向闸例外声明【跑前】

- 引证匹配项：**BAN-01**（ETF 横截面动量）、**BAN-02**（ETF 横截面反转）、**BAN-03**（单名 5/10/20 日择时反转与动量）。
- 例外类型：**new_data**（兼 new_mechanism 项逐族注明）。
- 不可能看见：原证伪面全部在 ETF 窄截面（≤48 员）或单名择时面上测得——本批的个股全 A 合格池截面（约 3500 员流动性合格个股、T+1 开盘保守代理、板位涨停拒单、桶账事件结构）在原证伪面中**结构性不存在**；原证伪面看不见个股截面的分散度、板位制度面与合格池动态闸，也看不见本批的 2015-01..2026-09 个股面板新数据面（akshare qfq 前向采集面板，cutoff 2026-09-30）。CEO 直令 O-1035 明示 ETF 面结论禁外推到股票面——本批即该令的股票面首烧。

## §0.4 意义门三问【TRIAL_LABOR_LAW §4】

1. **研究问题**：超跌反弹 / 低振幅 / 动量三族在个股全 A 合格池面上是否存在成本后超额与稳健显著带（ETF 面证据不外推，问题独立重开于新数据面）？
2. **消费方**：千人试用期**股票语法**（首批股票面候选供给，票面 OUTPUT 逐字）+ REV-OSC 淬炼对照面 + 日报股票面成绩行。
3. **语法登记簿查重**：REV_OSC_STOCK_P1 已判决 7 格语法（BASE/BASE_BG/FY_BG/FY_BG_TP8/FY_BG_H10/DWR_BG_TP8/FY_BG_INVVOL）=本批 REV 枚举面的真子集，**逐格剔除不重烧**（判负格 closed，O-2325 §5）；LOWAMP-P1 ETF 带消费行（W∈[77,104]×N∈{2,3}×sizing×core48 常开）=ETF 面消费，本批为个股面 new_data 非同语法重跑；TRIAL_LABOR_W1-W14 生成语法均为 ETF core48 面，与个股面零重叠。本批消费带于 finalize 时登记 TRIAL_GRAMMAR_LEDGER（append-only）。

## §1 α 机制段【D6·逐族】

- **REV 超跌反弹族**（CEO 原发现·票面正主）：行为偏差=过度反应修正×处置效应（20 日深跌=恐慌抛售终点，短期反弹溢价；T-73 s2 中国行为律、T-22 分段 bear 证据、REFINE-BENCH-20260926-P1 代理炉定谳轴系）。付出代价方=恐慌割肉散户与被迫平仓杠杆盘。机制对照结论（人工预读行）：与 ETF 代理炉同构但个股池分散度与制度面（板位涨停/停牌顺延）为代理炉看不见的新面。
- **LOWAMP/LOWVOL 低振幅族**：行为偏差=彩票偏好溢价收割（低波动异象，Betting-Against-Beta 族面；个股面比 ETF 面更经典——票面 GM 注记逐字）。机制=低振幅个股的彩票折价系统性存在，被动供给方=追涨散户；new_mechanism 项=个股截面日再平衡 + 合格池流动性闸（ETF 面无此面）。
- **MOM 动量族**：独立重开（票面：ETF 面证伪≠股票面证伪，诚实注记=A 股文献面反转主导、预期低、问题独立）。机制=趋势延续 vs 反转主导的个股面检验，new_data 面。

## §2 数据与面板【跑前探针事实】

- **面板=data/astock_daily/per/<code>.csv**（bm-b akshare 全 A 采集面板·T-87 collector 车道·qfq 面）：5217 文件·cutoff=**2026-09-30**（panel complete=true·results/astock_daily_update_status.json）；字段 date/open/high/low/close/volume/amount（amount=元，实测 000001 近端 ~8-12 亿元/日）。加载窗=**2013-06-01 起**（零跑修正案 r502·r251 先例：保证 510300 MA200 200 日 warmup 在 2015-01-01 验证窗起点前完成，验证窗内 gate_undefined=0；修正前 2014-06 起点使 2015 年 1-3 月闸未定义，判据零改动）。
- **宇宙（冻结）**：eligibility 6 位码 0/3→sz·6→sh（B 股 2/9+北交 4/8/92x 诚实跳过，collector law）∩ b_layer_mask **ok_static=True**（静态 ST/亏损近似，REV_OSC_STOCK_P1 §2 同法披露）∩ 有 per 文件；**动态资格=P4_BATCH2 §2 逐字**：amt20（自身 20 bar 均值）≥5000 万 ∧ close≥1 元 ∧ 上市≥20 bars ∧ 末 bar≤250td 新鲜度。哨兵门=合格池截面中位 ≥150（全加载窗）——探针记录，跑时断言恒等。
- **regime 面**：510300 close（data/daily/sh510300.csv，2012-05-28+）MA200 熊市闸——REFINE-BENCH 家族约定面（510300<MA200）；REV_OSC 用 sse 指数面的差异如实注记（闸语义同构：指数<MA200）。2015-01 验证窗起点后全覆盖。
- **日历面**：sh510050.csv 日期列（2005-02-23+，exclusion_marginal_scan 同法）。
- **数据完备门（FAIL-CLOSED exit 2）**：probe_facts.json 在场 ∧ run 侧重 derive 逐键恒等（per_files/cutoff/ok_static 宇宙数/哨兵中位/510300 覆盖）∧ panel complete=true。
- **算力门**：free-RAM 门随 worker 数缩放 floor=2.0+0.55×workers GB（12 workers=8.6GB；workers=6=5.3GB——零跑修正案 r502·r251 先例，判据零改动）；每 worker 面板常驻 ~500MB·workers≤12 BelowNormal。

## §3 方法学【冻结】

- **成本口径（全族统一）**：V1 股票日频 13.041bp/边（26.082bp 回合）×1=x1 主面／×2=x2 压测描述列（rev_osc_stock_p1.COST_X1 单源 import，禁手抄）。
- **REV 族引擎=rev_osc_stock_p1.py 引擎原样 import**（sim_stock/pick_cohort/sim_cell/cell_stats 零重写；禁改 engine/exit_rules.py 铁律不触及）：5 交易日信号批（offset=60 起算）→ drop20 升序 Top10（tie 低代码优先）→ T+1 开盘入场（涨停开盘拒单=un-captured premium 计数；板位 floor main 0.0975 / 创业板 2020-08-24 起·科创板 2019-07-22 起 0.1975）→ 出场三件：时间止 H／止盈 +8%（当日开盘已越线按开盘出）／再止损 −10%，同日双触先止损保守，停牌顺延首个可交易开盘 → 2 桶摊薄日序列。**枚举面**：gate{无,熊市闸}×首阳{无,有}×dwr{无,drop60<0}×tpsl{无,有}×H{5,7,10,20}×仓位{eq,invvol}=128 − 已判 7 格=**121 格**；H=20 → 信号批尾部余量 28 日（t+1+H+停牌顺延余量，引擎尾界常量面）。
- **LOWAMP 族（向量化日再平衡勘探引擎）**：amp=close-to-close 收益 W 日滚动 std（min_periods=W，lowamp_p1.build_signal 同法定义）→ 合格池内升序 Top-N → 权重 eq 或 1/amp 归一 → 日持仓收益 Σw[t−1]·r[t] − cost×Σ|Δw|（换手成本近似，勘探面口径如实注记；判决面须 fill-sim 引擎）；gate=bear 时仅熊市日持仓（非熊市日 100% 现金）。**枚举面**：W{40,50,60,70,77,85,89,95,104}×N{2,3,5,10}×sizing{eq,invvol}×gate{none,bear}=**144 格**。
- **MOM 族（月度再平衡勘探引擎）**：mom=close[t]/close[t−L]−1 → 合格池内**降序** Top-N（强者先入）→ 月末信号、次月首个交易日建仓持有整月 → eq 权重、换手成本同 LOWAMP 口径、gate 同法。**枚举面**：L{20,60,120,252}×N{5,10}×gate{none,bear}=**16 格**。
- **窗（冻结·零重叠）**：发现窗=2025-10-01..2026-09-30（近 12m，LOWAMP-FURNACE 先例对齐）；验证窗=2015-01-01..2025-09-30（10.75y，独立于发现窗）。逐窗指标：年化/Sharpe(252)/maxDD/胜日率/换手/entries/beat（vs 同窗合格池 EW 被动代理 ew_ret）。
- **逐格双 nulls（票面 ≥2000 逐格）**：sign-flip 置换 2000 draws + block bootstrap 2000 draws（块长 10 日），作用于**验证窗**日序列（主筛面），p 值双报；seed=SEED_REGISTRY['stock_face_furnace_nulls']=20333000 + cell_index×4000 + k（新键本批注册，带 20333000..20334200 与全部既有带 disjoint 自检）。
- **语法登记**：finalize 时 TRIAL_GRAMMAR_LEDGER append 三族带行 + trials 台账 N_eff=281 append（勘探试验诚实入账，DSR 折减面不重置计数）。

## §4 筛选判据【跑前写死·勘探面非注册面】

- **robust 铅跑格**（LOWAMP-FURNACE 先例口径）：双 nulls p 均 <0.05 **且** 发现窗与验证窗年化同号为正 **且** 验证窗 Sharpe>0。
- 排序表=验证窗 Sharpe 降序；显著带清单=robust 格的参数邻域聚合（逐族列出连续参数带）；预期假阳性数如实披露（281 格 × α0.05 双法 ≈ 14 格假阳性先验，邻域聚合缓解单点噪声）。
- 负结果照报（REFINE_BENCH_LAW §3：淬炼不出=合法产出）；**零判决宣称、零 skill_line 注册、零纸盘开舱**——真出样=显著带进股票语法后由试用期判决漏斗承担。
- 诚实注记：勘探面换手成本近似口径、静态 ST 近似、幸存者面（在建市面板历史退市股缺位）三面如实携带进消费面。

## §5 跑前预测【写死】

1. REV 族：熊市闸格族 > 无闸格族（代理炉第一杠杆方向）；首阳轴在个股池**方向存疑**（REV_OSC 判决批实证=个股池毒药，Sharpe 面负增量——预期本批枚举面复现该负增量而非代理炉正增量）；H=20 长持有格换手成本低但反弹溢价衰减。
2. LOWAMP 族：低振幅带在个股面预期为**三族最强**（文献面经典+ETF 面先验）；W 长窗（77-104）×N 小（2-3）×invvol 预期领先（ETF 面最优形态镜像）；但个股面 N=2 集中度风险（单票尾部）使 N=5/10 格可能更稳。
3. MOM 族：预期**弱至负**（A 股反转主导先验）；若 L=252 长回溯格正，则与文献面个股长动量证据一致为意外正向。
4. 三族共面：bear 闸对 LOWAMP/MOM 族或降 Sharpe（防御面在震荡市空仓拖累）——与 REV 族方向相反。

## §6 产物

- script: scripts/stock_face_furnace.py（probe|selftest|run --family --cells a:b|finalize；per-cell JSONL checkpoint 幂等；FAIL-CLOSED exit 2/算力 exit 3；池握手=burn 完成+幂等 no-op 双调用点，lowamp_p1 范式）
- results/stock_face_furnace/：probe_facts.json + cells/<family>/cell-*.json（281 件）+ <family>_summary.json（顶层 evidence_cutoff + 排序表 + 双 nulls + 显著带清单）+ <family>_cells.csv
- 池入账：STOCKFURN-{REV,LOWAMP,MOM}-AKSHARE-SHARD-{a} 共 12 入池条目（每族 4 分片·lane_owner=bm-b·data/astock_daily 面本机独有·runner_args 带 --workers 6 适配共享机常态空闲 RAM；本会话 3 格真跑冒烟已落 cells/ = 分片内幂等续跑面）；finalize=观测轮动作（族分片全 done 后由轮会话执行，不入池）。
- 本文件 §7/§8 跑后回填一次定稿。

—— bm-b 策略部+研究部 r502 冻结（T-139 akshare 面 · 跑前一次定稿）

## §A1 修订·r503【数据面再锚·判据零改动】

- 事由：r502 收尾 S6 update_fundamental 日快照（2026-10-01 12:13）轮换 data/fundamental/eligibility.csv 字节（np 列刷新），烧波中途 raw-sha 探针钉假阳性——LOWAMP-108/MOM-0/MOM-4 三分片 crash-fuse（12:14-12:18），MOM-8/12 认领面停摆，watermark 红（runnable-work-idle-low-cpu）。
- 证据：旧（bd4da77b6·09-30 11:02）vs 新（3f6c8dde7·10-01 12:15）blob 逐行比对=行数 11635=11635、eligible=True 码集 7273=7273、增删空集；b_layer_mask.csv 零 diff。
- 修法：runner r503 语义钉（elig_face_sha16=_universe 实际消费的 6 位 0/3/6 码集哈希；raw sha16 降为 provenance 字段；码集任何增删仍 fail-closed）；re-probe 2026-10-01 12:28:26 复核=universe_n 3514 / panel_rows 3242 / elig_median 1565.5 / mask_sha16 cf00cd8389b56c03 全部与 r502 冻结钉逐值恒等。
- 面等价声明：已烧格（REV 121 格 + LOWAMP 0-108 共 108 格）在原钉下产出、续烧格（LOWAMP 108-144 共 36 格 + MOM 16 格）在再锚钉下产出——同码集、同 panel lockbox（cutoff 2026-09-30）、同判据；§4 判据零改动、勘探面零判决宣称不变。
