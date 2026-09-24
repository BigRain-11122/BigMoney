# A158_TRUEGAP_IC 预注册：Alpha158 真缺口 7 族股票池小 K IC 参照批（日频 h10）

> **状态：FROZEN——跑前 commit 冻结（r119 bm-b）；跑后只许回填 §7/§8 占位节，
> 禁改判据禁重跑；产物写坏=确定性重执行合法（G2_FOLK 口径）。**
> 母版=PREREG_TEMPLATE.md（T-02 6/7）；判据血统=P-1c 股票池四件同式
> （research/shortline/P1C_STOCK_IC.md §32-33，bm-b r32 严口径）；
> 素材裁定=DIGEST-20260924-alpha158-comparison F2（B 类·开批路径 §五-2）+
> T-23 wave1 判定（开放池认领制）+ bandit 队列 event-attention-factors 臂。
> 认领：F-04 先行=MSG-20260924-2246-bm-b-claim-a158-truegap（r119）。

## §0 批件身份【跑前】

- **批名**：A158_TRUEGAP_IC；**批内格数（N_eff）**=5 主格 + 2 仿射克隆披露列 +
  50 null + h5/h20 报告列（若产出，各 +1；P-1c 先例=报告列入账）——精确计数
  finalize 时按统一链口径逐项披露。
- **车道**：bm-b 研究部（dept:研究）；执行链 r119=本件冻结+SEED 登记+队列翻面 →
  r120+=实现（`scripts/a158_truegap_ic.py`，复用 P-1c harness 面板/IC/null 件禁重写）
  → selftest → 后台批（>10min 强制后台化+跨轮 checkpoint，R41 律）→ finalize
  一次定稿。**续作点：r120 从实现腿起**。
- **算力预算**：5 因子 ×（5129 股 × ~8000 期）单次 IC pass + 50 null 同掩码——
  P-1c 先例（181 因子+50 null 全批数小时内）→ 本批 ETA ≤10min 量级；仍按
  R41 后台化执行；批报告必带 audit 段（compute_audit CLEAN 否则不入账）。
- **多重性声明（前置第二眼）**：本批=Alpha158 缺口族**第 1 次**试验。**若本批
  FAIL（0/5 主格过三线）→ Alpha158 缺口线收线**，复活须新预注册+新机制论证
  （禁跑到达标为止）；PASS 员=STRATEGY_LIBRARY 参照行升级（参照→实测过线），
  **策略级转化须另开预注册**（G1' v2 共享库门+股票域成本模型 P4_BATCH2 先例）。
- **账本**：零引擎跑（引擎 N 不动）；因子账本 added=§0 口径逐项入统一链
  （`science_gates.append_ledger`，dict schema 唯一禁手抄 prev）。

## §1 α 机制段【D6——无机制段=批不受理】

四选一（本批=7 特征 3 信息族 2 机制，逐族勾选）：

- [x] **行为偏差（Aroon 三族 IMAX/IMIN/IMXD）**：新鲜度锚定——投资者锚定近期
  极值，创新高/新低的**时间距离**编码趋势强度与羊群拥挤度；代价支付方=陈旧
  高点后的迟到追涨者/陈旧低点后的恐慌割肉者。GTJA191+WQ101 机械扫描同构缺失
  实锤（digest F2）=四库内无既有覆盖，真缺口。
- [x] **微观结构（WVMA + 量 RSI VSUMP/VSUMN/VSUMD）**：量加权波动率与量向
  分享=订单流不平衡/流动性需求代理；代价支付方=流动性需求方（大单冲击成本）。
  邻件先验=STREAK −0.976 深负、振荡超卖四族全灭律 → **先验打折如实入 §5**。

**批内同族去冗余（冻结）**：
- **仿射克隆律（数学事实，跑前写死）**：`VSUMN=1−VSUMP`、`VSUMD=2·VSUMP−1`
  （分母同 `Sum(|Δvolume|,d)+1e-12`，loader 202-296 行公式逐字）→ 逐日横截面
  z 化后 **VSUMN_z=−VSUMP_z、VSUMD_z=VSUMP_z 恒等**。故二者降为**披露列**
  （零信息增量，不入主格、不占 N_eff 主计数——防 P-2 弱尾稀释，小 K 纪律）。
- **Aroon 三族**：IMXD=IMAX−IMIN 为双源差分（非线性于单源 z），与 IMAX/IMIN
  各自保留独立信息 → 3 格均入主格。
- **跨机制 corr 披露门（D6 数值面）**：跑时算 5 主格两两日频信号序列
  max|corr|（pairwise-complete，重叠≥200 交易日）入 §7 披露；**同机制内
  高相关=预期（不拒收）**，跨机制对 ≥0.7 = 意外发现如实呈报（无既有在册
  策略比较=因子层批，策略级 D6 逐对名单归转化批，XSTOCK §1 先例）。

## §2 数据与面板【跑前事实】

- **面板** = P-1c Stage-A 股票缓存（`Money02/data/cache/p1c_stock/`，float32
  T×N，open/high/low/close/volume/amount/pct_chg；688/689 双归一已内建 r49 口径）；
  **宇宙=缓存 ok 集（5129）**（P-1c/XSTOCK 同口径；b_layer 3517=策略级宇宙，
  因子层不用，如实披露）。
- **窗口与 evidence_cutoff（D2 前向锁盒）**：日期轴截断 **cutoff=2026-09-22**
  （与 P-1c/P-1d/XSTOCK 全链一致）；cutoff 后新 bar 锁定不得回流本批；结果 JSON
  顶层必须带 `science_gates.cutoff_meta(cutoff)`（缺字段=science_audit C2
  VIOLATION）。IS 段 ≤2024-12-31（composite_ic.IS_END），OOS 段 2025-01-01→cutoff。
- **数据完备门（不过不跑批）**：缓存 ok 集=5129（±1 容差如实披露）；pct_chg
  与 close 逐日逐股一致率 ≥99%（P-1c 构建期已验，跑时抽验 500 股）；IMAX/IMIN
  依赖 high/low 无 NaN 期 ≥95%。
- **滞后规则（禁未来数据）**：全部 7 特征=t 日收盘可算 → panel[t]（GTJA 腿
  同约定）；实现必须过 truncate-and-compare 因果自检（P-1c/XSTOCK 同款）。

## §3 方法学【跑前冻结】

- **因子定义（vendored loader 逐字公式，window d=20 冻结，永不 import 源件）**：
  - `IMAX20 = IdxMax($high, 20)/20`（距 20 日高的天数占比）
  - `IMIN20 = IdxMin($low, 20)/20`
  - `IMXD20 = (IdxMax($high,20)−IdxMin($low,20))/20`
  - `WVMA20 = Std(|$close/Ref($close,1)−1|·$volume, 20)/(Mean(同式,20)+1e-12)`
  - `VSUMP20 = Sum(Greater($volume−Ref($volume,1),0),20)/(Sum(Abs($volume−Ref($volume,1)),20)+1e-12)`
  - 披露列：`VSUMN20=1−VSUMP20`、`VSUMD20=2·VSUMP20−1`（仿射克隆律 §1）
  - 主口径窗=20（Alpha158 窗集 {5,10,20,30,60} 中位窗；单窗冻结=小 K 纪律，
    全窗扫=35 特征大 K 陷阱，digest F2 明令禁止）。
- **h 口径（跑前冻结，换口径=数据窥探红线）**：**h10 主口径**（判格）；h5/h20=
  报告列（无判格语义，P-1c 先例；h20 仅 V1 过线员披露+snooping 折价标签）。
- **null 对照（MSG-1800 令股票池口径）**：K=50 白噪声因子（`seed=55_000+i`，
  i=0..49；**新基 55_000 本轮已登记 `science_gates.SEED_REGISTRY['a158_truegap_ic']`**），
  掩码=tradability 同真因子同掩码；null 线 p95 按 h 分列（h10 主判线）；独立
  checkpoint 步。
- **成本口径**：IC 参照批无成本腿（因子层零成交）；股票域成本（V1 26bp 域基线
  +null 校正，digest F5）**归策略转化批**，本批不触及。
- **账本**：`science_gates.append_ledger('a158_truegap_ic', trials, file_name,
  evidence_cutoff='2026-09-22')`，dict schema 唯一。

## §4 判据【跑前写死，禁看结果调线】

**P-1c 股票池四件同式（bm-b r32 严口径，逐字）**，h10 主口径，全 |绝对值| 判：

- **V1**：|IC_mean| > max(0.02 地板, 本批 K=50 null p95)；
- **V2**：|IC_IR| ≥ 0.30（P-2/XLIB/XSTOCK 同墙）；
- **V3**：OOS IC 与 IS 同号 且 |OOS IC_mean| ≥ 0.5×|IS IC_mean|（PS2 同式）；
- **A3 期数门**：IS 段 n_periods ≥ 500。

**PASS = V1∧V2∧V3∧A3（逐格判）**；族级结论=任一主格过线（Aroon 族/波动量族/
量 RSI 族）；批级=5 主格过线数。判据引用=共享库 `scripts/science_gates.py` 既有
因子门禁函数（P-1c 消费面），禁手抄判线（MSG-0226）。缺输入=诚实拒收。

## §5 跑前预测【写死于跑前，跑后 §7 对账】

1. **Aroon 三族（机制张力主战场）**：反转 DNA 支配域（GTJA 081/070 簇货架）vs
   Aroon 趋势新鲜度 Lore——方向不确定如实写死：IMAX20（新高新鲜度）IC **负向
   概率 60%**（新鲜高点=追涨拥挤→反转域惩罚）；IMIN20 正负各半；IMXD20 随
   IMAX 主导。带：|IC| ∈ [0.005, 0.030]，IR 多数 <0.30。
2. **WVMA20**：低先验（波动率族在反转 DNA 域弱语义+streak 深负邻件）：
   |IC| ∈ [0.002, 0.020]，V2 预计不过。
3. **VSUMP20**：振荡/占比族先验打折：|IC| ∈ [0.003, 0.025]；量向分享≠价格
   分享（SUMP 判死不迁移），方向偏负概率 55%（放量上涨=注意力峰值→反转）。
4. **null 线**：K=50 h10 p95 ∈ [0.0013, 0.0022]（P-1c 0.0016 复现带）→
   **V1 有效判线=0.02 地板**（null 线远低于地板，同 P-1c）。
5. **过线总数**：5 主格中 [0, 2]，点估计 1（若有过线，最可能 IMXD20 或 IMIN20
   ——双源差分/新鲜低点）；整体 PASS 概率 25-40%（先验打折口径）。
6. **批内跨机制 corr**：IMAX|IMIN 负相关 [−0.7,−0.2]；IMXD 与两者正相关；
   Aroon×WVMA×VSUMP 跨机制对 |corr| <0.5（≥0.7=意外呈报）。

## §6 产物【冻结】

- `scripts/a158_truegap_ic.py`（gates/run/selftest 子命令；**import 复用**
  P-1c harness 面板加载/横截面 z/逐日 rank IC/null 机件，禁重写；vendored
  定义件永不 import）+ selftest（仿射克隆律断言=VSUMN_z≡−VSUMP_z、
  VSUMD_z≡VSUMP_z 逐位；IdxMax/IdxMin 边界 fixture；truncate-and-compare
  因果自检）；
- `results/shortline/a158_truegap_ic.json`（顶层 evidence_cutoff=2026-09-22
  =science_gates.cutoff_meta 合法键 + prereg_sha256 + 批内 corr 表 + null 线
  按 h 分列 + 逐格 V1/V2/V3/A3 输入全披露）；
- `research/shortline/a158_truegap_ic_cells.csv`（逐格账）+ 本文件 §7/§8 回填。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（待跑批轮回填）

## §8 批后复盘【必填·s7-T——跑后回填】

（预测对账+门禁链损耗账 gate_attrition.json 追加行+判线当批读数；回执入轮
报告+CODELY.md 行级追加；若过线：STRATEGY_LIBRARY 参照行升级+转化批前置披露）
