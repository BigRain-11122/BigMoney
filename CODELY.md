## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### [2026-09-29 21:4x r240 bm-c] tick 15min 时限强杀·完整工件零 commit 接续律（死 tick 实弹·烧完全批+S6 37 腿全绿后死于 S7 收口前·state 未进位轮报告未落=下 tick 轮号回读同号）：正解=取证三步后 adopt-verify-close——①进程链起止时刻核（wscript→powershell→codely·Last Run=在飞锚）确认零他执行体②工件完整性锚验（verdict 全 face+trials_ledger 键+prereg 判据零触碰 diff+attrition 双面）③账本并发叉核（他机同窗 landed 批=later-yields 重基）；禁盲目重跑（RANDOM_LARGE_SAMPLE_LAW）禁 reset 丢产物。附带坑：ack 名带 .md 尾（差集脚本须按 basename 全名比）；attrition 双数组=entries 详单+history 统一链、T-101 线批走车道文件 gate_attrition.bm-a.json 非共享面；内联 hash 锚序列化法须留痕否则不可复验。
- [2026-09-30 01:0x r443 bm-b] jsonl 追加写吞换行腐败坑+union 双侧同族修复律（x2_watch_log 实弹·死轮遗产收编窗）：追加型 jsonl 生产者在并发/异常退出窗下 append 未带前置换行→两 JSON 对象同线拼接=逐行 json.loads 全断（本机死轮 23:5x 写入+origin bm-a 侧同族各 1 例=双侧腐败非单机面）；正典修复=JSONDecoder.raw_decode 循环拆拼接行零丢失（工具 results/_r443bmb_x2log_repair.py·修复后行数==对象数核验 1814）+rebase union 解后必对产物再跑同族拆分（r442 resolver 只验 raw-decode 可解不拆行=粘连行存活进 commit）。How to apply：凡 append-only jsonl 面收编/union 后，最终产物以「行数==对象数」为验收线；新追加写者一律带「ensure trailing newline before append」守卫。
- [2026-09-30 03:1x r455 bm-a] S5 轮报告路径孤儿坑（r454 实弹）：轮 prompt S5 文本「round_reports-<本机id>.md」未带目录→r454 执行体轮行误落根目录 untracked 孤儿（正典=logs/iteration-loop/round_reports-bm-a.md 带全史且 .gitignore 白名单 !logs/iteration-loop/round_reports*.md 锚定正典位）=轮行永不入 git·370 轮历史险断链；正法=本机轮报告恒追加 logs/iteration-loop/round_reports-<id>.md·发现根级同名件=孤儿即 verbatim 并回正典后删除（r455 已修）；How to apply：S5 落笔前先核正典位路径，根级面存在即孤儿处置。
- [2026-09-30 03:4x r445 bm-b] 采集器无超时挂死盲区坑（conn-fuse 对 hang 失明·r445 实弹）：ak.stock_zh_a_daily 无 timeout——死 socket CLOSE_WAIT recv 挂 5h 零异常零 CPU（进程活/日志冻结@1500/5217/面板 cutoff 停 09-28），conn-fuse 只数异常故对 hang 永不触发（r440 spawn 的 refresh 静默停滞一夜）；修=fetch_one daemon-worker+join 硬死限 45s，超时 raise TimeoutError 走既有 CONN_MARKERS fuse 路（探针 _r445bmb_hang_shield_probe.py 4/4：死限准点/快路通/异常 verbatim 中继）；诊断三证=CPU 双采样 delta=0+netstat CLOSE_WAIT+日志 mtime 长静默。How to apply：一切外部源拉取入池前必带死限包装；见「进程活+0 CPU+日志静默」三联=挂死非慢，直接手术勿等。

### Project

- 冷层指针：r433 同门换用法反向证伪律+r431 探针条件率 NaN 归桶伪影律+r443 跨索引 reindex 静默全 NaN 接线坑+r438 轮中猝死脏树 autofill 认领锁死链+r233 阶梯目录消耗态盲区五条全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r440 bm-b 窗批』节（r233 条=r438 bm-b 窗批节在位引用·水位 11,849B 超 ≤10KB 硬线当窗即办·行级零丢失校验·r440 bm-a 撞批三查律+r229 LHB 源改史+r235 core48 源分层热层保留=操作面活跃）。
- 冷层指针：r440 撞批三查律+r449 风暴 union 复活去重律全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r245 bm-c 窗批』节。
- 冷层指针：r440 bm-b 初筛富集面≠注册级增量律全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节（法面已由 TRIAL_LABOR_W10_PREREG §7/8+CEO-REPORT-WAVE10+attrition 承载）。
- 冷层指针：r242 bm-c runner 外科手术四连坑族全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节（W11 runner 已建毕 selftest 47/47·坑律由 _r242bmc_w11_surgeon 系列工件承载）。
- 冷层指针：r246 W4 配额槽判决收编行（VOLREGIME-TIMING-P1 0/3 全负·流水型）全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r455 bm-a 窗批』节；正典=research/INNOVATION_QUOTA_W4_PREREG.md §7/§8+results/innovation_quota/VOLREGIME-TIMING-P1.json。
### Reference
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。

- 冷层指针：流水型条目按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md；坑律一〇九~一一六批等历史指针行 verbatim=archive 202609.md『指针合并归档 r444』+『指针迁移归档 r445』两节。
- 冷层指针：r236 GBK 控制台吞链+r444 fork-point 过时基点重放两律全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r452 bm-a 窗批』节（r440 撞批三查律=同窗 r245 bm-c 节在档去重单存·r449 dedupe 律；操作面活跃度=runner 入口 reconfigure 惯例/rebase 风暴窗两步——法面由 iteration_prompt S3+r444 步骤文承载，热层指针在位即可发现）。
- 冷层指针：r229 LHB 源改史+r235 core48 源分层+r237 波级泊位窗先例三律全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r447 bm-a 窗批』节（r440 bm-b 批曾热留=操作面活跃·本批水位 10,606B 复超线当窗即办·r237 先例已由 DECISION_CHAIN §四.7 法面+W12 draft 头部双载）。
- 冷层指针：r445 dual-nulls seed 声明≠实跑基坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r455 bm-a 窗批』节（法面=冻结清单 ⑤ seeds 三步律面+runner rebind fv.UNC_BASE 惯例承载）。

- 冷层指针：r441 泊位种子撞带竞态活处理律全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r448 bm-a 窗批』节（法面双载=T-123 spec+W12 draft ⑤收编清单）。
- 冷层指针：r442 A10 NaN 双坑律（法面已由 attrition 72 行/guard 脚本+preref §7/8 承载）+r446 账本对账律（已机械化=scripts/attrition_ledger_guard.py r448 遗产 r449 落地）全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节。
- 冷层指针：r447 dict-of-Series 构帧对齐全 NaN 坑（法面已由 results/_r447bma_rsqr_w12_probe.py 修点+facts+探针件承载）+r448 账本外写者吞行坑（已机械化=scripts/attrition_ledger_guard.py r448 遗产 r449 全机接线）全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r450 bm-a 窗批』节。
- 冷层指针：r450 批件已落地态未验即 run 重复烧批坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r455 bm-a 窗批』节（法面已机械化=runner 入口 fail-closed 单射守卫 A13+9 腿 selftest 全绿）。
- 冷层指针：r244 seed 三步律验证禁源文本正则计数坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r455 bm-a 窗批』节（法面=import 全量视图重验范式 _r244bmc_w4_seed_reverify.py·其 ⚠水位注记已由本批兑现清账）。
- 冷层指针：r452 判据字段语义漂移坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r455 bm-a 窗批』节（法面=research/SCIENCE_AUDIT_S9C_AMEND_PREREG.md·否决窗至 10-07·10-01 审计窗 C6 误报复现时按 amend §1.2 裁定注记）。
- [2026-09-30 02:4x r444 bm-b] S6 批跑器无参腿伪参数坑（本轮 5 腿 rc=2 假红实证·重跑后 33/33 全绿）：PS 批跑腿参数化 `$leg.Split(' ')[1..($leg.Split(' ').Count-1)]` 在无参腿（Count=1）下 `[1..0]` 倒序越级=@($null, 元素0)=把脚本名自身传成子命令→「unknown subcommand」rc=2（update_options/sina_mf/astock_daily/ths/ah 五 gate 无参默认腿全中）——无参腿必须走无参分支（参数计数判别）；附带：分类器 UNKNOWN 件手工定性范式=先逐键 deep-compare 双 blob，files 全同+唯一差=顶层 ts→take-new by ts 零风险（探针=results/_r444bmb_guardscan_probe.py·_attrition_guard_scan.json 撞车实战）；时间戳缩写 strftime("%H:%M")[0]+"x" 生成「0x」丢小时位，正解 strftime('%H:')+分首位+'x'。How to apply：S6/批量腿批跑器先查无参腿分支；UNKNOWN 件先逐键比对定性再选配方。
- [2026-09-30 03:2x r249 bm-c] pandas to_csv 浮点回读非逐位坑（W5 runner selftest 首跑实弹）：fixture 锚面从内存帧派生 vs load_panel 从 CSV 读回帧派生 → 691/3737 close 值低尾位 ULP 漂移；ICU 稳健回归端点常恰落末价（tie 面）→ above/below/tie 三分类零点邻 ULP 敏感 → long_open 1312≠1308 面漂移假红（W4 量能阈值面未踩中=幸存者偏差）。正法=selftest derive-then-freeze 锚一律从 CSV 读回帧取数（与被测路径同源逐位）；真实数据面不受影响（探针与 runner 同读同一真 CSV·G-ANCHOR 实测逐位过）。How to apply：含零点邻分类面（tie/阈值穿越）的 runner selftest，fixture 锚派生必须走读回帧勿信内存帧。
