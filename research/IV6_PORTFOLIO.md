# IV6 组合风险预算批 — 预注册（跑前写死）

- 批名：IV6-portfolio-riskbudget（组合与资金部报告制 pass 2）
- 认领：F-04 先行——fleet/inbox/MSG-20260924-0253-ALL-iv6-claim.md 先于本预注册 commit；
  上游指针=research/shortline/EW6_PORTFOLIO.md §6.7 续作① + firm/portfolio.md 章程 §一.1
  （「EW 基线→IV 风险预算升级路径」=章程指名路径，非 P1 级新方向，GM 自决权 O-1620 范围内）。
- 部门归属：dept:组合（org_chart v3 组合与资金部）／dept:研究（执行面）
- 算力预算：12 引擎跑 + 2 组合求值 ≈ 5-8s @ workers=min(worker_cap, 6)（parallel_runner
  ProcessPool，audit.workers 落盘）；远低于 10min 线，无需后台化。
- 任务单映射：EW6 批（T-2026-09-23-06）续作；报告制 pass 2——零注册、零资金再分配、
  零触碰 level/paper、零载体更换（EW=在验证载体，IV6=升级路径测量；跑后禁择优翻案，
  IV 采纳与否=charter §五 T1 呈报路径，本批不产生分配后果）。

## §0 批件身份（模板 §0）

- 批内格数（N_eff 计账）= **14**（12 成员引擎跑 anchor-cum-sleeve x1+x2 + 2 组合求值
  IV x1/x2 纯派生）。零搜索 ⇒ 零 null 采样（组成披露口径同 EW6 §2.3）。
- 账本：`science_gates.append_ledger("IV6-portfolio-riskbudget", 14,
  file_name="results/portfolio_iv6.json", evidence_cutoff="2026-09-22", ...)`（dict schema 唯一）。

## §1 α 机制段（D6，四选一）

- [x] **结构性**：IV 风险预算不是新 α 主张——是组合构建力学。P3 实证（round-13）：
  非平衡 EW 让高波 composite 袖主导组合风险（**波动率失配稀释**——低相关结构未被收割），
  IV 逆波动率权重等化各袖风险贡献 → 把已被 EW6 证实的低相关结构（民间三员 0.02-0.29）
  按风险刻度收割。付费方=无新付费方（不主张新超额来源；主张=同一组员的风险效率重排）。
  P3 §6.3-① 边界条款同时入注：**IV 只缩风险不造 α**（SLEEVE_P3 A-IV9 复证）——若 IV6
  出现 Sharpe 提升，读作「权重碰巧倾向高 Sharpe 防守袖」的政体红利，禁读作新 α。

**同族相关性准入检查（D6）**：
- 本批**不引入任何新策略函数**（成员名册=注册 6 员固定，与 EW6 逐字相同）；
  组合层 IV6 vs EW6 日收益相关**按构造必然极高**（同一组 sleeve 仅权重倾斜，预注册点估
  ≥0.97，跑后如实披露）——D6 max|corr|≥0.7 拒收条款的立法目的（防相关新员膨胀 N_eff）
  在本批不触发：IV6 零注册、零 N_eff 策略面增量（14 格全部为既有组员复现+纯派生）。
  该相关值作为**披露项**记入 §7，不作为拒收门。

## §2 数据与面板

- 宇宙：core48 裸码现行面板（live.paper load_core）；成员=firm/traders/*.json 非下划线
  全集 6 员（=EW6 名册逐字：VOLATILITY-CE-01 / COMPOSITE-CE-01 / COMPOSITE-CE-02 /
  ENGULF-CE-01 / NEEDLE-DE-01 / DROUGHT-CE-01）。
- evidence_cutoff（D2 前向锁盒）：各成员 sleeve 逐员截断至注册件 evidence_cutoff
  （全员=2026-09-22）；结果 JSON 顶层 `science_gates.cutoff_meta("2026-09-22")`；
  IS=面板起点..2024-12-31、IS2（D2 降格段）=2025-01-01..cutoff、真样本外=cutoff 后
  锁盒经 paper 通道（本批不消费）。
- 数据完备门（不过禁跑）：①smoke 23/23；②live.paper 补丁自检 + 组合数学自检
  （ew6_portfolio.self_test_portfolio_math 复用）；③**EW6 双子门（本批新增，批 VOID 条件）**：
  重跑成员统计（full/is2 sharpe、n_trades、cutoff）与 results/portfolio_ew6.json 记录值
  |Δ|<1e-9 逐位一致 + corr 矩阵 full/is/is2 avg 逐位一致 + EW 组合再推导（等权 1/6）
  与 EW6 记录组合统计 |Δ|<1e-9——数据漂移绊线（EW6 于 00:54 落盘，若其间面板被改动
  即此处暴露）。任一破 ⇒ 批 VOID，无 verdict，禁修复重跑（新预注册另开）。

## §3 方法学

- **IV 权重公式（冻结）**：w_i = (1/σ_i) / Σ_j(1/σ_j)，σ_i = 成员 x1 sleeve 日收益
  （pct_change）在 **IS 段**（日期 < 2025-01-01，成员自身净值轴）的标准差。P3 先例
  （「IV（IS逆波动率）」）。权重四舍五入 6 位、和=1 披露。**不再平衡**（combine 语义与
  EW6 逐字相同：port=Σ w_i·(eq_i/eq_i0)，inner-join）。跑后禁调权重、禁换 σ 窗口
  （IS2 σ 重排=政体漂移，只作 §7 披露不作门）。
- 滞后规则：与注册证据同链（live.paper SIGNAL_BUILDERS + ExitPatch/CostPatch 复用
  禁重写；引擎语义 T 信号→T+1 开盘执行不变）。
- null 对照：零搜索 ⇒ 零 null 采样；被动基线=p2_calibration 记录常数（EW48 buyhold
  +monthly，照 EW6 引常数不重跑）。
- 成本口径：**V1 legacy 费率**（引擎加性旗标全 OFF；x1/x2 经 CostPatch；与注册证据口径
  连续优先，cost_v2 启用另开预注册——EW6 §2.6 同句）。新增 additive 引擎旗标
  `report_num_entries=True`（逐成员传入，仅 metrics 增一键，PnL 路径零改动，加性铁律；
  目的=组合层 F6 双口径 entries 求和）。
- 政体切片（charter §三必报）：IS/IS2 段分 + 日历年逐段 + R-配3 大熊态/常态日切片
  + R-配3 overlay pass 2（cap(t)=state(t-1) 因果、现金腿 0 收益、唯一源=firm/risk/regime.py
  常量 import，末日三布尔一致性门沿 EW6 §2.9——破 ⇒ VOID）。

## §4 判据（跑前写死）

- **主判据 = G1' v2**：`science_gates.g1_prime_v2(sharpe_full=IV6@x1 全期 Sharpe,
  returns=IV6@x1 日收益, batch_cells=14, n_trades=Σ成员 trades, n_entries=Σ成员
  num_entries)`——全期 Sharpe > skill_line_v2（数据驱动活线）且平稳 bootstrap CI 下界>0
  且 **entries_ok 为准**（F6 双口径，report_num_entries 注入为此服务）。逐列披露
  skill_line/bootstrap/trade_gate 全输入。
- **连续性描述条款（批级披露，EW6 同模板，非注册门）**：G1' 六条款（i>0.3521 记录线、
  ii 年化>0、iii 回撤≥-35%、iv 笔数≥30=成员和、v IS2 双正、vi>vi_bar 0.4004 记录线）
  + x2 存活（full>0.4004 且 IS2>0）+ worst_year>-30% + benefit_iv>0
  （benefit=IV6 Sharpe − Σw_iv·成员 Sharpe）+ DR_iv。
- G2 注册资格 v2：**本批不适用**（零注册；g2_registration_v2 不调用，如实声明）。
- **IV vs EW 头对头（本批核心交付问题，P3 之问）**：ΔSharpe/Δ年化/Δ回撤/Δworst_year/
  Δx2/benefit/DR 全表 + corr(IV6,EW6)。**预注册裁定**：头对头结果不改变 EW=验证载体
  事实（择优禁令）；IV 采纳与否=charter §五 T1 呈报总经理，本批零动作。
- EW 再推导（双子门腿）另记 v2 现行线读数（batch_cells=14 同 N_eff 语境，标注
  「今日线读数非 EW6 注册时点判定」）。

## §5 跑前预测（写死于跑前，跑后对账）

| # | 预测 | 置信 |
|---|------|------|
| P1 | 双子门全 PASS：锚定 6/6 + 成员统计/corr/EW 组合再推导 vs EW6 记录逐位一致 | 0.95 |
| P2 | IV 权重序：VOLATILITY 最大（0.30-0.50）；COMPOSITE 双员合计最小（<0.25）；民间三员居中 | 0.60 |
| P3 | IV6 full Sharpe ∈ [1.00, 1.40]（EW6 1.1438；向最高 Sharpe 防守袖倾斜=上行源，单袖集中=下行源）点估 +0.06 vs EW | 0.50 |
| P4 | benefit_iv ∈ [+0.15, +0.40] 且 DR_iv>1；benefit 可能低于 EW 的 +0.3763（分母=IV 加权成员均值被防守袖抬高）——方向不定如实预注册 | 0.50 |
| P5 | IV6 x2 存活（成员 x2 全 0.40-0.59 + 分散化；EW6 0.7574 先例） | 0.90 |
| P6 | IV6 worst_year ≥ EW6 -0.94%（防守袖加权改善尾部）或劣化不超 -0.5pp | 0.55 |
| P7 | corr(IV6, EW6) ≥ 0.97（同 sleeve 权重变体按构造） | 0.95 |
| P8 | R-配3 overlay：ΔSharpe ∈ [-0.15, +0.15]（EW6 +0.0505 同带）；熊态日切片 Sharpe<常态日（政体红利预期现象） | 0.70 |

## §6 产物

- scripts/iv6_portfolio.py（import ew6_portfolio 复用 member 跑数路径原语；成员跑数
  仅增 report_num_entries 注入点，其余逐字）；
- results/portfolio_iv6.json（顶层 cutoff_meta + audit 段 + prereg sha256 +
  trials_ledger dict schema + IV 权重 + 头对头表 + v2 门全输入 + 政体切片）；
- research/iv6_results.csv（12 成员行 + 2 IV 组合行 + 2 EW 再推导行）；
- **results/gate_attrition.json 首建**（science_audit C4 诚实发现闭环：IV6 本批条目 +
  EW6 条目回填标注 retro_fill=true；schema=批条目列表，measurement 批记门结果非淘汰数）；
- 本文档 §7 回填（唯一跑后追加区）。

## §7 跑后实证【跑前必须为空——占位纪律】

> 跑前冻结版 commit=3c4c147（sha256=`0f33111afd302001dc2189155a0adc8611fe073d78c2
> cba52063db480114b20d7`，=batch JSON `prereg_sha256_at_run` 逐位一致=冻结实证）；
> 跑数 2026-09-24 03:0x 一次定稿（4.6s @ 6 workers，
> 12 引擎跑 + 2 IV 求值 + 双子门再推导腿，账本 2753→**2767**）。本节为跑后唯一追加区。

### 7.1 硬门（全 PASS，批 non-VOID）
- 补丁自检 + 组合数学 + IV 数学自检 3/3；锚定门 6/6（x1 IS/IS2 逐位 + x2 注册
  cost_x2 证据全 OK）。
- **双子确定性门 PASS**：12 成员统计（full/is/is2 sharpe、trades、oos_trades、
  cutoff）与 portfolio_ew6.json 记录 |Δ|<1e-9 逐位一致 + corr 三段 avg 逐位一致
  （full 0.1761/is2 0.3313 与 EW6 记录同）+ **EW 组合再推导与记录组合 10 字段
  全等**（1.1438/3.68%/-5.67%/2127 笔/worst -0.94%/benefit +0.3763/DR 1.4904/
  x2 0.7574/x2_survive）——数据零漂移实证，IV 结果继承 EW6 同源可信度。
- 政体唯一源一致性门 PASS（as_of 09-23 非大熊，warmup 249 日诚实计数）。

### 7.2 IV 权重结构（IS σ 口径，冻结公式产出）
σ_IS：NEEDLE 0.001505 < VOLATILITY 0.001606 < DROUGHT 0.001966 < ENGULF
0.002061 << C1 0.004212 << C2 0.008412 → 权重 NEEDLE 0.2520 / VOLATILITY
0.2361 / DROUGHT 0.1928 / ENGULF 0.1840 / **C1 0.0900 / C2 0.0451（COMPOSITE
双员合计仅 13.5%** = 高波轮换袖被风险预算压缩 86%仓位）。

### 7.3 主结果（IV6 报告制 pass 2）
- **IV6 full Sharpe 1.3702 / 年化 2.79% / 回撤 -2.42% / 2127 笔（=成员和）/
  worst_year +0.01%（七年无亏损年保持，2022=+1.3%）**；IS2 1.7119。
- **benefit +0.5670 / DR 1.7058**（IV 加权成员均值 0.8032 → 组合 1.3702）=
  超越 EW6 的 +0.3763/1.4904 = **项目史上最厚分散化增益再破纪录**。
- **x2 存活 0.8989**（EW6 0.7574，安全垫 +0.357→+0.499）+ IS2 x2 双正。
- 六条款描述性全绿（i>0.3521、vi>0.4004 记录线均过）。
- **G1' v2 主门 PASS**：1.3702 > skill_line_v2 **0.9339**（N_eff=2767 活线，
  μ_null+σ_null·√(2lnN) 项主导）+ 平稳 bootstrap CI 下界>0 + F6 entries
  1798≥30（entries_ok 为准，trades 2127 双口径全披露）→ **pass_v2=True**。
- EW 再推导今日线读数亦 PASS（1.1438>0.9339；标注=今日线读数非 EW6 注册时点判定）。

### 7.4 IV vs EW 头对头（P3 之问的 6 员答案）
ΔSharpe **+0.2264**（1.3702 vs 1.1438）· Δbenefit **+0.1907** · ΔDR +0.2154 ·
Δ回撤 **+0.0325（-2.42% vs -5.67%）** · Δworst_year +0.0095 · Δx2 +0.1415 ·
**Δ年化 -0.89pp**（2.79% vs 3.68%）· corr(IV6,EW6)=**0.8882**。
机制读数（诚实律）：①Sharpe 增益**非新 α**——IV 加权成员均值同步抬升
（0.8032 vs EW 0.7675，权重倾向高 Sharpe 防守袖 VOLATILITY/NEEDLE）=§1 预注册
「权重碰巧倾向政体红利」条款精确应验，P3「IV 只缩风险不造 α」边界条款维持有效；
②真增益=风险刻度重排：同源 sleeve 下回撤近半减、benefit/DR 双升、年化让渡
0.89pp——**风险预算是正确拧法**（P3 §6.3 结论在 6 员外推成立）；③IS2 段
1.7119<EW 1.7727（IS σ 权重在 2025+ 民间簇收敛政体下轻微次优，预期内如实报）。
**载体裁定不变：EW=验证载体（择优禁令），IV 采纳=charter §五 T1 呈报总经理。**

### 7.5 R-配3 应用层（IV6 口径）
熊态日 188 天；overlay（cap(t-1) 因果）full 1.3293（Δ-0.0409 ∈ 预注册带）、
年化 1.91%、**worst_year -1.32%（劣化：基线 +0.01%→-1.32%，EW6 同病**——防守型
账本被 20% 大熊帽拖累第三次实证：熊态日本身正收益 0.9933 Sharpe）；切片：熊态日
0.9933 < 常态日 1.4606（政体红利预期现象 ✓）。

### 7.6 预测对账（J19 闭环）
| # | 预测 | 实测 | 判 |
|---|------|------|----|
| P1 | 双子门+锚定全 PASS | 6/6+全字段逐位 PASS | ✓ |
| P2 | VOLATILITY 最大 0.30-0.50；COMPOSITE<0.25；民间居中 | 最大=NEEDLE 0.252（VOL 0.236 次之）；COMPOSITE 0.135 ✓；民间居中 ✓ | 半（排序错，带对） |
| P3 | full ∈[1.00,1.40] 点估 +0.06 | 1.3702（Δ+0.2264） | ✓（方向对，量级低估） |
| P4 | benefit ∈[+0.15,+0.40] | +0.5670 | ✗（高估带外，同 EW6 P4 低估同根） |
| P5 | x2 存活 | 0.8989 ✓ | ✓ |
| P6 | worst_year ≥ EW 或劣化≤0.5pp | +0.01%（改善） | ✓ |
| P7 | corr(IV6,EW6) ≥ 0.97 | 0.8882 | ✗（权重倾斜去相关超预判） |
| P8 | overlay Δ∈[-0.15,+0.15]；熊<常态日 | -0.0409 ✓；0.9933<1.4606 ✓ | ✓ |

5✓ 1半 2✗：两处低估同根（低相关结构的可收割厚度连续三批被低估：EW6 P3/P4 →
本批 P4；P7 错=权重倾斜的组合面去相关效应无先验锚，记入方法学）。

### 7.7 账本与产物
- trials_ledger：prev 2753 → **+14 = 2767**（12 引擎 + 2 IV 求值，与冻结预算 14
  精确一致零偏离；双子门再推导腿与 v2 读数=门/披露非账本格）。
- **results/gate_attrition.json 首建**（science_audit C4 诚实发现闭环）：EW6 条目
  retro_fill=true 回填 + IV6 本批条目（gates 全记录）。
- 产物：results/portfolio_iv6.json（prereg sha256 在录 + 顶层 evidence_cutoff=
  2026-09-22 + audit.workers=6）+ research/iv6_results.csv（16 行）+ 本节。

### 7.8 verdict
**IV6 组合 validated（报告制 pass 2）+ G1' v2 主门 PASS**——benefit +0.5670 项目
史上最厚、回撤 -2.42%、七年无亏损年、x2 0.8989；政体红利折价（P-5B）与 G2.5
晋升前置不变，零注册零分配零载体更换。IV 采纳与否=T1 呈报（总经理决策面），
续作指针：corr-watch 盯防（EW6 §6.7-②，IS2 0.33 若续升收窄安全垫）、
IV 权重月更机制 spec（组合部 charter §一.2 相关性月更合流）、现金腿预注册（Phase 1）。

## §8 批后复盘（s7-T）

- 预测对账（对/部分/错）+ gate_attrition 追加行 + 判线 v2 当批读数（skill_line_v2 数字
  随活线）+ 回执入轮报告与 CODELY.md 行级追加；零注册 ⇒ 无注册件/接线面。
