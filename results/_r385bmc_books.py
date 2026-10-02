# -*- coding: utf-8 -*-
# r385 bm-c closeout books: CODELY(pit+union) / round report / state / heartbeat(orders_ack carry) / HANDOVER 5x
import subprocess, json, os, time, datetime
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
NW = 0x08000000
now = datetime.datetime.now()
ts_full = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
ts_short = now.strftime('%Y-%m-%d %H:%M:%S')

def gout(args):
    return subprocess.check_output(['git'] + args, creationflags=NW)

# ---------- 0) small probes: waiting pool entry + gpu ----------
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
entries = pool.get('entries', pool if isinstance(pool, list) else [])
waiting = [(e.get('id'), e.get('status'), bool(e.get('park_note')), bool(e.get('defer_note'))) for e in entries if e.get('status') == 'waiting']
print('waiting_pool_entries:', waiting)
gpu_free = 4709
try:
    q = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], creationflags=NW, text=True)
    gpu_free = int(float(q.strip().splitlines()[0]))
except Exception as ex:
    print('gpu read fallback:', ex)
cpu_pct = 4.4
ram_gb = 12.2

# ---------- 1) CODELY: append pit line locally, then union with origin ----------
PIT = "[2026-10-02 22:1x r385 bm-c] 收口 commit 误托引擎 append commit=簿记四件滞留坑（r382 实弹·r385 治愈）：会话把引擎 batched append commit（仅含分片路径）当本轮收口推送并自证 0/0——state/心跳/轮报告/CODELY 从未入该 commit·滞留工作树 1.5h 不上 origin（下轮读数与 fleet 心跳面全陈旧）。连带收养补面：收养猝死会话在制活时令面 re-check 先于技术定性（本窗 W115 半冻结=r384 死会话在 O-2115 供给序令落地后仍按旧序推进的遗产——直接技术收编=把引擎火力烧向 CEO 已降优先的 N1 面；正解=撤编辑+存档+席位保留公示）。How to apply：①收口 commit 前 git diff --cached --stat 自证簿记四件在 staged 集；②收养半成品先重扫令台账——在制活方向可被新供给序令反转。"
PIT = PIT.replace('22:1x', now.strftime('%H:%M'))
codely_path = 'CODELY.md'
codely_bytes = open(codely_path, 'rb').read()
eol_c = b'\r\n' if b'\r\n' in codely_bytes[:2000] else b'\n'
if not codely_bytes.endswith(b'\n'):
    codely_bytes += eol_c
codely_bytes += PIT.encode('utf-8') + eol_c
open(codely_path, 'wb').write(codely_bytes)
print('CODELY pit appended, local bytes=%d' % len(codely_bytes))

origin_blob = subprocess.check_output(['git', 'show', 'origin/main:CODELY.md'], creationflags=NW)
o_lines = origin_blob.replace(b'\r\n', b'\n').decode('utf-8', 'replace').split('\n')
l_lines = codely_bytes.replace(b'\r\n', b'\n').decode('utf-8', 'replace').split('\n')
o_set = set(o_lines)
only_local = [l for l in l_lines if l and l not in o_set]
merged = [l for l in o_lines if l != ''] + only_local
union_bytes = ('\n'.join(merged) + '\n').encode('utf-8')
open(codely_path, 'wb').write(union_bytes.replace(b'\n', b'\r\n'))
print('CODELY union: origin_lines=%d only_local=%d result_bytes=%d (LF-blob space)' % (len([x for x in o_lines if x]), len(only_local), len(union_bytes)))

# ---------- 2) round report 2 lines ----------
R1 = ("2026-10-02T" + now.strftime('%H:%M:%S') + "+08:00 | r385 | watermark: 红（red=true·lane=runnable-work-idle-low-cpu·py_series 0.1/0.7/0·next_pick null——红牌定性=O-2115 供给优先序切换过渡窗：pool ready=0〔323 done+1 waiting〕+N1 已 park+探针 work-cand 面计入 open 未认领 T-146〔GM 会话在飞执行中·非真可烧批〕；整改=T-147/T-145 新方向 prereg 落地恢复池供给·10-09 开市前窗）｜当前活=r385 收口（W115 park+4 令回执+T-147 开票认领+簿记滞留治愈）｜最近实物=fleet/inbox/MSG-2026-10-02-2200-bmc-ALL-w115-park.md+results/_r385bmc_w115_parked.diff+fleet/tasks/T-2026-10-02-147-P1.json（本轮 commit 送达）｜下个里程碑=T-147 s1 深轴证据提取+s2 家族 prereg（10-09 前·验收 10-08）→ T-144(c) 协议+流水下沉 10-07 → 月界首考 10-31 ‖ 本轮主产：①W115 PARK per O-2115——死会话 r383/r384 遗产收养核验后令面反转：五面冻结编辑撤出（git restore --source=origin/main 三面·n1 selftest PASS〔腿收 W114〕+pf 9/9）+引擎不点火实证（21:58 tick W115 行消·queue=0 idle·face_bm-c.json）+席位保留 bm-c 公示（MSG-2200）+存档三件套（prereg PARKED 横幅〔锚=W114 落账值 merged mu −0.09291186715985847·K=248,720〕+22,244B diff+工具集三件）；②r382 簿记滞留坑治愈（其收口 commit 实为引擎 append commit 仅含分片路径→state/心跳/轮报告/CODELY 四件滞留工作树 1.5h·本轮全量重落+坑律入 CODELY）；③4 令回执（O-2100 捕获律接线在场核验=iteration_prompt 4 提及+库 E07/E08 双机活证据；O-2115 三线接令·T-147 线2 本司开票认领·T-145 bm-a 在飞让路；O-2124=City3D@bm-a 无本司义务；O-2135=GM T-146 在飞不认领防双头）；④T-147 同轮开票认领（O-2115 §一.2 深轴家族线：P3 +55~60% 67 笔面→家族 prereg·一出生即主考格·证据面 16cells+cont16+e1 清点入票） ‖ 验证证据：smoke 47/47 / S6 28 腿全 rc0（dualrun ZERO-DRIFT 51/3·scorecard/dscore/build_status 三面 L3 陈旧接管合法〔bm-a 心跳>20min·R31/r378 判例〕·fund_premium 车道幂等 no-op·国庆 paper 块诚实跳 r588 先例）/ D-19 MATCH 937A373D / orders 147/147 双扫零未回执 / attrition CLEAN（4 ledger）/ 自愈 4/4（loop pin=5 no-op·watchdog 重注册 22:03 首燃·双爪安装） ‖ 下轮指针：(a) T-147 s1 证据提取+REFINE_BENCH §2 排序变体表→s2 家族 prereg 起草（出场轴双件门+主考格内建·science_gates 共享库）；(b) T-144(c) 协议+流水下沉 10-07；(c) 红牌过渡窗观察（新方向批入池后自愈）；(d) 号码学披露=r383 已公开（W113 finalize 0fd20d1ff 署名）/r384 phantom（零公开输出）→本轮取 385 [via bm-c r385]")
R2 = ("2026-10-02T" + now.strftime('%H:%M:%S') + " | r385 | 本地未达 origin commit 数=3（9cb8ddb6c/61904cf56/a154dcbcc 全=GM 会话未推 commit·其 CAS 孪生已自达 origin〔5d234b3d7/5228c16f4/f7972fdb6〕·非本司产出禁代推；本司收口走外科直投不占本地 main）")
rr_path = 'round_reports-bm-c.md'
rr_bytes = open(rr_path, 'rb').read()
eol_r = b'\r\n' if b'\r\n' in rr_bytes[-300:] else b'\n'
if not rr_bytes.endswith(b'\n'):
    rr_bytes += eol_r
rr_bytes += R1.encode('utf-8') + eol_r + R2.encode('utf-8') + eol_r
open(rr_path, 'wb').write(rr_bytes)
print('round report: 2 lines appended, bytes=%d' % len(rr_bytes))

# ---------- 3) state-bm-c.json ----------
st = json.load(open('state-bm-c.json', encoding='utf-8'))
st['round_no'] = 385
st['last_round_at'] = 'r385'
st['last_round_ts'] = ts_short
st['updated'] = ts_full
st['cpu_pct'] = cpu_pct
st['idle_ram_gb'] = ram_gb
st['gpu_free_vram_mib'] = gpu_free
st['verify'] = ("r385: W115 PARK per O-2115 supply-priority (five-face edits unwound via git restore --source=origin/main; engine no-ignition verified: 21:58 tick W115 row gone, queue=0, idle; seat retained bm-c non-abandon, MSG-2026-10-02-2200-bmc-ALL published; estate archived: PARKED-banner prereg [anchors=W114 landed values] + 22,244B diff + toolset x3) + r382 books-stranding healed (closeout was the engine append commit carrying shard paths only -> state/heartbeat/round-report/CODELY re-landed this round; pit law -> CODELY) + 4 orders acked (O-2100 wiring verified live 4 mentions + E07/E08 library evidence; O-2115 lines taken: T-147 opened+claimed same-round, T-145 bm-a in-flight yielded; O-2124 City3D@bm-a no bm-c duty; O-2135 GM T-146 in-flight no OS claim) + T-147 deep-axis family prereg line opened+claimed + S6 28 legs rc0 (dualrun ZERO-DRIFT 51/3; scorecard/dscore/build_status L3 stale-takeover legal bm-a hb>20min; fund_premium lane idempotent no-op; Golden Week paper block honest skip r588) + smoke 47/47 + D-19 MATCH 937A373D + attrition CLEAN 4 ledgers + self-heal 4/4 (loop pin=5 no-op, watchdog re-reg 22:03, both claws installed) + watermark RED transition-window honest (pool ready=0, N1 parked, T-146 open-GM-executing counted as work-cand; remedy = new-family preregs T-147/T-145 restore pool supply by 10-09)")
st['did'] = "r385: W115 parked per O-2115 (edits unwound/engine idle/seat retained/estate archived); T-147 deep-axis family line opened+claimed; r382 stranded books re-landed; 4 orders acked"
st['current_task'] = "r385 wrap: surgical closeout push (books + park estate + S6 products); watermark RED transition-window disclosed (N1 parked, pool empty, new-family prep in flight)"
st['next'] = ("(r386)(a) T-147 s1 deep-axis evidence extraction (results/lowamp_p3/* 16cells+cont16+e1) + REFINE_BENCH sec.2 ranked variant table; "
             "(b) T-147 s2 family prereg draft from research/PREREG_TEMPLATE.md (alpha-mech four-choose-one + D6 same-family corr gate + exit-axis explicit gate [67-trade main judge, no naked default stack r301] + main-exam qualification at birth + science_gates shared lib, no hand-copied thresholds); "
             "(c) T-144(c) protocol+flow domain sinking due 10-07; "
             "(d) watermark RED transition-window observation (expect green when new-family batches enter pool); "
             "(e) T-143 month-exam prep 10-29; month-boundary first exam 10-31")
st['heartbeat_epoch_utc'] = int(time.time())
st['clock_read'] = ts_full
st['last_ts'] = ts_short
st['last_round'] = "2026-10-02 r385 bm-c: W115 park per O-2115 + T-147 opened/claimed + r382 books heal + S6 28 legs rc0 + smoke 47/47 + orders 147/147"
st['last_seen'] = ts_short
open('state-bm-c.json', 'w', encoding='utf-8', newline='\n').write(json.dumps(st, indent=1, ensure_ascii=False) + '\n')
print('state-bm-c.json written round_no=385')

# ---------- 4) heartbeat (carry orders_ack, r583 law) ----------
hb = json.load(open('fleet/machines/bm-c.json', encoding='utf-8'))
acks = hb.get('orders_ack')
if not isinstance(acks, list):
    acks = []
new_acks = ['O-20261002-2100-bm-c.md', 'O-20261002-2115-bm-c.md', 'O-20261002-2124-bm-c.md', 'O-20261002-2135-bm-c.md']
added = [a for a in new_acks if a not in acks]
acks.extend(added)
hb['orders_ack'] = acks
hb['cpu_util_pct'] = cpu_pct
hb['cpu_pct'] = cpu_pct
hb['cpu_idle_pct'] = round(100 - cpu_pct, 1)
hb['free_ram_gb'] = ram_gb
hb['ram_free_gb'] = ram_gb
hb['idle_ram_gb'] = ram_gb
hb['gpu_free_vram_mb'] = gpu_free
hb['gpu_vram_free_mb'] = gpu_free
hb['gpu_idle_vram_mb'] = gpu_free
hb['gpu_idle_vram_mib'] = gpu_free
hb['gpu_free_vram_mib'] = gpu_free
hb['round_no'] = 385
hb['updated_at'] = ts_full
hb['last_seen'] = ts_full
hb['last_seen_at'] = ts_short
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = ts_full
hb['health'] = 'ok'
hb['prod_lanes'] = ("r385: W115 PARKED per O-2115 supply-priority (N1 deprioritized; engine idle by design, transition window); fleet chain head = W114 finalize 615,348 K=248,720 (all landed); bm-c active line = T-147 deep-axis family prereg (O-2115 line-2, due 10-09); next N1 wave = W115 parked (resume conditions in MSG-2026-10-02-2200-bmc-ALL)")
hb['current_task'] = "r385 wrap: surgical closeout push; next = T-147 s1 deep-axis evidence extraction"
hb['activity_now'] = "S7 wrap (books healed from r382 stranding + park estate + closeout surgical push)"
hb['latest_artifact'] = ("fleet/inbox/MSG-2026-10-02-2200-bmc-ALL-w115-park.md + results/_r385bmc_w115_parked.diff + fleet/tasks/T-2026-10-02-147-P1.json (r385 22:1x; W115 park per O-2115 with full resumption estate; T-147 deep-axis family line opened+claimed)")
hb['next_milestone'] = ("T-147 deep-axis family prereg in pool by 10-09 open (evidence extraction next round first action); T-144(c) protocol+flow sinking 10-07; month-boundary first exam 10-31")
hb['verdict'] = ("healthy: W115 parked clean per O-2115 (engine no-ignition verified, seat retained, estate archived); watermark RED = transition window honest (pool ready=0 post-park, T-146 open-GM-executing counted as work-cand; remedy = T-147/T-145 new-family preregs restore supply); S6 28 legs rc0; smoke 47/47; self-heal 4/4; attrition CLEAN; orders 147/147")
open('fleet/machines/bm-c.json', 'w', encoding='utf-8', newline='\n').write(json.dumps(hb, indent=1, ensure_ascii=False) + '\n')
print('heartbeat written: orders_ack=%d (added %d)' % (len(acks), len(added)))

# ---------- 5) HANDOVER 5x window entry ----------
H5 = ("- [2026-10-02 22:1x r385 bm-c] HANDOVER 5x window entry (window r336-r385, OVERDUE-BACKLOG DISCLOSED: r340..r380 5x stamps never filed -- window carried the never-dry engine wave era + crash chains r373/r383/r384 + books-stranding heal; per r420/r500/r335 precedent no backfill fabrication, single window covered compactly; bm-a r510/r525/r590/r594 + bm-b r525/r595 rows cross-read for their lanes). LEDGER LIVE-READ ANCHOR THIS ROUND = 615,348 (results/perpetual_faces/n1_w114_results.json trials_ledger.total, live-read r385; window delta from the r335 stamp anchor 415,148 = +200,200 = 91 N1 engine waves x 2,200 fleet-wide W24..W114, per-owner attribution per bm-a/bm-b owner rows; bm-c-owned finalized in window = W26/W29/W32/W37/W39/W41/W42/W43/W46/W50/W51/W52/W53/W58/W60/W63/W66/W69/W71/W78/W80/W83/W85/W88/W92/W99/W102/W105/W108/W113 [W113 finalize landed 0fd20d1ff by dead r383, SS5 4/4 PASS]). THIS-WINDOW bm-c PRODUCTS (r336-r385): (1) never-dry wave line one-pass chains freeze+ignite+burn+finalize (r576 anchor-roll law family; D-20261002-05 sec.4 jump-semantics pin co-signed; seat MSG first-push r565 law; r589 reset-FF-reland loops over appender/origin races). (2) T-144 claws: (a) pre-push ownership claw three legs DONE r367 71e0e9b4d; (c) pit-domain splits DONE = git 49 entries (r369) + pool 16 (r373) + data 5 (r380) -> research/pit-{git,pool,data}.md byte-verified; engine domain bm-a r585; remaining protocol+flow due 10-07. (3) T-134 s2 multicore conversion chain (census 38->30). (4) crash-adoption chain r373/r383/r384 + r385 W115 PARK per O-2115 supply-priority (five-face edits unwound origin-authoritative, engine no-ignition verified 21:58 tick, seat retained, estate archived = PARKED-banner prereg + 22,244B diff + toolset x3; MSG-2026-10-02-2200-bmc-ALL). (5) r382 books-stranding pit healed r385 (closeout was the engine append commit, shard paths only; books re-landed + pit law -> CODELY). (6) T-147 opened+claimed r385 (O-2115 line-2 deep-axis P3 +55~60% 67-trade face -> family prereg, main-exam qualification at birth, exit-axis double gate, due 10-09). Maintenance per rounds: smoke 47/47 chains; S6 28-33 legs rc0 chains (dualrun ZERO-DRIFT streak to 51/3; Golden Week paper-block honest skips r588); attrition CLEAN chains; orders dual-scan zero-pending chains (147/147 after O-2100/2115/2124/2135); D-19 MATCH chains (937A373D). NEXT 5x = round 390 bm-c. Pointers: T-147 s1 evidence extraction -> s2 family prereg draft (REFINE_BENCH sec.2 axes, 10-09 open-market deadline, 10-08 acceptance); T-144(c) protocol+flow sinking 10-07; T-143 month-exam prep 10-29; month-boundary first exam 10-31; W115 parked (resume conditions in MSG-2026-10-02-2200-bmc-ALL); watermark RED transition-window face (pool ready=0 post-park + T-146 open-GM-executing counted as work-cand -- honest note each round until new-family burns resume).")
H5 = H5.replace('22:1x', now.strftime('%H:%M'))
h_path = 'research/HANDOVER.md'
h_bytes = open(h_path, 'rb').read()
eol_h = b'\r\n' if b'\r\n' in h_bytes[-300:] else b'\n'
if not h_bytes.endswith(b'\n'):
    h_bytes += eol_h
h_bytes += H5.encode('utf-8') + eol_h + eol_h
open(h_path, 'wb').write(h_bytes)
print('HANDOVER 5x entry appended')
print('BOOKS DONE')
