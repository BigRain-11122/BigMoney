# S5_01_ZT_PILOT 预注册——vibe-astock 情绪指标适配回放 pilot（数据面·mechanics-verification）

> 冻结律：本文件跑前 commit 冻结；§7 跑前必须为空；改判据=重跑。
> 权威链：research/BACKTEST_SCIENCE.md + research/BACKTEST_PLAN.md 三铁律 + research/COMPUTE_AUDIT.md；OSS_HARVEST_LEDGER §八（S5-01 准入 GO 判定）；fleet/orders/O-20261001-2103-bm-a.md R2 供给线；T-67 §2 冻结律（前向史 ≥12 个月才准预测值面 prereg——本批=pilot 面·纯机制验证·零预测主张）。
> 先例：OPTIONS_WAVE2_PREREG.md（pilot 面→definitive 推迟形态）。

## §0 批件身份【必填·跑前】

- 批名 / 批号：S5_01_ZT_PILOT（pilot 面；批内格数 = 回放窗交易日 × 4 面，N_eff 按 (日,面) 格计；扩宽即弃单）
- 认领：F-04 先行——`fleet/inbox/MSG-2026-10-08-0250-bma-ALL-s501-zt-pilot-prereg-claim.md`；任务引用：research/OSS_HARVEST_LEDGER.md §八 S5-01（准入探针 GO）+ O-20261001-2103 R2 情绪周期三轴门供给线
- 部门归属：dept:数据（REGIME-5 供给前置数据面）
- 算力预算：~52 次 EM 请求 × 2.5s 限速 ≈ 3 分钟单核网络 + 秒级确定性计算；<5min 单核 = 轮内内联合法；批报告带 audit 段
- 车道：bm-a 独占（与 scripts/update_zt_pool.py 同车道 R31 判例；他机 stdout-only 诚实 no-op 零共享态写·R65 律）

## §0.5 禁开方向硬门【必填·跑前】

- 跑前已过 `python Tools/banned_direction_gate.py --prereg research/S5_01_ZT_PILOT.md`（rc=0 放行·回执见轮报告）
- 命中编号：BAN-03（needle 误命中——见下豁免声明）
- 例外类型：new_data
- **原否证不可能看见的东西**：EM 涨停池族 as-collected 数据面与采集器存储机械（r856 才落地·r855 探针）——BAN-03 判负网格=ETF 单名 5/10/20 天择时 18 组合（单名时间序列维度·docs/audits/retail-quant-conclusions-v2#3），从未触及全市场横截面情绪计数数据面；本批零持仓、零收益序列、零单名择时（纯日级横截面数据验证），两维度正交，判负结论不可迁移。
- 已烧格数计入浪费台账（若判负）：~52 格 fetch（EM 只读查询·无回测格）

## §1 α 机制段【必填】

四选一（勾选）：**[x] 行为偏差**——涨停池/炸板池/跌停池/强势池 = A 股散户打板族的注意力与羊群行为显性度量（游资 folk 判据「发酵→扩散→加速→退潮」的数值化锚点族）；代价付出方=追高接盘的滞后者（打板族的对手方）。

**散户凭什么赢（§1.2 必答）**：**本批不主张赢**——纯数据面机制验证批，不产出场、不产收益序列、不入册交易员；「凭什么赢」由下游预测值面批（≥12 个月前向史后另开 prereg）正式论证。本批 DATA_GAP 显式声明：EM zt-pool as-collected 深史仅 ~2-3 周（r856 bisect 实证 `results/_r856bma_zt_depth_bisect*.json`：09-07=0 / 09-14=55 / 09-21=103 / 09-30=52 行），预测值面缺口影响=无法做长史情绪周期判据验证——推迟至前向积累 ≥12 个月（T-67 §2·OPTIONS_WAVE2 先例）。

**同族相关性准入检查【必填】**：本批无日收益序列入册（纯测量面），D6 corr 门**不适用于 pilot 面**；显式声明：三轴门未来入 REGIME-5 供给 prereg 时必过 D6（vs 在册交易员全部成员+在队/同批全部函数日收益序列口径 max|corr|≥0.7 拒收）——数值对照清单届时逐对列出。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙/池：EM 涨停池族四面（zt / zbgc / dtgc / strong），A 股全市场，无扩池、无白名单。
- 数据锚定义四元组【G-ANCHOR-FACE】：
  1. 回放参考面：`akshare stock_zt_pool_em 族日参 fetch（scripts/update_zt_pool.py ENDPOINTS 注册）` / `scripts/zt_pool_pilot_replay.py`（复用 gate.fetch_day） / 起算窗 2026-09-14（bisect 实证首非零采集日）/ 窗终 2026-09-30；无预热窗（日级横截面）
  2. 面板面：`data/zt_pool/<key>.parquet` / `pd.read_parquet` / FIRST_DATE=2026-10-08 前向积累（当前面板空·PANEL_DIR 实证 absent，今晚 15:30 首采后 accrue）/ 无
  3. 日账面：`data/zt_pool/collected_days.json` / `json.load` / 与面板同步 / 无
  4. 本地交易日历面：`data/daily/510300.csv` / `pd.read_csv`（本地 ETF 日历主源·与采集器同源） / 全史 / 无
- **探针-锚同面断言**：runner 实载路径与上述声明逐位比对（gate.PANEL_DIR / gate.ENDPOINTS 面 / gate.CORE_CALENDAR_FILE 在位）——一观不相等 = 面错配 VOID（fail-closed 拒烧）。
- **evidence_cutoff（D2 前向锁盒）：2026-09-30**——回放窗日集全部 ≤ cutoff；cutoff 后新数据（10-08 起前向积累行）锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta.evidence_cutoff = "2026-09-30"`。
- 数据完备门：回放窗 = 本地 ETF 日历 ∩ [2026-09-14, 2026-09-30]（预期 ~13 个交易日·以日历 derive 为准非手抄）；四面逐日 fetch；失败日=豁免单列披露不判负（conn 家族诚实律·池日片收盘即终态）。
- 探针种子选位律：不涉种子（确定性纯计算·无随机基线；见 §3 三铁律映射声明）。

## §3 方法学【必填】

- 指标定义（冻结；vibe-astock 参考宣称=未验证假设，本批以自有实现独立验证其可计算性·借力三律）：
  - 三轴：N_zt（日涨停数）/ N_zbgc（日炸板数）/ N_dt（日跌停数）；zb_rate = N_zbgc / (N_zbgc + N_zt)（分母 0 = None；构造界 [0,1]）；N_strong 辅助记录
  - 连板梯队：zt 面「连板数」列直方图（≥1 整数；max_board 记录）——vibe-astock `_ladder_by_boards` 同语义（consec_boards）
  - 赚钱效应（vibe 腾讯实时通道 opening pct）：**范围外**——腾讯通道=新数据通道未过接线门不入本批（诚实范围裁剪·留下游批另开）
- 存储语义（与采集器一致·防语义分叉）：去重键 (日期,代码) keep-first；代码列 str 化；涨跌幅 NaN==NaN；面板首列=日期。
- 回放双 derive 机制验证：路径1 = 原始 fetch DataFrame 直接派生（同去重语义）；路径2 = 经采集器存储机械（gate.append_day 写临时面板→pd.read_parquet 读回→按日过滤→派生）——两路径三轴整数恒等 + zb_rate 浮点恒等（tol 1e-9）+ 梯队直方图恒等（机制验证主判据·采集器 selftest 18/18 的回放面复验）。
- null 对照（BACKTEST_PLAN 三铁律映射声明）：数据面批无随机信号 null——映射为 ① 双 derive 字节恒等 ② 独立路径重算（fetch 直取 vs 面板读回）③ 幂等重跑（同窗重跑结果除时间戳外字节恒等；池日片收盘即终态律）。
- 成本口径：不适用（零交易零持仓纯测量面）。
- 账本：burn 开始时 `science_gates.append_ledger('S5_01_ZT_PILOT', batch_trials=<回放窗交易日数×4>, file_name='results/zt_pool_pilot_replay.json', evidence_cutoff='2026-09-30')`（dict schema 唯一·禁手抄 prev）。
- 闭合族对号声明【必填】：family_key = `zt_pool_data_face`——不在 science_gates.CLOSED_FAMILIES（新证据线首批·无对档判负 delta 语义·无复跑窗）。

## §4 判据【必填·跑前写死·禁看结果调线】

- **G1'/G2 注册资格：不适用**——本批无收益序列无 sleeve（纯数据面）；注册级判据由 ≥12 个月前向史后的预测值面 prereg 承担（OPTIONS_WAVE2 pilot→definitive 先例）。
- **J1 完备门**：回放窗四面 fetch 成功 (日,面) 格占比 ≥ 90%（MIN_FACE_SUCCESS=0.90）；失败格豁免单列（不判负）。
- **J2 双 derive 恒等门**：路径1 vs 路径2——三轴整数恒等 + zb_rate 浮点恒等（tol 1e-9）+ 梯队直方图恒等，**100%**；原始帧日内重复代码格=单列观察披露（dup_codes 计数·非判负）。
- **J3 分布界（硬界设计三件套）**：
  - (a) 分布界主判：N_zt 日序列 median ∈ [40, 120] 且 p99.9 ≤ 250（median/p99.9 承担检测主责·禁裸 max 作主判）
  - (b) max 硬界须配危机日感知：N_zt 裸 max 硬界 250；命中先记危机日日志+豁免路径=单点删除优先于整批判负（指数 |r1|≥5% 危机日单列豁免披露）
  - (c) 极端日先验见 §5-P4
  - zb_rate 构造界 [0,1] + median ∈ [0.05, 0.70]
- **J4 梯队 sanity 门**：consec_boards 全体为 ≥1 整数；max_board ≤ 10（超出=形状漂移旗标 exit 3 待人工裁定·采集器形状门同族）。
- **J5 幂等门**：同窗重 derive（冻结 raw 快照二次派生）结果除时间戳外字节恒等。
- **出场轴显式门（O-20261001-1108 三选一）**：= **②持有到底声明**——纯测量面零持仓零出场语义；runner 显式禁用引擎缺省出场栈（不实例化任何仓位对象）。

## §5 跑前预测【必填·写死于跑前·跑后对账】

- **P1**：回放窗 ~13 个 EM 交易日（09-14..09-30·日历 derive），四面 fetch 成功率 100%（bisect 探针已实证该窗 API 日参可返数）。
- **P2**：N_zt 日序列全部落 [40, 120]（探针锚 55/103/52），median 落 [50, 90]。
- **P3**：zb_rate median ∈ [0.05, 0.70]（构造界内经验带·炸板率无极端政体日预期）。
- **P4（极端日先验）**：窗内预期无指数级 |r1|≥5% 危机日；若有→N_dt 异动单列豁免披露不判负（J3(b) 危机日感知）。
- **P5**：双 derive 恒等 100%（J2）——采集器存储机械 r856 selftest 18/18 同族断言的回放面复验。

## §6 产物

- scripts/zt_pool_pilot_replay.py（run / selftest 子命令·车道守卫·复用采集器同面函数）
- results/zt_pool_pilot_replay.json（顶层 science_gates.cutoff_meta.evidence_cutoff="2026-09-30"·冻结 raw 快照摘要+逐日指标）
- results/zt_pool_pilot_replay_days.csv（日 × 面 × 指标回放台账）
- 本文件 §7 回填

## §7 跑后实证【跑后一次定稿回填·r857 同窗烧录】

- 烧录：r857（冻结 commit 1fb041a22 → 当窗内联点火）；runner `python scripts/zt_pool_pilot_replay.py run` → **rc0 全 PASS**；网络面 131.4s / 48 请求格（12 交易日 × 4 面）零豁免零形状旗零重复代码。
- 判据读数（8/8 PASS）：J1 完备 48/48；J2 双 derive 恒等 100%（含梯队直方图）；J3 N_zt median=53.5 ∈ [40,120] ✓·p99.9=103 ≤ 250 ✓·裸 max=103 ≤ 250 ✓·zb_rate median=0.2323 ∈ [0.05,0.70] ✓；J4 max_board 逐日 4..7 ≤ 10 ✓；J5 幂等重 derive 字节恒等 ✓。
- 三轴序列（as-collected 冻结快照·详 results/zt_pool_pilot_replay_days.csv）：N_zt 逐日 55/32/89/47/78/103/63/51/52/33/57/52；N_dt 逐日 16/27/4/1/0/2/3/13/13/56/10/9；窗=2026-09-14..09-30 共 12 个交易日（09-19/20/26/27 周末+09-25 中秋假期·本地 ETF 日历 derive）。
- 预测对账（§5）：P1 **部分对**——fetch 成功率 100% ✓；日数 12 vs「~13」近似差 1（以日历 derive 为准条款内·如实记）。P2 **部分错**——median 53.5 ∈ [50,90] ✓；「全部落 [40,120]」✗：09-15=32 / 09-28=33 两日低于下带（10/12 落带）→ 教训=带下沿对弱情绪日过紧，N_zt 可低至 32；判据主判面（median/p99.9 分布界）不受影响照过。P3 对（0.232）。P4 对（窗内无指数 |r1|≥5% 危机日）；**附加观察（供给面正向证据）**：09-28 N_dt=56 ≈ 5.9×窗内中位（~9.5）而指数无危机级波动——跌停轴异动独立于指数级危机=三轴门 N_dt 轴携带微观结构独立信息量（预测值面待 ≥12mo 前向史另批验证·本批不升级主张）。P5 对（J2/J5 100%）。
- 门禁链损耗账：本批无 G1'/G2 判据面（数据面批）——`results/gate_attrition.json` 无新增行（不适用·如实）。
- 试验量归因：单批 48 格 = 回放窗 12 交易日 × 4 面（唯一可得 as-collected 窗；深史不存在 = EM 源硬界·r856 bisect 实证）。

## §8 批后复盘【必填·r857】

- 预测对账汇总：对 3（P3/P4/P5）+部分 2（P1 日数近似差 1 / P2 median 对但全带断言错）+部分错内含 1 真教训（带下沿过紧）；零门禁损耗。
- **全起点分布【必答】**：本批为数据验证批·单窗（2026-09-14..09-30 as-collected 唯一可得窗）——单窗如实披露；多窗推迟至前向积累（深史不存在=EM 源硬界非本批可解）。
- 宝藏捕获收口步（O-20261003-2030 §1）：问「本批有无新宝藏？」——**无**（EM zt-pool 数据面已在 r856 登记；双 derive 机制验证=既有 selftest 族的回放复验非新方法；N_dt 独立异动观察=候选证据非已验证宝藏，入轮报告流转）。
- 方法论资产卡捕获步（O-20261002-2100）：问「本批有无新方法？」——**无**（monkeypatch-temp-panel 路径2 复用采集器存储机械=标准复用范式；无新算法件）。
- 批结论：**pilot 面 PASS**——采集器存储机械+三轴派生在 as-collected 浅窗 100% 机制验证通过；预测值面（情绪周期三轴门→REGIME-5 供给）按 T-67 §2 待 ≥12 个月前向积累后另开预注册。
