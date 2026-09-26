## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project
- [2026-09-27 r290 坑律·自治体自脏自堵] 自动循环体（autofill tick）每跳写自家运行态件（autofill_state/crash_fuse）＝轮间树恒脏＝其自带的 r282 push-拒后 rebase 恢复路径恰在被需要时恒不可达（实证=r288 CN-TREND keepalive push 滞留→claim 滞留本地→远端 STALE_MIN takeover 门重开→双烧）。根因类：**自治写者的自有心跳脏会结构性堵死自己的恢复路——写者必须把自有脏并入同一 commit（自提交律），他者脏（会话在飞件）仍让路**。修法已编码 Tools/autofill.py `_tick_owned_dirt()`（claim/keepalive git 流 add POOL+STATE+FUSE·存在过滤·selftest S15i/S17e）。指针=archive 202609 r288/r289 条；同窗 S0 stash-pop 池冲突 take-upstream 解（零丢失：stashed 53⊂upstream 54）已留痕 results/_r290_resolve.py。

### Reference
- 冷层指针：流水型条目（轮报告定案/执行记录/让路裁定）按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md，全量留 git，检索按日期段。

- 坑律正典全量归档（2026-09-27 集团令 O-20260927-0230-bm-a·CODELY ≤10KB 整编）：全部坑律条目已外迁 research/memory-archive/202609.md『坑律归档 2026-09-27』节（行级零丢失·全量留 git·检索按条目内『指针=』字段定位）；新坑律仍先入本件，**≤10KB 硬线**——append 后超线=当窗即办热冷整编勿等月（水位律自 >50KB 重锚·集团令优先）。
- 集团令台账：fleet/orders/O-20260927-0230-bm-a.md（集团 orders.md L45 承接·CODELY ≤10KB·已执行·判据=字节落线）；根 CODELY.md ≤20KB 为 @HQ 面。

- [2026-09-27 02:4x] 坑律（bm-a R287·CENSUS_FUS_S2 runner 建造期·E1 selftest 期自捕零外泄）：**blend/基准 sizing 分母必须随实际 target 集——fixed_all 基准（EW48）沿用 TOP_K 常量分母=每员 1/16 权重、Σw=3.0 收益放大 3 倍（实弹：EW48 ann 0.4876 vs 真 ~0.169，无噪漂移夹具 [3a] 当场红）**；正律=want=NOTIONAL/len(target) 于 target 定后取；连带=「完美信号」夹具必须截面单调——时序单调列=常数截面被 ic_series 正确跳过=夹具自病非机器病（P-1 S6 无噪漂移范式是正解）。指针=scripts/census_fusion_s2.py blend_top16 want 行+selftest [2][3a] 修正史
- [2026-09-27 02:4x] 纪律（bm-a R287·集团令扫描面新维·D-20260927-05② 自评采纳落地）：**集团 docs/orders.md 直令面可承载 @BigMoney dispatched 令而不落本司 fleet/orders/——实弹：L45「CODELY ≤10KB」令经 fleet/orders 差集=空漏接，集团台账全文件扫描面捕获（R287 承接执行 8a00f514）**；正律=每轮 S0.5 decisions.md 同位步加扫集团 orders.md 全文件 @BigMoney/quant 行（dispatched 未回执=落 O 件入册执行），本律入本件=轮读面自动携带。指针=fleet/orders/O-20260927-0230-bm-a.md+集团 orders.md L45
- [2026-09-27 03:0x] 执行记录（bm-a R288·S0.5 扫描面二次实弹）：集团两令承接闭环——P-202609-26-04（U231 块面件·金融商业区块六必答）+P-20260926-18（九司调研部建制·BigMoney 复用正名）→O-20260927-0302-bm-a+`research/R-20260926-city-block-finance.md`+org_chart 研究部行席位注记；复用优先零新车道（RESEARCH_MECHANISM 双频=超配章程周轮律）。指针=同 O 件
- [2026-09-27 03:1x] 坑律（bm-b R291·S0 两连 rebase 撞车窗实弹）：**git stash pop 产冲突时条目必保留——解完必须显式 git stash drop，否则下一次 pop 仍是同一条目（r291 实证：post_review 同 stash 双 pop=38 行重复注入 UU 面，靠 zone⊂merged-face 验证零丢失收口）**；正律=pop 冲突解后流程=add→drop→再 pop 下一条目。指针=results/_r291_resolve.py+r291 轮报告
- [2026-09-27 03:1x] 事实（bm-b R291·S0.5 扫描面机器分工）：**bm-b 本机无集团仓本地 clone（集团仓在 bm-a 机面·本机 E:\Fluxgroup=迁移未落地空壳）——D-20260927-05② 集团 orders.md 直扫面在 bm-b 不可达，bm-b 赖 fleet/orders/ O-件镜面承接（bm-a 落册推送），每轮报告如实注记直扫面不可达、禁静默跳过**。指针=O-20260927-0230/0302-bm-a 镜面链
