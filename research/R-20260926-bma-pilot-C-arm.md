# R-20260926 bm-a 本地编码试点 C 臂预注册（MSG-20260926-0925-bm-a·跑前冻结）

- 上游令：fleet/inbox/MSG-20260926-0925-bm-a-pilot-C-arm.md（bm-c 交互会话签发·O-20260925-2313-bm-c 续行件·CEO 令 2026-09-26 09:2x「直接让bm-a开工并干一些活，然后告诉我结果和质量」）
- 母批件：research/R-20260925-bma-local-coding-pilot.md（批次 1 一切冻结面不动：A/B 产物、盲评 01-10、ledger 既有行零触碰·只允许 append）
- **冻结律：本文件落 git 后才准开跑 C 臂；判据/循环协议/解读线跑后禁改（改=VIOLATION 如实上报）**
- 隔离变量声明（MSG 原文照录）：「C arm isolates the self-correction variable」——C 与 B 的唯一差异=交卷后自我修正环节；反馈面仅限模型自家前轮交付+冻结验证命令的失败输出，**零编排者提示**（任何人工提示入反馈=变量污染=本批作废如实上报）

## §1 C 臂协议（跑前冻结）

- **同模型同提示词**：qwen3-coder:30b（env BIGMONEY_PILOT_MODEL 缺省同 B）；冻结提示词=批次 1 的 01-10 原件零改动（`---` 分隔线以上正文=模型可见面，与 B 切割恒等）；transport/temperature 0.2/num_ctx 32768 全沿 B 客户端（import 复用零重实现）。
- **自我修正循环**：每件允许 ≤3 轮「跑冻结验证命令→读取失败输出→自行修复」；总尝试上限=4（round 0 单射 + 3 轮修复）；3 轮未过即记 FAIL 不再续。
- **验证语义**：arm-placement 协议形态 `python tasks/<NN>/C/<name>.py selftest`（与冻结验证命令语义恒等·selftest 契约=离线 hermetic 零仓读）；超时 120s/次。
- **修复轮提示词模板**（冻结全文=scripts/pilot_c_client.py FIX_TEMPLATE，跑后禁改）：冻结正文 + 上一轮完整代码 + 失败输出（exit code + stdout/stderr 尾部截 4000 字符）+ 修复指令；失败输出=模型唯一信息增量。
- **产物隔离**：results/local_coding_pilot/tasks/<NN>/C/——逐轮 roundK_code.py / roundK_verify.out / roundK.diff（K≥1）/ roundK_gen.md + 最终 <name>.py + metrics.json + verdict.json；失败记录禁删。
- **抽块失败处理**：任一轮无 python 代码块=该轮验证面 FAIL（raw 留痕、轮次照消耗、循环续走）——诚实统一口径，禁编排者代抽/代修。
- **资源门**：沿母批 §1 冻结口径（让路主产线；RAM 空闲<30GB 禁跑；NUM_PARALLEL=1 顺序执行）；本批=周末窗·板全闭环·池 ready 0·主产线零在飞批，让路面空载。

## §2 判据与第五列（令 §3 冻结口径 + MSG 新增列）

- 四判据沿母批同口径：功能通过率（冻结验证命令 exit 0）/ 码质盲评（四维·评者盲）/ 时延（逐轮 gen metrics）/ 资源面（tok_s·零 OOM·零让路）。
- **新增第五列「修复轮数分布」**（MSG 原文口径）：0 轮单射即过 / 1-3 轮 / 3 轮未过；batch 汇总=results/local_coding_pilot/C_batch_status.json summary.dist。
- 记账：ledger.jsonl 逐件 append arm=C_selffix 行（既有行零触碰）。
- 盲评收口（批后独立步·非本批内跑）：C 产物新 mask 重评（RUBRIC.md 双盲面·评者不见臂标签），与 A 均分差=C 臂盲评读数。

## §3 预注册解读线（MSG §5 原文照录·跑前冻结·零再推导）

- C 臂功能 ≥8/10 且盲评差 ≤1.0 → 中期判读可呈「带 agent 循环达产线可用·建议 P1 购买卡」；
- C 臂功能 <7/10 或盲评差 ≥1.5 → 如实定谳「30B 级不达产线码质标准·购买卡不呈」；
- 中间带 → 10-09 中期判读如实呈两面证据呈 CEO 裁决。

## §4 执行与监督

- 分离批执行：scripts/pilot_c_batch.py run（顺序 01-10·checkpoint=verdict.json 在位即跳过·断点续跑幂等）；批日志=results/local_coding_pilot/C_batch.log（spawn 重定向）；状态镜像=C_batch_status.json（轮监理腿读此件）。
- 时间预算：B 单射基线 ~85-97s/件（~29 tok/s）；C 最坏 4×10 件 ≈ 30-60min 量级，横跨多轮=监理腿照常（T-72 首拉先例范式）。
- 汇报面：C 臂收口后轮报告一行 + 心跳 orders_ack 沿 O-20260925-2313 回执；本 MSG 处理毕移 inbox/processed/；收口产出「B 单射 vs C 循环」对照小结（两轴：功能通过率 + 盲评均分）回填 HQ R-20260925-local-coding 与 P-08 映射表。

—— bm-a 总经办 R238 收令即冻结（2026-09-26 09:3x · 落 git 即生效 · 跑后禁改）
