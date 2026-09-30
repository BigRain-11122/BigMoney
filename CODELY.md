## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project
- 冷层指针（r483 合并·指针合并归档 r444 范式）：r478 验收判据多读法坑（判据原文量化面钉死）+r270 改革正典范围分工定谳（RW-5 冻结令）+r277 stash-pop 撞活跃运行件坑+r280 r277 前置避坑腿（plain pull 法）+r280 LHB 改史守卫误伤迟披露形态（is_pure_addition 第二判）+r471 同机猝死半成品处置律+UD 坑+r482 science_gates 调用模式坑（-m 模式律）——七条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r483 bm-a 窗批』节。
- [2026-09-30 22:0x r289 bm-c] 共享 JSON 整文件重写格式坑（runnable_pool.json 翻面实弹·两连犯当场抓回）：python json.dump 整文件重写前必核原件 indent+行尾——runnable_pool.json=indent2+CRLF，裸 dumps(indent 不匹配) 或 LF 行尾都会刷 5,300+ 行整排 diff（dualrun 下轮漂移误报面）；正解=dumps(pool, ensure_ascii=False, indent=2) 后 .replace('\n','\r\n') 再 newline='' 写入，写后必 git diff --stat 核外科性（本窗两次整排均靠 diff --stat 当场抓回）。How to apply：一切对仓内共享 JSON 的程序化改写，写前探行尾（ReadAllBytes 数 CRLF/LF）+写后 diff 外科断言，勿信默认参数。
- 冷层指针（r480 合并·指针合并归档 r444 范式）：r479 bm-b O-2054 S2 烧批回执（550 runs/370.9s·批 3/4）+merge_lane_views owner_since=null 字符串比较坑（null 键 str(None)="None" 恒胜真时间戳+比较前 or "" 归一修法·selftest 0 FAIL）——两条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r480 bm-b 窗批』节。
- [2026-09-30 r291 bm-c] 正典引用字符面坑（BEHAVIOR_GUARDRAILS 锚校验实弹）：机器校验「引用是否在场」扫中文正典文本时，负数拼写=U+2212 全角负号（−7.43%）非 ASCII 连字符（-7.43%）——单态子串匹配必假阴（锚校验 FAIL 误报漂移）。How to apply：对含负数引用的中文正典做机器在场校验，须双拼写兼容（ASCII - 与 U+2212 −）或先归一字符面；凡跨「人写正典×机读断言」界面一律先探字符面再写匹配（同族=破折号/引号全半角面）。
- 冷层指针（r292 合并·r444 范式）：r281 决策复触发先查前轮办结面坑+r483 bm-a D-41 轨道接管定谲指针条+r480 bm-b EOL 异面 union 假阳性坑+r491×2/r288 三指针条（滞留窗收口序/引擎语义×参数钉才/崩轮遗产恢复序）+r290 集团决策面盲读坑+D-19 新鲜读律接线——七行全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r292 bm-c 窗批』节（r290 接线正典面=iteration_prompt.txt 决策审核步+state 水位键在役；r292 后续坑=PS 管道哈希假漂移已入热层本节尾）。
- [2026-09-30 r292 bm-c] D-19 决策水位哈希 PS 管道转码假漂移坑（r290 接线的直接续篇）：`git show origin/main:docs/decisions.md` 输出经 PowerShell 管道（`$d -join "`n"` 再 UTF8.GetBytes+SHA256）=转码面哈希（81175e…）≠ 存值 raw-blob 面哈希（21b5c4…）→ 假「新决策落账」信号（本窗当场识别·未触发误消费）。正解=python `subprocess.check_output(['git','-C',…,'show','origin/main:docs/decisions.md'])` 取原始字节直接 `hashlib.sha256`（raw-blob 面·零转码）。How to apply：一切 git show/cat-file 内容寻址水位比对禁走 PS 管道文本面（管道改行尾/编码=恒假漂移），一律 python raw-bytes；假漂移出现时先换算法复算再当新行消费。
### Reference
- 冷层指针（r276 合并·r444 范式）：r476 bm-a RW-4 数据门禁三腿定谳+RW-1~4 全绿里程碑条目（正典面=knowledge/panel_gate.py+T-127 票·RW-5 解冻条件满足〔10-03 外审复核〕+RW-6 复算重发下一片）全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r276 bm-c 窗批』节。
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批及历史批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。
- 冷层指针：流水型条目按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md；坑律一〇九~一一六批等历史指针行 verbatim=archive 202609.md『指针合并归档 r444』+『指针迁移归档 r445』两节。
- 冷层指针（r281 合并·指针合并归档 r444 范式）：r473 断头 rebase 诊断序+r473 盘中标记零价蒸发坑（『r466 bm-b 窗批』节）+r454/r455/r236/r444/r229/r235/r237/r445/r441/r442/r446/r447/r448/r450/r244/r452/r456/r457/r252/r255/r449/r462/r464/r258/r259/r269/r459+W8 构造事实诸坑律——全文 verbatim=archive 202609.md 各『窗批』节；原指针行 verbatim=archive『热冷整编 2026-09-30 r281 bm-c 窗批』节。






- [2026-09-30 r492 bm-a] Start-Process 长命令引号吞没坑（G2 矿源安装实弹·分离进程静默零动作）：PowerShell Start-Process -ArgumentList 传含嵌套路径+重定向的长  字符串→进程起而命令体引号被吞→零执行零报错（日志只有父进程写的头行·7 分钟零 CLONE 行暴露）。Why：-ArgumentList 拼接不再保证内部引号成对传递。How to apply：分离进程启动后必立即查效果面（日志/目标文件）验证已动工；未动工=改前台直跑或写 .ps1 脚本件再 -File 启动（引号不进命令行）；本例前台重试三源全落地零损失。
- [2026-09-30 22:2x r493 bm-a] 普查批书写变体保守判律（G2_OVERLAP_CENSUS_P1 实弹·M4/M5 续片适用）：跨仓同源公式比对（M1 alpha101 vs M3 alphas.py 同为 Kakushadze verbatim 英译）在「规范化字符串恒等」判据下系统性判 DRIFT（15/101 面·括号风格变体如 SignedPower(x, 2.) vs SignedPower((x),2.)）——两独立第三方英译的括号/常数书写风格恒不同，恒等判据=安全侧 fail-closed（不引用 verdict 不重烧·SLOT 轮数值对照可升级）；skip 面教训=在库批判决空间的 skip 集（neutralized/cap 19 面）必须从 vendored 模块 ast 静态单源并入 verdict 空间，漏并=skip 编号误判 NEW-FACE（19 面假阳性当场抓回）。How to apply：M4/M5 普查 runner 复用 g2_overlap_census.py 四腿骨架+把「书写变体预筛」加 norm（去冗余括号）降 DRIFT 噪声；任何「在库不可算面」先并 skip 集再分类。
- [2026-09-30 22:4x r481 bm-b] bm-b 无集团树坑+D-19 新鲜读 temp partial clone 配方（r481 首例实弹）：本机无集团仓检出——bm-c r290 正典配方路径 K:\Fluxgroup\FluxGroup 在本机 fatal（C 盘迁移后 K: 门面不存在·bm-b 只有 BigMoney 仓），D-19 新鲜读正解=temp partial clone：git clone --depth 1 --filter=blob:none --no-checkout git@github.com:BigRain-11122/FluxGroup.git $env:TEMP\fg-dec-bmb 后 git -C … show origin/main:docs/decisions.md 与 docs/orders.md（零树触碰·blob:none 只拉树对象·秒级）；首跑水位基线 last_decisions_sha=21B5C469…FAFDCB 已入 state.json。How to apply：bm-b 一切集团台账消费走此配方（git show 面），禁信本机任何「集团树工作树」（不存在）亦禁按他机 K:\ 路径硬套。
- 冷层指针（r481 合并·指针合并归档 r444 范式）：r472/r473/r485/r486 四条 mem- 档案指针行+r475 冷层指针行+r492 O-2054 回执流水行+r282/r284/r285/r286×2/r476×2/r477 九条截断指针行——全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r481 bm-b 窗批』节；mem 全文另在 .codely-cli/memory/mem-20260930-q-002~005.md；原九条截断行所指内容另见 archive『热冷整编 2026-09-30 r491 bm-a 窗批』+『r492 bm-a 窗批』两节。
