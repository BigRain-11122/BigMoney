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
- **宇宙（冻结）**：b_layer ok_static=3517（O-1820 件3b）∩ P4_BATCH2 §2 动态资格逐字（20日均额≥5000 万·上市≥20 bars·价格≥1 元·末 bar≤250td 新鲜度）＋ 板位排除 other（2 只北交所，30cm 限价机制无先例引擎面=诚实剔除披露）；ST/退市历史态=静态近似（eligibility 快照 as-of 面）如实注记。哨兵门（**R278 零跑修正案：全史中位≥150 ∧ 2010+ 中位≥500 双面**，见数据完备门修正案注记）；<5 只=该 cohort 跳过（thin-market skip 计数披露）。
- **regime 面**：sse.parquet 上证指数（1990-12-19..2026-09-22，8558 行）reindex 到 p1c 日历 **ffill 桥**（235 缺日全在 1991-01..1993-08 早域，覆盖 97.33%）；MA200 窗内有限值 <200=闸未定义→fail-closed 不入场。
- **数据完备门（不过即拒批 exit 2）**：meta shape T==8792∧N==5222 ∧ dates[0]==1990-12-19∧dates[-1]==2026-09-22（cutoff 锁盒）∧ sse 覆盖率≥0.97 ∧ mask 行数==5222 ∧ ok_static==3517 ∧ bars 符号集==cache 符号集。
- **【零跑修正案 R278·r251 探针权威】哨兵门单面 300→双面**：全史网格中位≥150 ∧ 2010+ 中位≥500。探针实证（2026-09-27 00:2x，零 judged 产物窗）：全史中位 190/p10=0（5000 万 amount20 闸=现代流动性尺度，1990s 薄市诚实清空→该年代 cohort 走 thin_market 跳过计数）·2010+ 中位 1114·2026 面 2961；XSTOCK 1524 中位=其 2015+ 窗口径非全史口径。跑前冻结后零跑修正合法（r251 先例），判据零改动。

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

## §7 跑后实证【R282 收割·R285 回填·跑后一次定稿】

**池执行留痕**：入池→tick 发射 00:10:07（pid 4720）+00:20:08（pid 18108）双发同点崩（d6_block 未解包 `load_member_rets` 元组·零 judged 产物窗·crash-fuse 同版本拒发如实计数）→ 工程修 commit 64d1c15c（R281·判据零动·r253 确定性重执行律）→ fuse code-change 放行→01:00:07 再发射（pid 53908）→ finalize+**同轮收割**（harvest commit a0425122 01:13:33·`results/_r282bma_revosc_harvest.py`）→ **N_trials=2014 入账**：ledger 187845+2014=**189859**；attrition 第 50 行入 `entries`（ts 2026-09-27 01:11:58·delta 2014·r248 消费面可见证）。

**14 格全量（x1=判决面·x2=压测描述列）**：

| cell | x1 Sharpe | x1 ann | x1 maxDD | x2 Sharpe | x2 ann | entries | DSR(x1) | G1'v2 | G2 |
|---|---|---|---|---|---|---|---|---|---|
| BASE | 0.3831 | +2.67% | −76.5% | −0.1523 | −1.44% | 10665 | 0.0122 | FAIL | ineligible |
| BASE_BG | 0.3778 | +1.85% | −45.0% | +0.0536 | +0.14% | 4464 | 0.0125 | FAIL | ineligible |
| FY_BG | −0.2777 | −1.52% | −71.0% | −0.6045 | −3.14% | 4417 | 0.0 | FAIL | ineligible |
| FY_BG_TP8 | −0.2190 | −1.44% | −57.2% | −0.5050 | −3.05% | 4417 | 0.0 | FAIL | ineligible |
| FY_BG_H10 | 0.2067 | +1.02% | −68.4% | −0.0865 | −0.65% | 4417 | 0.0005 | FAIL | ineligible |
| DWR_BG_TP8 | −0.1687 | −1.17% | −49.4% | −0.4457 | −2.77% | 4377 | 0.0 | FAIL | ineligible |
| FY_BG_INVVOL | −0.2645 | −1.42% | −72.3% | −0.5983 | −3.04% | 4417 | 0.0 | FAIL | ineligible |

**G1'v2 面：0/7**——line=**13.5951**（μ_null 0.193+σ_null 2.7183×√(2·ln 189859)；n_eff=189859·ledger head=p1_results.json；null 族=2000 件合成 52-cohort 年化 Sharpe 抽样，稀疏事件年序列天然高散布→线位高于 CN 族先例一个量级=族构成不同非线松动）；**判负稳健性：passive_term 0.5606（stock_b_layer 0.4606+0.10）单独已高于本批最优 0.3831→结论不依赖 null 项刻度**。bootstrap CI：仅 BASE_BG 下界 +0.002>0（point 0.3778·CI[0.002,0.7267]），BASE CI[−0.0084,0.7454] 含零，其余 5 格全负含零；trade_gate 7/7 过（entries 4377-10665≥30 双口径）。DSR 7/7 远低于 0.95（0-0.0125·n_trials=189859）。

**G2 面：7/7 ineligible**——g1 false ∧ DSR false ∧ family PBO=**0.4**（CSCV-8·70 组合·observe 带 0.25<pbo≤0.5：7 格选优面近半组合 OOS 排名劣于 IS=族内选优不稳定）。

**D6 准入面**：vs 在册 6 CE 员逐对 max|corr| 0.1128-0.1909（BASE=ENGULF-CE-01 0.1192·FY_BG_TP8 最高 0.1909）全 <0.7 **零拒收**；批内格间相关照册。个体事件族 vs ETF 组合成员相关结构=族先验（CN-REV-TILT 0.2583）同量级低相关。

**双法 nulls（§3 双报律·描述性并列）**：block bootstrap p_le_0——BASE 0.1795/BASE_BG 0.177（最优两格），首阳族 0.712-0.782；sign-flip p——BASE **0.0215**（唯一 <0.05·但单法不作注册判据）、BASE_BG 0.0305、H10 0.232、DWR 0.3125。两法对 BASE/BASE_BG 给「边缘显著」读数、对其余 5 格一致非显著——与 G1'v2 判负并存=描述面信号不足以越注册线。

**虚拟起点 census（RANDOM_LARGE_SAMPLE_LAW §2.1）**：n_starts=**8466**（=T−126−200 ✓≥1000）；分段 bull 2415／bear 3170／deep_bear 717／chop 2164 **全 sufficient（≥500）**。逐格 beat6m：BASE 0.4421／BASE_BG 0.4629／FY_BG 0.4382／TP8 0.4363／H10 0.4838／DWR 0.4386／INVVOL 0.4382——**全史≈coin flip**；deep_bear 分段 beat **0.5481-0.6220**（H10 最高 0.622·INVVOL 0.5481 微出下沿 0.0019 照登）＝7 格同向最高分段。OOS halves：BASE +0.0199/+0.0069 双正·BASE_BG +0.0016/+0.0152 双正·H10 −0.0227/+0.0292·其余 4 格双负；walk-forward 5 折 Sharpe 逐格两正三负至全负混布（BASE [0.18,−1.67,1.53,0.36,−0.003]）；随机分窗 split_sign_agreement 7/7=100%。

**描述条款（批级披露·不替代 v2 门）**：年化>0=3/7（x1）；OOS 双正=2/7；**回撤 −35% 线 7/7 全破**（−45.0%..−86.0%·BASE x2 −86.0% 最深）；x2 成本压测仅 BASE_BG +0.0536 一格转正边缘=成本敏感面如实。跳过/拒单披露：BASE thin_market=645（1990s 薄市哨兵门内诚实跳过）；BG 格 gate_closed=929（熊市闸外）+gate_undefined=28（MA200 窗内 fail-closed）+thin 334-346；unfillable（涨停开盘拒单=un-captured premium）BASE 82／BG 格 19-29；出场结构：纯时间格 100% 时间止，TP8 格 tp 1439/1593+sl 1020/1198（止损触发≈入场数 23-27%）。**极端日：15% 硬界零击穿**（crisis_single_list 全空·p999_abs_r≤3.95%——§5.5 预期危机窗击穿未发生：10 只分散+桶摊薄效应，豁免单列零记录如实）。

**r282 单位病披露（defect_disclosure 摘要·产物在档全文）**：beat 面消费 cache pct_chg（百分比单位）当分数→EW 代理 ×100 膨胀→beat_rate 全格 0.0 退化（跑前 s5 带 0.55-0.75 当场露馅）；修 /100+面重 derive（r253 单计：append prev_total 复用自身链位+skill_line n_eff_override+attrition 本批行原位替换）；判定面 byte-stable（价格模拟 g1/g2/dsr/pbo 免疫）；量化伪影面 |pct|>30 共 772 行全在无涨跌幅限制 1990s 代、elig 门内仅 1 行（30.27%·2010）。

## §8 批后复盘【R285·s7-T】

**§5 逐条对账**：
1. BASE 带 [−0.40,+0.10]：**MISS 上沿**（实际 +0.3831——个股池裸接比 ETF 代理毒丸预期强，但仍 3× 低于注册线；「最强格=裸 BASE」本身=预测结构反转）。
2. 闸内格带 [+0.10,+0.65]：**2/6 带内**（BASE_BG 0.3778 HIT·H10 0.2067 HIT·其余 4 格 MISS）；「过 0.5606=边缘事件」**HIT**（0/7）；判负概率 55-75% **应验**。
3. 首阳轴胜率增量 +10~+25pp：**大 MISS 方向反转**（FY_BG −0.2777 vs BASE_BG +0.3778=Sharpe 面负增量 −0.66；ETF 代理炉胜率第一杠杆在个股池失效反转——胜率面未单列产物如实注记，Sharpe 面即证伪）。
4. TP8+SL10 ≈中性：**MISS 偏负**（TP8 −0.219 vs FY_BG −0.2778 微改善 +0.06 但绝对负；DWR −0.1687 同）。
5. DWR+H10 代理炉最优组合预测：**MISS**（DWR_BG_TP8 −0.1687）。
6. deep-bear 段 beat 最高 0.55-0.75：**HIT**（7 格 0.5481-0.6220·6/7 带内·全分段最高）；「bull 段最低」**MISS**（chop 最低 0.3701-0.5166；BASE bull 段 mean_win_ret +0.051 反为最大正贡献段——「牛市接刀毒段」在个股池不成立=预测 #4 后半反向）。
7. 极端日击穿先验：**未发生**（零击穿·三件套 (b) 豁免单列零记录）。

**skill_line_v2 当批判读**：line 13.5951 为本批 null 族（2000 合成年 Sharpe·μ0.193/σ2.7183）与 n_eff 189859 的唯一权威派生——稀疏事件年序列（52 cohort/年·半桶空闲）天然高散布，σ_null 2.72 Sharpe 单位 vs CN-REV-TILT 0.0591/REGIME-POLICY 月集族=族构成差异非线松动；**判负距线 −13.21 但被动项单独即判负（0.3831<0.5606）→双重稳健**。

**gate_attrition 留痕**：runner 已追加第 50 行（`entries` 列表·g1_pass 7×false+g2_eligible 7×false+d6_reject 7×false+family_pbo 0.4+eliminated 2014）。

**判决行**：**REV_OSC-STOCK 判负收线**（G1'v2 0/7+G2 0/7+回撤描述线 7/7 破）→ slot closed per O-2325 §5 禁翻案（新证据=新预注册）；不开纸盘账户不入判决台。**CEO 呈件面诚实呈报**：O-2330「20日跌幅Top10 持有7天 +20.30%·胜率59.8%·102笔」在保守 T+1 开盘代理+双向成本+25 年全史+闸门全景下**不复现**——呈件口径疑为窗口/选段敏感形态（深跌段=强反弹段同源）。**家族证据沉淀**：deep-bear 段反弹溢价**描述性存在**（7 格 beat 0.55-0.62 同向）但全史 beat6m 0.44-0.48≈随机＝分段条件效应不构成注册级 α；首阳轴=个股池毒药（与 ETF 代理炉方向相反）＝代理炉外推边界的独立实证。供给链状态注记：学校供给队列 #1 CN-TREND-ETF（bm-b 在飞）·#2 CN-SOE ready 待 tick——本批判负不阻塞队列（SCHOOL_SUPPLY_S1.md §2 序继续）。

**复审三态**：立法=git 可验（freeze a7761433 先于 runner 建 0182a8cf 先于任何跑 ✓）／生效=判据跑通（14 face+2000 nulls+8466 vstarts+双法 p 值全落地 ✓）／验收=复审行本轮注册（T-87-REV-OSC-P1·json_field 锚稳定产物件）→ 复审器 run 判读。

—— bm-a 策略部+研究部 R285 收割回填（2026-09-27 02:xx · 跑后一次定稿 · 零编数）
