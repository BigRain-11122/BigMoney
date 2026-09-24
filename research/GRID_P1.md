# GRID_P1 预注册（A 层网格收割迁移批）· QUANT_STYLE_ATLAS #8 · T-2026-09-25-40 slice-2

> 本件按 `research/PREREG_TEMPLATE.md` 起草，跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。

## §0 批件身份

- 批名 / 批号：**GRID-P1**（批内格数＝2 cells ×(x1+x2) + 100 null + 被动 2 + 锚定 6 ≈ 112 计 N_eff）；
- 认领：F-04 先行 `fleet/inbox/MSG-20260925-0300-bm-b-grid-lane.md`＋任务板 `fleet/tasks/T-2026-09-25-40-P1.json`（bm-b 认领，slice-1=骨架+本预注册，slice-2=runner+池批）；
- 部门归属：dept:研究（A 层自主过闸，QUANT_STYLE_ATLAS 行 8「骨架迁入过闸」，O-1620 非必需=非 P1 新方向）；
- 算力预算：est <10min serial（48 池全史 ~1600 bars ×112 runs）；仍按 O-2100 入 `results/runnable_pool.json` 后台化（workers=1 BelowNormal 即可，C8 autofill 续跑）；批报告必带 audit 段。

## §1 α 机制段【D6】

- [x] **行为偏差**：锚定/处置效应——低波稳态品种内，通道底部买入＝向恐慌性/惰性卖流提供流动性，赚「位置回归」的钱（Money0923 原典「与趋势/反转正交」）；付费方＝通道区间内追涨杀跌的往返流量。
- [ ] 风险溢价 / [ ] 结构性 / [ ] 微观结构（ETF 稳态震荡结构为背景条件非主机制）。

**同族相关性准入检查【必填·D6】**：与在册 6 员（VOLATILITY/COMPOSITE×2/ENGULF/NEEDLE/DROUGHT）＋同批全部 cells 的日收益 `max|corr|`，runner 批内计算（sleeve-tag 先例，`new_signal_p1.py` 同构）；**`max|corr| ≥ 0.7` → 拒收**（不得入候选池，诚实披露数值；主张新机制须另开预注册）。VOLATILITY-CE-01 同池低波族为最大撞车风险（同 n_targets 池构造），预测见 §5。

## §2 数据与面板

- 宇宙/池：core48-bare-codes（`live.paper.load_core`，48 只，无扩池）；
- 窗口与 **evidence_cutoff**：面板全史，cutoff=截断到 runner 读取日的最新完整 bar（`2026-09-24`，smoke freshness 同源）；cutoff 后新 bar 锁定不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)`；
- 数据完备门：`live.paper.self_test_patches()` PASS＋48/48 OHLCV 可读（smoke 同门）＋anchor 复现 6/6（硬门，任一 BROKEN=批 VOID）。

## §3 方法学

- 信号定义（冻结参数，`strategies/grid.py` 已冻结提交）：`grid_channel_harvest(channel_len=60, n_grids=6, n_targets=12, top_k=5, rebal_days=10, vol_win=30)`——通道位置 pct=(close−roll_min)/(roll_max−roll_min)，分档 `1−floor(pct×6)/6`，低波池（年化σ 30d 窗 rank≤12）内按分数取 top5，会员每 10 个交易日冻结（`_topk_frozen` 房契）；滞后规则：信号 t 收盘算、t+1 开盘执行（T+1，引擎因果）；中心参数=Money0923 param_space 中带值，零搜索（NSP1 单点先例，防 p-hacking）；
- **与 Money0923 原典的已知发散（披露）**：连续权重阶梯→二元会员制（房子引擎无权重面）；出池即归零→冻结窗内会员续持（成本现实）；目标总暴露 target_exp→引擎 sizing 0.95/5（composite 注册约定）；
- null 对照：K=100（每 exit regime 50，`p∈{0.02,0.05}`×25 seeds，seed 基=**55_500** 需先登记 `science_gates.SEED_REGISTRY`）＋被动基线 ew48_buyhold/ew48_monthly_rebal（一致性 info）；
- 成本口径：**V1 legacy 13bp** 基线 + `CostPatch(2)` x2 压测面（NSP1/T-33 同构；V2 迁移另开批不混本批）；
- 账本：`science_gates.append_ledger("GRID-P1", batch_trials=实测, file_name="results/grid_p1.json", evidence_cutoff=...)`（dict schema 唯一）。

## §4 判据【跑前写死】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`**：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）**且**平稳 bootstrap CI 下界>0**且** entries≥30（F6 双口径以 entries_ok 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入；批级描述条款（年化>0、OOS 双正、回撤≥−35%、x2 成本面逐年稳定）披露不替代 v2 门；
- 本批零 max 型腐坏检测判线（纯收益门），硬界三件套不适用——极端日先验仍按 §5 披露；
- 生存者=**G1' 候选 ONLY**：不注册（G2 深化=另开预注册）；D6 `max|corr|≥0.7` 拒收律见 §1。

## §5 跑前预测【写死于跑前】

1. **撞车风险主预测**：与 VOLATILITY-CE-01 的 max|corr| 落 0.4–0.8 带内（同低波池构造、top5/20d vs top5/10d 相邻），≥0.7 拒收概率不低——若拒收=机制面「网格≠低波持有」未获数据支持，诚实收线禁翻案；
2. **量级**：Money0923 sane 先验（853d×190 标的 +27.7%/dd −7.7%/S 0.96）不可直接迁移——core48 短史+T+1 成本+x2 面压制，预测全期 Sharpe 0.2–1.0、OOS 弱正或不正；
3. **门槛读数**：skill_line_v2 近批读数 1.10（T-33）–1.46（CTA-P2）区间，单 cell 过线概率低，预期 FAIL=诚实负（与 CTA/T-33 attack 波同向：紧成本下外部 folklore 多负）；
4. **极端日先验**：深史含 2015-07 救市涨停锁价、2016-01 熔断、2026-01-19 极端溢价日——低波池有抑制作用但非免疫；本批无 max 硬界，此类日只会体现在 Sharpe/CI 门读数中，不构成 VOID 条件；
5. **锚定门**：6 员 anchor 复现须全 OK（引擎漂移=批 VOID）。

## §6 产物

- `scripts/grid_p1_screen.py`（slice-2 交付，NSP1 同构：patch selftest→cells→nulls→passive→anchors→gates→sleeve/D6→JSON+CSV）；
- `results/grid_p1.json`（顶层 evidence_cutoff＋gate 全输入＋audit 段）＋`research/grid_p1_results.csv`；
- 本文件 §7/§8 回填＋`results/gate_attrition.json` 追加一行。

## §7 跑后实证【跑前必须为空——写数字即造假】

- 批运行：2026-09-25 03:10–03:21 C8 autofill 双弹（03:10:03 首弹 latency 3.5min→finalize 接线 bug 计算后崩溃（零科学损失）→修复 commit 55f9b8c9（J18 实现修零判据改）→03:20:03 复弹 checkpoint 恢复（104/104 行零重算）→finalize 落盘）；audit n_backtests=110（4 cells+100 nulls+6 anchors，2 passive=公式腿不计）。
- 硬门全过：patch selftest PASS／48/48 面板 2020-01-02..2026-09-24（lockbox 生效 raw end=cutoff）／anchor 复现 **6/6 OK**。
- cells（判据面=x1 V1）：default **full Sharpe −0.4091**（ann −5.1%、dd −44.9%、OOS S −0.1403）；ce **full Sharpe +0.0683**（ann −0.07%、dd −41.7%、OOS S −0.0540）；x2 面 default −0.1958／ce −0.7303。
- 技能线：**1.1068**（ledger 60,547+112=**60,659** 数据驱动；被动项 0.4606 不主导）；两 cell line_ok=False、bootstrap CI 下界非正（ci_ok=False）、entries_ok=True（641/470≥30）→ **pass_v2 双 False**。
- D6：注册面 max|corr| default **0.3301**／ce **0.2419**（argmax 均 VOLATILITY-CE-01）——**均 <0.70 无拒收**；同批 pair **0.6608 < 0.70 → unique 无合并**（同族未撞线，§5-1 预测未中）。
- nulls：K=100 mu=0.0074 sigma=0.2191，批内 p95 default 0.384／ce 0.3191（披露面；技能线=共享采集器）；passive：ew48_buyhold 0.2825／ew48_monthly_rebal 0.3606（J8 一致性 info）。
- **生存者=0（诚实负）**；产物：results/grid_p1.json＋research/grid_p1_results.csv＋gate_attrition GRID-P1 行＋ledger 60,659。

## §8 批后复盘【必填·s7-T】

- **预测记分**：§5-1 撞车带 0.4–0.8 → 实测 0.24–0.33 **未中**（二元会员+10d 冻结持有的收益流形与低波持有族差异大于预测）；§5-2 量级 0.2–1.0 → 实测 −0.41/+0.07 **未中**（方向「诚实负」命中、量级低于预测带下沿）；§5-3 门槛 1.10–1.46 → 1.1068 **命中**；§5-5 锚定 6/6 **命中**（2/4）。
- **结论**：网格收割 A 层迁移在 core48+T+1+13bp 面未获数据支持——两 exit regime 全期 Sharpe 均远低于技能线且 CI 下界非正；Money0923 sane 先验（+27.7%/S 0.96）不可迁移获实证确认。主因候选=§3 已披露发散面（二元会员制／池内冻结持有／0.95÷5 sizing）+短史+成本面；归因分解=本批范围外。**收线：按预注册禁翻案，复活须新预注册+新机制论证。**
- **工程复盘**：finalize 首跑接线 bug（x2 压测 sharpe 未接进 verdict cells）→计算后崩溃零科学损失、checkpoint 行级恢复确定性闭环实证（T-33 律生效面）；C8 池批自愈双弹链路（launch→crash→relaunch→finalize）全程零人工干预。教训：verdict 组装前对新增字段做存在性核（r89 引用件审计律的批内变体）。
