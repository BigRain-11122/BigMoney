## Codely Structured Memories
### User
- [2026-09-24 16:07:32] CEO 最高判据宣言「实战出真知」（2026-09-24 原话「对，不管什么玩意，实战出真知！」·2026-09-24 系列令的元哲学）：一切策略/因子/理论/外部方法论的最终裁判=实战数据（真实历史行情重演+当前市场模拟+前向纸盘），理论漂亮度、来源光环（学术/名库/民间经验）、叙事合理性一律不作数。与既有北极星「未回测=未测量」同源但更强：回测也要是「实战级」的（海量虚拟时点+指定起点窗+成本压测），不是单次历史曲线。How to apply：呈报只给实战数字与结论；对任何新策略/外采方法的评估先问「实盘级检验过没有」；叙述性框架（如 V3/V4 系统设计类文件）在 CEO 面永远次于跑出来的数字。（R156 热冷整编时自 09-24 批单条热恢复——User 节元律不随批归档；归档侧迁移记录留痕。）
### Feedback
### Project

### Reference
- 冷层指针：流水型条目（轮报告定案/执行记录/让路裁定）按 D-20260924-01 月度整编至 research/memory-archive/<YYYYMM>.md，全量留 git，检索按日期段。
- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十三批』节。

- [2026-09-27 22:3x r360 bm-a] 坑律：rolling-ledger union 解方禁自造 cap 截留（r360 实弹：resolver 发明 cap=max(len) 把 201+201 截成 201 静默丢最老行 vs 正典 |A∪B|=202——r85 生产者滚动窗律=反假丢旗 adjudication 非截留许可、r344 先例 236 全留；修正窗=推前 amend 补行+resolver 去 cap；滚动窗归生产者写回面非 resolver）——指针=results/_r360bma_resolve.py。
- [2026-09-27 23:3x r113 bm-c] 坑律：认领动作=fetch 紧贴认领原子窗（r239 律实弹第三犯：S0 22:50 pull『already up to date』后经 3 分钟勘察窗才认领，窗内 bm-b 22:49:09 认领提交已落 origin=本机按陈旧快照盲领 T-94→push 撞锁→§4 后到让路，整轮 s1 产物移侧支；正典=fetch+board 复核+claim+push 一气呵成零勘察间隙，调研一律认领后做；让路处置=产物保全侧支 machine/<id>-r<N>+MSG 移交回执禁裸弃）。指针=origin/machine/bm-c-r113+MSG-2261。
- [2026-09-27 23:2x r347 bm-b] 坑律：census 门必须绑定与 binding cutoff 同栅格的机检冻结枚举（r347 实弹：TRIAL_LABOR_W1 起草面引 t22 记录 legacy=1,255 系 09-23 栅格口径，本波 09-22 binding 下重枚举「逐位==1255」=构造性假红未跑先知；正典=同栅格机检冻结枚举整体 import 禁重实现——P-5C 栅格 EVIDENCE_CUTOFF_GRID=2026-09-22+FROZEN_CENSUS 两腿 L{1253,1127,875}/D{3104,2978,2726}，零跑修正案 §9.3 留痕·G-V3 虚假前提同族）——指针=research/TRIAL_LABOR_W1_PREREG.md §9.3。



- [2026-09-27 23:5x r116 bm-c] 坑律：compute_audit 等共享 JSON 的 blob 血统混行（bm-a API 直构上传 blob 带 CRLF·本机正常 git add 归一 LF·autocrlf=true）→ 风暴 rebase 对撞时整件假 churn（11.7k 行 diff=换行符翻转非数据损坏）；正解=①churn 面先按内容判（union 行数对账+JSON parse+键序 indent 与 producer 对齐）②取侧走 LF 归一面保本树干净（CRLF blob 经 --no-filters 落地会造本机永脏假象=慢性脏树面）③写后 --stat 核 churn 但区分假 churn（换行翻转）与真损坏（裸 CR/尾字节）——r339 尾态律补面。指针=results/_r116bmc_resolve_storm.py


- [2026-09-28 00:3x r118 bm-c] 坑律：SEED_REGISTRY 并发登记同名键=python dict 重复字面键静默 last-win（T-95 实弹：bm-c 20261002 与 bm-a 20284110 两机同窗各自 commit 登记 "decision_chain_v2"→风暴 rebase automerge 双条目并存 L676/L971→运行时 20284110 静默胜出·零报错零冲突标记）——正典=①认领/采纳裁决后凡涉 SEED_REGISTRY 键改动，commit 前 rg '<键名>' 计数==1 断言②rebase automerge 后同断言复跑③双条目既成=零跑修正窗去重留痕（本例 a3·commit 6957668d）。同轮 owner 采纳裁决首例闭环（T-95：bm-a 侧支采纳为正典+§9 零跑修正三件 a1 YELLOW0.65 正典逐字/a2 checkpoint 车道/a3 种子归一·零格已烧窗合法·MSG-2261 先例），详指针=research/DECISION_CHAIN_V2_PREREG.md §9+research/DECISION_CHAIN_LEDGER.md 变更日志 00:2x 行。

- [2026-09-28 00:2x r349 bm-b] 坑律：轮中共享 JSON 编辑可被长跑 tick 进程陈旧内存模型写回静默吞掉（r359 族新面）——r348 实弹：会话 00:01:4x 落池 TRIAL-LABOR-W1-SCREEN（81 条目自证过），00:00:01 起跑的 autofill tick 持 80 条目旧模型、00:02:49 keepalive 写回+自提交 c52a056a 覆盖吞行，00:03:36 收尾 add 见池净=丢失不可见于当事会话。正典=①有自提交写者（tick/watchdog）在飞的文件，编辑后必须同窗立即定向提交封死竞态（或收尾 commit 前对实文件 watch-face 复验——r359 律补面：脚本落盘自证≠提交时盘面仍在）；②诊断=git log --all -S 全分支缺席证明+tick 提交时间线对齐；③恢复=幂等收养脚本重跑（断言守卫）+竞态窗验证（psutil 验 tick 退场+下 tick 时钟）后即提交推送。指针=results/_r348bmb_pool_entry.py 幂等重跑+commit 49275797+round_reports r349。
- [2026-09-28 00:5x r366 bm-a] 坑律：rolling-ledger union 行身份键必须 per-face 探测禁硬编码（r319 实弹第二例：regime_state history 行键=asof 日期非 (ts,machine)，硬编码 → 全行坍缩 ident=(None,None) → 身份并集断言 fail-closed 当场拦住=零丢失校验链承重实证；正典=同身份碰撞新侧行胜+断言用身份级 |A∪B|==identities 而非行数≥max；另 blob 探针失败先 repr 自检参数串——本例 f-string ':2:'+':path' 双冒号=git show 静默读错路、险先误归因并发）。指针=results/_r366bma_resolve.py（15 UU 解面：快照族全取新+孪生同侧+autofill 47 恒等合并 tie 取 HEAD+compute_audit 202+201→203 身份并集）。
- [2026-09-28 00:5x r350 bm-b] 坑律：append-only 台账 md 行新增时 replace 工具的 old_string 锚禁含既有数据行——new_string 必须旧行+新行双含（r350 实弹：TRIAL_GRAMMAR_LEDGER 补 MASS_TRIAL_W1 行时误把新行整行替换掉 TRIAL_LABOR_W1 旧行，当窗自捕双行复原零外泄——r29 bm-c 账本追加三查律的 replace-工具新面；正典=台账补行 old_string 只锚表头/相邻行界，写后立即目验全行在场）。指针=results/_r350bmb_resolve.py 同窗+commit 9d3f2de3 收尾前置窗。

- [2026-09-28 00:5x r119 bm-c] 坑律：①python -c 内联命令经 PS 传参，中文字面量走命令行 GBK 编码面=mojibake 炸点（read_parquet columns 中文名匹配失败首症；本机 lhb_detail.parquet 列名「上榜日/龙虎榜净买额」与 market_clock reader 字面量实为一致——probe 失败纯属 -c 传参编码非 parquet 血统漂移）；正典=中文面探针一律走 UTF-8 脚本件+落盘读（read_file），控制台显示 mojibake 禁当源码真值引用。②rebase 冲突 merge.conflictStyle=diff3 时 <<<<<<< HEAD 段内含 ||||||| 基段=三段式（单段解析器把基段混入 HEAD 侧、JSON 'Extra data' 首症）；正典=三段分治解析（HEAD/base/mine 各自 JSON 化）+共享池=身份并集禁截留（r344/r360 律承重·81+83→83 对 base 零丢失断言）+tick=最新时戳侧（r349 分类律）。指针=results/_r119bmc_pool_union.py+results/_r119bmc_af_tick.py。

- [2026-09-28 01:1x r120 bm-c] 坑律：tick 陈旧模型回写吞行可命中**他机已认领在途件**（r348/r349 族第二例·新面）：bm-b tick b5be80cd 整件重写把 DECISION-CHAIN-V2 两池件连同 bm-a 00:50:05 sleeve shard 认领字段一并吞掉（零 launch 记录=吞非消费）——恢复禁盲加回：须从 last-known-good blob（8a1f8613）逐字收养保全他机 claim（盲加回=复置认领→他机双跑/丢跑）；诊断=多版本身份集对账（4756eca2/8a1f8613/b5be80cd/HEAD 计数+MISSING-DIFF 扫描）×零 launch 记录交叉证；正典=幂等收养脚本（断言守卫·在场即 no-op）+同窗定向提交封竞态+双机通报（认领机=claim 保全可续跑·吞行机=tick 读新面纪律）。指针=results/_r120bmc_pool_adopt.py+results/_r120bmc_resolve_storm.py+commit 9c0c3a8b。
- [2026-09-28 01:2x r368 bm-a] 坑律：git rebase --continue 拒绝报「You must edit all merge conflicts and then mark them as resolved using git add」但 git ls-files -u 为空、diff --cached --check 零冲突标记时——真实拦截者=任意 unstaged 改动（REBASE_MERGE continue 路径的 has_unstaged_changes sanity check 文案误导，与冲突面无关）；正典=同窗把全部 unstaged 件 git add（含他写者 tick 态收养=r348 零丢失律）后再 continue，勿死磕冲突面勿 abort（r220 律）。r368 实弹：tick 01:00:01 写后 continue 连拒 3 次，add autofill_state 后即过。指针=results/_r368bma_resolve.py。
- [2026-09-28 01:2x r368 bm-a] 坑律：tick 自提交 keepalive（r290 腿）已成池面跨机常设写者——bm-b tick 陈旧模型写回（b5be80cd 00:52:51）吞了其祖先 8a1f8613 在册的 2 个 T-95 s2 池条目（含 claimed-in-flight 认领行），r348 家族跨机新面（r349 实例=本机 tick 吞会话编辑；本例=他机 tick 吞本机 tick 的 claim）；防御=认领后对任何后续 keepalive 提交做 claim 存活对账（git show 池面 diff 计数），吞失=r312 union 收养恢复；双源同谳实证=bm-c r120 verbatim 收养与 bm-a r368 stage2/3 union 同窗独立恢复收敛 83=83=83。指针=results/_r368bma_resolve.py+commit 1e0c5289。
