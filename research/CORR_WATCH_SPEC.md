# CORR-WATCH v1 — IV 权重月更 × 相关性监控合流 spec（组合与资金部 · charter §一.2）

- 批名：corr-watch-v1（监控/运维链，非评估批）
- 认领：F-04 先行——fleet/inbox/MSG-20260924-0345-ALL-corr-watch-claim.md（commit ffca0bb）先于本 spec commit。
- 上游指针：R35 bm-a 续作指针（corr-watch 盯防 + IV 权重月更与相关性监控合流 spec）+ firm/portfolio.md §一.1/一.2
  + research/IV6_PORTFOLIO.md §6.7（EW6 续作）+ P3 §6.3-（b）（OOS 相关抬升→分散化由 low_vol 袖独扛的盯防条款）。
- 部门归属：dept:组合（执行面复用研究 harness）。
- **类裁定（跑前写死）**：本件=**记录格复现 + 监控**（成员 sleeve 逐字复现注册配置、零搜索、零新主张），
  同类先例=smoke 锚定门（每轮 6 员复现不计账）与 g25 家族矩阵（「零新试验·记录格复现」口径）。
  ⇒ **零 N_eff 入账**；JSON 带 audit 段披露（charter §三 产出纪律）。任何未来把 corr-watch 扩成
  「新组合评估/新载体比较」的用法 ⇒ 另开 PREREG_TEMPLATE 预注册并恢复记账。

## §1 监控对象与数据

- 宇宙/成员：core48 面板 + firm/traders/*.json 非下划线 6 员（与 EW6/IV6 名册逐字）。
- **registered window（RW）**：成员 sleeve 截断至各自注册件 evidence_cutoff（全员 2026-09-22）——
  该窗相关矩阵**按构造冻结**（除非新员注册/注册件变更），本监控对其只做「复现+漂移绊线」。
- **forward window（FW，纸盘窗）**：cutoff 后新 bar 累积窗——真实盯防目标（P3「OOS 相关继续抬升
  收窄组合 ×2 安全垫」条款 + R35「IS2 0.33 续升」读数的 continuation 观察）。
  **FL 门槛（跑前写死）**：FW 两两相关需 ≥ **MIN_PERIODS=60** 根 paper bars；当前 bars=1
  ⇒ v1 诚实报 `insufficient_data`。FW 日收益序列**不在** results/paper/*_paper.json（只存聚合
  window_metrics）——FW 机械（live.paper 暴露窗口日权益或 fresh-signal 复推）= **deferred**，
  待 bars 靠近 60（≈2026-12）另开轮实现，本 spec 不预支。

## §2 复现与漂移绊线（twin gate）

- 成员 x1 sleeve：live.paper SIGNAL_BUILDERS + ExitPatch/CostPatch 逐字复用（EW6 harness
  import：E.member_run，禁重写）。
- **TWIN（VOID 条件）**：重推成员 full/is2 sharpe、n_trades 与 portfolio_iv6.json members 记录值
  `abs(got − recorded) < 1e-9`（记录值 4dp 舍入口径，比较前同位舍入）；corr 全窗/IS/IS2 avg_pairwise
  同法比对；IV 权重重推（§3 公式）与 iv_weights.weights 逐员 `abs(Δ)<1e-9`。任一破 ⇒ **watch VOID**
  （数据/注册漂移），只报不修，零静默（新预注册另开）。
- 复现 6 跑（x1 only）串行 ≈ 12-15s，无需后台化（r52 坑律：轮龄预算内）。

## §3 IV 权重月更公式（与 IV6 §3 逐字冻结）

`w_i = (1/σ_i) / Σ_j(1/σ_j)`，σ_i = 成员 x1 sleeve 日收益（pct_change）在 **IS 段**（<2025-01-01，
成员自身净值轴）标准差；6 位舍入、和=1 披露。**只做披露与 diff，不做采纳**——权重采纳=
charter §五 T1 呈报路径，本监控零分配后果。月更意义=新员注册/数据前向扩展时机制自动重算。

## §4 判据（跑前写死，禁看结果调线）

| 旗 | 条件 | 级别 |
|---|---|---|
| W1 | 任一 RW 全窗 pairwise \|corr\| ≥ **0.70** | RED（D6 机制线组合面反馈） |
| W2 | 任一 RW IS2 pairwise \|corr\| ≥ **0.70** | ORANGE（政体趋同越线预警，未破全窗 D6 线） |
| W3 | max IS2 pairwise 较上一 watch 记录抬升 ≥ **+0.05** | INFO（趋势预警；首跑=基线，无门） |
| W4 | corr(IV6, EW6) 披露（构造变体事实，IV6 §1 口径） | 披露无门 |
| W5 | EW6 或 IV6 组合 ×2 margin（x2_full − vi_bar）≤ 0 | RED（组合 ×2 死亡=安全垫归零实锤） |
| TWIN | §2 任一破 | watch VOID（无 verdict） |
| FL | FW bars < 60 | insufficient_data（诚实留白） |

- vi_bar 活读 science_gates.recorded_lines（禁手抄判线，T-02 6/7 纪律）；×2 margin 用的
  x2_full 活读 results/portfolio_ew6.json / portfolio_iv6.json 记录值（冻结产物只读）。
- rolling-60d pairwise 轨迹：RW 尾段（末 252 交易日）逐对 rolling corr(60d)，产出末值与
  IS2 段均值对照——「续升/回落」证据供 W3 趋势判读，本身不开新门。

## §5 产物与节律

- results/corr_watch.json：本跑 verdict + W1-W5/FL/TWIN 读数 + rolling 轨迹摘要 + audit 段
  （elapsed/workers/class=zero-Neff-monitoring）+ `history`（按 ISO 日 key 追加滚动，同日复跑幂等替换）。
- 节律=**月更**（每月首轮随 science_audit 跑）+ 新员注册/门禁批落盘后按需；不入 10 分钟 S6 链
  （scorecard 同款 automation_note 口径）。
- 面板接线（build_status _corr_watch_state + 事件行）= 后续轮候选，本 spec 不预支（防撞 bm-c 车道）。

## §6 占位纪律（跑前为空）

（跑后回填——跑前写数字即造假）

## §7 跑后复盘（跑后回填）

（跑后回填）
