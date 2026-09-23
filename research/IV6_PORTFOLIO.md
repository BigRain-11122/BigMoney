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

（跑前为空。跑后一次定稿；工程修复重跑须双跑留痕如实记账。）

## §8 批后复盘（s7-T）

- 预测对账（对/部分/错）+ gate_attrition 追加行 + 判线 v2 当批读数（skill_line_v2 数字
  随活线）+ 回执入轮报告与 CODELY.md 行级追加；零注册 ⇒ 无注册件/接线面。
