# T-101-V4-A2-CORRSOURCE 预注册（幸存格相关性来源分解·D6 REJECT 出口子批）

> 父批：research/T-101-V4_PREREG.md（T-101-V4-A2-PRESCREEN·r433 bm-a 实跑冻结）。本件=父批 §7/§8 预先承诺的 D6 出口：「存活格升格全量判决面前须另开预注册论证相关性来源（beta 同源分解）」。
> 权威：research/BACKTEST_SCIENCE.md（v2 判据）＋ BACKTEST_PLAN.md 三铁律 ＋ research/COMPUTE_AUDIT.md（批件纪律）。模板=PREREG_TEMPLATE.md。
> 用法：跑前 commit 冻结；跑后只许回填 §7/§8 占位节，禁改判据禁重跑。

## §0 批件身份【跑前】

- 批名 / 批号：**T-101-V4-A2-CORRSOURCE**，批内格数＝**1**（父批唯一幸存格 510050|RSV30_low<0.2 的分解面；判决收口分析批=非新假设族开拓，N 计 1 防口径争议）；
- 认领：F-04 先行——fleet/inbox/MSG-20260929-1535-bma-t101v4-corrsource.md；任务板引用=T-101 v4 版本批（DECISION_CHAIN v1.2 §四.7 锦标赛节拍）；车道 bm-a；
- 部门归属：dept:研究；
- 算力预算：<10s 单进程（1 格 OLS/恒等式分解+K=200 同掩码循环位移 null），≤10min 无需入池；批报告带 audit 段。

## §1 α 机制段【必填·D6】

- [x] **行为偏差**（继承父批 A2 臂机制主张，本批不主张新 alpha）：RSV 超卖门=处置效应驱动的超卖修复（panic-selling 后修复窗收取对手盘「割肉者」付出的代价）——本批任务=检验幸存格收益流是否真含该机制的**时机 alpha**，还是 merely 内嵌 beta 敞口的同源复制（父批 §1 预声明的「beta 同源主险」被 D6 max|corr|=0.9424 实测命中，本批=既定出口的归因分解）。

**同族相关性准入检查**：本批不引入新策略函数——分解对象=父批已计数的 510050|RSV30_low<0.2 格自身；max|corr|（vs 510050 B&H 日收益）=0.9424（父批实测·本批的分解主题非准入项）。

## §2 数据与面板【跑前探针事实】

- 宇宙：单员 510050（父批幸存格）；数据锚面四元组＝`data/daily/sh510050.csv` ＋ `t101_v4_a2_prescreen.load_panel`（raw `pd.read_csv` 直读截断〔非引擎池面〕·内建探针-锚同面断言：路径在位+尾行==cutoff，不符=FACE-MISMATCH VOID fail-closed）＋全史起算（首行 2005-02-23 族）＋RSV30 预热 30 bar（父批 first_valid=2005-04-06）；
- **evidence_cutoff（前向锁盒 D2）=2026-09-28**：面板截断到 cutoff，cutoff 后新 bar 不得回流本批；结果 JSON 顶层带 `science_gates.cutoff_meta(cutoff)`；
- 数据完备门：load_panel 断言（尾行==cutoff）即门；不过门=VOID 拒烧；
- 成本口径：**V1 恒定**（COST_LEG=0.0005/腿，父批锚点复现双轨防漂移律——历史锚点子批禁换 V2）。

## §3 方法学【冻结】

- 信格重建：**零重实现**——import 父批 `t101_v4_a2_prescreen` 的 `load_panel/gate_mask/position_series/daily_returns/sharpe/ann_ret`（掩码=RSV30<0.2·T+1 开盘保守代理·成本 0.05%/腿，与父批逐位一致）；
- 分解面（判读恒带）：
  - **敞口分解**：ON-share（pos=True 日占比·全窗+OOS）——相关性结构解释（多数在市掩码≈beta 复制器）；
  - **OLS 归因**：r_strat = a + β·r_bh + ε（OOS 窗与全窗各一遍；Newey-West HAC lag=5 t 值）——α 年化=a×252、t(α)、β、R²；
  - **超额恒等式**：策略超额 vs B&H ≡ −(OFF 日 B&H 收益和) − 成本拖累——OFF 日规避收益年化、成本拖累年化、top-5 OFF 日规避额占比（尾部集中度·描述条款）；
- null 对照：**同掩码循环位移**（父批同法）：K=200，seed 基＝**t101_v4_a2_corrnull=20308500**（新基·registry 随本件冻结 commit 注册·rg 扫带 20308500 零 seed-face 命中）；每位移重算 OOS 超额→null p95；
- 账本：`science_gates.append_ledger("T-101-V4-A2-CORRSOURCE", 1, "t101_v4_a2_corrsource.json", evidence_cutoff="2026-09-28")`。

## §4 判据【跑前写死】

- 本批**不调用 G1' v2/G2**（判决收口分析面·非注册面·无新策略宣称）；冻结 D6 出口双出口规则：
  - **TIMING_ALPHA（升全量判决面资格·须超额框架+beta 中性披露）**：OOS α 的 HAC t ≥ 2 **且** 真实 OOS 超额 > 同掩码位移 null p95——两腿全过才许入全量判决面；
  - **BETA_SAME_SOURCE（关线）**：任一腿不过（t < 2 或 超额 ≤ null p95）→ 幸存格=beta 同源复制、**A2 前导臂整线关闭**（9 KILL+1 关线=10/10 终结，零格升全量判决面，禁换参重跑）；
- 硬界三件套：不适用（非数据腐坏/健康检测判线批）；描述条款=OFF 日规避集中度如实披露（§5 极端日先验）。

## §5 跑前预测【写死于跑前】

1. **敞口解释**：ON-share ≈ corr²≈0.888 → 门在 OOS ~85-92% 日子开着（多数在市=结构性 beta 复制器）；
2. **α 不显著**：OOS 超额 +0.27%/年 ≈ 每 2 日 1bp vs 日 σ≈1.3% → HAC |t| 预期 0.2-0.8（≪2）；
3. **超额在 null 带内**：父批 OOS Sharpe 0.394 vs null p95 0.392（剃刀边）→ 超额面大概率 ≤ null p95；
4. **判决预测**：BETA_SAME_SOURCE → **关线**（A2 前导臂 10/10 终结·零格升全量判决面·负结果照报）；
5. **极端日先验**：OFF 日规避收益预计集中于 2015-06/07 股灾+2016-01 熔断+2018 bear 窗——top-5 OFF 日预期占规避总额 >30%（政体运气尾部集中，非系统时机，如实入描述面）。

## §6 产物

- script：`scripts/t101_v4_a2_corrsource.py`；
- results JSON：`results/t101_v4_a2_corrsource.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+audit 段）；
- 本件 §7 回填。

## §7 跑后实证【跑前为空——占位纪律：写数字即造假】

## §8 批后复盘【跑前为空】

