# CNY_WINDOW_P1 预注册（春节效应具体窗批）· zoo §八 #38 证据升级件

> 血统：排队项兑现——DIGEST-20260924-source-matrix 外证行「春节效应具体窗预注册底稿排队波-3（窗定义跑前冻结防 window shopping）」＋ ASTYLE_ZOO.md §八 #36-38 行（骨架在库 seasonal.py；P1 期粗近似 holiday_effect=整月持有判负 −0.07）。本件=把粗月近似升级为**具体窗**的一次定稿判读批；非新方向（日历季节族已在册，O-20260923-1545 研究部自主域）。
> 模板：research/PREREG_TEMPLATE.md（T-02 6/7）。**冻结点=本件 commit**；跑后只回填 §7，禁改判据禁重跑（一次定稿）。

## §0 批件身份【跑前】

- 批名/批号：**CNY_WINDOW_P1**（春节窗择时批，批内格数 N_eff=3：PRE-5 / POST-5 / PREPOST-5+5 三臂）；本批附带 K=20 同掩码随机 null（计入试验总数）。
- 认领：F-04 先行已落——`fleet/inbox/MSG-20260926-0905-bm-b-claim-cny-window-prereg.md`（防双机在制撞车）；任务板引用=无既有票（zoo 排队项直认，反重复已查：全仓零 SPRING_FESTIVAL/CNY_WINDOW 命中）。
- 部门归属：**dept:研究**（短线动物园车道）。
- 算力预算：单机 <2 分钟（core48 面板 3 臂+20 null 全引擎跑，远低于 10min 批阈值，无需后台化）。

## §1 α 机制段【D6】

- [x] **行为偏差**（主选）：春节=境内最长连续闭市（7-9 天）+ 最大现金需求季（红包/礼赠/节前赎回）——节前**流动性需求方**（要用钱的持有人）被迫在闭市前折价卖券，耐心持有方赚取节前贴水；节后**资金回流+风险偏好重启**（春季躁动 folklore），晚到追涨者付出溢价。**谁付代价**：节前被迫折价卖出的流动性需求方；节后付溢价的后知追涨者。
- 辅证外源（registry 级）：arXiv 2609.20224《The Year-End Toll: Frictions Embedded in Option-Implied Rates》（CC-BY 4.0）——长闭市窗周边存在结构性摩擦的学术同构证据（年末摩擦⇒春节闭市摩擦，机制相邻非同证）。

**同族相关性准入检查【D6·批前声明】**：在册交易员（firm/traders/ 全员）与同批三臂逐对——本批三臂为**预声明变体**（PREPOST=PRE∪POST 构造性并集，臂间高相关是构造使然非独立发现，N_eff 照计 3 格不作扣减）；与在册交易员的相关性由 G1'v2 共享线（core48 null 池口径）承担判读，另列与 P1 期族内粗近似 holiday_effect（整月掩码）的构造包含关系披露：本批窗=其 Jan/Feb 面的**子集**（5+5 天/年 vs 整月），非新机制主张，属 #38 行内证据升级——变体并入既有族路径，禁另立行（r216 判定消费裁定同律）。

## §2 数据与面板【跑前探针事实·非结果】

- 宇宙/池：**core48**（data/daily 裸代码 CSV，J6 定义，p1_strategy_screen.load_core 同装载器）；日历面=510300.csv（2020-01-02→2026-09-24，1633 bars）。
- **窗提取探针已跑（确定性零网络）**：`scripts/cny_window_probe.py`→`results/cny_window_probe.json`——7 事件全验真（已知 CNY 日 2020-01-25…2026-02-17 全部落入探出的闭市括号内；规则=年内 [1/15,3/1] 起的 ≥5 天无交易最长 gap，tie 取近 2/10）。**2020 COVID 延期闭市（gap 10 天，重开 02-03 首日大跌）如实披露不剔除**（无事后手术）。
- 窗口与 **evidence_cutoff（前向锁盒 D2）**：面板截断到 cutoff **2026-09-24**（当前最后完整 bar 日）；cutoff 后新 bar 锁定不得回流本批。结果 JSON 顶层带 `science_gates.cutoff_meta("2026-09-24")` 块。
- 数据完备门：探针 validation.all_pass=true（7/7）+ core48 装载 ≥40 员——不过门禁跑批。

## §3 方法学【跑前】

- 信号定义（冻结）：掩码语义=p1 seasonal 族同构（mask_panel：entry=窗内 True、exit=窗外；引擎 T+1——窗前最后一根 close 发入场信号→窗首 open 进场，窗末 close 发出场→次 bar open 出场）：
  - **PRE-5**=闭市前最后 5 根交易 bar（含 last_pre_bar）；
  - **POST-5**=重开后首 5 根交易 bar（含 reopen_bar）；
  - **PREPOST**=两者并集（10 bar/年）。
  - 具体日期=探针件 `cny_window_probe.json` 逐字消费（禁批内重定义窗）。
- null 对照：**K=20 同掩码随机窗 null**（每年随机放 2 段 5 连续 bar 窗=同 ON 日统计；seed 基=`science_gates.SEED_REGISTRY["cny_window_p1"]=68_000`，本基已登记 commit 先于本批冻结）＋技能线用共享库默认 null 池（core48 校准级人口，p2_calibration lineage）。
- 成本口径：**V1 legacy（13bp×2 引擎默认，成本恒开）**——与 P1 期族内行（month_end/weekday/holiday）同引擎同成本=可比血统；另按描述性条款跑 ×2/×3 成本压测披露。
- 账本：`science_gates.append_ledger("CNY_WINDOW_P1", 23, file_name, evidence_cutoff="2026-09-24")`（3 臂+20 null=23 试验；返回 dict 嵌入结果件顶层，禁丢弃返回值——r217 律）。

## §4 判据【跑前写死·共享库禁手抄】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=3, pool="core48", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）**且**平稳 bootstrap CI 下界>0 **且** entries≥30（F6 双口径）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑，n_trials=23）**且** 家族 PBO≤0.25（screening/pbo.py CSCV 8 块）——G1' 未过则 G2 诚实缺输入拒收，禁补跑。
- 描述性条款（批级披露不入判）：年化>0、OOS（2025-01-01 恒盲分割）双正、回撤≥-35%、成本 ×2/×3 存活。
- **硬界设计三件套（c）极端日先验**：见 §5-3（2020-02-03 重开日危机先验）。

## §5 跑前预测【写死】

1. **PRE-5 臂**：节前贴水 folklore 方向为正但量级微弱；诚实预判=年化读数噪声大、**不预期过 skill_line_v2**（族内 P1 期三行全负先验；7 事件统计功效低如实披露）。
2. **POST-5 臂**：春季躁动方向为正；但含 2020 事件（重开首周深跌）拖累，OOS 段仅 2 个春节（2025/2026）——双正判定大概率不成立。
3. **极端日先验（三件套 c）**：2020-02-03 重开日单 bar |r| 可达 **≈8%**（COVID 跳空，公开史实），若 POST-5 命中该日其窗收益深负——本批无 max 硬界判线（掩码择时无逐日腐坏检测面），先验仅为读数解读披露服务。
4. **trade gate**：预计 entries≈7 事件×48 员≈336/臂——entries≥30 应过。
5. **总判读预测（一次定稿前的诚实预判）**：**FAIL G1' 概率高**（族先验全负+低功效）——判负=有效信息，兑现排队项收线 #38 具体窗证据升级，禁翻案禁重跑。

## §6 产物

`scripts/cny_window_p1.py`（selftest 子命令离线自检）＋ `results/cny_window_p1.json`（顶层：evidence_cutoff 块、三臂全指标+G1'v2 判定面、null 族披露、成本压测、§7 回填指针）＋ 本件 §7 回填＋ zoo §八 #38 行状态更新。

## §7 跑后实证【跑后一次定稿回填·2026-09-26 bm-b r235】

- **判定=诚实负收线：G1' 3/3 臂全 FAIL（line=1.1631；全期 Sharpe PRE-5 −0.114 / POST-5 −0.075 / PREPOST −0.053；bootstrap CI 下界均负；trade gate 46/44/76 全过但无助于线）**——与 §5-5 预判一致；批内同掩码 null 族（K=20）mean −0.033 / p95 0.598，三臂读数在 null 噪声带内无边缘信号；DSR 0.012/0.016/0.018 远低于 0.95（纯噪声面）；成本 ×2 三臂全灭（描述性条款负）。
- **POST-5 OOS 段双正（sharpe +0.438 / 年化 +0.0055）但全期负**——OOS 仅含 2025/2026 两春节（低功效如实披露），不构成翻案依据；PRE-5 OOS −1.017（2025/2026 春节前窗双负）。
- **§5-4 预测未中（诚实披露）**：预测 entries≈336/臂，实跑 46/44/76——掩码入场信号同时点亮 48 员，引擎 max_positions=5 并发帽把每窗实际入场压到 ~5-11 员/事件；语义=族内先例同构（month_end 行同帽），判读不受影响但**掩码类批的 §5 entries 预测必须按并发帽换算**（下批教训）。
- **2020 COVID 延期事件按冻结规则原样计入**（POST-5 2020 窗=重开首周含 02-03 大跌日，极端日先验 §5-3 兑现为深负贡献），无事后剔除。
- **收线**：#38 假日效应具体窗证据升级=判负闭环；春节窗（PRE-5/POST-5/PREPOST，冻结窗定义）在 core48 无稳定盈利边缘=有效信息，禁翻案禁重跑（一次定稿律）。账本 +23（184826→184849）。产物=results/cny_window_p1.json（evidence_cutoff 2026-09-24）+ scripts/cny_window_p1.py。
