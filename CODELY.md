## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback

- 冷层指针（合并）：r458 泊位族选双面核验坑（rg results 判决面先行·zoo/登记行状态只作线索）=『热冷整编 2026-09-30 r459 bm-a 窗批二』节+r445 采集器无超时挂死盲区坑（fetch_one 45s 死限+TimeoutError 走 CONN_MARKERS fuse 路·探针 _r445bmb_hang_shield_probe.py 承载）=『热冷整编 2026-09-30 r457 bm-a 窗批』节，全文 verbatim=archive 202609.md。
- 冷层指针（r261 合并·指针合并归档 r444 范式）：r459 bm-a fill_ladder 门串坑（泊位登记三验已全机械化=fill_ladder fail-closed 三门+r460 落地）+r460 bm-a autofill crash-fuse 控制面坠机误锁坑（pool_worker 通道正解=fuse 锁死先判真缺陷再走独立发射器）两条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r261 bm-c 窗批』节。
- [2026-09-30 r261 bm-c] rebase --continue 幻影拒走坑（stopped-rebase 脏工作树面·本仓每轮 rebase 必撞）：rebase 停点处 `git rebase --continue` 报「You must edit all merge conflicts and then mark them as resolved using git add」但 `git ls-files -u` 空、无 UU 件——真因=后台 dispatcher/autofill 常驻进程持续写脏运行态文件（autofill_state/crash_fuse/dispatcher_state 族），continue 把未暂存改动误报为冲突语；正法=先 ls-files -u 验零未合并→git add 脏态件（r290 律允许随行提交）→continue；或 `git commit -F .git/rebase-merge/message` 先落该 pick 再 continue。连带=continue 消费 staged 态可产出 sidecar 同名消息提交（内容合法无害·勿误判重复提交去 revert）。
- [2026-09-30 r261 bm-c] 判决落地即同窗 done-flip 止损 churn 律（SLOT-8 实弹+SLOT-9 当日应用）：judged 产物落地后池条目滞留 ready>20min=任机 pool_worker/dispatcher stale 认领撞 r450 守卫 fail-close（SLOT-8 被 bm-a 09:37 撞+本机 dispatcher 09:38 撞·守卫单射零重复烧实证）；正法=判决观测轮即翻 done+result_ref（r244 收割律的止损面），勿等收割轮。How to apply：观测到 trials_ledger 落地（live head 前进）=同窗池翻面，s7/s8 回填仍归收割轮（W7 r256→r257 镜像不破）。

### Project

- 冷层指针（r464 合并·指针合并归档 r444 范式）：r440 撞批三查律+r449 风暴 union 复活去重律（『热冷整编 2026-09-30 r245 bm-c 窗批』节）+r440 bm-b 初筛富集面≠注册级增量律（法面已由 TRIAL_LABOR_W10_PREREG §7/8+CEO-REPORT-WAVE10+attrition 承载）+r242 runner 外科手术四连坑族（W11 runner 已建毕 selftest 47/47·坑律由 _r242bmc_w11_surgeon 系列工件承载）（两律=『热冷整编 2026-09-29 r449 bm-a 窗批』节），全文 verbatim=archive 202609.md。
### Reference
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。

- 冷层指针：流水型条目按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md；坑律一〇九~一一六批等历史指针行 verbatim=archive 202609.md『指针合并归档 r444』+『指针迁移归档 r445』两节。
- 冷层指针（r464 合并）：r236 GBK 控制台吞链+r444 fork-point 过时基点重放两律（操作面=runner 入口 reconfigure 惯例/rebase 风暴窗两步·法面由 iteration_prompt S3+r444 步骤文承载=『热冷整编 2026-09-30 r452 bm-a 窗批』节）+r229 LHB 源改史+r235 core48 源分层+r237 波级泊位窗先例三律（r237 先例已由 DECISION_CHAIN §四.7 法面+W12 draft 头部双载=『热冷整编 2026-09-29 r447 bm-a 窗批』节），全文 verbatim=archive 202609.md。
- 冷层指针（r464 合并）：r445 dual-nulls seed 声明≠实跑基坑（冻结清单 ⑤ seeds 三步律面+runner rebind fv.UNC_BASE 惯例承载=『热冷整编 2026-09-30 r455 bm-a 窗批』节）+r441 泊位种子撞带竞态活处理律（法面双载=T-123 spec+W12 draft ⑤收编清单=『热冷整编 2026-09-29 r448 bm-a 窗批』节），全文 verbatim=archive 202609.md。
- 冷层指针（r255 合并·指针合并归档 r444 范式）：r442 A10 NaN 双坑（attrition 72 行/guard 脚本+preref §7/8 承载）+r446 账本对账律（已机械化=scripts/attrition_ledger_guard.py）+r447 dict-of-Series 构帧对齐全 NaN 坑（_r447bma_rsqr_w12_probe.py 修点承载）+r448 账本外写者吞行坑（同 guard 承载）+r450 批件已落地态未验即 run 重复烧批坑（runner 入口 fail-closed 单射守卫 A13 承载）+r244 seed 三步律验证禁源文本正则计数坑（import 全量视图重验范式承载）+r452 判据字段语义漂移坑（SCIENCE_AUDIT_S9C_AMEND_PREREG.md·否决窗至 10-07·10-01 审计窗 C6 误报按 amend §1.2 裁定）七条全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449/r450 bm-a 窗批』+『2026-09-30 r455 bm-a 窗批』节。
- 冷层指针：r444 S6 批跑器无参腿伪参数坑 全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r457 bm-a 窗批』节（法面=无参腿分支参数计数判别+UNKNOWN 件逐键 deep-compare 定性范式承载·探针 _r444bmb_guardscan_probe.py）。

- 冷层指针（r464 合并）：r456 a158 冻结面抽位点对账 eps 分母坑（a158_tsgate_probe 参考式同款 eps 分母+镜像孪生族构造恒等自检承载=『r459 bm-a 窗批』节）+r457 风暴 resolver 非幂等追加坑（append 型收口脚本 add 前幂等守卫+半途失败 git checkout -- 恢复惯例=『r253 bm-c 窗批』节）+r446 bm-b 手术过继残漏三连坑（tlN→tlN+1 过继必带真数据 identity face 三命令实弹首跑收口步·W13 过继者=bm-a berth=『r459 bm-a 窗批三』节）+r252 泊位/冻结步开工前 inbox 零未读腿坑（供给类开工前置检查单三查扩四查=『r459 bm-a 窗批二』节），全文 verbatim=archive 202609.md。
- [2026-09-30 05:5x r254 bm-c] push 假拒绝坑（reflock 竞态）：报 `remote rejected cannot lock ref: is at <本人commit> but expected <基点>`=同树 FleetPush 抢先已落同一 commit——正法=**先 fetch 验 origin 落点再决定重试**，禁盲目 rebase 重推（r254 实证 fetch 后 origin 已在本人泊位 commit 57636c713·零重复零损伤）。
- 冷层指针（r464 合并）：r255 pool worker stale-tree claim 假失败坑（worker 秒级 rc=2 先查 runner 在树性再判机制故障·正法=claim 前置在树核验=O-2210 待单写者窗）+r449 冻结面 replay 漂移三源定谳律+W8 构造事实（对照员字节恒等=机制身份隔离定谳法·λ 中位 0.131·16/66 奇异窗·退化窗配对差分剔除禁 pinv·正典面=research/INNOVATION_QUOTA_W8_PREREG_DRAFT.md §C1+results/_r449bmb_w8_probe.json），两条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r258 bm-c 窗批』节。
- 冷层指针（r465 合并·指针合并归档 r444 范式）：r462 同机并行会话鉴别律+S6链分离后台驱动律（_r462bma_s6_chain.py 范式承载）+r464 surgeon 锚面取自实跑文件律（三实证实跑锚坑族·其规模化解=r465 收割器范式条留在热层）两条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r465 bm-a 窗批』节。
- 冷层指针（r259 合并）：r448 bm-b 族选防重三键面 rg 补律（法面=results/_r258bmc_zoo_eligibility_scan.json 扫描工件承载）+r258 bm-c 族选第三例（census 盘点行主面法·机械三键面 rg 仅确认面·SLOT-9 定谳）+r259 bm-c 孤儿收养逐件直验律（死会话 prereg 头「已落地件」≠落地证据·泊位-冻结分轮不因会话死亡并窗）三条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r259 bm-c 窗批』节。

- [2026-09-30 r465 bm-a] 过继手术锚律收割器范式（W13 sec11 实弹·r464「锚取自实跑文件」律的规模化解）：100+ sub 的 sections 11-15 手工逐锚不可行→正法=ast 收割器（_r465bma_w13_harvest.py）从前代 surgeon 提取全部 sub1/subn 的 (old,new,what) 常量折叠 payload+逐条验证 new verbatim∈live SRC——验证过=payload 即实跑文本（等价满足锚律），miss 桶=payload 漂移点如实标旗建段时活读（本窗 107/109 绿·2 miss=judge-prep per-leg+L9a 占位符后置 replace 面）；锚库 JSON 供 builder（_r465bma_w13_sec11_build.py）程序化生成 sub 调用（repr 字面量自包含 splice 进 surgeon），杜绝手敲千行字面量。追加型锚的尾部换行陷阱：old 尾无 \n 时 replace 锚含 \n 必 no-op（诊断=repr 尾部字节）。
- [2026-09-30 r454 bm-b] S6 分离链驱动=reconfigure 律漏网面（r236 族）：驱动 stdout 重定向文件仍 GBK 写，腿输出含 U+FFFD 即 print 当场炸整链——链驱动模板必带 sys.stdout.reconfigure(utf-8)；断链续跑=cont 驱动自断腿重放幂等安全。
