# PROFILE-CARDS-P1 预注册 · T-81 slice-1 适用域画像卡 · O-20260926-1342 CEO 直令

> 跑前冻结件。跑后只许回填 §7；禁改判据（改=新版本号+CEO 判据线程序）。
> 语义=**读数派生面**（零新回测零新搜索零新成员）：对 T-79 既有 17 台账（A6 六员+B4 AGGR前三含 B_MAXDIV 正典+C7 ALLOC）做逐状态战绩分解+死区+激活+击杀申报；挂载体=三卡系统（T-63）`scripts/strategy_scorecard.py` 扩展面 `profile_cards`（O-1342 §三：交易员卡 §6 政体画像面扩展到组合卡+因子卡，零新框架）。
> 账本政策：`append_ledger('PROFILE-CARDS-P1', 0, ...)` **+0**（读数/台账面非试验，T-56 slice-2 marks 范式）。

## §0 批件身份与候选枚举（全家族如实，禁挑面）

- 在册画像对象 17：COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01（A 组六员）+ AGGR-CONC-TOP2、AGGR-OFFENSE、AGGR-REGIME、B_MAXDIV（B 组四台账）+ ALLOC-P1/P2/P3/P3B/P4/P5/P6（C 组七 cell）。
- 缺席申报（沿用 T-79 LEADERBOARD absent_families 冻结面 + 今晨实况）：AGGR-MOM/AGGR-NOCASH=无回放台账（marks 09-24 起=无状态面）→ 构造性 NO_EVIDENCE；GRID 族=grid_sleeve_p1 0/5 生存者判负（观察 marks 车道，无激活面）；CN 族（T-73）=首个批 CN-REV-TILT-P1 4/4 G1v2 判负已收割、后续模型在飞 → 落地即画像（O-1342 §四 item4 落地钩子）。

## §1 状态分类法与数据源（零重建，全既有面）

- **主面=v3 四态**（GREEN/YELLOW/ORANGE/RED）：台账逐日 `shadow_regime_states`（回放录得、shift(1) 收盘因果、市场级序列）；跨台账恒等门=全载体的序列 sha 恒等（实勘 10 载体同 sha `03c5872d3f62`）+17 台账日期集恒等；C 组台账不自带序列（结构性）→ 复用市场级序列（账户无关由构造）。
- **热档复合 v0**：`import scripts/market_clock_backtest.build_heat` 逐字复用（s1 冻结法：H_act=当日 LHB 行数、H_net=当日净买额、p80=尾 250 LHB 日 min60、HOT⇔H_act≥p80 且 H_net>0；LHB=Money02/data/lhb/lhb_detail.parquet 全量）。**热档归属=前收市档（shift(1)，镜像州惯例）**：收益日 d 归 d−1 收市热档；窗首日无前收市=热档 n/a（计入州面、不计入格面）。
- **长史面 t22 代理段**（仅 A 组六员）：`results/corps_roster.json` registered 段证据（bull/bear/chop、beat_rate_12m/n_startpoints/worst_dd）；分类法≠v3（510300×MA200 代理）→ 段面如实带「代理分类法」标签，不与 v3 面混读。
- 因子卡面：六员继承其 corps/segments 证据（本切片无独立因子批——P1_IC 批面另有车道）。

## §2 收益日序列口径（冻结）

- r₀ = eq[0]/initial − 1（A 组 hire 日 eq[0]=1e6 → r₀=0 零收益日、计入州 n_days 如实）；rᵢ = eq[i]/eq[i−1] − 1（i≥1）。全窗逐日积=台账 cum_ret（恒等校验）。
- x1 面=V1 legacy 成本面；x2 面=台账 x2（C 组 x2=None →「v2 成本已内建于 x1（retro §3 口径）」如实标签）。
- 州归属：收益日 d → 台账录得州 s(d)（已 shift(1)）；A 组交易单逐笔按单日州归类计数（B/C 组 blend/alloc 无逐日交易单 → n/a 如实）。

## §3 判据线（跑前冻结·FROZEN）

1. **v3 窗面逐州判定**（4 态×17 候选）：
   - 证据充分门：n_days(州) ≥ **20** 且 episodes(州) ≥ **2**（独立政体窗下限——单一连续段=零复制，O-1342 §二「每状态最少独立政体窗数」在单窗面的落法；多窗 CI 分层=本票 slice-3 四必报面，届时升格）。
   - **PASS** = cum_x1(州) > 0 **且** excess(vs B_MAXDIV 同州 cum) ≥ 0（双重线：绝对赚钱+跑赢正典替代项）。
   - **DEAD_ZONE** = 证据充分 且 非PASS（州内亏钱或跑输正典）。
   - **NO_EVIDENCE** = 证据不足（fail-closed → 不激活，宁缺毋滥；O-1342 §一.4）。
2. **热档格面**（州×{HOT,COOL}）：同线逐格（n≥20 且格 episodes≥2 才判；窗首日热 n/a 不入格）。预期多数格=NO_EVIDENCE=如实。
3. **长史 t22 段面**（A 组）：corps 冻结线逐字（beat_rate_12m ≥ 0.5、min_n=30、blowup −0.35，源=corps_roster rule 面）——PASS/DEAD_ZONE(n≥30 且 beat<0.5)/NO_EVIDENCE(n<30)；零新线。
4. **自洽门（机制校验非判线·v1.0.1 判据感知式）**：T-79 冻结分段面对 day-1 收益存在家族异质惯例（实测：A 组 engine 面 hire 日零收益、B 组 marks 面含 day-1 应计、C 组 alloc 面通用剔首日）→ 门=逐台账双惯例择一恒等：本面 GREEN/YELLOW 州积在「含 day-1」或「剔 day-1」恰一惯例下与台账 bull/chop cum 恒等（**容差 2e-6=跨算术路径噪声上界**，逐日积 vs 台账内部累算实测差 ~5e-7；真实错切差≥1e-4 量级仍全被捕获；基准=6dp 同基准比），双州同惯例，命中惯例逐台账披露；双惯例皆失配=机制故障诚实拒发。混合州窗（含 ORANGE/RED 日）该门 ORANGE/RED 映射未验证 → 跳门+注记。
5. **哲学律（O-1342 §一）**：画像卡**无总分**（readout-only；总分=派生索引视图仅索引不作依据）；激活集=PASS 州集合（空集=处处不激活=fail-closed）；本窗 ORANGE/RED 零日 → 「全时在线」主张本窗构造性不可能成立，任何未来全州 PASS 主张=默认存疑+最宽 CI 披露（slice-3 接线）。

## §4 击杀条件申报（预注册读数·衰减探针挂接·O-1342 §二）

- **A 组六员**：①hr 开除面逐字（paper_dd>20% / live_monthly_loss<−8% / IC衰减>50% / risk_violation，源=firm/hr.py FIRE_REASONS，自动开除已接线 hr.run_review）；②成本剃刀线（OPERATING_PLAN §2 冻结数）：COMPOSITE-CE-02 x2 余量 +0.031、ENGULF-CE-01 +0.002——余量≤0=击杀（载体=live.paper x2_watch/cost_x2_check 月度自动）；③非剃刀员 x2 窗积≤0<x1=cost-fragile 披露旗（非自动击杀）。
- **B/C 组（blend/alloc 台账）**：①单纸盘月 <−8%（hr live_monthly_loss 线镜像到账户级；载体=marks 月度再derive——aggressive_lab.py paper/alloc_paper.py 车道）；②激活集=空 → 构造性不运行（fail-closed）；③状态失配自动降级=本票 slice-2 L3 激活表接线钩子（申报在册，落地在 slice-2）。
- **全体**：画像每新 bar 随三卡刷新再 derive（本件=载体）；击杀读数全部挂既有探针，零新监视器。

## §5 跑前预测（写死于跑前）

1. 窗内州谱=GREEN 54 日+YELLOW 124 日、ORANGE/RED 零日（T-79 §7 已公开）→ 全部 17 卡 ORANGE/RED=NO_EVIDENCE(n=0)；自洽门生效（§3.4）。
2. GREEN/YELLOW 多为长连续段 → episodes 门（≥2）下预计相当比例州面=NO_EVIDENCE；**B/C 组预期 fail-closed 主导**（C 组 5/7 窗积为负=公开面；其州面若证据充分更可能 DEAD_ZONE/NO_EVIDENCE 而非 PASS）——宁缺毋滥为正确产出非缺陷。
3. A 组 t22 段面：在册编队段（chop/attack 编制段）预期 beat_rate_12m≥0.5（corps_roster 已公开读数），非编队段如实呈报不预设。
4. 热档格面：LHB 热档在 2026 窗分布未知 → 格 n 预期大量 <20=NO_EVIDENCE（如实）。
5. 激活集非空的候选预期集中在 A 组（双面证据）+B 组前三（若州面证据充分）；空激活集候选=如实呈现（CEO 认可门外的观察面）。

## §6 产物

- `scripts/strategy_scorecard.py` 扩展：`profile_card`/`build_profile_cards` 纯函数+selftest 腿（合成夹具+在位实腿）+`run()` 挂 `profile_cards` 面。
- `results/strategy_scorecard.json` 新顶层面 `profile_cards`（batch/ticket/order/prereg+sha16/evidence_cutoff/lines/cards/absent_families/summary/自洽门读数）。
- 轮报告回执+心跳 orders_ack（O-1342 既有回执不重复）+T-81 progress 行+CODELY.md 记录。

## §7 跑后实证（跑后回填·一次定稿）

- 发放：17 卡全落面（state=ok，2.3s 全三卡刷新含画像面）；自洽门 **PASS 17/17**，命中惯例披露：with_day1 ×10（A6+B4 全含 day-1，A 组 hire 日零收益两惯例数值恒等）/ without_day1 ×7（C 组，台账分段面剔首日）——家族异质惯例实勘与 §3.4 v1.0.1 修正案吻合。
- 州谱与判定计数：GREEN 54 日/10 独立段、YELLOW 124 日/10 段（证据充分门全过）→ GREEN=13 PASS/4 DEAD_ZONE、YELLOW=7 PASS/10 DEAD_ZONE；ORANGE/RED 零日 → 17×NO_EVIDENCE（构造性）。
- 逐州战绩要点（x1 净成本面）：
  - **AGGR-REGIME GREEN +4.94%/YELLOW −1.43%**、AGGR-OFFENSE +4.16%/−1.27%——CEO 实证锚「状态条件化>永远在线」在逐州面上复现（GREEN 激活/YELLOW 死区）。
  - **B_MAXDIV 正典双州 PASS**（GREEN +0.68%/YELLOW +0.25%）但 **YELLOW 面成本脆旗**：x2 −0.15% ≤0<x1（薄余量双倍成本即死——§4 非剃刀员披露旗如实点亮）。
  - ALLOC-P3/P3B 双州 DEAD（GREEN 微正但跑输正典 −0.03pp/−0.07pp、YELLOW −4.4%/−4.5%）→ **空激活集 fail-closed 不激活**；ENGULF-CE-01 双州 DEAD 同入空激活集（剃刀员 +0.002 最薄余量+窗内负收益，与榜面一致）。
  - **VOLATILITY-CE-01=震荡专家双面印证**：v3 面 GREEN −0.29% DEAD/YELLOW +3.19% PASS + 热档格 YELLOW×COOL +2.57% PASS/GREEN×HOT −0.70% DEAD；t22 长史面 bull/bear/chop 三段全 PASS（beat_rate 0.57/0.59/0.62）——州面与长史面同向。
  - A 组六员 t22 长史面三段全 PASS（在册编队证据一致性成立）；NEEDLE-DE-01 GREEN PASS/YELLOW DEAD。
  - 热档格全 4 格有证（GREEN×HOT n=21/GREEN×COOL 32/YELLOW×COOL 90/YELLOW×HOT 34，全≥20 过线）→ 逐格判定产出真读数非全 NO_EVIDENCE。
- 预测对账：①州谱=**对**；②「B/C fail-closed 主导」=**错**（州序列交替充分、独立段 10——证据比预期富，如实记；「C 组 YELLOW 更可能 DEAD」半对=7/7 C 组 YELLOW 全 DEAD）；③A 组 t22 段面 PASS=**对**（6/6 三段全过）；④「热档格大量 <20」=**错**（四格全过线）；⑤激活集非空集中 A/B+部分 C=**对**（14/17 非空）。
- 万金油面：17/17 无全州 PASS 主张（ORANGE/RED 构造性不可能）；空激活集 3 员如实呈现（宁缺毋滥产出）。
- slice-2 指针：激活表证据化（T-74 L3）——17 卡激活集/死区/热档格/击杀申报全部就位，L3 八格表改由本面证据驱动=下一切片开动面；slice-3 四必报分层（CI 宽度/独立窗计数）待接。

## 变更记录

- v1.0.1 (2026-09-26 R254 bm-b)：§3.4 自洽门改判据感知式（selftest 自检期红项修复，首发放前；判线 §3.1-3.3 零改动）——实勘 C 组台账分段面剔 day-1（A/B 含），双惯例择一恒等+惯例披露。
- v1.0 (2026-09-26 R254 bm-b)：跑前冻结（O-1342 §四 item1 画像卡面；判线全冻结于跑前）。
