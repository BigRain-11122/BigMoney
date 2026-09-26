# REV_OSC_STOCK_PREREG · 超跌反弹袖个股版判决批（T-87 第一优先席位）

- 令链：CEO 呈件 O-2026-09-26-2330（「超跌反弹 20日跌幅Top10 持有7天 +20.30%·胜率59.8%·102笔」+ T-87 第一优先席位）→ 淬炼令 O-2026-09-26-2335（个股版细化炉即刻进台）→ REFINE-BENCH-20260926-P1（ETF 代理炉首炉定谳轴系=本批镜像起点）
- 批性质：**judged 判决批**（非淬炼勘探面）——变体轴系由 ETF 代理炉+CEO 呈件冻结于此，批内零选优；RANDOM_LARGE_SAMPLE_LAW v1.0 全律绑定（O-2026-09-26-2325）
- 反重复注记：CN-REV-TILT（60d 月度倾斜族）judged-closed 不重开——本批=20d 周批事件族（O-2330 CEO 特选显式派工，new-family 非翻案）；WILD-S1 12 战法不含超跌反弹轴（rg 实核 2026-09-26 23:4x）

## §0 批件身份

- 批名：REV_OSC_STOCK_P1 · 批号格数 N_eff=**2014**（7 judged cells × 2 cost faces = 14 + 2000 nulls；每格计入 N_eff）
- 认领：F-04 MSG-20260926-2345-bm-a 先行；任务板 T-2026-09-26-87（claimed_by bm-a R277）；部门 dept:策略+研究
- 算力预算：est 8-20min wall，workers=4 BelowNormal（ProcessPool 每 worker 独立载面板 ~2GB 峰值；free-RAM<16GB 拒批 exit 3）；>10min 批池化跨轮 checkpoint（per-cell JSON 幂等）

## §1 α 机制段【D6】

- [x] **行为偏差**：过度反应修正×处置效应——20 日深度跌幅=散户恐慌性抛售终点，短期反转溢价（T-73 s2 中国行为律「短期反转>动量」实证、T-22 分段 bear 63.9%>bull 47.1%、ETF 代理炉同向）；付出代价方=恐慌割肉的处置效应散户与被迫平仓的杠杆盘。regime 条件注记：反转溢价集中在下跌/震荡市（熊市闸=第一杠杆，代理炉实证 always-on −41% vs 闸内 +15~+21%）——与市场时钟 ORANGE 态反转袖激活三源实证一致。
- **同族相关性准入（in-runner D6 面，CN-REV-TILT 同法）**：逐 judged cell 对在册 6 CE 成员（ew6 canon member_run）日收益序列 max|corr| + 批内两两 |corr|；**≥0.7 vs 在册成员=拒收**（族先验 CN-REV-TILT 0.2583；本批为个股事件族 vs ETF 组合成员，预期 <0.35）。数值在批报告 D6 表逐对列出。

## §2 数据与面板【跑前探针事实】

- **面板=P1C-StageA 股票缓存**（Money02/data/cache/p1c_stock）：T=8792（1990-12-19..2026-09-22）×N=5222，float32，字段 open/high/low/close/vwap/volume/amount/pct_chg，qfq bars（event-day gate 已证）；**cutoff=2026-09-22（D2 前向锁盒）**；符号面=Money02/data/bars 5222 parquet（wild_route 同源对齐法）。幸存者偏差=cache 为在建市快照（A158/XSTOCK/P1E/CN-REV-TILT 同批先例披露）——历史退市股缺位，判读携带该面。
- **宇宙（冻结）**：b_layer ok_static=3517（O-1820 件3b）∩ P4_BATCH2 §2 动态资格逐字（20日均额≥5000 万·上市≥20 bars·价格≥1 元·末 bar≤250td 新鲜度）＋ 板位排除 other（2 只北交所，30cm 限价机制无先例引擎面=诚实剔除披露）；ST/退市历史态=静态近似（eligibility 快照 as-of 面）如实注记。哨兵门：**逐信号日合格数中位 ≥300**（早期年代市场薄）；<5 只=该 cohort 跳过（thin-market skip 计数披露）。
- **regime 面**：sse.parquet 上证指数（1990-12-19..2026-09-22，8558 行）reindex 到 p1c 日历 **ffill 桥**（235 缺日全在 1991-01..1993-08 早域，覆盖 97.33%）；MA200 窗内有限值 <200=闸未定义→fail-closed 不入场。
- **数据完备门（不过即拒批 exit 2）**：meta shape T==8792∧N==5222 ∧ dates[0]==1990-12-19∧dates[-1]==2026-09-22（cutoff 锁盒）∧ sse 覆盖率≥0.97 ∧ mask 行数==5222 ∧ ok_static==3517 ∧ bars 符号集==cache 符号集。

## §3 方法学【冻结】

- **信号（信号日 t，全部 qfq 面）**：drop20[t] = close[t]/close[t-20] − 1（窗内有限值≥20）；drop60 同法（双窗共振用）。排名=合格池内 drop20 升序（最深者第 1，tie→低代码优先）取 **Top10**。
- **入场（T+1 开盘保守代理，O-1132 披露律）**：t+1 开盘价入场，仅当可交易（open 有限 ∧ 非涨停开盘：open/prev_close−1 < floor−0.002，floor main 0.0975/chinext 0.1975（2020-08-24 起，之前 0.0975）/star 0.1975（2019-07-22 起，之前 0.0975）——wild_route 冻结面逐字）；涨停开盘=un-captured premium 计数披露。
- **出场（冻结三件）**：①时间止：持有 H 交易日（H∈{7,10} 按格），t+1+H 开盘出；②止盈 +8%：持有期内 high ≥ entry×1.08 即按 1.08 出（若当日开盘已高于止盈线按开盘出）；③再止损 −10%：low ≤ entry×0.90 按 0.90 出；**同日双触按先止损保守**（代理炉律）；三件按格激活（见 §3.1 格表）。停牌/跌停不可卖=顺延至首个可交易开盘（wild_route 律，顺延计数披露）。
- **闸与仓位**：熊市闸=sse_close[t] < MA200[t]（仅闸内格）；首阳=close[t]>open[t]（信号日收阳才接刀）；逆波动=权重 ∝ 1/std20[t]（20 日日收益 std，等权格为 1/10）。2 资金桶（bucket accounting，wild_route 律：cohort 净收益按持有日数均摊入日序列，桶空闲日=0）——信号网格=**每 5 交易日**（周批，确定性 offset=60 起算），最大并发 cohort=2。
- **null 对照（RANDOM_LARGE_SAMPLE_LAW §3）**：nulls=**K=2000** same-mask 随机事件日（随机信号日×随机合格 10 只，BASE 机械无闸无过滤，seed=SEED_REGISTRY['rev_osc_stock_p1']=20261230+k k<2000）→ skill_line own-null 池；**双法并列**：block bootstrap 2000 draws（块长 10 日，逐 judged cell 日序列均值分布）+ sign-flip permutation 2000 draws（逐 cell）——p 值双报。被动基线=stock_b_layer 注册池活读（XSTOCK 先例不重跑）。
- **成本口径**：V1 型股票日程 13.041bp/side（26.082bp roundtrip，P4_BATCH2 §3.2 锚；wild_route COST 同面）×1=x1 judged face／×2=x2 压测描述列（judged face=x1，wild 先例）。
- **账本**：`science_gates.append_ledger('REV_OSC_STOCK_P1', 2014, 'rev_osc_stock_p1', evidence_cutoff='2026-09-22')` dict schema 唯一。
- **虚拟起点面（RANDOM_LARGE_SAMPLE_LAW §2.1）**：**全史枚举 census**（PROSPECT 范式全族化）：全部合法起点=日序号 ∈ [200, T−126]，每起点 126 交易日窗（≈6m）——窗收益/胜率/beat vs 合格池 EW 日序列代理；预期 K≈8466（≥1000 ✓）；分段=4 类（**bull**: sse>MA200∧60d ret>+5%／**bear**: sse<MA200∧60d ret≥−15%／**deep-bear**: sse<MA200∧60d ret<−15%／**chop**: 其余）按起点日 sse 态打标——分段 n、分段均收益、分段 beat 率逐列；任一分段起点数 <500=该分段 insufficient-sample 如实注记（禁算该分段 pass，不自动翻批负）。**随机分窗（§2.3）**：train/validation 随机划分 ≥100 次（seed 同基，起点集 50/50 划）+ walk-forward 5 顺序折叠双证（训练/验证窗均收益同号一致性）。

### §3.1 judged 格表（7 cells × {x1,x2}，全冻结）

| cell | 入场 | 闸 | 出场 | H | 仓位 |
|---|---|---|---|---|---|
| BASE（CEO 原版） | Top10 裸接 | 无 | 纯时间止 | 7 | 等权 |
| BASE_BG | Top10 裸接 | 熊市闸 | 纯时间止 | 7 | 等权 |
| FY_BG | +首阳 | 熊市闸 | 纯时间止 | 7 | 等权 |
| FY_BG_TP8 | +首阳 | 熊市闸 | 时间止+止盈8%+止损−10% | 7 | 等权 |
| FY_BG_H10 | +首阳 | 熊市闸 | 纯时间止 | 10 | 等权 |
| DWR_BG_TP8 | 双窗共振(drop20<0∧drop60<0) | 熊市闸 | 时间止+止盈8%+止损−10% | 10 | 等权 |
| FY_BG_INVVOL | +首阳 | 熊市闸 | 纯时间止 | 7 | 逆波动 |

（轴系=REFINE-BENCH-20260926-P1 定谳面镜像：首阳=胜率第一杠杆、熊市闸=收益第一杠杆、止盈/持有 10d=加数点；DWR+H10=代理炉 9m 验证窗最优组合）

## §4 判据【跑前写死】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2014, n_trades, n_entries, pool='stock_b_layer', null_pool=<本批 2000 nulls>)`**：全期 Sharpe > skill_line_v2 且平稳 bootstrap CI 下界>0 且 entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（deflated_sharpe_ratio 原始日序列，n_trials=line.n_eff）∧ 家族 PBO≤0.25（screening/pbo.cscv_pbo CSCV-8，7-cell 家族矩阵）。
- **硬界三件套（D-20260925-01①）**：(a) 日序列腐坏检测=median/p99.9 分布界主责；(b) max 硬界 |r_day|>15%=单点入危机日志豁免单列（2015-06/07 救市、2016-01 熔断、2024-01/02 微盘崩、2024-09/10 暴力反弹=预期危机窗，先验见 §5.5），豁免逐日披露禁整批判负；(c) 极端日先验见 §5。
- 描述性条款（批级披露不替代 v2 门）：年化>0、OOS 双正（虚拟起点窗前后半双正）、回撤≥−35%、无崩年（−35% 线）、x2 成本压测逐年稳定。
- 判负=slot closed+新证据=新 prereg 重开律注记（O-2325 §5）。

## §5 跑前预测【写死于跑前】

1. **BASE（无闸裸接）全期 Sharpe 带 [−0.40, +0.10]**：A 股裸接自由落体刀+26bp 回合成本拖累；ETF 代理毒丸同构（代理池 −41% 由病尾品种主导，个股池深度更真但牛市接刀段照毒）。
2. **闸内格（*_BG）全期 Sharpe 带 [+0.10, +0.65]**：熊市闸浓缩历史至高反弹密 regime；**过 0.5606 skill 线=边缘事件非大概率**（stock_b_layer 被动项 0.4606+0.10 主导线位；两前批 0/4+0/4 墙先例同库同成本面）——诚实风险置顶：**判负概率 55-75%**。
3. **首阳轴胜率增量 +10~+25pp**（代理炉 26.9→61.3 同向但个股池预期弱于 ETF 池——个股收阳噪声更大）；TP8+SL10 组合 ≈ 中性（代理炉加数个点）。
4. **分段面**：deep-bear 段 beat 率最高（预期 0.55-0.75）；bull 段最低（信号少+质量差）；BASE 的 bull 段=最深负贡献（牛市接刀=毒段主源）。
5. **极端日先验（三件套 (c)）**：2015-06/07 千股跌停/停牌簇（出场顺延激增）、2016-01 熔断 4 日、2024-02 微盘流动性塌陷（SL −10% 连环触发）、2024-09/10 与 2015-07 反弹期涨停开盘拒单簇（un-captured premium 峰值）——日序列 |r| 可合法击穿 15%（10 只集中组合单日限位叠加），全走豁免单列禁判负。

## §6 产物

- script: scripts/rev_osc_stock_p1.py（run|selftest；per-cell JSON checkpoint 幂等；fail-closed exit 2；free-RAM exit 3）
- results/rev_osc/p1_results.json（顶层 evidence_cutoff + cutoff_meta + 14 格全量 + nulls 双法 + D6 表 + 虚拟起点分段面 + walk-forward/split 一致性）+ cells_summary.csv
- 本文件 §7/§8 跑后回填；ledger 单次 finalize（REV_OSC_STOCK_P1_REFINALIZE=1 唯一重跑门）

## §7 跑后实证【占位——跑前必须为空】

## §8 批后复盘【占位】

- 预测对账与 gate_attrition 行：跑后回填。
