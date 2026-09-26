# LANDING-HOOKS-P1 预注册 · T-81 slice-4 落地钩子（落地即画像）· O-20260926-1342 §四④

> 跑前冻结件。跑后只许回填 §7；禁改判据（改=新版本号+CEO 判据线程序）。
> 语义=**读数派生面**（零新回测零新搜索零新成员零判定线）：对三族「落地观察名单」做确定性落地判定+落地后画像管线动作契约（O-1342 §四④「CN 模型落地即画像」的机制化落法；T-81 票 spec slice-4 全名=CN models (T-73 s3) + grid sleeve (T-78) + wild-route survivors profiled on landing）。
> 判据纪律：**本切片零判定线**——各族落地判据=该族自家冻结批预注册判词面逐字消费（O-2250 单源律：读冻结产物，禁手抄判词）；落地≠激活（激活仍走 profile_cards 逐州证据门+L3 格证据门，本件只管「谁落了地→进画像管线」）。
> 账本政策：`append_ledger('LANDING-HOOKS-P1', 0, ...)` **+0**（读数/台账面非试验，T-56 slice-2 marks 范式）。

## §0 落地观察名单（三族·全量如实·禁挑面）

1. **CN 族（T-73 s3 五模型链）**：CN-REVERSAL-TILT（=CN-REV-TILT）、CN-GRID-SLEEVE、CN-DIV-LOWVOL-ROT、CN-REGIME-POLICY、CN-CORE-SATELLITE。判定面=各自冻结批产物 `results/cn_*/p1_results.json`（g1_prime_v2 逐 cell pass 位）+ CN-GRID-SLEEVE 判定面=results/grid_sleeve_p1.json（与 GRID 族同件，见下）。
2. **GRID 族（T-78 网格袖）**：判定面=results/grid_sleeve_p1.json（s5b 判词 verbatim：science survivor = G1'v2 AND GATE-A；paper candidacy 另需 D6<0.70 注册面）。**观察 marks 车道（GRID-* 纸盘观察账户）≠落地**——O-20260926-0958 unlock-4 明文「实验观察账户」+PROFILE_CARDS_P1 §0 明文「观察 marks 车道，无激活面」，落地=晋升候选资格非观察接线。
3. **WILD 族（T-57 野路子）**：判定面=results/wild_route/wild_route_s1.json（g1_prime_v2 逐 cell pass 位）；幸存者=未来 satellite 袖成员供给面（SLEEVE_REGISTRY satellite 结构标签的消费源）。

## §1 落地判据（冻结·全为既有冻结判词面的逐字消费）

- **CN 族单模型**：LANDED ⇔ 其 p1_results.json 内 `g1_prime_v2` 存在 ≥1 个 `pass=true` cell（该模型自家 prereg 冻结判线的判词位，本件零重判）。产物缺件/不可解析=该模型 `ABSENT`（fail-closed 诚实态，非不落地判定）。
- **GRID 族**：LANDED ⇔ `paper_candidates` 非空（=science survivor ∧ D6 注册面双过；s5b 判词 verbatim）。`survivors_science` 非空而 `paper_candidates` 空=`SURVIVORS_NO_CANDIDACY` 如实中间态。
- **WILD 族**：LANDED ⇔ `g1_prime_v2` ≥1 cell pass=true。
- 三族皆零落地 ⇒ 钩子面 state=ok + `n_landings=0`（armed 态：钩子在位、本轮无人落地=如实非缺陷）。

## §2 落地后动作契约（冻结·hook semantics）

1. **画像管线入口（自动）**：落地面进入 action_required 队列，动作=「profile on landing」——落地族的 marks/paper 台账一旦落 results/retro_paper_2026/*_ledger.json（T-79 台账范式），build_profile_cards 既有 *_ledger.json 扫描面自动纳卡（零新框架；无台账=`LANDED_AWAITING_LEDGER` 诚实中间态，禁无账画像）。
2. **L3 袖结构标签联动（申报面）**：无成员袖（grid/satellite/divlowvol）的结构性状态标签=本钩子面判词的单源引用——标签文案更新走 L3_ACTIVATION_EVIDENCE.md 变更记录（机制零改：全格不激活、不因格证据翻转=该件 §1 冻结律）；本切片同窗刷新 divlowvol 标签陈旧面（IN_FLIGHT「runner pending」→ JUDGED_NEGATIVE，R252 判词实况）=状态读数更新非判据变更。
3. **再 derive 节律**：钩子面挂 strategy_scorecard.py run()（三卡载体同件）；S6 链接线 `python scripts\strategy_scorecard.py`（market_clock_call 之前位）——每轮自动重 derive，落地判定随批产物落盘自动翻面，无需人工触发。
4. **落地≠激活**（哲学律·O-1342 §一.4 镜像）：落地族进画像管线后，激活集仍=逐州 PASS 证据门（PROFILE_CARDS_P1 §3 冻结线）×L3 格证据门×设计提名交集（L3_ACTIVATION_EVIDENCE §2 冻结线）；全时在线主张禁令沿袭。

## §3 跑前预测（写死于跑前）

1. CN 族五模型**全负零落地**：REV-TILT 0/4（R248 判负）、GRID-SLEEVE 0/5（R244 判负）、DIV-LOWVOL-ROT 0/4（R252 判负）、REGIME-POLICY 0/3（R256 判负）、CORE-SATELLITE 0/4（R261 判负）=五模型链 ALL-NEGATIVE 收口（R261 harvest note 明文），n_landings=0。
2. GRID 族零落地：survivors_science=[]+paper_candidates=[]（0/5 生存者判负）；观察账户 marks 在跑=观察车道如实披露非落地。
3. WILD 族零落地：g1_prime_v2 25 cell 0 pass（0/25 判负）。
4. 三族状态全 ok（产物在位可解析）→ 钩子面 armed+零动作队列。

## §4 产物

- `scripts/strategy_scorecard.py`：`landing_hooks()` 纯读数函数（results_dir 可参数化=hermetic 夹具入口）+`run()` 挂 `landing_hooks` 顶层键+selftest P11 新腿（合成夹具：三族落地正例/负例/缺件 fail-closed/GRID 中间态）。
- `results/strategy_scorecard.json` 顶层 `landing_hooks` 面（batch/ticket/order/prereg+sha16/evidence_cutoff/families/landed/action_required/summary）。
- `scripts/market_clock_call.py` SLEEVE_REGISTRY divlowvol 结构标签状态刷新（§2.2 契约首例）+research/L3_ACTIVATION_EVIDENCE.md 变更记录 v1.1 行。
- S6 链接线：Tools/iteration_prompt.txt `python scripts\strategy_scorecard.py`（market_regime 之后、market_clock_call 之前）。
- 轮报告回执+T-81 progress 行+CODELY.md（如有坑律）。

## §5 判据引用纪律

- 本面全部读数=冻结批产物单源派生禁手抄（O-2250）；G1'/G2/L3 判线零触碰。
- 幂等律：同输入重跑产物字节恒等（唯一漂移=generated/elapsed_sec 运行时元数据，SAMPLE_SCIENCE §7 先例口径）。
- 缺件=诚实态（ABSENT/FACE 系），禁编数禁默认落地。

## §6 跑后实证（跑后回填·一次定稿）

（待跑后回填）

## 变更记录

- v1.0 (2026-09-26 R265 bm-b)：跑前冻结（O-1342 §四 item4 落地钩子；判线零改动=三族自家冻结判词逐字消费）。
