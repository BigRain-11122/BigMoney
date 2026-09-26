# CN_TREND_ETF_PREREG · 时序趋势跟踪袖 ETF 版判决批（T-87 s2 队列 #1·行 14）

- 令链：CEO 流派学令 O-20260926-0926（调研国内流派建立组合模型）→ O-20260926-2325 全域解锁令（RANDOM_LARGE_SAMPLE_LAW v1.0 全律绑定在案）→ T-73 s1 调研正典 `research/digests/DIGEST-20260926-t73-cn-schools-s1.md` 行 14（趋势跟踪·可建模性「高」·均线/突破跟随·ETF 日线面板直用）→ `research/SCHOOL_SUPPLY_S1.md` §二 队列 #1（零发明：只按既立队列顺序开线）。
- 批性质：**judged 判决批**（非淬炼勘探面）——变体轴系=社区共识 folklore 冻结面（双均线金叉/MA200 牛熊线/海龟 Donchian 突破=全球趋势跟踪三大最广流传战法）+仓内正典锚（REGIME_GUARD v3 MA200 面），冻结于此，批内零选优。
- 判负族边界披露（判负不重开律）：**期货 CTA ×3 judged-negative**（趋势机制×期货杠杆+移仓面）≠本批——本批=A股现货 ETF 长多时序趋势（无杠杆无移仓无保证金），新预注册+新证据=合法再入；**CN-REGIME-POLICY / CN-CORE-SATELLITE / CN-CORE-DDCTL judged-negative**（配置β/ETF 轮动/核心卫星族）≠本批——政体择时倾斜与配置结构非本面，本批=逐器械时序趋势入场出场（D6 相关面批内如实披露）；T-47 截面动量=s2 slice-A 已判面，时序（绝对）动量与截面动量机制面不同（survey 行 14 原文注记）。
- 反重复注记：仓内无任何趋势跟踪 runner/prereg（rg 全档零命中 2026-09-27 00:2x）；ETF 趋势面=PRODUCT_MATRIX 时间轴「短线波段/长线配置」之间的中段空白，本批不新开资产维度（股票/ETF 在册轴内）。

## §0 批件身份【跑前】

- 批名：`CN_TREND_ETF_P1` · 批号格数 N_eff=**2007**（7 judged cells ×1 判面 + 2000 nulls；x1 成本=披露列不计 N，家族先例 CN-DIV-LOWVOL-ROT）
- 认领：任务板 T-2026-09-26-87（claimed_by bm-a R277；s2 队列 #1 续作切片）；F-04 MSG 先行（本机 inbox 声明批名+票引用，bm-a R280）；部门 dept:研究+策略
- 算力预算：est 5-15min wall（23 腿×~3300 bar 向量化+2000 nulls+虚拟起点 census，workers=4 BelowNormal）；**仍按 O-1137 真实载体供给律池提交**（R251 CN-REV 41s 批照池提交同例）；per-cell JSON 幂等 checkpoint（>10min 批池化跨轮）。

## §1 α 机制段【D6】

- [x] **行为偏差**：锚定/反应不足×羊群——信息扩散缓慢使 ETF 指数面趋势延续（风格轮动史多季度长趋势：2017 核心资产→2021 成长→2023 微盘→2024 红利，仓内 digest §s2 在册）；付出代价方=过早止盈的处置效应散户（卖掉赢家留输家）与锚定逆势抄底者。T+1 长多约束下趋势溢价归于耐心多头。**截面月度反转>动量实证（s2 slice-A）不与本面矛盾**：截面相对强弱（horizon 周/月）≠时序绝对趋势（本批逐器械持续数月持有）。
- **同族相关性准入（in-runner D6 面）**：逐 judged cell 对在册 6 CE 成员（ew6 canon member_run 日收益）max|corr| + 批内两两 |corr|；**≥0.7 vs 在册成员=拒收**。ETF 时序趋势袖 vs 股票 CE 成员预期 <0.4（含现金腿+跨域腿），数值在批报告 D6 表逐对列出；judged-negative 家族（CN-REGIME-POLICY 等）返回序列=advisory 披露列（已闭族不作准入面）。

## §2 数据与面板【跑前探针事实·冻结引用件 `results/cn_trend_probe.json`】

- 面板：`data/daily/*.csv` ETF 板（OHLCV 收盘面；total_files=1724）；**cutoff=2026-09-22（D2 前向锁盒·与家族前批同 cutoff=比较性成立）**；cutoff 后新 bar 不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta('2026-09-22')`（缺字段=science_audit C2 VIOLATION）。
- **宇宙（冻结过滤器·机械再derive 禁手抄名单）**：rows≥2600 ∧ first≤2016-06-30 ∧ last==cutoff ∧ OHLCV 零 NaN ∧ med(amount20)≥¥50M ∧ ann_std≥3%（现金/货基型趋势信号结构性无定义=诚实剔除，511010/511880/511990/159001/511810 五只）→ **universe_n=23**（探针实证 2026-09-27 00:2x；min med_amount20=¥56.8M；含宽基/行业/跨境/黄金/红利面，全名单在引用件）。
- **数据完备门（不过即拒批 exit 2 零产物）**：universe re-derive==23 ∧ 逐件（**D2 截断至 cutoff 后**）末 bar==2026-09-22 ∧ 截断面 OHLCV 零 NaN ∧ 引用件在位。**【零跑修正案 R280·D2 锁盒语义】**：活面板由 S6 维护链持续前进（中秋 2026-09-25 休市后末完整 bar=2026-09-24，活文件必超 cutoff）——完备门与宇宙过滤器的「last==cutoff」一律作用于 **runner 装载后截断至 2026-09-22 的锁盒面**（禁止要求活文件末 bar 停在 cutoff=防维护链正常前进炸门）；冻结原文「逐件 last==2026-09-22」语义按此读，判据零改动（r251 零跑修正先例·REV_OSC R278 同型）。
- 诚实披露：data/daily 为收盘价面（分红除息缺口照传如现——红利腿 510880 面该噪声明；家族先例 CN-REGIME-POLICY 同 corpus 同面）。

## §3 方法学【冻结】

- **信号（逐腿，全部 close 面，t 收盘算 t+1 开盘执行·T+1 禁未来数据）**：
  - MA 族：MA20/MA60 简单均线（close）；MA200 牛熊线（close）；上证政体闸=sse 日线 close>MA200（regime_deep_replay 基准面同源，MA200 窗内有限值<200=fail-closed 不入场）。
  - Donchian 族：入=close[t]>max(close[t-20..t-1])（DON20）/t-55（DON55）；出=close[t]<min(close[t-10..t-1])（DON10）/t-20（DON20）。
  - 追踪止：MA_TRAIL=MA 多头态内自持有期最高 close 回撤 15% 触发出（t+1 开盘执行）。
- **组合构造**：信号驱动入场/出场（事件制）；权重每 5 交易日（offset=0）再归一到活跃腿等权，单腿帽=20% 权益（集中度守卫），事件间份额恒定（防 churn 家族语义）；现金腿 0 收益。
- **null 对照（RANDOM_LARGE_SAMPLE_LAW §3）**：K=2000 同掩码随机激活 null——逐腿周网格 Bernoulli(p=该腿 MA_BASE duty cycle) 生成随机多/空仓路径（同宇宙同执行同成本），seed=SEED_REGISTRY['cn_trend_etf_p1']=20270201+k（k<2000；跑前登记，段位碰撞扫描零命中 2026-09-27）→ skill_line own-null 池；双法并列：block bootstrap 2000 draws（块长 10）+ sign-flip 2000 draws，p 值双报。被动基线=宇宙 EW 日序列（批内 derive）。
- **成本口径**：V2 单源（`alloc_backtest.side_cost_v2(gross, adv20)`，ADV20=volume×close 滚动 20，本面板直算）；**judged face=x2 恒开**（ETF CN 家族先例 CN-DIV-LOWVOL-ROT/CN-REGIME-POLICY）；x1 披露列。成本作用于每笔名义（t+1 开盘价×份额）。
- **账本**：`science_gates.append_ledger('CN_TREND_ETF_P1', 2007, 'cn_trend_etf_p1', evidence_cutoff='2026-09-22')` dict schema 唯一禁手抄 prev。
- **虚拟起点面（RANDOM_LARGE_SAMPLE_LAW §2.1）**：全史枚举 census——起点日序号∈[200, T−126]，每起点 126 交易日窗，窗收益/胜率/beat vs 宇宙 EW 代理；分段 4 类（bull/bear/deep-bear/chop，sse 态打标同 REV_OSC §2.1 冻结面）逐列；任一分段起点数<500=insufficient-sample 如实注记。**随机分窗（§2.3）**：train/validation 随机划分 ≥100 次 + walk-forward 5 顺序折叠双证。

### §3.1 judged 格表（7 cells，判面 x2，全冻结）

| cell | 信号 | 闸/过滤 | 出场 |
|---|---|---|---|
| MA_BASE | MA20>MA60 | 无 | 反交叉 |
| MA_DUAL | MA20>MA60 | close>MA200（逐腿） | 反交叉 |
| MA_BG | MA20>MA60 | sse>MA200（政体闸） | 反交叉 |
| MA_INVVOL | MA20>MA60 | 无（权重∝1/std20） | 反交叉 |
| DON20_10 | close>20d 高 | 无 | close<10d 低 |
| DON55_20 | close>55d 高 | 无 | close<20d 低 |
| MA_TRAIL | MA20>MA60 | 无 | 反交叉∨15% 追踪止 |

## §4 判据【跑前写死·共享库调用禁手抄判线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2007, pool='core48', n_trades, n_entries, null_pool=<本批 2000 nulls>)`**：全期 Sharpe > skill_line_v2 ∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（deflated_sharpe_ratio 原始日序列）∧ PBO≤0.25（screening/pbo.py CSCV 8 块）。
- 批面要求（披露列）：annualized>0 ∧ OOS（≥2025-01-01·composite_ic.IS_END 共享分割）双正 ∧ maxDD≥−35%。

## §5 跑前预测【写死于跑前，跑后对账】

1. MA 族全期净 Sharpe 落 0.2-0.6 带（x2 后；23 腿分散+现金腿摊薄），<0.70 注册线概率高——判负照报不翻案。
2. DON 族胜率 30-45%（右偏收割），DON55_20 交易数最少（≈MA_BASE 的 1/3 量级）。
3. MA_BG 相对 MA_BASE 交易数降 30-50%（熊市闸砍半仓时段）；MA_INVVOL 波动率相对等权降 10-20%。
4. 极端日先验：2015-06/07 崩盘、2016-01 熔断、2024-02 微盘事件、2024-09-24 政策脉冲——均线交叉滞后翻红成本如实入账；黄金腿（518880/518800）2024-2026 段对冲披露。
5. x1 面净 Sharpe ≥ x2 面（周频 churn 成本敏感带：V2 面双腿成本对周再平衡侵蚀 20-40% 毛收益）。

## §6 产物

- `results/cn_trend_ETF/p1_results.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+D6 表+judged 判读+N 计数）；`results/cn_trend_ETF/cells/*.json|npy` per-cell checkpoint；census+§2.3 分窗产物；`results/gate_attrition.json` 追加一行（entries 列表面 r248 律）。
- runner=scripts/cn_trend_etf_p1.py（冻结 commit 后建；selftest 子命令=离线自检）。R99 律：prereg 冻结 commit 先于 runner build 先于任何 run。

## §7 跑后实证【跑前为空——占位纪律】

（跑后回填）

## §8 批后复盘【必填·s7-T】

（跑后回填）
