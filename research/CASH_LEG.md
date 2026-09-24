# CASH_LEG 现金腿引擎特性 · 预注册（T-2026-09-24-09 · 跑前冻结件）

> 批类声明：**引擎特性验收批（tool-validation 类）**，非策略试验批、非因子批。本批零注册主张、零幸存者筛选、零判据门（G1'/G2 不适用）；账本口径=cost_v2_gates 先例（`ledger_trials_added=0`，结果件 JSON 必带 audit 段与顶层 evidence_cutoff）。任何未来把本特性当策略面使用的批=另开预注册走全门禁链。
> 权威：任务单 T-2026-09-24-09（GM 令 O-20260924-1045）＋ firm/portfolio.md mandate 3/4（R-配3 熊市 80% 现金停泊/20% 帽；现金腿=exit-to-asset 引擎特性）＋ firm/risk/iron_rules.md R-配3（现金/逆回购 ≥80%，数值零改动）＋ PREREG_TEMPLATE 结构。

## §0 批件身份【跑前冻结】

- 批名：CASH_LEG（现金腿 · exit-to-asset 停泊收益）；批内格数＝**0**（验收批无筛选格，N_eff 零增长）。
- 认领：F-04 先行=MSG-20260924-1130（bm-c，T-2026-09-24-09，commit 即锁）。
- 部门归属：dept:组合+工程（组合与资金部 mandate 4 主责；引擎加性改动走工程纪律）。
- 算力预算：6 交易员锚定复跑（flag OFF）+6 交易员描述性运行（flag ON）+合成面板 fixture×2 ≈ 14 次引擎跑，单跑秒级，**inline 可完成，无需后台化**；结果件 results/cash_leg_acceptance.json 带全字段 audit 段。
- 实现排期：本件=纯冻结轮（r36/r67/R49 纯 spec 先例）；实现轮=下轮起（引擎加性块+scripts/cash_leg_gates.py+验收跑一次定稿；轮龄 20+ 分钟禁开代码车道律）。

## §1 机制段【D6 必填——引擎特性批的机制=收益来源声明】

- 四选一：**[x] 结构性**——交易所质押式逆回购（GC001/R-001 族）是制度性短期无风险利率腿：防御性停泊现金在制度结构内按公开市场利率获得隔夜/短期收益，由金融体系短期资金需求方（正回购方）按市场价支付，**非任何交易对手的定价错误**。无未来数据：当日利率于当日早盘公布，收盘口径下非未来信息。
- **预期诚实声明**：本特性在历史上 188 个大熊日（EW6 实测 2020-2026）× 80% 停泊 × 1-2% 年化利率的量级 ≈ 全期累计 +0.1~0.3pp 年化收益抬升——**微小正 carry，不构成 alpha，不改变任何注册证据**；用途=R-配3 落地件的基础设施（停泊收益使 80% 现金停泊的经济成本下降）+REGIME_GUARD RED 响应的依赖件。
- 同族相关性准入检查【D6】：**N/A（无新信号函数入策略库）**——本批不产生任何策略候选、不触碰 SIGNAL_BUILDERS、不注册任何员；若未来某策略主张「停泊收益改善」，须另开预注册并按在册/在队全名单做 max|corr| 检查。

## §2 特性设计冻结【跑前写死——实现轮逐字执行】

- **加性旗标**：engine/backtester.py 新增参数 `cash_parking=None`（默认 None=OFF=legacy 路径逐字节不变；O-2250 引擎加性铁律）。旗标为 dict，三键：
  - `repo_rate`：pd.Series，年化利率百分数（如 1.475=1.475%），date 索引（引擎不 IO、不联网——数据由调用方装配传入，引擎保持纯函数可测）。
  - `major_bear`：pd.Series(bool)，date 索引，大熊日掩码——**唯一实现源=firm/risk/regime.py 大熊判定**（O-1820 R-配3/O-2311/O-2315 三令裁定：复用禁重建）；实现轮允许在 regime.py 加**加性序列助手**（返回全史布尔序列）供调用方装配，判定常数零改动。
  - `bear_park_frac`：停泊目标比例，**冻结值=0.80**（R-配3 现金/逆回购 ≥80% 原文数值；引擎按调用方传入值执行以便可测，验收/应用面恒传 0.80）。
- **停泊滚动语义（日频·冻结）**——引擎日内处理顺序不变（开盘买入→收盘退出→按现有引擎时序），停泊块追加在收盘估值之后：
  1. **晨结算**：上一交易日收盘停泊余额 `parked_prev` 归还可用现金（GC001 式 T+1 滚动，每日滚动一次）。
  2. **当日收益**：`parked_prev`（held into 当日 T）按 `rate(T)/100/252` 计息一次（交易日计息惯例；**保守近似**——真实逆回购含周末节假日利息，本模型只计交易日=系统性低估收益，方向诚实）。利率缺值日（如 2026-09-22 后源未更）→ **ffill 末值已知利率**（缺利率日禁计零利率=不虚增也不虚减口径外天数）。
  3. **收盘停泊**：若 `major_bear(T)`：`parked_T = min(cash_T, 0.80 × equity_T)`（equity_T=现金+停泊+持仓收盘估值）；否则 `parked_T = 0`（非熊日自动全解停泊）。停泊资金当日不可用于新开仓（已在晨结算归还，顺序天然满足）。
  4. **强平缺位声明**：若持仓>20% 权益致停泊目标不可达，**本特性不强制减仓**（min 天然只停泊可用现金）——强制配置到 80% 目标=组合配置层/enforce 面，**gated behind T-10 校准+GM 批**（REGIME_GUARD 纪律，本批零耦合）。
- **新字段纪律（new-field-only）**：flag ON 时 metrics 新增且仅新增：`parked_days` / `bear_days_in_window` / `parking_yield_total` / `parked_balance_end` / `parking_accrual_series`（可选日序列）；equity 曲线含停泊收益。**flag OFF 输出键集=legacy 键集逐字节相同**（T-03 先例：新键只在旗标 ON 时出现）。

## §3 数据源冻结【跑前探针事实】

- **repo_daily.csv**：`Money0923/data/repo_daily.csv`（仓内 95.8MB 有用集一部分，O-20260923-1514 triage 入库；**只读消费，Money0923 归档零触碰**）。实测（api.github.com 探针 2026-09-24 11:2x）：size=52,301B，sha=7f528a3746a62d7a346bfb998456c96cb3436262，两列 `date,rate`，覆盖 2013-08-27→2026-09-21（6 交易员全窗口覆盖，无前置缺口）。
- **bm-c 取件路径**：`git sparse-checkout add Money0923/data/repo_daily.csv`（52KB 单文件 sparse-checkout add 秒级，bm-c 入网配方；api.github.com 单 blob 取块为备胎）。他机已全量=直接读。装配守卫：文件缺件=验收 harness 诚实 exit 2+取件指引（不静默零利率）。
- 面板与窗口：core48（6 员注册口径）；**evidence_cutoff=2026-09-22**（锚定纪律；repo 序列同步截断 09-22——其自然末值 09-21 经 ffill 规则覆盖 09-22）；结果 JSON 顶层 `science_gates.cutoff_meta("2026-09-22")` 必带。
- 数据完备门（不过禁跑）：repo CSV 在盘＋regime 判定器全窗口可算（510300 本地日线覆盖）＋6 注册件在册。

## §4 验收门（写死·实现轮一次定稿；门全过=特性收编，任一门红=修复后全门重跑）

- **G0 smoke**：23/23（旗标缺席=默认路径零扰动）。
- **G1 legacy 字节同一**：6 交易员锚定门 6/6（live.paper 锚定机件，flag OFF）——引擎改动后注册证据逐位复现=端到端零扰动硬证据。
- **G2 确定性**：flag ON 合成面板双跑字节相同。
- **G3 手算 fixture**（J18 自洽律：fixture 期望值须按 §2 语义手算）：合成两符号面板+已知利率序列（熊日/非熊日/缺利率日三态）→ 停泊余额/收益逐位相等。
- **G4 无未来数据**：rate(T)=当日早盘公布信息（文档声明）+截断序列在 cutoff 处运行干净；停泊决策只用当日及以前信息。
- **G5 键集纪律**：flag OFF 输出键集≡legacy 键集；flag ON 新键仅 §2 清单。
- **G6 描述性报告（无门裁决）**：6 员 flag ON 逐员披露——bear_days/parked_days/parking_yield_total/ΔSharpe/Δannual（honest delta，无 G1'/G2 判定、无注册、无门禁链步）；audit 段（runs 数/耗时/ledger_trials_added=0）。

## §5 跑前预测【写死于跑前，实现轮跑后对账】

1. 六员窗口内大熊日 ≈ 188 日（EW6 实测复用）；Δannual ∈ [+0.05pp, +0.40pp]（VOLATILITY-CE-01 高现金闲置者受益最大，ENGULF/NEEDLE 低闲置者近零）。
2. ΔSharpe ∈ [-0.03, +0.15]；ΔmaxDD 不变或改善 ≤1pp（停泊只增现金不加仓）。
3. G0-G5 首跑全绿概率高（纯机械件）；最可能 bug=停泊滚动次序错位（G3 fixture 兼职抓取）。
4. 无任何员因本 delta 触及任何注册门（特性≠alpha，若出现大幅 Sharpe 变动=实现 bug 而非真收益，优先怀疑计息方向）。

## §6 产物

- 实现轮：engine/backtester.py 加性块（~60-80 行）＋firm/risk/regime.py 加性序列助手（若需）＋scripts/cash_leg_gates.py（gates/selftest 子命令）＋results/cash_leg_acceptance.json（顶层 evidence_cutoff+audit）＋本文件 §7 回填。
- 账本：零入账（tool-validation 类；无 append_ledger 调用；audit 段明示 ledger_trials_added=0）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（实现轮回填）

## §8 批后复盘【s7-T】

- 预测对账（§5 逐条对/部分/错）＋回执入轮报告＋CODELY.md 行级追加；无注册面故无 SIGNAL_BUILDERS/注册件动作。
- **REGIME_GUARD 依赖披露（任务单 item 3）**：本腿=REGIME_GUARD RED 响应「新资金现金停泊」的基础设施依赖件；enforce 恒 gated behind T-10 校准过门+GM 批+7 天否决窗，本批与其零耦合（shadow 状态机继续）；R-配3 应用面（强制配置到 80% 目标）=组合配置层后续件，不在本批。

## §9 零触碰清单【任务单 spec 原文逐条落地】

- 交易员注册件/level/paper 字段、iron_rules 数值、REGIME_GUARD shadow 写入与其阈值指纹、在制车道（J13 mill / XSTOCK / moneyflow / margin 拉取链）、live paper 管道接线（=未来独立批）、Money0923 归档本体（只读 repo_daily.csv）、engine 现有旗标语义（只加不改）。
