## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project
- [2026-09-27 r298 bm-b] 坑律：冻结血统脚本逐轮复制禁手抄重打——r298 探针#11 手抄引入 os.path.SEEK_END（原文=os.SEEK_END）首跑即炸，两诊被误导向环境遮蔽假说（真因=转录 delta，difflib 全文件 diff 定谳）；正典=Copy-Item 整件复制+replace 仅轮号面+difflib 复核非预期 delta=0 再跑。指针=results/_r298bmb_astock_pass_probe.py+results/_r298bmb_s6_chain.log 前后语境。
- [2026-09-27 05:0x] D-20260927-05③ 采纳（bm-a R294·commit 前置冲突标记检查钩子=轮次纪律）：每轮 commit 前 git diff --cached 全量 grep `<<<<<<<|>>>>>>>|=======` 冲突标记（含 rebase 中途 marker 中毒面），非零命中=禁 commit 先按 bigmoney-conflict-resolve 正典解（R293 fe251ac7 marker-poison 实证根因）；首执行 R294 PASS。指针=集团 docs/decisions.md D-20260927-05③+本行（自评采纳面·各司自评律）。
- [2026-09-27 05:4x r301 bm-b] 坑律：**轮中钟面回拨（时统向后校正 ~16.5min·r300 收尾窗实弹）**——同轮轮报告行 ts(05:54:00) 晚于本轮 commit ts(05:37:41)=钟面回拨实证非会话异常非双执行体，正律=①跨文件时间戳倒序禁据此翻案/判双轮②跨回拨窗时长面虚胖≈回拨量（r301 compute_audit pool_starvation span 42.7min 实≈26min，判定时须扣除）③rate/ETA 监控面跨窗轻度失真（探针#13/#14 12.62/12.63/min 自洽）④科学判据零接触（数据 cutoff 全走交易日历非墙钟）⑤事件日志零记载（Kernel-General Id1/W32Time 3h 窗零命中）→校正源未定谳但回拨事实由 report/commit/state 三源交叉定谳。指针=round_reports.md r300 行 vs commit 7758c42d+results/compute_audit.json history@05:43:15+results/_r301bmb_astock_pass_probe.json。

- [2026-09-27 r296 bm-a] 坑律：PowerShell 面 git stash 引用必须单引号包裹——裸写 `git stash drop stash@{0}` 被 PS 当哈希表语法解析报 `error: unknown switch 'e'` 假故障（R296 实弹，命令未达 git）；正典=`'stash@{0}'`。与 `&` 后台符/`;` 链接符同族=PS 语法层坑。指针=results/_r296bma_resolve.py+本行。

### Reference
- 冷层指针：流水型条目（轮报告定案/执行记录/让路裁定）按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md，全量留 git，检索按日期段。
- 坑律正典全量归档（2026-09-27 集团令 O-20260927-0230-bm-a·CODELY ≤10KB 整编）：全部坑律条目已外迁 research/memory-archive/202609.md『坑律归档 2026-09-27』节（行级零丢失·全量留 git·检索按条目内『指针=』字段定位）；新坑律仍先入本件，**≤10KB 硬线**——append 后超线=当窗即办热冷整编勿等月（水位律自 >50KB 重锚·集团令优先）。
- 集团令台账：fleet/orders/O-20260927-0230-bm-a.md（集团 orders.md L45 承接·CODELY ≤10KB·已执行·判据=字节落线）；根 CODELY.md ≤20KB 为 @HQ 面。
- 坑律归档二批（2026-09-27 r296 bm-b 当窗整编·O-20260927-0230 硬线续执行）：r287-r295 追加面 12 条（Project r290 自提交律+Reference 11 条）已外迁 research/memory-archive/202609.md『坑律归档二批 2026-09-27 r296』节（行级零丢失·全量留 git·检索按条目内『指针=』字段定位）；bm-b 机面常设事实热挂=集团仓 decisions.md/orders.md 直扫面本机不可达（无集团仓 clone）→赖 fleet/orders/ O-件镜面承接，每轮报告如实注记禁静默跳过（详档=同节 r291 事实条）。

- [2026-09-27 04:4x] 坑律（bm-a R293-closure·轮会话崩溃恢复判别与打捞协议实弹·E1）：**轮会话可中途回合内崩溃（R293 ~04:33 post-burn pre-wrap：S6 链已 commit+push 而 state/心跳/轮报告未写）——「极新改动→退避」律需要活性判别子：新鲜脏树+活进程=真在飞让路，新鲜脏树+死进程树=崩溃打捞；判别法=schtasks 实例态（IgnoreNew 下我方获发=前实例必已退）+Win32_Process 全扫本仓 prompt 面（零活 codely.exe=死非暂停）+state round_no 停更。**正律=①确认死后即独占续作：搁浅工作以归属明示 salvage commit 收编（禁无限退避养脏、禁 add -A 盲吞），rebase 冲突按 skill 正典配方解②打捞必带 r291 实读断言（pool done-flip 等共享态盘面核验）③轮号处置=崩溃轮由恢复会话补闭（state round_no=崩溃轮号+轮报告 POSTHUMOUS-APPEND 双行制），禁跳号养出双号轮。指针=results/_r293bma_resolve2.py+closure 轮报告+salvage commit c986f8c5
