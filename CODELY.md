## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project
- [2026-09-30 r281 bm-c] 决策复触发先查前轮办结面坑（D-20260930-04④ 实弹）：S0.5 读 decisions 新行触发本仓义务时，同一义务常已被前轮办结（本例=r271 F-20260930-01 已呈报 presented·r280 已判「办结=反重复零动作」）——未查前轮 round_reports/HQ-FEEDBACK 办结面即动手=重复产出（本窗误发 MSG 幸未推送即撤零损失）。How to apply：S0.5 决策触发执行前必先 rg 本仓 round_reports-*与 HQ-FEEDBACK 找该决策号既有回执/办结行，命中即零动作+轮报告指针行收口。
- 冷层指针（r483 合并·指针合并归档 r444 范式）：r478 验收判据多读法坑（判据原文量化面钉死）+r270 改革正典范围分工定谳（RW-5 冻结令）+r277 stash-pop 撞活跃运行件坑+r280 r277 前置避坑腿（plain pull 法）+r280 LHB 改史守卫误伤迟披露形态（is_pure_addition 第二判）+r471 同机猝死半成品处置律+UD 坑+r482 science_gates 调用模式坑（-m 模式律）——七条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r483 bm-a 窗批』节。
- [2026-09-30 r483 bm-a] D-20260930-41 散户研究轨道接管定谳（指针条·正式件已载勿复述）： → 全文档案: .codely-cli/memory/mem-20260930-q-001.md
- [2026-09-30 22:0x r289 bm-c] 共享 JSON 整文件重写格式坑（runnable_pool.json 翻面实弹·两连犯当场抓回）：python json.dump 整文件重写前必核原件 indent+行尾——runnable_pool.json=indent2+CRLF，裸 dumps(indent 不匹配) 或 LF 行尾都会刷 5,300+ 行整排 diff（dualrun 下轮漂移误报面）；正解=dumps(pool, ensure_ascii=False, indent=2) 后 .replace('\n','\r\n') 再 newline='' 写入，写后必 git diff --stat 核外科性（本窗两次整排均靠 diff --stat 当场抓回）。How to apply：一切对仓内共享 JSON 的程序化改写，写前探行尾（ReadAllBytes 数 CRLF/LF）+写后 diff 外科断言，勿信默认参数。
- [2026-09-30 21:5x r479 bm-b] O-20260930-2054 回执+执行：e-item P2NULL-KLIFT-K2200-S2 烧批完成（550 runs/370.9s，A500+B50 验证 PASS，批 3/4）+S0/S1 harvest done-flips 防重复烧；EXCLUSION/FACEB refresh 窗 defer_note 泊位+S1 closed claim（21:40 tick pool_empty_or_busy 实证零假烧）；低效诊断律自查=py 低位系 astock 刷新 I/O-bound 在飞+板全闭环=合法 idle，无可领票滞留>30min
- [2026-09-30 r479 bm-b] merge_lane_views owner_since=null 字符串比较坑：_merge_shard_same_key 对键在值 null 的行 str(None)="None" 恒胜一切真时间戳（"N">"2"）→null 行恒为 base 吞 done 翻面（S1 实锤=done 被 settle 回 ready；S0/S2 幸存仅因对侧行带真时间戳）。修法=比较前 `or ""` 归一（一行），selftest 0 FAIL，修后 S1 翻面复活。How to apply：共享库时间戳键比较必须先归一 null/None，禁裸 str() 可能 null 的值；done/harvest 翻面被 settle 吞回时，先查配对行时间戳字段有无 null 值键。
### Reference
- 冷层指针（r276 合并·r444 范式）：r476 bm-a RW-4 数据门禁三腿定谳+RW-1~4 全绿里程碑条目（正典面=knowledge/panel_gate.py+T-127 票·RW-5 解冻条件满足〔10-03 外审复核〕+RW-6 复算重发下一片）全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r276 bm-c 窗批』节。
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批及历史批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。
- 冷层指针：流水型条目按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md；坑律一〇九~一一六批等历史指针行 verbatim=archive 202609.md『指针合并归档 r444』+『指针迁移归档 r445』两节。
- 冷层指针（r281 合并·指针合并归档 r444 范式）：r473 断头 rebase 诊断序+r473 盘中标记零价蒸发坑（『r466 bm-b 窗批』节）+r454/r455/r236/r444/r229/r235/r237/r445/r441/r442/r446/r447/r448/r450/r244/r452/r456/r457/r252/r255/r449/r462/r464/r258/r259/r269/r459+W8 构造事实诸坑律——全文 verbatim=archive 202609.md 各『窗批』节；原指针行 verbatim=archive『热冷整编 2026-09-30 r281 bm-c 窗批』节。

- [2026-09-30 r472 bm-b] 冻结探针事实消费三坑（W14 runner build 实弹·r471 半成品收养窗）： → 全文档案: .codely-cli/memory/mem-20260930-q-002.md
- [2026-09-30 r473 bm-b] 同轮双 rebase 撞车窗三坑（r472 断头收口实弹·r461/r261 姊妹面）： → 全文档案: .codely-cli/memory/mem-20260930-q-003.md
- [2026-09-30 18:2x r485 bm-a] sina ETF 日线面节前发布滞后坑（09-30 实弹·r484 观察项闭环）： → 全文档案: .codely-cli/memory/mem-20260930-q-004.md
- [2026-09-30 18:5x r486 bm-a] 脏树并发窗双同步坑律（r484/r485 连续弃 pull 后 r486 实弹修正）： → 全文档案: .codely-cli/memory/mem-20260930-q-005.md
- 冷层指针（r475 合并·指针合并归档 r444 范式）：r472 冻结探针事实消费三坑（W14 runner 门键名口径/面前缀/CSV 新列）+r473 同轮双 rebase 撞车窗三坑（ours-theirs 逐轮翻转/r261 幻影拒走双面/GIT_EDITOR 同调用）+r485 sina ETF 节前发布滞后四腿探针定谳——三条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r475 bm-b 窗批』节。

- [2026-09-30 r282 bm-c] SSH…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r491 bm-a 窗批』节）
- [2026-09-30 r284 bm-c] aps…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r491 bm-a 窗批』节）
- [2026-09-30 r285 bm-c] astock…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r491 bm-a 窗批』节）

- [2026-09-30 r476 bm-b] rebase…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r491 bm-a 窗批』节）
- [2026-09-30 r476 bm-b] 并发窗种子带撞号坑（exclusion_marginal…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r491 bm-a 窗批』节）
- [2026-09-30 r477 bm-b] 探针≠门覆盖面坑（EXCLUSION-MARGINAL…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r491 bm-a 窗批』节）

- [2026-09-30 r286 bm-c] inbox…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r491 bm-a 窗批』节）

- [2026-09-30 r286 bm-c] 有新bar触发判读面坑：判「本轮有无新…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r491 bm-a 窗批』节）

- [2026-09-30 21:1x r491 bm-a] 滞留窗收口序（r484-490 六窗 watch 后 r491 全收口实证·r471/r486/外科净路 组合律）…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r492 bm-a 窗批』节）
- [2026-09-30 21:4x r491 bm-a] 引擎语义变更×参数钉扎≠证据复现律（PROSPECT 锚漂 22/22 实弹·RW-1 余波）…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r492 bm-a 窗批』节）
- [2026-09-30 21:4x r288 bm-c] 崩轮遗产恢复序+rebase 侧 S6 面冲突矩阵（r287 15min-kill 遗 65 件未提交+push 被拒双态实弹·r491 滞留窗姊妹面）…（指针条·全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r492 bm-a 窗批』节）
- [2026-09-30 r492 bm-a] O-20260930-2054 机队 CPU 效率确保令已回执执行（指针条·回执面=轮报告+心跳 orders_ack 130）：总动员实况=K-lift 四分片 bm-c 在烧+bm-b 双批在烧+G2 三矿安装清点本机落地（results/g2_install_inventory_20260930.json）+W14 维持 r483 D-41 泊位（「无冻结依赖面」限定词正典适用·禁按令面清单字样翻转禁开族）；日报三机利用率分机行已接线=§二①落地。后续供给面（G2 重叠普查/组合书 O-1147/政体门-RSV-588000 stress 预注册）窗 ≤48h。
- [2026-09-30 r492 bm-a] Start-Process 长命令引号吞没坑（G2 矿源安装实弹·分离进程静默零动作）：PowerShell Start-Process -ArgumentList 传含嵌套路径+重定向的长  字符串→进程起而命令体引号被吞→零执行零报错（日志只有父进程写的头行·7 分钟零 CLONE 行暴露）。Why：-ArgumentList 拼接不再保证内部引号成对传递。How to apply：分离进程启动后必立即查效果面（日志/目标文件）验证已动工；未动工=改前台直跑或写 .ps1 脚本件再 -File 启动（引号不进命令行）；本例前台重试三源全落地零损失。
