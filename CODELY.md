## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback

- 冷层指针：r458 泊位族选双面核验坑（zoo 行状态面滞后于 results 判决面）全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r459 bm-a 窗批二』节（法面=防重核双面序：rg results 判决面先行·zoo/登记行状态只作线索）。
- [2026-09-30 r459 bm-a] fill_ladder 门串坑（泊位登记三面坑族·step-6 同窗三连实弹）：①catalog enqueue_gates 裸串 prereg_frozen=checker unknown-gate-ref 永堵，正典=prereg_frozen:<路径>；runner 字段须裸路径（描述另放 runner_note）②pool entry 缺 workers_plan=autofill._pick 硬跳「no workers_plan」→ ready 批搁浅 3 tick（verdict pool_empty_or_busy 假象·SLOT-1 dict 式为正典；fill_ladder 已加 fail-closed 门镜像 consumer_plan）③缺 runner_args=首发即 argparse no-cmd exit 2（r444 无参腿族·W12-JUDGE ['judge',...] 惯例）——泊位登记面三验=enqueue_gates 语法+workers_plan+runner_args 三查后再宣告 pool-ready（r460 三面已全机械化=fill_ladder runner_args fail-closed 门落地）。SLOT-5 同病 latent（done 态不再撞检）；SLOT-7 冻结窗将撞新门=如实拦。
- [2026-09-30 r460 bm-a] autofill crash-fuse 控制面坠机误锁坑（r459 泊位族第二面续弹）：首发坠于控制面因（当时 runner_args 未回填=argparse exit 2），06:40 tick 照 O-0947 确认 code-crash count=1 并拒同哈希重燃（门语「edit runner to clear」）——真修复在控制面（池 runner_args=['run'] 已落 r459 repair-2），代码 10/10 自检+verify 位对齐无缺陷，「编辑代码解锁」=伪修禁走。正解=pool_worker 通道（O-2210 独立发射器不吃 C8 fuse·self-contained 条目 20min stale 认领窗）带正确参数重跑=首次正确武装发射非 crash-loop；fuse 记录留档无害。How to apply：首发坠机后 autofill 通道被 fuse 锁死时先判代码是否有真缺陷（selftest+verify 面），无缺陷走 pool_worker 通道或补真实代码修复，禁为解锁而编辑。
- 冷层指针：r445 采集器无超时挂死盲区坑（conn-fuse 对 hang 失明） 全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r457 bm-a 窗批』节（法面=fetch_one daemon-worker 45s 死限+TimeoutError 走 CONN_MARKERS fuse 路+探针 _r445bmb_hang_shield_probe.py 承载）。

### Project

- 冷层指针：r440 撞批三查律+r449 风暴 union 复活去重律全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r245 bm-c 窗批』节。
- 冷层指针：r440 bm-b 初筛富集面≠注册级增量律全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节（法面已由 TRIAL_LABOR_W10_PREREG §7/8+CEO-REPORT-WAVE10+attrition 承载）。
- 冷层指针：r242 bm-c runner 外科手术四连坑族全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节（W11 runner 已建毕 selftest 47/47·坑律由 _r242bmc_w11_surgeon 系列工件承载）。
### Reference
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。

- 冷层指针：流水型条目按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md；坑律一〇九~一一六批等历史指针行 verbatim=archive 202609.md『指针合并归档 r444』+『指针迁移归档 r445』两节。
- 冷层指针：r236 GBK 控制台吞链+r444 fork-point 过时基点重放两律全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r452 bm-a 窗批』节（r440 撞批三查律=同窗 r245 bm-c 节在档去重单存·r449 dedupe 律；操作面活跃度=runner 入口 reconfigure 惯例/rebase 风暴窗两步——法面由 iteration_prompt S3+r444 步骤文承载，热层指针在位即可发现）。
- 冷层指针：r229 LHB 源改史+r235 core48 源分层+r237 波级泊位窗先例三律全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r447 bm-a 窗批』节（r440 bm-b 批曾热留=操作面活跃·本批水位 10,606B 复超线当窗即办·r237 先例已由 DECISION_CHAIN §四.7 法面+W12 draft 头部双载）。
- 冷层指针：r445 dual-nulls seed 声明≠实跑基坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r455 bm-a 窗批』节（法面=冻结清单 ⑤ seeds 三步律面+runner rebind fv.UNC_BASE 惯例承载）。

- 冷层指针：r441 泊位种子撞带竞态活处理律全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r448 bm-a 窗批』节（法面双载=T-123 spec+W12 draft ⑤收编清单）。
- 冷层指针（r255 合并·指针合并归档 r444 范式）：r442 A10 NaN 双坑（attrition 72 行/guard 脚本+preref §7/8 承载）+r446 账本对账律（已机械化=scripts/attrition_ledger_guard.py）+r447 dict-of-Series 构帧对齐全 NaN 坑（_r447bma_rsqr_w12_probe.py 修点承载）+r448 账本外写者吞行坑（同 guard 承载）+r450 批件已落地态未验即 run 重复烧批坑（runner 入口 fail-closed 单射守卫 A13 承载）+r244 seed 三步律验证禁源文本正则计数坑（import 全量视图重验范式承载）+r452 判据字段语义漂移坑（SCIENCE_AUDIT_S9C_AMEND_PREREG.md·否决窗至 10-07·10-01 审计窗 C6 误报按 amend §1.2 裁定）七条全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449/r450 bm-a 窗批』+『2026-09-30 r455 bm-a 窗批』节。
- 冷层指针：r444 S6 批跑器无参腿伪参数坑 全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r457 bm-a 窗批』节（法面=无参腿分支参数计数判别+UNKNOWN 件逐键 deep-compare 定性范式承载·探针 _r444bmb_guardscan_probe.py）。

- 冷层指针：r456 a158 冻结面抽位点对账 eps 分母坑（W13 探针首跑实弹） 全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r459 bm-a 窗批』节（法面=a158_tsgate_probe 参考式同款 eps 分母+镜像孪生族构造恒等自检承载）。
- 冷层指针：r457 风暴 resolver 非幂等追加坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r253 bm-c 窗批』节（法面=append 型收口脚本 add 前幂等守卫惯例+半途失败 git checkout -- 恢复惯例承载）。
- 冷层指针：r446 bm-b 手术过继残漏三连坑（tlN→tlN+1 过继必带真数据 identity face 三命令实弹首跑收口步）全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r459 bm-a 窗批三』节（W13 过继者=bm-a berth·r459 state next 指针直引本条）。
- 冷层指针：r252 bm-c 泊位/冻结步开工前 inbox 零未读腿坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r459 bm-a 窗批二』节（法面=供给类开工前置检查单三查扩四查：job_list+tasks+fetch 标题扫+inbox 未读清零）。
- [2026-09-30 06:4x r448 bm-b] 族选防重 rg 键面补律（r458 双面律本窗第二例·W8 泊位实弹·零污染拦截）：zoo 行族名拼法 rg（path_continuity/salience 等）**漏检 P-1e 已烧面**——批件与判决产物用 zoo 编号别名（zoo92_coin_team/zoo85_stv），族名零命中≠零前判；本窗幸被消费位指针链（P-1c harness→P1E_NEIGHBOR_CORR 受检侧名单）拦下。正法=泊位族选防重 rg pattern 必并 **zooNN_\* 别名键面**+顺消费位指针走链复核。How to apply：任何族选/防重核，rg 键面=族名∪zooNN 别名∪消费位批名三键。
- [2026-09-30 05:5x r254 bm-c] push 假拒绝坑（reflock 竞态）：报 `remote rejected cannot lock ref: is at <本人commit> but expected <基点>`=同树 FleetPush 抢先已落同一 commit——正法=**先 fetch 验 origin 落点再决定重试**，禁盲目 rebase 重推（r254 实证 fetch 后 origin 已在本人泊位 commit 57636c713·零重复零损伤）。
- [2026-09-30 06:1x r255 bm-c] pool worker stale-tree claim 假失败坑（SLOT-6 实弹）：本机 worker 06:02 从 origin-fetched 池视图认领他机刚入池条目——runner 仅存在于本地未拉取的 origin commit 中=claim 后 0.0s rc=2 机制假失败（0.0003 core-hours·零科学烧批·outcome=fail 语义=freed 正确返还池·本地拉取后下 tick 自愈真烧）；危害面=ledger 假失败行+认领周期空耗。正法方向=worker claim 前置 runner 本地在树核验（O-2210 机件改动须单写者窗·本轮未擅改）。How to apply：他机新入池条目真烧=本地树已拉取之后；worker 秒级 rc=2 先查 runner 在树性再判机制故障。
[2026-09-30 r449 bm-b] 冻结面 replay 漂移三源定谳律+W8 构造事实（W8 feas 探针实弹·死会话遗产收编轮）：重放历史冻结批成员面 vs 冻结产物不一致时，定谳序=①代码史（git log 冻结 commit 后）②数据史（core48 cutoff 前行=纯追加否）③注册件史（firm/traders/*.json）；本例零代码+零数据漂移、漂移=T-78 s4 注册进化（d65f2d4ac 三员退出覆盖层接线）合法——**对照员字节恒等测试**（未改注册件员 replay==frozen 2/2 全中）=机制身份隔离定谳法，禁据单员漂移误判机制漂移。W8 构造冻结事实：28 员 252d 滚动 16/66 窗样本协方差奇异（A 臂生产配方不可算=病逆防御靶现象实弹）、λ∈[0.039,0.898] 中位 0.131、cond 303k→36、A 臂全 pg_fallback vs B 臂 14 窗翻回闭式；退化窗政策=配对差分剔除+计数披露禁 pinv（A=生产配方 verbatim 禁改）。指针=research/INNOVATION_QUOTA_W8_PREREG_DRAFT.md §C1 + results/_r449bmb_w8_probe.json。
