## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project
- [2026-09-29 r407 bm-b] 坑律八十一批（收割回执路径必须源码常量解析律·静默长活死亡推断禁律）：W5-JUDGE finalize 收割时以直觉路径 results\w5_judge.json Test-Path 探活→「pid3108 死亡无回执」假诊断，险致误重启双 finalize（真路径=results\trial_labor_w5\w5_judge.json，JUDGE_FILE 常量在 scripts/trial_labor_w5.py:118）；实况=分离 finalize 03:26:33→03:48:39 正常 22min 静默烧（W2/W4 同构 25-27min，静默段零日志写+mtime 停更≠死亡），err 空非崩溃证据。姊妹面：PS `git show >` 重定向=UTF-16 转码，git blob 字节级取证必须 python subprocess 直取（本轮 indent 假差异两连坑皆直觉路径+转码所致）。How to apply：分离长活收割判据=先 rg runner 源码定产物路径常量再探活；重启前必先读代码序（_dump 先于 print=日志 print 齐≠未落盘）。
- [2026-09-29 04:1x] 坑律·自开票认领字段面（r197 bm-c 实录·T-116）：开票同轮自认领必须落 claimed_by/claimed_at 两字段——认领事实只写进 note/created_by 散文=他机「他人 claimed 禁碰」守卫读字段时看到 None=碰撞风险面（T-116 r193 开票漏字段·r197 补登时 origin 零竞争认领实证）；范式=票面 JSON 字段即法，散文注记非法源。How to apply：任何机器开票+自认领，同 commit 必带两字段；缺字段票=发现即补登+验证 origin 无竞争。
### Reference
冷层指针：坑律正典 2026-09-28 六十七/六十八批+r403 bm-a 执行记录+r187 判定回执+六十九批（共 5 条·r189 bm-c 窗水位律当窗整编·行级零丢失校验）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r189 bm-c 窗批』节。
- 冷层指针：流水型条目（轮报告定案/执行记录/让路裁定）按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md，全量留 git，检索按日期段。
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。
冷层指针：坑律归档 25~57 批（2026-09-28 各窗水位律当窗整编·行级零丢失校验）各批全文 verbatim=archive 202609.md 对应『坑律归档 2026-09-28 <N>批』节（四十一批节在本仓 archive 缺=其全文在 quant 镜像 CODELY 面在册）——r173 bm-c 窗五十八批整编时 24 条老批指针行合并为本行，批内容零删零改动。
冷层指针：坑律正典 2026-09-28 五十八批（r173 bm-c 窗·水位律当窗整编：本批新坑律入册即超 ≤10KB 硬线）：r173 T-106 采集批五条（akshare×pandas3 read_excel bytes 全死+sse 空日期硬崩→采集器直连端点律；SZSE 千分位逗号串 float 静默 0 行假阳=audit 零行判败；SSE STAT_DATE 管道滞后=walk-back 回执制；PS & 数组 splat 坑；datetime.date getset 描述符坑）+国家队三面接口正面知识 全文 verbatim=archive 202609.md『坑律归档 2026-09-28 五十八批』节（行级零丢失校验）。
冷层指针：坑律正典 2026-09-28 五十九批（r391 bm-b 窗·G-REPRO-v1 假红双连坑）：①位级复现门拿本批 CI 种子（20284110）重算 ci95 去与 v1 冻结件（种子 20261001）做 dict 全等=两冻结条款实现面互斥的构造性必红（种子探针律：k/n 定值双种子复算一测定谳；ci95/ci95_width=(k,n,seed) 纯函数=k/n 已在比对集即剔除零完整性损失）；②门后死代码族——repro 门史上从未真实通过=其后 prediction_reconciliation/backfill_prereg 载荷路径笔误（axes.legacy.<face> vs 实构 axes.legacy.tables.<face>）首次放行连环揭=hermetic selftest 覆盖不到实弹载荷形状。How to apply：位级复现门先做种子自由度盘点再定比对面；从未执行段首次放行前全 payload 路径穷扫。全文 verbatim=research/DECISION_CHAIN_V2_PREREG.md a6/a6-补 append-only 节（正式件已载=本条不复述，指针即止）。

冷层指针：2026-09-28 晚窗批（r398-cont/r399/r175/r393/r394/r401 执行记录+坑律补/六十/六十一/六十三批）全文 verbatim=archive 202609.md『坑律归档 2026-09-28 晚窗批·执行记录+坑律补/六十/六十一/六十三批』节（r395 bm-b 窗水位律当窗整编·行级零丢失校验·本机 62→63 撞号让位=bm-c 62 批先在 origin）。

冷层指针：坑律正典 2026-09-28 六十二/六十四/六十五/六十六批+r397 批三面教训+r398 五员 ETF 通道定谳〔verbatim 重复旗去重保一〕+r182 双批判定回执（INNOVATION-QUOTA-W1 3/4 出金+MEMBER-REINFORCE x2 cost-fragile）全文 verbatim=archive 202609.md『坑律归档 2026-09-28 r183 bm-c 窗批』节（r183 bm-c 窗水位律当窗整编·行级零丢失校验）。
冷层指针：坑律正典 r400 bm-b（S0 冲突降级轮 playbook·三活实证）+r189 bm-c 七十批（状态行权威律+取模相位值域坑）+r191 bm-c 七十一批（崩确认窗连发坑·同版本 relaunch 冷却律）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r407 bm-a 窗批』节（r407 bm-a 窗水位律当窗整编·行级零丢失校验）。

冷层指针：坑律正典 2026-09-29 r403 bm-b 窗整编批（r402 bm-b 七十二批（rebase 解面侧别假设坑·fetch 基动态推进）/r406 bm-a 七十一批（死窗双杀·claims 面 origin 盲区+链子进程随父死）+r406 bm-a 七十一批补（rebase --continue 绕爪钳实弹）/r407 bm-a 七十三批（预注册锚交叉表必须探针基逐字复算）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r403 bm-b 窗批』节（行级零丢失校验）。

冷层指针：坑律正典 2026-09-29 七十四~八十批（r403 bm-b 七十四批 CPU-delta 探针律死会话归因/r193 bm-c 七十五批集团令面移动断链·义务定义交棒律/r404 bm-b 七十六批 resolver take-NEW 公式方向坑·t3>t2 修正/r410 bm-a 七十七批 T-116 迁移窗 lane 镜像滞后假阳性·共享面权威律/r194 bm-c 七十八批 llama-bench 均值列坑+跨服字段域/r411 bm-a 七十九批指针写≠执行律/r406 bm-b 八十批 CJK 命令通道写面腐蚀坑·文件面写盘律·水位律当窗整编）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r406 bm-b 窗批』节（行级零丢失校验）。
冷层指针：坑律正典 2026-09-29 七十一~七十三批清仓（r402 bm-b 七十二批 rebase 侧别坑+r406 bm-a 七十一批 claims 面 origin 盲区+补批 rebase --continue 绕钳+r407 bm-a 七十三批探针基逐字复算律）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r193 bm-c 窗批』节（行级零丢失校验）。
