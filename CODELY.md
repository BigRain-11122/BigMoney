## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project
### Reference
- 冷层指针：流水型条目（轮报告定案/执行记录/让路裁定）按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md，全量留 git，检索按日期段。
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。
冷层指针：坑律正典 2026-09-28 风暴批十条（r349/r366/r350/r119/r120/r368×2/r121/r369/r351）已 verbatim 整编至 research/memory-archive/202609.md『坑律归档 2026-09-28 二十五批』节（r370 bm-a 窗·行级零丢失校验）。
- [2026-09-28 02:0x r370 bm-a] 坑律：冲突 resolver 的 union 本身可吞他机已上链修复面（r348 族第三例·新面）——bm-a r369 钉定的 V2-P1 lane_owner=bm-b+lane_note+清死认领三面，在 bm-b r351 三波 rebase 的 pool identity-union 中被旧 blob 侧全部回吞（union 只比 identity/行数，无治理字段非空优先规则）。正典=①resolver union 前必扫对岸该件最近修复提交做修复面清单比对（r369 面可用 git show <fix>^..<fix> 提取）；②同 id 条目字段级合并对 lane_owner/lane_note/claimed 类治理字段=非空优先+注记，禁整条目取侧盲并；③被吞恢复=幂等收养脚本从 last-good 提交逐字重放（断言守卫）+同窗定向提交+立即 push 封竞态。指针=results/_r370bma_resolve.py+commit 208c487d。
- [2026-09-28 02:1x r352 bm-b] 坑律：PS `>` 重定向写文件默认 UTF-16 LE——git show :N:path 三 stage blob 提取经 PS 重定向中转必坏（0xff BOM 首症=「'utf-8' codec can't decode byte 0xff」），险误诊为 blob 损坏。正典=resolver/取证面提取 git blob 一律 python subprocess `git show` 直读 stdout utf-8 decode（r366『blob 探针失败先 repr 自检』姊妹面·本机 r352 实弹 autofill_state UU 三段提取一步绕开）。How to apply：写 resolver 见 `> $env:TEMP` 面=改 subprocess；已坏件禁当真值引用。
- [2026-09-28 02:1x r352 bm-b] 坑律：**rebase 中 blob stage 映射与 merge 相反**——:2:=HEAD=上游对侧、:3:=被重放的本机提交；resolver 以 merge 直觉标 ours/theirs=语义面全反（本机 r352 实弹：池 V2-P1 采纳面错取本机保全面、弃 bm-a 外科清认领终局面——幸 :2:/:3: 双探针+git show HEAD 交叉证当场抓获外科换正）。正典=①rebase 窗 resolver 动手前必先 `git show :2:`/`:3:` 各与 `git show HEAD:` 比对定侧（HEAD=上游）；②深时戳取新/身份并集=标签无关自愈面不受害，**语义承重采纳（治理字段/认领/单写者侧）必带侧向断言**；③写后 watch-face 复验对 git show HEAD 终局面。姊妹面=r344/r366 三段分治律族。指针=results/_r352bmb_resolve2.py 尾部 POST-RUN CORRECTION LOG。
