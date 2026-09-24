# T24_G2_PACK 预注册 — PROSPECT 22 员 G2 证据包批（neighborhood + cost x3 + per-year）

> 从 research/PREREG_TEMPLATE.md 起草（T-02 6/7 律）。本批=已入册 PROSPECT 成员的
> **稳健性证据层**（G2_NSP1/G2_FOLK 范式），非新信号发现批：22 员已在 T-24 slice-2
> 过 anchor-repro 门入册，机制主张归各自 p4 源批预注册（指针见 §1）。
> 消费方=scripts/t24_prospect_promotion.py g2_full 腿（hr.PROSPECT_PROMOTION_GATE
> 三子腿 neighborhood_pass/cost_x3_pass/per_year_pass，本批为其唯一证据生产者）。

## §0 批件身份【跑前】

- 批名/批号：`t24-g2-pack`；批内格数（入 N_eff 账本）：**98** = 76 neighborhood 新格
  + 22 cost-x3 新格；center-1x 22 跑=recorded-cell 复现（onboarding 先例 ledger+0）；
  engine_runs 合计 120（98 新 + 22 复现）。
- 认领：T-20260924-24 slice 续作（bm-a 已 claim，R83 起；本片=R87 指针第一顺位，
  无新开票=无新认领 MSG；F-04 只约束新票认领）。
- 部门归属：dept:交易+工程（T-24 票面 owner）。
- 算力预算：~25-40 分钟，分离后台 BelowNormal 进程池（O-1612 满载载体=水位红牌真处置），
  JSONL checkpoint 逐格断点续跑（R41 教训）；批报告带 audit 段。

## §1 伪 α 机制段【必填·指针+稳健性逻辑】

本批不引入新信号、不产新 G1' 主张——四选一机制论证**指针**到 p4 源批预注册
（p4_batch1 状态面 / p4_batch2a ta 族 / p4_folk s10-s11 / p4_queue s9），各员机制
主张已在其入册链冻结。本批自身的机制逻辑=**参数脆弱性证伪**：真实结构性优势不应对
邻近参数塌缩（neighborhood OAT），真实优势应扛住 3× 成本（cost x3），真实优势不应
有崩溃年（per-year）。**D6 同族相关性门槛**：无新族入场（22 员已入册、同族折扣已
在 p4 预注册登记，如 VOB vs P1 breakout_confirm），故无 corr 计算——本批不产生
新入场决策，产出仅喂晋升门三子腿。

## §2 数据与面板【跑前探针事实】

- 宇宙：core48（48 员，入册面板口径，与 onboarding anchor 批同窗）。
- **evidence_cutoff = 2026-09-22**（池与成员件冻结口径；面板截断到该日，
  cutoff 后新 bar 锁定不得回流本批）；结果 JSON 顶层必带
  `science_gates.cutoff_meta(cutoff)`（缺=science_audit C2 VIOLATION）。
- 数据完备门（不过门禁跑批）：48/48 符、close 索引严格单调、截断后窗口尾
  =2026-09-22、**逐符号 first_valid_index 之后零 NaN**（晚上市员前沿 NaN=合法面板
  结构，p4/anchor 同约定——首跑实证 11 员有前沿 NaN 共 2275 格，批诚实中止零产数，
  跑前窗内修正本门条款，判据零触碰）。
- **inside_bar_breakup 族诚实披露**：冻结构造（`inside_bar_breakup()`）无任何可扰动
  参数（单格族，p4_folk 亦无兄弟变体）→ 该族 2 员（PROS-IBB-01/CE-01）邻域网格为空，
  neighborhood_pass=REFUSED（missing-input 拒收先例，g2_registration_v2 缺输入诚实
  拒收同款），**非缺陷非降门**——待未来研究波为该族引入参数化变体后补验。

## §3 方法学【必填】

- 因子/信号定义=live/paper.py SIGNAL_BUILDERS 冻结参键（T-24 slice-2 冻结件，
  禁改）；滞后规则=引擎既有 T→T+1 契约，无未来数据。
- **邻域=OAT 单参数扰动**，逐族冻结步长表（跑前 normative，缺省=函数默认中心）：

| 族 | 中心（冻结默认） | OAT 步（lo/hi） | 点/员 |
|---|---|---|---|
| oversold_bounce | 20/−15%/0.8 | lb∈{15,25}, drop∈{−10%,−20%}, shrink∈{0.70,0.90} | 6 |
| rsrs_timing | 18/250/0.8/−0.8 | win∈{12,24}, z∈{120,480}, buy∈{0.70,0.90}, exit∈{−0.90,−0.70} | 8 |
| vol_breakout | 20/1.5/20/10 | brk∈{15,25}, mult∈{1.3,1.7}, avg∈{15,25}, exit∈{7,14} | 8 |
| hammer_reversal | 0.35/2.0/−0.05 | body∈{0.25,0.45}, shadow∈{1.5,2.5}, drop∈{−0.04,−0.06} | 6 |
| three_methods_up | big_yang=0.03 | ∈{0.02,0.04} | 2 |
| doji_at_low | drop_th=−0.05 | ∈{−0.04,−0.06} | 2 |
| inside_bar_breakup | 无参 | —（grid empty→REFUSED） | 0 |
| ma_converge_break | spread=0.015 | ∈{0.010,0.020} | 2 |
| duck_head | neck=8 | ∈{5,12} | 2 |
| immortal_guide | shadow_pct=0.015 | ∈{0.010,0.020} | 2 |
| ants_climb | max_day=0.012 | ∈{0.008,0.016} | 2 |
| bb_squeeze_breakout | 20/2.0/60 | bb_n∈{15,25}, k∈{1.7,2.3}, width_n∈{40,80} | 6 |

  76 邻域格=上表×员数（双 regime 员=default+ce 各自独立判）。脚本内参数化构造器
  在中心参数处必须与 SIGNAL_BUILDERS 键输出**逐位相等**（selftest S1 硬门，
  防「参数化重写≠冻结构造」漂移）。
- null 对照：**随机基线判据经 recorded i-line 机器联动进入**（red 定义=§4），
  `recorded_lines()` 现算 i_line/vi_bar/ce_null_p4_batch1，禁手抄数字；本批不产新
  G1' 主张故无新 null 抽签（BACKTEST_PLAN 铁律之「随机基线」以源批已校准 null 线
  +i-line 判据承接，批报告披露）。
- 成本口径：V1 双轨防漂移（历史锚复现恒 V1）；x3=CostPatch(3.0) 单边 3 倍费率表
  （COST_X2_RATE 同源谱系）。
- 账本：`science_gates.append_ledger("t24-g2-pack", 98, file_name=…,
  evidence_cutoff="2026-09-22")`（dict schema，prev=运行时 ledger_head 数据驱动链头）。

## §4 判据【必填·跑前写死·禁看结果调线】

全部判线运行时经 `recorded_lines()` 现算（写入时已知历史值仅作披露参考：
i_line=0.3521 / vi_bar=0.4004 / ce_null_p4_batch1=0.4474）：

1. **anchor re-verify（批内复验，员级前置）**：center-1x full sharpe vs 成员件
   recorded_full_sharpe，|Δ|<0.002 且 n_trades 逐位同（onboarding 同门同容差）。
   FAIL → 该员 pack=anchor_broken，三子腿全 false，批不废（员级隔离，全披露）。
2. **neighborhood_pass**：红点=邻域格 full sharpe ≤ I_LINE[本员 exit_regime]
   （default→RL["i_line"]，ce→RL["ce_null_p4_batch1"]）；pass=red×2 ≤ points
   （G2_FOLK 条款 2 逐字：红点不过半）。grid empty（IBB）→ REFUSED=false。
3. **cost_x3_pass** =（新证 x3 center full sharpe > 0）**且**（x3 center OOS
   sharpe > 0）**且**（成员件 recorded_x2_full_sharpe > vi_bar）。第三 conjunct=
   注册标准 G2 条款 3（x2>vi）以录制证据判、不新跑——**无放松**：晋升仍须 2× 成本
   下跑赢被动（在册 6 当年注册标准），另加 3× 成本下存活（本批新证）。
4. **per_year_pass**：center-1x 权益逐日历年收益最差年 > −0.35
   （WORST_YEAR_FLOOR，G2_FOLK 条款 4 逐字）。
5. 三子腿 AND 进 g2_full（hr.py 门已冻结读取三键 bool；本批只产证据不改门）。
6. 禁跑到达标为止：每员每格恰跑一次，verdict 落盘即终局；重跑仅限工程修复双跑留痕。

## §5 跑前预测【必填·≥3】

1. anchor re-verify 22/22 PASS（onboarding 已双验同管线，tol 同 0.002）。
2. IBB 双员 neighborhood_pass=REFUSED（§2 设计必然，非实证发现）。
3. cost_x3_pass 第三 conjunct（recorded_x2>vi）：**预计通过员数 0-4**
   （已见录制值 OVB 0.14/0.15、RSRS −0.17、VOB 0.20、HAM 0.03 全不过 vi_bar；
   duck/TMU/IMM/MCB/ANTS/BBS/DOJI 未见值不点名）。0 员过=与「零合格=闸设计态」
   （O-1727）一致，是诚实态非事故。
4. per_year_pass 预计 18-22 员 PASS（录制 max_dd 全部浅于 −24%）。
5. neighborhood：录制 full 已低于本员 regime i-line 的 sleeve 员（OVB/RSRS/HAM/
   DOJI 等）大概率红点过半→FAIL；录制强员（duck 0.68 等）邻域更可能过半绿。
   通过/失败均按 §4 判，不因预测调线。

## §6 产物【跑前】

- scripts/t24_g2_pack.py（run/status/selftest；selftest 全离线合成面板）；
- results/prospect_g2/<成员ID>.json ×22（顶层=三子腿 bool 键 + evidence_cutoff +
  cutoff_meta 键 + 邻域逐格明细 + x3 指标 + 逐年表 + anchor 复验 + 判线值与来源）；
- results/t24_g2_pack.json（**批级+trials_ledger 链载体**（ledger_head 只扫 results/ 顶层，
  链断风险防御）：engine_runs=120/ledger+98/完备旗/审计段；prev=双目录 max 链头 r60 惯例）；
- results/prospect_g2/t24_g2_pack_cells.jsonl（checkpoint 逐格幂等）；
- research/shortline/t24_g2_pack_results.csv（邻域+成本行，批级披露表）。

## §7 跑后实证【跑前必须为空——占位纪律】

（一次定稿；工程修复重跑须双跑留痕如实记；确定性引执级写 bug 的合法重跑口径≠结果重跑）

## §8 批后复盘【必填·§7-T】

- 预测对账（§5 逐条对/部分对/错+量级）；
- gate_attrition measurement 行（若产耗损面；本批=证据生产非筛选漏斗，无 attrition
  则记 no-attrition 一行）；
- 轮报告+CODELY.md 行级追加；若三子腿有翻转影响晋升门读数：下一新 bar 轮
  t24_prospect_promotion.py 自动拾取（S6 已接线，无需人工）。
