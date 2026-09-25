# CE-ADMISSION-B1 预注册（CE_ADMISSION_V1 §6 首个准入判定批）· 跑前冻结

> 批件身份：`research/CE_ADMISSION_INTAKE_B1_PREREG.md` v1.0。规则=**research/CE_ADMISSION_V1.md v1.0（冻结件 e1001da0）**——本批为其 §6 协议下首个准入批；本 prereg 与规则冲突时**规则从严者优先**。
> 认领：F-04 先行——`fleet/inbox/MSG-20260925-1514-bm-b-ce-admission-b1-claim.md`（commit edffca5a，先于本件）。票：T-2026-09-25-54 slice-3。

## §0 批件身份【跑前】

- 批名 / 批号：**CE-ADMISSION-B1**（判定批，零新引擎跑）；批内格数=22 候选（PROSPECT 池全员）。
- 认领：F-04 MSG 如上；任务板引用 T-2026-09-25-54-P1（claimed_by bm-b 自 r175）。
- 部门归属：dept:策略（准入规则执行面）。
- 算力预算：**零新引擎算力**——判定腿全部复读冻结件（T54 网格测量件 + 成员件 recorded 字段 + G2 包盘档 + corr-watch 监控档）；预估 <1min 磁盘读；无 >10min 批、无池提交（批执行纪律：无可后台化长活）。批报告带 audit 段（零引擎=audit 面引用 T54 测量批既有 CLEAN 档）。

## §1 α 机制段【D6——判定批消费面照填】

候选为 PROSPECT 池在册模式族成员（ANTS/BBS/DOJI/DUCK/HAM/IBB/IMM/MCB/OVB/RSRS/TMU/VOB 12 族 22 员），机制主张与冻结参数**逐员在册**（`firm/traders/PROS-*.json` params + notes；源头批 `research/shortline/p4_folk` 及其族批 prereg）——本批零新机制主张、零新参数，α 段四选一**承袭各员在册机制卡不重述**（重述=复述禁令违例）。

**同族相关性准入检查【D6·触发性腿】**：本批为判定批——D6/corr 检查按规则 §3 CORR 条款在 **MW 过线员**上触发；零 MW 过线员 ⇒ 腿不触发（§7 跑前预测 #1 预期态）。批内同族变体对（X-01 vs X-CE-01 出场政体对，11 对）如实披露为「同族双员」——其批内两两去重条款（规则 §3 确定性去重）同为触发性腿，不触发时零裁决。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：候选面=PROSPECT 池 22 员（`firm/traders/PROS-*.json` 全目录实读）；测量面=legacy core48 轴（census 1256 起点）+ deep 2013 growing-membership 轴（census 1506 起点）——T54 测量批冻结正典（`research/shortline/T54_PROSPECT_GRID.md` §2/§3/§4/§5 逐字）。
- 窗口与 **evidence_cutoff**：测量件 cutoff=**2026-09-24**（`results/t54/t54_grid_summary.json` 顶层字段实读）；成员件 chain 读数 cutoff=2026-09-22（onboarding 冻结面）；corr-watch N_eff 描述面 generated 2026-09-24 03:26:59。**本批零新数据拉取**——cutoff 后新 bar 不回流本批（前向锁盒 D2：判定面消费的测量件早于 2026-09-25 一切新 bar，锁盒天然成立）。结果 JSON 顶层带 `science_gates.cutoff_meta` 合法键（C2 面）。
- 数据完备门（不过门禁跑批）：§2 证据面在场性门——22/22 员在测量件 per_member_beat_rates 有 6 值读数（双轴×双面×三窗；跑前实读 22/22 在场）+ anchor_excluded 空 + census 门对账（legacy 1256/deep 1506 与 T54 冻结 census 逐字相等）。

## §3 方法学【判定批=复读协议】

- 判定腿（零新引擎）：
  1. **既有链读数**（§4.1 漏斗前段）：判定律预检=成员在册冻结定义+anchor repro PASS（`results/t24_prospect_onboard.json` 档）；G1'v2=成员件 `prospect.g1_pass` recorded 字段（onboarding 批冻结判读）；G2=包盘档 `results/prospect_g2/<ID>.json` 逐员腿（neighborhood/cost_x3/per_year/anchor_reverify——t24-g2-pack prereg 冻结判读）。
  2. **MW 条款**（规则 §2 逐字）：只读 **legacy 轴 base 面**——beat_6m≥0.70 且 beat_12m≥0.50 且 beat_24m≥0.50 三窗同过；读数=测量件 per_member_beat_rates 复读；deep 轴与 x2 面读数逐格披露零门线。
  3. **CORR 条款**（规则 §3 逐字）：触发性腿——仅对「既有链全过＋MW 过线」员触发；测量协议=corr-watch §2（x1 sleeve 日收益、真两两、full-RW+IS2 双面各取 max 再总 max、MIN_PERIODS=60 缺腿=DEFERRED）；零触发员=腿不跑、零裁决。
- null 对照：**不适用**——本批零新回测零新信号（三铁律 N 计数=0；测量批 null/seed 面已在 T54 测量批冻结件内，不重述）。
- 成本口径：消费既有件口径（T54 网格=V1 legacy+CostPatch x2 双面；G2 包=x3 survival 腿）——本批零新成本面。
- 账本：`science_gates.append_ledger("CE-ADMISSION-B1", 0, ...)`——**实际计数 0**（判定批零新试验；T54 测量 121,528 cells 已在册 r183，不重复计数）；`results/gate_attrition.json` 追加一行（漏斗双列损耗账）。

## §4 判据【跑前写死——规则条款照抄禁改】

- **既有链**（G1'v2/G2 判读）：按 §3.1 消费在册 recorded 判读——**本批不重跑不重判既有链**（测量与判定分批；重跑=翻案禁令违例）。
- **MW 门线（冻结·legacy base 面三窗同过）**：6m ≥0.70（P-5/P-5B 口径）｜12m ≥0.50｜24m ≥0.50——任一窗破线=MW FAIL 照交不翻案。
- **CORR 帽（冻结）**：总 max|corr| <0.50=PASS；≥0.50=拒收；面腿 <60 bar=DEFERRED；批内 ≥0.50=确定性去重（legacy base pooled beat_6m 高者胜，平手 id 字典序）。
- **漏斗双列（规则 §4.1）**：considered → 判定律预检 → G1'v2 → G2 → MW → CORR → admitted（进入口径｜过闸口径逐级点名）。
- 硬界设计三件套：不适用（本批无数据腐坏/健康检测类判线；MW/CORR 门为比较判非分布界）。

## §5 跑前预测【写死·批后对账】

1. **损耗为主（规则 §7.1 预测继承）**：J-1 先例 0/22 ≥0.70 ⇒ 本批 MW 读数预期 **0/22 过线**（max legacy base 6m 实读在档 0.5876 <0.70）；诚实负=预期首读非规则失效。
2. **既有链先行清空**：G1'v2 recorded 3/22 → G2 包 0/22 eligible（cost_x3 0/22 在档）⇒ 预期漏斗在 G2 段清空、MW/CORR 触发面=零员——「全链零过线」=双列漏斗的诚实满读。
3. **CORR/N_eff 描述面**：CORR 腿零触发 ⇒ 零新 pairwise；N_eff 描述面=cite corr-watch 最新档（池零变动）——预期 N_eff 首读 <4（规则 §7.3：0.8687 对拖累在档）。
4. **极端日先验**：不适用（零新引擎零新序列；消费面无 max 硬界判线）。

## §6 产物

- script：`scripts/ce_admission_intake.py`（判定跑——复读+漏斗装配+账本/损耗账追加；selftest 子命令=离线自检）。
- results：`results/ce_admission/CE_ADMISSION_B1.json`（顶层 evidence_cutoff+cutoff_meta 合法键；漏斗双列+逐员表+MW 读数+CORR 触发面+N_eff 描述面）。
- 批报告：本文件 §7 回填 + `research/CE_ADMISSION_V1.md` §8 追加一行 + 轮报告回执。

## §7 跑后实证【2026-09-25 15:06 跑后一次定稿回填】

- **漏斗双列（进入｜过闸）**：considered 22｜22 → precheck 22｜22 → G1'v2 22｜3 → G2 3｜0 → MW 0｜0 → CORR 0｜0 → **admitted 0**。
- **G1'v2 过线员 3**（recorded）：PROS-DUCK-01 / PROS-DUCK-CE-01 / PROS-VOB-CE-01；**G2 段清空**：DUCK-01 nbhd✓+per_year✓ 但 cost_x3 ✗（x3 full S=−0.161）；DUCK-CE-01/VOB-CE-01 同 cost_x3 ✗（VOB nbhd 5/8 red 亦 ✗）——0/22 G2 eligible 与 bm-a R88 t24-g2-pack 档读一致。
- **MW 描述读（全 22 员 legacy base 面）**：max beat_6m=**0.5876**（PROS-DOJI-CE-01）<0.70 ⇒ **0/22 过 MW 线**；3 名 G1 过线员读数=DUCK-01 0.5462 / DUCK-CE-01 0.5533 / VOB-CE-01 0.5414（皆 <0.70——即使 G2 过线亦将 MW FAIL）；deep 轴与 x2 面全读数逐格披露于结果件（零门线）。
- **CORR 腿**：untriggered（零 MW 过线员）——§3 测量协议未开跑，零新 pairwise；触发面=0 员如实记。
- **N_eff 描述面**：ρ̄_avg=**0.2576**（15 对 rolling-60d last 读数均值）⇒ 等波动 N_eff=**2.6225**（M=6）——首读 <4 与 §7.3 预测一致；W2 ORANGE 0.8687 对在档。
- **账本**：append_ledger 实际计数 **0**（判定批零新试验；T54 测量 121,528 cells 已在册 r183）→ ledger total 182,945 平持；gate_attrition +1 行（kind=judgment, eliminated 22, mw_pass 空）。
- 产物：`results/ce_admission/CE_ADMISSION_B1.json`（顶层 evidence_cutoff=2026-09-24 + science_gates.cutoff_meta 合法键 C2 面）+ `scripts/ce_admission_intake.py`（selftest 6/6 离线夹具）。

## §8 批后复盘【跑后回填】

- **预测对账**：①§5.1「MW 0/22 过线」=**对**（max 0.5876<0.70）；②§5.2「漏斗 G2 段清空、MW/CORR 触发面零员」=**对**（G2 0/3）；③§5.3「N_eff 首读 <4」=**对**（2.6225）；④极端日先验不适用面=如宣告。4/4 全对——损耗为主首读=规则 §7.1 预测态，非规则失效。
- gate_attrition 追加一行；轮报告回执 r185；无新员注册 ⇒ 零注册管线动作、零 live/paper 接线、零 smoke 锚定门重跑（注册面未开）。
- 诚实边界：本批零翻案零改线——0.70/0.50/0.50 与 0.50 帽纹丝不动；PROSPECT 池治理归 T-24 promotion 管线不变；10-31 J-line 重跑面不受本判定约束（本批只关 CE 准入）。
