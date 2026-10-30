# fleet/backlog.md · 集团常设备货池（C-20261001-03 根治四条②）

> 律：GREEN-IDLE 机器领池即产（claim-by-file 协议·O-2210 既有范式）；池 <10 件=秘书处补货责任；备货单须过 C-02 产出计分面（能跑/能玩/能看才入池）；领单机器在行尾记 `claimed@<机>@<ts>` 完工记 `done@<ts>+commit`。

## 资产线（3+）
1. 【城线】砖集扩 96 件全族（程序化 autotile 16 变体×草/广场/人行道/路缘四族·本地零额度）——claimed@bm-c 生产泵@10-01 11:5x → done@10-02 00:05+MiniGame 1ffc9b510（五族×16=96 全族+cross 族顺带清 U266 斑马 punch·QC 8.3）
2. 【城线】引擎 5×5 可行走 demo（Tilemap+CompositeCollider2D+A* 首步·Unity 工程）——claimed@bm-c@10-02 00:0x → done@10-02 00:2x+MiniGame 21c9c44bf（P09_CityWalkDemo·Tuanjie 2022.3.62t15·batchmode 15 项断言全 PASS·报告 verify-report.json）
3. 【城线】消息雀 PIL mini-cycle（4-6 帧行走动画合成+demo 页行走层）——claimed@bm-c@10-01 23:5x → done@10-02 00:05+MiniGame 1ffc9b510（6 帧 hop 循环 sheet+GIF+demo 页·QC 8.0+相位数据实测分层）
4. 【游戏线】G17 UnboxIt 待审件推进（审计 lane 72 存量待泄洪）——claimed@bm-c@2026-10-11T11:09:45+08:00 → done@2026-10-11T11:09:45+08:00（r868 bm-c 归档核验非代工：G17 实况已由 MiniGame 侧收割闭环=提交 C1832 10-11 10:31「G17/G18/G22/G27四包收割+due队排干」·due 队已排干零残留·本行按完成归档+idle_trigger 计数面修复）

## 内容线（3+）
5. 【BigLife】台词池补齐至 1200 池水位（P-54 目标·7b 本地生成零额度）——**池单过期清出**（10-02 核水位：1200 已于 09-25 达标自停=F-20260925-BL01 回执·axes 72×15+sprite 12×10·建池时未核水位误入·bm-c 补池批即停零损失）
6. 【BigLife】问候库 200-500 开建（城主问候预生成·P-54 既有令）——**池单过期清出**（10-02 核水位：greet 28 桶全 17+faq 7×3=518∈500 顶已达标·GREETINGS.md 达标自停律）
7. 【BigStream】漫画试点 SC-003 双话（既有产线续作）——claimed@bigstream@2026-10-06 14:26:00（O-20261006-1410-HQ-C 领池①路·双话跨轮产·ETA 10-09 前后随轮推进）
8. 【FluxVerse】城内 DECISION 光脉冲族接线（P-34 既有转办· DECISION_MADE 事件类型）——可领（claimed@bm-a@2026-10-07T22:33:00+08:00，O-20261007-1850 派单领池·P-34 转写接线·下窗起排）

## 研究线（3+）
9. 【CPH4】低配机 2D 渲染性能基准（bm-b 3070 档·确定 tile 大城帧预算）——claimed@bm-b@2026-10-10T21:59:03+08:00 → done@bm-b@2026-10-10T22:38:00+08:00（standalone player 隐藏窗路线 r844 诊断 blocked〔零窗律冲突〕→ r845 editor-batchmode 手动 RT 渲染循环路线 8 配置矩阵 8/8 rc0 全 GREEN：pan p99 ≤5.04ms ≪16.67ms；**帧预算结论=每帧可见 tiles ≤19,728（60fps p99 口径·含 20% 安全余量·editor 口径=player 保守下界）**；产物=results/tile_bench/（REPORT.md+summary.json+8 run JSON+harness 三件）+工作面 C:\Fluxgroup\bench-work\tile-bench\）·r868 bm-c 归档（2026-10-11T11:09:45+08:00）：done@ 已在位零残留·原行「claim @」空格形漏 claimed@ 串致 idle_trigger 假计数·本归档补齐串+注记·非代工
10. 【BigMoney】T-94 千人题库烧批续片（永续线 W9+ 分片）——可领（claimed@bm-a@2026-10-07T22:33:00+08:00，O-20261007-1850 派单领池·永续引擎 W178 烧批=本片在飞·T-94 题库续片随波推进）·claimed@bm-b@2026-10-09T01:00:39+08:00（O-20261006-2358 致 bm-b §2 trio 燃毕自领补录——r806 23:30 已领但死于 wrapper 斩首未落 git·r807 补录；bm-b 分片=本机 SatEngine 永续波队列随波推进，当前本机队列 0 在册如实注记）
11. 【BigDomain】19.9 旅程 v2 双案用户文案件（M2 预备·纯内容零额度）——可领（claimed@bm-a@2026-10-07T22:33:00+08:00，O-20261007-1850 派单领池·纯文案零额度·下窗产出）
12. 【BigHouse】城市接入件设计（复刻范围/构件清单/城内选址/City3D 库 AD-NNN 引用选件·消费 R1 研究件 §2.2 解剖+§五接口·纯设计零额度·BLUEPRINT v0.4 为纲）——claimed@bm-b@2026-10-11T13:26:29+00:00（BigHouse 席循环班议程·O-20261011-1917-bm-c §2① idle-claim 接线 r896 落位·R1 研究件已落地 house/BigHouse commit 16fda71·due ≤10-15·产出计分面=城内选址图+构件清单设计件入仓）→ 2026-10-17T12:2x+08:00 bm-c M1 idle-claim 查重核验注记：R1 前提 16fda71 远端实证在册；设计件本体 due 已过期未交付，催办归 BigHouse 席（bm-b loop）下窗，本机不代工不重领；原「可领」前缀缺 claimed@ 标准串致 IdleTrigger 假可领误判复发，本手术补标准标记消除 done@bm-b@2026-10-17T17:25:27+08:00+BigHouse 3409e53（T-2 清偿=r991·设计件 design/city-integration-v1.md·催办件闭合·AD 对库核验门+§四待核双门前置留档）
13. 【BigMoney】r998 git 面收口解锁单（O-20261018-0348-bm-a §1 · bm-b 盘面专属车道：git add fleet/inbox/MSG-20261018-0216-bm-b-taskaudit.md + r998 遗产件（round_reports/state 心跳面）→ commit → push origin main；push 挂死按 §1.3 promisor 判例收手并回执 BLOCKED）——产出=MSG-0216 上链 + O-0137 §1 回执节补行（产物只存于 bm-b 磁盘=物理面锁死 bm-b 车道，他机不可代工；领单即全量轮，S0.5 必扫 O-0348 P0 同义单） → claimed@bm-b@2026-10-18T05:34:00+08:00 → done@bm-b@2026-10-18T05:55:00+08:00+BigMoney b15d5e699（O-0348 §1 同轮收口：r998 遗产 40 件含 MSG-0216 正身上链 DELIVERED；post_review 标记行手术+树手术重放正法·三 stash 保全待下轮回收）

——池建立 2026-10-01 11:5x·首任补货员=秘书处
14. 【BigMoney】bm-b O-0948 rootfix 采纳收口解锁单（O-20261018-0948-bm-a §1/§3 回执窗=本机拉取后 2 轮内·bm-b bigmoney 循环面 origin 停更 07:54→3h+·r1046 fast-path 解锁配方二连·发令机=bm-a r1053）——产=①S0 拉取后核 v2 采纳（spawning 行新话术 hard-cap 240min/silence-kill 25min 引用原文）②本机 run_*.log TIMEOUT 历史清账（总数+最近一例）③MSG-20261018-<HHMM>-bmb-rootfix.md 回执+O-0948 回执节追加④心跳/状态/轮报告常规收口——lane=bm-b 专属（本机日志本机清账·他机不可代工）——可领 claimed@bm-b@2026-10-18T13:05:00+08:00（补录标记·实质 r1004/r1005 窗完成） done@bm-b@2026-10-18T13:05:00+08:00+BigMoney MSG-20261018-1035-bmb-rootfix.md（O-0948 回执节 r1004 已落·bm-a MSG-20261018-1145 确认回执窗双机全闭·8/8 字节恒等·CEO 看片通道落位）

——2026-10-26 23:4x bm-b 复机补货（停摆 10-23→10-26 后池干涸·秘书处补货责任·四件全 CPU-only 零额度）
15. 【BigStream/B站线】回复候选离线批（bm-b 盘）：取 bili_corpus 留出 30 条 + 今日只读发现 10 条评论 → 本地 14B 四候选择优 + G1-G18 全闸 → 候选板 markdown（人工点选用·零写操作·账号安全令保留面）——产出计分面=可看候选板——可领（lane=bm-b 本机 GPU 单车道·须先查 keepwarm 阀与 vram） —— claimed@bm-b@2026-10-30T18:27:13+08:00（lane 锁定登记·bm-c M1 idle-claim 2026-10-30 核验：本条产物面=bm-b 本机 bili_corpus + 本机 14B 四候选，bm-c 不可代工不重领；原缺标准标记致 IdleTrigger 假可领，本注补标记消除）
16. 【BigStream/漫剧线】60 集成片回归复验（bm-b 盘）：audit_durations.py 全 60 集 ffprobe 对账（±0.25s）+ 抽 6 集字幕裁切/孤字/字卡复检 + BUILD_FAIL/MISSING 零残留核对 → 报告件入 cph4/fleet/drama-dept-v1 ——产出计分面=可核验报告——可领（纯 CPU+ffprobe） —— claimed@bm-b@2026-10-26T23:52:00+08:00 → done@bm-b@2026-10-26T23:56:00+08:00+FluxGroup d300c823（60/60 片长 diff=+0.00·规格 540×960@25 全一致·折行 worst 17.00/10.00 孤字0 行首标点0·blackdetect 4 命中全为设计内黑底字卡〔EP001 时间跳卡逐帧核实〕·报告=R-20261026-drama-60ep-regression-01）
17. 【BigStream/MV线】18 曲锚点覆盖体检+补货单：anchors/*-words/-beats/-calibrated/-shotgrid 四面覆盖矩阵 → 缺口清单 + 物理件需求单（缺 mp3 源=优先列 CEO 物理件；缺 madmom 分析=本机可直接跑）——产出计分面=可看矩阵表——可领（纯 CPU） —— claimed@bm-b@2026-10-26T23:57:00+08:00 → done@bm-b@2026-10-26T23:59:00+08:00+FluxGroup（实测四面齐 6 曲/部分 8 曲/别名 3 组；7 曲缺 beats 因本机已无专辑音频〔media+archive 全盘零命中〕→ 物理件需求单 7 曲入 §四；报告=R-20261026-mv-anchor-coverage-01）
18. 【治理】L0 记忆预算+台账去重（bm-b 记忆治理席）：今日实测 53565→49758B 已回到 51200 执法线内、OVERSIZE-LAWS 0；残留=LEDGER 重复行 11 条待去重 + topics 主题件索引回写——产出计分面=可核验台账——可领（纯 CPU） —— claimed@bm-b@2026-10-26T23:42:00+08:00 → done@bm-b@2026-10-26T23:50:00+08:00+FluxGroup a19f3946/e728525f（4 条超长法条迁 L2 topics·LEDGER 87→73 行去重〔含并集补正：a19f3946 曾用旧本地件覆盖丢 33 行 DASHENG，e728525f 已并集恢复〕·闸 v2.3 台账幂等修〔双任务同机同台账双行根因〕）
