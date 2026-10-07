"""r831 closeout legs: pit direct-write + round report line append (fresh read-modify-write, r619 law)."""
import io, os, datetime

now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')

# --- Leg 1: pit direct-write to pit-engine-finalize.md (engine domain, pre-finalize face) ---
PIT = 'research/pit-engine-finalize.md'
entry = (
"\n- [2026-10-07 15:5x r831 bm-a] **引擎自燃分片带语义=闭区间标注+左闭右开烧录（W175 首遇·r752 三恒等门判读修正）**："
"引擎 tick 自燃波的分片件 a_range/b_range 写 [start,end] 闭区间标注而烧录语义=左闭右开 [start,end)"
"（families.n=真值烧录数；相邻片共享标注边界点、烧录去重——span 宽度和恰比 families.n 每片多 2）。"
"r752 门若按闭区间 naive 判读 Σspan=2012+212≠2000+200 假红；正法=①Σfamilies.n==A 2,000/B 200"
"②Σaudit.n_backtests==2,200③半开 tiling 判据（首片 x0==0/末片 x1==N/相邻 y0==x1）。"
"科学面幂等重烧恒等实证（shard-10 三烧 audit.elapsed 12.5/12.9/12.4 差异=runtime 元数据·冻结字段逐项恒等=确定性自保护）。"
"How to apply：引擎烧录波 pre-finalize 三门一律按半开语义判读；会话手工跑的历史波（W165 判例）保持 +1 恒等判读——两形态判别=families.n 与 span 宽度差。\n"
)
src = io.open(PIT, encoding='utf-8', newline='').read()
assert '引擎自燃分片带语义' not in src, 'already written'
before_sz = os.path.getsize(PIT)
io.open(PIT, 'a', encoding='utf-8', newline='').write(entry)
after_sz = os.path.getsize(PIT)
print(f'pit direct-write: {PIT} {before_sz}->{after_sz}B (entry {after_sz-before_sz}B, line {30720}B: {"OK" if after_sz<=30720 else "OVER"})')

# --- Leg 2: round report line (bm-a round ledger, append-only) ---
RR = 'round_reports-bm-a.md'
line = (
f"\n{now} | r831 bm-a W175 判决批全链收口+rebase 治愈窗 (dept:研究/工程/舰队) | [watermark verdict: 绿 red=false; satengine alive rc0 queue0 idle 12/12 burned] | "
"当前活: S0 rebase 中间态治愈（r825 族 6 面 UU/AA：state/face deep-ts origin-freshest 15:42:05 胜 local 15:41:05+ledger/pool_core live-wins 超集验+history 三方 union 131 行剔 3 行标记残渣+shard-10 三侧幂等恒等科学面零伤；r787 原子批 add+continue 收口 f9b27a258）→ W175 pre-finalize 三恒等门 GREEN（半开 tiling 语义首遇判读修正=r831 新坑律直写 pit-engine-finalize.md）→ finalize one-pass ledger 788,212+2,200=790,412 EXACT/K 382,920 EXACT/skill_line 1.1845→1.1844（K-lift -0.0001）→ §5 四预键全过（|Δmu| 0.0031<0.02/sigma -0.0111%<±10%/A p95 -0.0215<0.05/K-lift -0.0001≤±0.02）→ §7/§8 机械回填（9+/2- 删除恰=占位两行=冻结面零改；三门回执 _r831bma_w175_three_gate.json） | "
"最近实物: results/perpetual_faces/n1_w175_results.json（15:57 finalize one-pass·账本 790,412 EXACT）+ sec7/8 回填件 research/PERPETUAL_N1_W175_PREREG.md | "
"验证: r776 账本自证 PASS（head 指本批件）+ 缺省 selftest 复绿（r522）+ smoke 48/48 + S6 30 腿全 rc0（黄金周 no-op 族诚实+dualrun streak 51 ZERO-DRIFT+compute_audit 旗 supply_gap/supply_floor 如实录+watermark py_low_board_clear 板净合法 idle）+ attrition CLEAN + S7 四件套绿（IterationLoop 针位 8 no-op/LoopWatchdog/双 claw 在位） | "
"计分: 2（能跑能看实物=W175 判决批收口：finalize 产物+三门回执+prereg 回填；S0 rebase 治愈=引擎面恢复）| 宝藏捕获问: 半开分片带语义判读修正=新方法论知识已入域件（判决批收口步履行·零新宝藏零新方法[nulls-deepening 例波]） | "
"下轮指针: r832=W176 席位链（probe→seat MSG→freeze 面探针→buildgen E41 血统·冻结窗禁手抄 43KB）+ 复市 10-08 数据链首刷（golden-week guard 解除面）+ O-1207 题材批 48h 窗 10-08 12:07 首版交付检查 | 本地未达 origin commit 数: 0（收尾 commit+push+fetch 复核） [r831 bm-a]\n"
)
src2 = io.open(RR, encoding='utf-8', newline='').read()
io.open(RR, 'a', encoding='utf-8', newline='').write(line)
sz2 = os.path.getsize(RR)
print(f'round report line appended: {RR} now {sz2}B')
