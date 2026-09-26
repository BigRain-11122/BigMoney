## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project
- [2026-09-27 05:0x] D-20260927-05③ 采纳（bm-a R294·commit 前置冲突标记检查钩子=轮次纪律）：每轮 commit 前 git diff --cached 全量 grep `<<<<<<<|>>>>>>>|=======` 冲突标记（含 rebase 中途 marker 中毒面），非零命中=禁 commit 先按 bigmoney-conflict-resolve 正典解（R293 fe251ac7 marker-poison 实证根因）；首执行 R294 PASS。指针=集团 docs/decisions.md D-20260927-05③+本行（自评采纳面·各司自评律）。

### Reference
- 冷层指针：流水型条目（轮报告定案/执行记录/让路裁定）按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md，全量留 git，检索按日期段。
- 坑律正典全量归档（2026-09-27 集团令 O-20260927-0230-bm-a·CODELY ≤10KB 整编）：全部坑律条目已外迁 research/memory-archive/202609.md『坑律归档 2026-09-27』节（行级零丢失·全量留 git·检索按条目内『指针=』字段定位）；新坑律仍先入本件，**≤10KB 硬线**——append 后超线=当窗即办热冷整编勿等月（水位律自 >50KB 重锚·集团令优先）。
- 集团令台账：fleet/orders/O-20260927-0230-bm-a.md（集团 orders.md L45 承接·CODELY ≤10KB·已执行·判据=字节落线）；根 CODELY.md ≤20KB 为 @HQ 面。
- 坑律归档二批（2026-09-27 r296 bm-b 当窗整编·O-20260927-0230 硬线续执行）：r287-r295 追加面 12 条（Project r290 自提交律+Reference 11 条）已外迁 research/memory-archive/202609.md『坑律归档二批 2026-09-27 r296』节（行级零丢失·全量留 git·检索按条目内『指针=』字段定位）；bm-b 机面常设事实热挂=集团仓 decisions.md/orders.md 直扫面本机不可达（无集团仓 clone）→赖 fleet/orders/ O-件镜面承接，每轮报告如实注记禁静默跳过（详档=同节 r291 事实条）。

- [2026-09-27 04:4x] 坑律（bm-a R293-closure·轮会话崩溃恢复判别与打捞协议实弹·E1）：**轮会话可中途回合内崩溃（R293 ~04:33 post-burn pre-wrap：S6 链已 commit+push 而 state/心跳/轮报告未写）——「极新改动→退避」律需要活性判别子：新鲜脏树+活进程=真在飞让路，新鲜脏树+死进程树=崩溃打捞；判别法=schtasks 实例态（IgnoreNew 下我方获发=前实例必已退）+Win32_Process 全扫本仓 prompt 面（零活 codely.exe=死非暂停）+state round_no 停更。**正律=①确认死后即独占续作：搁浅工作以归属明示 salvage commit 收编（禁无限退避养脏、禁 add -A 盲吞），rebase 冲突按 skill 正典配方解②打捞必带 r291 实读断言（pool done-flip 等共享态盘面核验）③轮号处置=崩溃轮由恢复会话补闭（state round_no=崩溃轮号+轮报告 POSTHUMOUS-APPEND 双行制），禁跳号养出双号轮。指针=results/_r293bma_resolve2.py+closure 轮报告+salvage commit c986f8c5
