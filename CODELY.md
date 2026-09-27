## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project

### Reference
- 冷层指针：流水型条目（轮报告定案/执行记录/让路裁定）按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md，全量留 git，检索按日期段。
- [2026-09-27 15:3x r331 bm-a] 坑律（十八批外迁·指针）：rebase 撞车核验自动合并件归属侧必先 CRLF 规范化（autocrlf 下 LF-blob 件必假报 HYBRID）/定侧正道=两 commit changed-file 交集（UU 必==交集）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 十八批』节。

- [2026-09-27 14:5x r330 bm-b] 坑律（十八批外迁·指针）：移植既有因子 ctor 前必探明返回形+真实调用形态探针先行（含崩类复现腿，hermetic 合成面测不到）——全文 verbatim=archive 202609.md 十八批节。
- 十六批外迁（r86 bm-c·2026-09-27·水位律当窗整编）：r83 union 配方律/r327bmb org_chart 面板律/r326bma pandas asi8 律三条目外迁=归档十六批节·行级零丢失。
- [2026-09-27 14:5x r328 bm-a] 坑律（十七批外迁·指针）：腾讯双 K 线端点互不互证/行序守卫 close∈[low,high]+修复面补/akshare 包装≠独立源/利率带先验 (0,200)——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 十七批』节。
- [2026-09-27 15:0x r329 bm-a] 坑律（十七批外迁·指针）：继承挂起 rebase 完成 resolver 三修（memory-union 条目级双向覆盖核验/daily_report 孪生 twin-side coupling/EOL 探测源=base blob 禁读冲突标记件）——全文 verbatim=archive 202609.md 十七批节。
- [2026-09-27 15:0x r86 bm-c] 坑律（十八批外迁·指针）：根迁移/仓重建后必须同轮盘点机器本地数据面（gitignored data/* 车道资产不随 clone 复活=不可逆灭失；status done 块必须可由盘上事实再 derive）——全文 verbatim=archive 202609.md 十八批节。
- [2026-09-27 15:5x r332 bm-a] 坑律（十九批外迁·指针）：实弹测试 commit 演练禁在脏工作树——staged 空即 commit 失败后照跑 soft/hard HEAD~1 会回退真 commit/抹掉在飞改动；正典=演练前 status --porcelain 必空+回退用显式 pre-test sha。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 十九批』节。
- [2026-09-27 15:5x r331 bm-b] 坑律（十九批外迁·指针）：autofill tick 自提交与轮会话 git 集成窗竞态——tick add 会把 rebase UU 静默解掉+孤儿提交+abort；轮 git 集成窗避 :X0:02±1min+撞后 reflog 定谳+salvage-union。全文 verbatim=archive 202609.md 十九批节。
- [2026-09-27 16:0x r334 bm-a] 坑律（十九批外迁·指针）：blanket max-ts 取侧会被载荷未来日期字段毒化（dashboard next-fire 2026-09-28 压过真生成 ts→假 tie 取旧侧）；正典=已知生产者探针路径优先+未来哨卫+pair/twin 断言防杂交不防双错侧。全文 verbatim=archive 202609.md 十九批节。
- [2026-09-27 16:1x r332 bm-b] 坑律（二十批外迁·指针）：autofill tick 自提交落点在 fire 后 ~2.5-3min（:X0:02 fire→:X2:5x 落 commit），轮首 :X1 读数到 :X5 行动已陈旧——丢弃类 git 动作前必现读 git log -1+status 与轮首读数比对，已变=弃手工丢弃改走 rebase 重放+union 收敛。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十批』节。

- [2026-09-27 16:2x r335 bm-a] 坑律（二十批外迁·指针）：PowerShell ConvertFrom-Json 会对合法 JSON 件假报 parse 失败——板面/多件扫描的权威解析一律用 python，PS 结果只作初筛。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十批』节。
- [2026-09-27 16:2x r335 bm-a] 坑律（十九批外迁·指针）：resolver 两坑——①未来哨卫比较先归一位 10 分隔符（T 0x54>空格 0x20，原串直比把 T 形 ts 全误判未来剔除）；②resolver 路径串与 ls-files 输出逐字节核对禁按规格记忆转写（daily_report 真路径=带连字符 REPORT-2026-09-27）。全文 verbatim=archive 202609.md 十九批节。
- [2026-09-27 16:1x r89 bm-c] 坑律（二十批外迁·指针）：stub-drop 配方锚全文形态防指针误伤+面积口径 encode 字节数——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十批』节。
- [2026-09-27 15:2x r87 bm-c] 坑律（十九批外迁·指针）：rolling-ledger union 的 dedup 键必须逐面先探字段存在——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 十九批』节。
- [2026-09-27 15:5x r88 bm-c] 坑律（十九批外迁·指针）：轮首定身份必读 fleet\machine.json machine_id——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 十九批』节。
- 十九批外迁（r89 bm-c·2026-09-27·水位律当窗整编·行级零丢失）：r332 bma commit 演练脏树律/r331 bmb tick 竞态窗律/r334 bma max-ts 毒化律/r87 bmc union 键探律/r88 bmc 身份律五条目外迁=归档十九批节（12633B 破 ≤10KB 硬线=律触发当窗办勿等月）。

- [2026-09-27 16:5x r338 bm-a] 坑律（二十二批外迁·指针）：共享 JSON 面 python 编辑必先探原写者格式逐字节复刻（EOL/indent/尾换行·默认 json.dump 整件重写=churn 放大）。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十二批』节。
- [2026-09-27 16:3x r333 bm-b] 坑律（二十一批外迁·指针）：tick 对 git 危险窗禁止（fire :X0:02→commit 落点 :X2:5x）——同窗双批十六批同象双存照 r85 勘注先例。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十一批』节。
- [2026-09-27 16:5x r90 bm-c] 坑律（二十一批外迁·指针）：resolver 对 auto-merged 存档 stage blob 反封锁人工核验（auto-merge 非 UU 面 :1:/:2:/:3: stage 不存在）。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十一批』节。
- [2026-09-27 16:1x r89 bm-c] 坑律（二十一批外迁·指针）：stub-drop 变方案锚全量归档态（指针保留）+probe/resolver 产物统一 encode 字节级。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十一批』节。
- [2026-09-27 17:2x r91 bm-c] 坑律（二十三批外迁·指针）：S0 pull 共享滚动台账 stash→pop 必 UU——resolver 定侧源=git show HEAD:<path>+stash@{N}:<path>（:2:/:3: 经任何 git add 即灭）；解完才 add 且赶 :X0:02 tick 前；PS 引 stash@{0} 必单引号——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十三批』节。指针=results/_r91bmc_resolve_autofill.py。
- [2026-09-27 17:4x r339 bm-a] 坑律（二十三批外迁·指针）：共享 JSON 字节拼接编辑取侧/去尾字节必按 blob 尾态（autocrlf 工作树 CRLF 假象·v1 b[:-2] 留裸 CR+整件假 churn；正典=blob 字节重建+写后 --stat 核 churn）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十三批』节。
- [2026-09-27 17:5x r340 bm-a] 坑律（二十四批外迁·指针）：round_no 周期义务（5x HANDOVER 对账等）在撞车风暴快轮窗会静默漏做（R335 实证·R340 补核覆盖 R331-340 全窗）；正典=%5==0 轮 5x 与撞车解平级必做、已漏=次轮首补核注明欠账——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十四批』节。
- [2026-09-27 16:3x r333 bm-b] 坑律（二十一批外迁·指针）：tick git 危险窗扩至 :X3 后（post-commit fetch+push 对账尾）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十一』节。
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。
- [2026-09-27 17:3x r334 bm-b] 坑律（二十三批外迁·指针）：rolling-ledger union dedup 键族必含面实时间键（asof 键 ts-only 塌缩 2+2→1 实弹；正典=逐面键探+union 数对账+写回前三方 blob 复验）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十三批』节。指针=results/_r333bmb_push_resolve.py+_r334bmb_verify_regime.py。
- [2026-09-27 17:5x r335 bm-b] 坑律（二十五批外迁·指针）：tick add/stash 腿不受 r201 mid-rebase 护栏管辖（r335 三连击实弹；正典=动态 sides 正典重建+原子 add-continue-push+行锚定终验+危险窗后 reflog 定谳）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十五批』节。指针=results/_r335bmb_resolve.py+_r335bmb_probe_race.py。
