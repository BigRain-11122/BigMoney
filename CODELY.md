## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project
### Reference
- 冷层指针：流水型条目（轮报告定案/执行记录/让路裁定）按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md，全量留 git，检索按日期段。
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。
冷层指针：坑律归档 25~57 批（2026-09-28 各窗水位律当窗整编·行级零丢失校验）各批全文 verbatim=archive 202609.md 对应『坑律归档 2026-09-28 <N>批』节（四十一批节在本仓 archive 缺=其全文在 quant 镜像 CODELY 面在册）——r173 bm-c 窗五十八批整编时 24 条老批指针行合并为本行，批内容零删零改动。
冷层指针：坑律正典 2026-09-28 五十八批（r173 bm-c 窗·水位律当窗整编：本批新坑律入册即超 ≤10KB 硬线）：r173 T-106 采集批五条（akshare×pandas3 read_excel bytes 全死+sse 空日期硬崩→采集器直连端点律；SZSE 千分位逗号串 float 静默 0 行假阳=audit 零行判败；SSE STAT_DATE 管道滞后=walk-back 回执制；PS & 数组 splat 坑；datetime.date getset 描述符坑）+国家队三面接口正面知识 全文 verbatim=archive 202609.md『坑律归档 2026-09-28 五十八批』节（行级零丢失校验）。
冷层指针：坑律正典 2026-09-28 五十九批（r391 bm-b 窗·G-REPRO-v1 假红双连坑）：①位级复现门拿本批 CI 种子（20284110）重算 ci95 去与 v1 冻结件（种子 20261001）做 dict 全等=两冻结条款实现面互斥的构造性必红（种子探针律：k/n 定值双种子复算一测定谳；ci95/ci95_width=(k,n,seed) 纯函数=k/n 已在比对集即剔除零完整性损失）；②门后死代码族——repro 门史上从未真实通过=其后 prediction_reconciliation/backfill_prereg 载荷路径笔误（axes.legacy.<face> vs 实构 axes.legacy.tables.<face>）首次放行连环揭=hermetic selftest 覆盖不到实弹载荷形状。How to apply：位级复现门先做种子自由度盘点再定比对面；从未执行段首次放行前全 payload 路径穷扫。全文 verbatim=research/DECISION_CHAIN_V2_PREREG.md a6/a6-补 append-only 节（正式件已载=本条不复述，指针即止）。


冷层指针：2026-09-28 晚窗批（r398-cont/r399/r175/r393/r394/r401 执行记录+坑律补/六十/六十一/六十二批）全文 verbatim=archive 202609.md『坑律归档 2026-09-28 六十~六十二批+晚窗执行记录批』节（r395 bm-b 窗水位律当窗整编·行级零丢失校验）。
- [2026-09-28 19:5x] r177 bm-c 坑律六十二批（S6 批跑两坑）：①PS 拼接路径陷阱——循环批跑 S6 腿用双引号字符串 + 反斜杠目录拼路径，尾反斜杠转义吞收尾引号→全部腿以「cant open file」rc=2 假红（harness 面非腿败）；正解=Join-Path 拼路径（或正斜杠），假红面先验文件名再定腿责。②守卫在位性核查假阴——grep 守卫用 First-12 只见文件头部 regime_guard 命中，真守卫在 main() 尾部（L1767 batch-3 C 族 single-writer）被截断漏读=险把「法-码漂移」假案当真去修；且非宿主机写共享面先查 stale-takeover 机制（bm-a 心跳 78min>C_HOST_STALE_MIN 20min=合法接管非车道违例）。How to apply：宣称守卫缺失前必全文件扫（count/全量输出）；非宿主写共享面先读 _host_heartbeat_age_min 判 stale-takeover 再定性。
