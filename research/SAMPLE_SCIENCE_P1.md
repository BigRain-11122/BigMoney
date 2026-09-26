# SAMPLE-SCIENCE-P1 预注册 · T-81 slice-3 状态内样本下限+四必报分层 · O-20260926-1342 §二/§四③

> 跑前冻结件。跑后只许回填 §7；禁改判据（改=新版本号+CEO 判据线程序）。
> 语义=**读数派生面**（零新回测零新搜索零新成员）：对 T-81 slice-1 已发放 17 画像卡（results/strategy_scorecard.json profile_cards，prereg=PROFILE_CARDS_P1 v1.0.1）加挂「状态内样本科学」面——四必报按状态分层重报+分样缩水披露+CI 加宽照报（O-1342 §二原令；BACKTEST_SCIENCE §10 四必报定义=OOS 交易笔数/覆盖年数/独立政体窗数/CI 宽度）。
> 判据纪律：**本切片零判定线变更**——PASS/DEAD_ZONE/NO_EVIDENCE 三态线=PROFILE_CARDS_P1 §3.1 冻结线逐字（n≥20 且 episodes≥2；双线=cum_x1>0 且 excess≥0）。CI 面=披露面非翻案面（ci_lower_bound_positive=诚实旗，非自动击杀——镜像 slice-1 §4 cost_fragile「披露非击杀」先例）；改判定线=另立新版本+CEO 判据线程序。
> 账本政策：`append_ledger('SAMPLE-SCIENCE-P1', 0, ...)` **+0**（读数面非试验，slice-1 范式）。

## §0 载体与范围

- 载体=`scripts/strategy_scorecard.py` profile_card/build_profile_cards 扩展（同一纯函数面，零新框架）；产物=results/strategy_scorecard.json profile_cards 面内逐状态/逐格新增字段+卡级 `sample_science` 块。
- 层级口径：主面=v3 四态（GREEN/YELLOW/ORANGE/RED）；细面=热档格（州×{HOT,COOL}，slice-1 heat_cells 面）——两面同法同律，L3 激活表（slice-2）消费的正是格面，四必报必须铺到格面才可被 11-01 路由切换呈报面引用。
- 输入零新增：17 台账既有 x1/x2 日序+逐笔单+州序列（slice-1 已验证恒等门 17/17 PASS）。

## §1 四必报字段定义（冻结·全既有先例逐字复用）

每个状态格（州面+格面）新增：

1. **oos_trades**：A 组=该州内逐笔单计数（slice-1 trades_by_state 既有面逐字）；B/C 组=null+诚实标签（blend/alloc 无逐日单面——slice-1 n_trades 同口径，禁编数）。
2. **covered_years**：该州日集日历跨度=(last_day−first_day).days/365.25，round 2dp（p5c_virtual_timepoint.py L675 / t22_virtual_timepoints.py L465 公式先例逐字）；n_days=0 → None。
3. **independent_regime_windows**：=slice-1 episodes 计数逐字（连续段计数；州面=州级段数，格面=格级段数）——O-1342 §二「独立政体窗数」即此计数，slice-3 只重报不改定义。
4. **ci95_lo / ci95_hi / ci95_width**：`science_gates.bootstrap_ci_sharpe` 逐字复用（Politis-Romano 平稳自助法、1000 重采样、均值块长 10 日、LCG 种子 **20260923**=预注册家族种子（G1' 面同族逐字，非新种子）、95% 分位），输入=该状态格内 x1 日收益序列；width=hi−lo（Sharpe 年化标尺，G1' 同标尺禁另造）。**门槛律**：n_days<20 → 三值 None+诚实注记（bootstrap 机制下限=science_gates 冻结 ValueError 面；与证据充分门 n≥20 对齐但独立执行——n≥20 而 episodes<2 的 NO_EVIDENCE 格仍照报 CI（披露面照报非判据面））。
5. **ci_lower_bound_positive**：ci95_lo>0 诚实旗（true/false）；None 当 CI=None。**披露非击杀**（§0 判据纪律）。

## §2 分样缩水披露（CI 加宽照报·O-1342 §二原令）

卡级新增 `sample_science` 块：

- `window_four_must`：全窗四必报（oos_trades=A 组全窗逐笔计数/其余 null；covered_years=全窗日历跨度；independent_regime_windows=全窗州序总段数；ci95_width=全窗 x1 日收益 bootstrap 宽度）。
- `per_state`：{州: {n_days, ci95_width, ci_lower_bound_positive}}——分样后各州读数一眼对照。
- `shrinkage_note`（冻结文案）：「分样后样本量缩水如实披露：州 n_days<全窗 n_days，州 CI 宽度>全窗 CI 宽度（CI 加宽照报，O-1342 §二）；NO_EVIDENCE 州=n 样本不足照报不豁免」。
- `widest_state_ci`：最宽州 CI（值+州名）——O-1342 §一.3「最宽 CI 披露」在全州主张面的落法（本窗 ORANGE/RED 零日=全州主张构造性不可能，如实携带）。
- `min_windows_gate`：{"min_n_days": 20, "min_independent_regime_windows": 2, "source": "PROFILE_CARDS_P1 §3.1 frozen verbatim — carried, not changed"}。

## §3 击杀条件与衰减探针（申报在册·slice-1 §4 逐字携带+读数基线挂接）

- 击杀条件预注册=**slice-1 §4 已冻结面逐字**（A 组 hr 开除面+成本剃刀线+x2 脆旗；B/C 月亏线+空激活集 fail-closed+状态失配降级 slice-2 接线钩子）——零新击杀线。
- 衰减探针挂接=slice-1 probe_carriers 逐字（hr run_review 自动开除/live.paper x2_watch 月度/每新 bar 三卡再 derive）+ **本切片新增读数基线**：逐状态四必报=每新 bar 再 derive 时的衰减对照基线（同州 CI 下界跨 0 向下/独立窗计数缩水=oos-decay 证据旗，披露非自动击杀，镜像 cost_fragile 先例）。
- 11-01 路由切换呈报面指针：完整路由切换目标=11-01 月界（firm/STYLE_CORPS §6 过渡纪律：前置=军种门禁齐过+路由 spec 冻结+月报呈 CEO）；本切片四必报面=届时呈报的逐状态披露载体，本切片不实现切换本体（月界任务另立）。

## §4 跑前预测（写死于跑前）

1. 全 17 卡 ORANGE/RED 州 n_days=0 → covered_years=None、CI 三值 None、oos_trades 该州=0（A 组）/null（B/C）——构造性诚实面。
2. GREEN（n=54）/YELLOW（n=124）均 ≥20 → 17 卡两州 CI 全可算；热档四格（n=21/32/90/34）全可算。
3. CI 下界正负分化预期：厚余量州（AGGR-REGIME GREEN +4.94%、AGGR-OFFENSE GREEN +4.16%）预期 ci_lower_bound_positive=True；薄余量州（B_MAXDIV YELLOW +0.25%、ENGULF 双州薄余量、ALLOC 多负州）预期 False 旗亮=诚实披露非缺陷。
4. 分样缩水方向律：州 CI 宽度>全窗 CI 宽度（样本缩水的数学后果）——若任一州 CI 反窄于全窗（同 Sharpe 标尺），=机制疑点须当轮实证（方差结构面自检）。
5. A 组 oos_trades 恒等门：逐州 oos_trades 求和=台账全窗逐笔计数（12 级小整数，机制校验非判线）。

## §5 产物

- `scripts/strategy_scorecard.py`：`_four_must_cell()` 纯函数+profile_card 州/格面挂接+卡级 sample_science 块+selftest 新腿（合成夹具：covered_years 公式/CI n<20 拒算/oos_trades 恒等门/缩水方向律）。
- `results/strategy_scorecard.json` profile_cards 面：逐卡逐州逐格新字段+sample_science 块+meta 新键 sample_science_prereg(+sha16)。
- 轮报告回执+T-81 progress 行+CODELY.md（如有坑律）。

## §6 判据引用纪律

- G1'/G2 判线不因本切片触碰（batch 面零改动）；本面全部读数=单源派生禁手抄（O-2250 单源律）。
- 幂等律：同输入重跑产物字节恒等（bootstrap 种子确定性）。

## §7 跑后实证（跑后回填·一次定稿）

- 发放：17 卡 ×（4 州面+热档格面）四必报全落 + 卡级 sample_science 块；selftest 10/10（P8 单格口径/CI 拒算/种子确定性 + P9 合成接线 + P10 在位 17 卡含 §4.5 逐笔恒等门）；生产刷 12.8s；幂等律=面内容跨跑恒等（唯一漂移=audit/envelope 两键 elapsed_sec/generated=既有运行时元数据，非面内容）。
- 预测对账（§4 五条）：
  1. ORANGE/RED 构造性 None/None/0-or-null=**对**（selftest 断言）。
  2. GREEN/YELLOW 34 州格 CI 全可算 17/17、热档四格全可算=**对**。
  3. CI 下界分化=**对且更锐**：34 州格仅 2 格 ci_lower_bound_positive=True（AGGR-OFFENSE GREEN lo=+0.7002、AGGR-REGIME GREEN lo=+0.7753）；薄余量预期 False 全中——**正典 B_MAXDIV GREEN（cum +0.68%）lo=−0.3216 亦 fragile**（54 日样本下连正典州面都不具 CI 稳健性=如实披露非缺陷）；DROUGHT-CE-01 GREEN lo=−0.0333 近稳健。
  4. 分样缩水方向律=**对**：0/34 州格 CI 窄于全窗（AGGR-REGIME 全窗宽 4.6747 vs GREEN 7.9448/YELLOW 5.5787）。
  5. A 组逐笔恒等门=**对**（P10 在位断言 6/6 过）。
- **CEO 哲学锚的 CI 级量化**（附加读数）：AGGR-REGIME 全窗混合面 CI lo=−1.1963（不稳健）vs GREEN 纯态面 lo=+0.7753（稳健）——「状态条件化>永远在线」从逐州 cum 读数升格为 CI 级证据：永远在线混合面的 alpha 被 YELLOW 段稀释到统计不可分辨，GREEN 条件面才具 CI 稳健性。
- 判据零翻案实证：state_verdict_counts 与 slice-1 §7 逐字恒等（GREEN 13 PASS/4 DEAD、YELLOW 7 PASS/10 DEAD、ORANGE/RED 17 NO_EVIDENCE）——CI=纯披露面（§0 判据纪律生效）。
- 衰减基线：decay_baseline_note 随卡落盘；每新 bar 三卡再 derive 时同州 CI 下界跨 0 向下/独立窗缩水=OOS-decay 证据旗（披露非自动击杀，cost_fragile 先例）。
- 11-01 呈报面：四必报面就位=届时路由切换呈报的逐状态披露载体；切换本体=月界任务另立（STYLE_CORPS §6 前置未齐：军种门禁+路由 spec 冻结+月报呈 CEO）。

## 变更记录

- v1.0 (2026-09-26 R257 bm-b)：跑前冻结（O-1342 §四 item3 状态内样本下限+四必报分层；判线零改动=slice-1 逐字携带；CI=披露面非翻案面）。
