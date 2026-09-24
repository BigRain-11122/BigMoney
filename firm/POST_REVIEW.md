# POST_REVIEW 事后复审机制正典 v1.0 · T-2026-09-24-37 · O-20260924-2115（CEO 直令）

> 立法：2026-09-24 21:08 bm-c r69（认领 commit 同锁）。集团法对接=`docs/governance.md` §10
> （诚实律三道防线管「宣称有没有证据」）；本机制管「**宣称的成果到底成没成**」——成果验证层，
> 不重复立法集团法，只引用。修订权=GM/CEO；复审器与判据 schema 改动须过判据前置（自体适用）。

## 一、三分离原则（不可违背）

1. **动作与成果分离**：立法/建件/派工=动作；**判据复验通过才算成果**。把动作报成成果=自我感动第一来源。
2. **宣称与验证分离**：干活者不得自证成果——复审由确定性脚本重 derive＋跨机复核；执行侧不得自证。
3. **判据与叙事分离**：复审只对照**事前冻结的判据**，不对照执行者的叙事。

## 二、判据前置 schema（一切令/票/机制批必带，事前冻结）

```json
{"item": "<T-x / O-x / 机制名>",
 "claim": "<宣称的成果，一句话>",
 "executor": "<bm-a/bm-b/bm-c/GM>",
 "criteria": [{"check": "<机器可验：file_exists:<path> | json_field:<path>#<key><op><value> | git_log:<path> | rc:<cmd>=<code>",
               "desc": "<人读描述>"}],
 "evidence_pointer": "<results/research 产物路径>",
 "due": "<到期日或事件（机制类=激活条件）>"}
```

- 判据必须在**开工前**随令/票/预注册冻结；跑后补判据=无效（审计红线）。
- 判据三型：`file_exists`（存在性）/ `json_field`（字段值比对，op ∈ {==, >=, <=, contains, in}）/
  `git_log`（提交存在性）/ `rc`（命令退出码，须确定性零网络）。
- **时效承诺字段化**（v1.0.1 补充卷·2026-09-24 r71 bm-c·源=T-27-VETO-FIELD fail 行）：
  凡含时效承诺（否决窗/生效门/到期日）的批，产物 JSON 必带机器可验时效字段
  （`veto_window_until`/`active_from`/`due` 等），判据模板对应 `json_field` 存在性检查；
  跑后补字段=补充卷模式补注记（带 provenance 键，禁改冻结数字面）——流程真值在而产物字段缺
  =「动作词冒充成果词」同族缺口。

## 三、verdict 行 schema（append-only，`results/post_review.jsonl`，单写者锁）

```json
{"ts": "<iso>", "item": "...", "claim": "...", "executor": "...",
 "criteria": [{"check": "...", "verdict": "pass|fail|error", "derived": "<实derive值>"}],
 "verdict": "pass|fail|pending",
 "pending_reason": "<未到期/依赖未落地 时必填>",
 "evidence_pointer": "...", "reviewer": "<deterministic-script|轮值机id>",
 "flags": ["action-word-no-evidence", "all-positive-suspect", "optimism-bias", "masked-partial"],
 "swept_window": "<24h|backfill-wave-1>"}
```

- 分级执法：`pass`=全判据过且当场重 derive；`pending`=判据含未到期/未激活条件（**禁把 pending
  报成 pass——✓掩🟡=flag**）；`fail`=任一判据 fail。
- 复审器=**零 LLM**（确定性脚本重 derive）；`fail`/存疑行→轮值机（**非执行机**）LLM 复核裁决
  追加 `reviewer_verdict`；执行机申诉=GM 裁定。

## 四、自我感动专项检测（复审器内置四检）

1. **动作词冒充成果词**：宣称文本含「已立/已建/已完成/已交付/已生效」处必须同格带证据指针
   （criteria 非空且 evidence_pointer 非空），缺=flag `action-word-no-evidence`；
2. **报喜不报忧率**：单份战报/轮报告全正流本身即嫌疑（健康样本=今晚 6/6 FAIL、0/22 晋升
   如实入报）；全 pass 行集=flag `all-positive-suspect`；
3. **预测-结果偏差**：判据预测系统性偏乐观（预注册 §5 vs §7 对账失败率连续偏高）=flag
   `optimism-bias`；
4. **宣称分级执法**：`masked-partial`=把部分达成报成全达（✓掩🟡）。

## 五、接线面

- **watchdog C9 腿**：每日一扫（24h 已闭件窗），复用 C7 tick 骨架；轮 mandate：S6 末位消费
  `results/post_review.jsonl`——**任一 fail 行=下一轮 P0 修复单**；
- **战报/战绩页复审列**（T-29 消费面）：每行「宣称→复验 ✓/✗/🟡＋证据指针」，CEO 面板直见；
- **GM 自缚**：GM 向 CEO 汇报一律三态标注——**立法**（git 可验）／**生效**（判据通过）／
  **验收**（复审 ✓）——禁三态混报；GM 的令与战报同受复审器扫描。

## 六、首波复审清单（回填本周已闭流·判据跑前冻结·post_review.py 首波即按此 derive）

| # | item | claim（宣称） | executor | criteria（机器可验，冻结） | evidence_pointer |
|---|------|--------------|----------|--------------------------|------------------|
| 1 | T-22 | 虚拟时点海量验证主轴 finalize，分段表交付 | bm-a(R91) | file_exists:results/t22_virtual_timepoints.json；json_field:results/t22_virtual_timepoints.json#census==1506；json_field:#main_verdict 存在 | results/t22_virtual_timepoints.json |
| 2 | T-24 slice-a | PROSPECT 纸面跟踪道 22/22 锚零漂移 | bm-a(R86) | file_exists:results/prospect_paper/_summary.json；json_field:#pass==22；json_field:#drift==0 | results/prospect_paper/_summary.json |
| 3 | T-24 slice-b | 晋升门评估器交付 0/22 eligible 诚实 | bm-a | file_exists:results/prospect_promotion/_summary.json；json_field:#eligible==0 | results/prospect_promotion/_summary.json |
| 4 | T-25 | 水位红牌判定+僵尸处置 C7 机制 | bm-c | file_exists:Tools/watchdog_c7_selftest.ps1；file_exists:results/watermark_red.json；git_log:Tools/watchdog.ps1 | Tools/watchdog.ps1 |
| 5 | T-26 | 扩张验收包 v1.0+新节点接入件 | bm-b | file_exists:fleet/EXPANSION_ACCEPTANCE.md；file_exists:Tools/bootstrap-machine.ps1 | fleet/EXPANSION_ACCEPTANCE.md |
| 6 | T-27 | 五法组合锦标赛 winner=B_MAXDIV 提案（7 天否决窗） | bm-c | file_exists:results/portfolio_blend_tournament.json；json_field:#winner==B_MAXDIV；json_field:#veto_window_until 存在 | results/portfolio_blend_tournament.json |
| 7 | T-28 | 稳定盈利批 J1-J4 判定（J4 fail 诚实负） | bm-a(R90) | file_exists:results/current_market_stable_profit.json；json_field:#verdict 存在 | results/current_market_stable_profit.json |
| 8 | T-29 | 每日战绩直达面 v0.1 | bm-c(r61) | file_exists:scripts/daily_scorecard.py；file_exists:results/daily_scorecard* | scripts/daily_scorecard.py |
| 9 | O-2012/T-33 d1 | 军团名册 v1 交付（28 员，诚实负注册 0 进攻员） | bm-c(r68) | file_exists:results/corps_roster.json；json_field:results/corps_roster.json#summary.assigned_total==6 | results/corps_roster.json |
| 10 | O-2012/T-33 d2 | 进攻招募波 G1' v2 0/20 诚实零 | bm-c(r69) | file_exists:results/t33_attack_wave.json；json_field:#summary.g1_prime_v2_pass==0；json_field:#ledger.total==58110 | results/t33_attack_wave.json |
| 11 | O-2030/T-34 | 早信号研究批已认领（prereg 冻结在 r114 途中） | bm-b | json_field:fleet/tasks/T-2026-09-24-34-P1.json#status==claimed | 票面（prereg 落地后补 row） |
| 12 | O-2045/T-35 | 百万纸盘 d1 勘察（构造性满足=零迁移） | bm-a(R91) | json_field:fleet/tasks/T-2026-09-24-35-P1.json#status==claimed；硬断言件=pending | live/paper.py L72（断言件落地后转 pass 行） |
| 13 | O-2100/T-36 | 算力调度机制批已认领（池/autofill/C8 未落地=pending） | bm-a(R91) | json_field:fleet/tasks/T-2026-09-24-36-P1.json#status==claimed；file_exists:results/runnable_pool.json（**未落地→预期 pending**） | 票面 |
| 14 | O-2115/T-37 | 复审机制立法（本件=立法态；生效=post_review.py 首波跑通；验收=首波报告） | bm-c(r69) | file_exists:firm/POST_REVIEW.md；Tools/post_review.py（pending）；results/post_review.jsonl（pending） | 本件 |

- 首波预期：多行 `pending`（11-13 项在制/依赖未落地）+ ≥1 行 pass/fail 诚实标注——
  **反全绿条款**：首波全绿=复核不严嫌疑，复审器自动 flag。
- 本表判据冻结于 post_review.py 首跑之前（本 commit 即冻结）；跑后禁改判据（J18 同律）。

## 七、验收（含反全绿条款）

首份复审报告必含 ≥1 处 🟡/✗ 诚实标注；注入虚报样本（无证据指针的动作词宣称）必被捕为 flag 行；
smoke 23/23 零回归；静默律合规。

（v1.0 完 · 正典修订走判据前置+GM 署名）
