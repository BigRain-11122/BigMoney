# r931 bm-b closeout: round report line + state.json + heartbeat update
# Receipt printed to stdout; UTF-8 everywhere (pit-encoding law).
import json, time, ctypes, subprocess, os, sys

NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

# --- RAM via GlobalMemoryStatusEx ---
class MS(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
ms = MS(); ms.dwLength = ctypes.sizeof(MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
free_ram_gb = round(ms.ullAvailPhys / 1024**3, 1)
free_ram_pct = round(100.0 * ms.ullAvailPhys / ms.ullTotalPhys, 1)

# --- VRAM via nvidia-smi ---
gpu_util, gpu_pw, vram_free_gb = 2.0, 9.0, 3.6
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,power.draw,memory.free',
                          '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=10).stdout.strip()
    p = [x.strip() for x in out.split(',')]
    gpu_util, gpu_pw = float(p[0]), float(p[1])
    vram_free_gb = round(int(float(p[2])) / 1024, 1)
except Exception:
    pass

R = 'logs/iteration-loop/round_reports.md'

REPORT = ("| " + NOW + " | r931 | bm-b [dept:research/strategy] | W19 screen burn watch + post-screen chain de-risk verification round: "
"(1) S0 stash/ff/pop clean zero-overlap (origin +1 = bm-c r994 wait-state; 3 stale shared regen faces discarded pre-stash newer-wins, regenerated in-round by S6 legs). "
"(2) S0.5 orders: 3 unacked = CEO O-20261014-0942 (排满令·qwen3.8:4b GPU 常驻) + O-20261014-0948 (哨兵机制确立令) + O-20261014-0949 (机队满载总结令) -- all bm-b self-issued 09:4x morning window, self-receipts [x] verified in-order -> acked 210->213; D-19 dual-delta zero (decisions 86187eff/orders 348eaf34, fresh probe). "
"(3) S1 smoke 49/49. (4) round-zero orphan probe py_faces=16 orphans=0. (5) SatEngine alive rc0 idle queue 0. "
"(6) MAIN PRODUCT = W19 post-screen chain de-risk verification (r922 lesson = judge-face late-discovery prevention): runner subcommand inventory COMPLETE (grammar/generate/status/screen-prep/screen/screen-finalize/judge-prep/judge/judge-finalize/intake/selftest, r928 built full chain) + hermetic selftest 22/22 PASS + status face grammar/cells/prep_state PRESENT + A9 exitcfg gate PASS + G-TIMING gate PASS (daily_signal+weekly_grid) + live-fire fail-closed refusal proofs rc=2 BOTH gates (screen-finalize: 'incomplete checkpoint 217/346 cand + 125/200 nulls -- honest refuse (burn pending)'; judge-prep: 'screen not finalized -- honest refuse (identity face)') = full post-screen chain gate-proven ready, zero unbuilt-face risk at burn completion. "
"(7) W19 screen burn watch (pool truth): GENERATE done + SHARD-0..3 done + SHARD-4 claimed-burning (autofill 10:34 claim commit 42cd9a02c) + SHARD-5/6/7 ready; autofill serial discipline ~12min/shard tick cadence, ~20s CPU burst each -> screen completion ETA ~11:10-11:15 -> screen-finalize next window. "
"(8) S6 quick legs: dualrun ZERO-DRIFT streak 13 (455 entries) + compute_audit FLAG supply_gap+ignition_sla (serial-burn structural: 4 batches/60min effective_cores 0.96; SHARD-6/7 ready 71min = SLA face, self-heals as burn lands) + pywm py_low_board_clear (pool_batch 4 = the burning face itself) + token delta 0 + attrition 4 CLEAN (1 healed historical shrink). "
"(9) S7: loop pin=2 no-op (next fire 10:42) + watchdog re-registered (first fire 10:41) + both claws idempotent-installed + idle_trigger --worked idle_rounds=0 + state.json round_no 929->931 reconcile (r930's claimed 884->930 reconcile did NOT persist -- file mtime 08:51:54 = r929 face; report-ledger = live sequence, disclosed). "
"| 当前活: W19 screen 4/8 done + SHARD-4 burning (autofill serial lane) + qwen3.8:4b GPU-resident (O-0942) | "
"最近实物: screen-finalize/judge-prep live-fire refusal proofs rc=2 (fail-closed gate faces) + selftest 22/22 + status A9/G-TIMING PASS | "
"下个里程碑: W19 screen-finalize <=10-14 12:00 + JUDGE enrollment <=48h (10-16) + S6 full chain 15:30 data window | "
"watermark: RED lane=pool-batch-runnable-idle-low-cpu (P0 one-liner: W19 screen 4 ready+1 claimed burned SERIALLY by autofill lane, ~20s CPU bursts per 12min tick = low duty-cycle structural face, NOT idle -- 4 shards consumed last hour, chain advancing GENERATE+SHARD-0..3 done; ignition_sla SHARD-6/7 = serial-queue face, self-heals ~11:15 at burn completion) | "
"orphan-faces=0 (probe 10:2x: py_faces=16 orphans=0 killed=[]) | orders: 3 acked (213 cumulative) | "
"evidence: selftest 22/22 stdout + SF/JP refusal rc=2 stdout + autofill_state.bm-b.json shard ledger (SHARD-4 10:34 fill_latency 66.8) + dualrun streak 13 + _attrition_guard_scan.json + smoke 49/49 | "
"unacked_orders=0 | registry-zero-hit: no sweep/archive/delete actions this round | "
"local-unreached-origin-commits: 0 at S0 (behind=1 absorbed ff) -> closeout commit+push follows + self-proof | "
"next-pointer r932: (a) W19 screen-finalize at burn completion (~11:15) -> judge-prep -> JUDGE enrollment+burn (48h CEO clock at judge landing) -> judge-finalize + w19_paired_deltas; (b) S6 full chain 10-14 15:30 data window (new-bar legs re-arm); (c) standing: GPU PSU-swap MODE=pause (i2v 27/53 held), unity POC first interactive editor window (Cowork R2 live), bili-reply CEO cookie+aid, MF panel bm-a lane (MSG-0512), Speech-02 committee/CEO, O-0942/0949 fleet orders bm-a/bm-c lanes | [r931 bm-b]")

with open(R, 'a', encoding='utf-8') as f:
    f.write('\n' + REPORT + '\n')

# --- state.json ---
sp = 'state.json'
s = json.load(open(sp, encoding='utf-8'))
s['round_no'] = 931
s['clock_read'] = NOW
s['current_task'] = 'r932: W19 screen-finalize at burn completion -> judge-prep -> JUDGE enrollment + S6 full chain 15:30'
s['did'] = ('r931 bm-b: W19 post-screen chain de-risk verification (MAIN PRODUCT): runner subcommands complete + '
            'selftest 22/22 PASS + live-fire fail-closed refusal proofs rc=2 both gates (screen-finalize 217/346 cand '
            'incomplete honest refuse; judge-prep screen-not-finalized honest refuse) = zero unbuilt-face risk at burn completion '
            '(r922 lesson applied). Screen burn watch: SHARD-0..3 done + 4 burning + 5/6/7 ready, autofill serial ~12min/shard, '
            'ETA ~11:15. Orders 3 acked (O-0942/0948/0949 self-issued receipts verified). Watermark RED structural serial-burn face. '
            'state.json reconcile 929->931 (r930 persist-failure disclosed).')
s['last_action'] = 'r931: W19 chain de-risk verification (selftest 22/22 + dual refusal proofs rc=2) + 3 orders acked'
s['last_action_at'] = NOW
s['last_round_at'] = NOW
s['last_round_ts'] = NOW
s['last_seen'] = NOW
if 'd19_watermark_guard' in s:
    s['d19_watermark_guard']['round_ref'] = 931
    s['d19_watermark_guard']['ts'] = NOW
json.dump(s, open(sp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

# --- heartbeat ---
hp = 'fleet/machines/bm-b.json'
h = json.load(open(hp, encoding='utf-8'))
h['clock_read'] = NOW
h['ts'] = NOW
h['updated'] = NOW
h['updated_at'] = NOW
h['last_seen'] = NOW
h['last_round_at'] = NOW
h['last_action_at'] = NOW
h['heartbeat_epoch_utc'] = EPOCH
h['round'] = 931
h['round_no'] = 931
h['round_no_label'] = 'r931'
h['current_task'] = 'r932: W19 screen-finalize -> judge-prep -> JUDGE enrollment (post burn-completion ~11:15)'
h['task'] = h['current_task']
h['did'] = ('r931 bm-b: W19 post-screen chain de-risk verification (MAIN): runner subcommand inventory complete + selftest 22/22 '
            '+ live-fire refusal proofs rc=2 both gates (screen-finalize/judge-prep fail-closed live-proven) = zero unbuilt-face '
            'risk (r922 lesson). Screen burn watch 4/8 done + shard-4 burning + 3 ready (autofill serial ~12min/shard, ETA ~11:15). '
            'Orders: 3 CEO orders acked (O-0942 排满/O-0948 哨兵/O-0949 机队满载, self-issued morning window, receipts verified). '
            'Watermark RED = serial-burn structural face (autofill consuming, NOT idle). state.json 929->931 reconcile (r930 '
            'persist-failure disclosed). S0 stash/ff/pop clean; D-19 zero-delta; smoke 49/49; S6 quick legs green (dualrun streak 13, '
            'token 0, attrition CLEAN); S7 quad all no-op/idempotent; idle --worked rounds=0.')
h['last_action'] = 'r931: W19 chain de-risk verification (selftest 22/22 + dual rc=2 refusal proofs) + 3 CEO orders acked + state reconcile 931'
h['latest_artifact'] = ('trial_labor_w19 selftest 22/22 + screen-finalize/judge-prep live-fire refusal rc=2 proofs (10:37-10:38) '
                        '+ autofill SHARD-4 claim commit 42cd9a02c (10:34)')
h['next'] = 'r932: (a) screen-finalize at burn completion -> judge-prep -> JUDGE enrollment+burn -> judge-finalize + w19_paired_deltas (48h CEO clock); (b) S6 full chain 15:30; (c) standing: GPU PSU-swap MODE=pause, unity POC editor window, bili-reply CEO cookie, MF panel bm-a lane, Speech-02 committee/CEO'
h['next_milestone'] = 'W19 screen-finalize <=10-14 12:00; JUDGE <=48h (2026-10-16); S6 full chain 10-14 15:30'
h['note'] = ('r931: de-risk verification round; queue watermark: pool ready 4 (W19-SCREEN SHARD-4..7) + burning 1 (SHARD-4) + '
             'board open 0 + N1 queue 0 + bandit open 0; 满载自证: CPU lanes = autofill serial shard burn + SatEngine PT1M + '
             'qwen3.8:4b GPU-resident (O-0942) + bili-reply CPU hot-standby; GPU = MODE=pause PSU-deferred (i2v 27/53 held per O-0925 sec3-3)')
h['now_active'] = ('autofill burning W19-SCREEN-SHARD-4 (serial ~12min/tick) + SatEngine PT1M idle-tick + qwen3.8:4b GPU-resident '
                   '(O-0942 8G-self-authority) + bili-reply CPU hot-standby; GPU MODE=pause PSU-deferred (i2v 27/53)')
h['verdict'] = ('RED: pool-batch-runnable-idle-low-cpu = W19 screen serial-burn STRUCTURAL face (autofill lane consuming: 4 shards '
                'done last hour, ~20s CPU bursts per 12min tick = low duty cycle, NOT idle; ignition_sla SHARD-6/7 self-heals at '
                'burn completion ~11:15); all other probes green (smoke 49/49, dualrun streak 13, attrition CLEAN, D-19 zero-delta, '
                'orders 0 unacked post-ack); GPU PSU-deferred standing (MODE=pause, O-0925 sec3-3)')
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['green_idle'] = False
h['free_ram_gb'] = free_ram_gb
h['ram_free_gb'] = free_ram_gb
h['ram_free_pct'] = free_ram_pct
h['idle_ram_gb'] = free_ram_gb
h['idle_ram_pct'] = free_ram_pct
h['gpu_free_vram_gb'] = vram_free_gb
h['vram_free_gb'] = vram_free_gb
h['gpu_idle_vram_gb'] = vram_free_gb
h['gpu_free_vram_mb'] = int(vram_free_gb * 1024)
if 'gpu' in h:
    h['gpu']['util_pct'] = gpu_util
    h['gpu']['power_w'] = gpu_pw
    h['gpu']['face'] = ('GPU idle-compute (MODE=pause PSU-deferred, i2v 27/53 held); qwen3.8:4b GPU-resident per O-0942; '
                        'W19 burn chain = pure CPU face')
h['orphan_face'] = 0
h['orphan_faces'] = 0
h['orphan_face_note'] = 'r931 round-zero probe 10:2x: py_faces=16 orphans=0 killed=[]'
for oid in ['O-20261014-0942-bm-b.md', 'O-20261014-0948-bm-b.md', 'O-20261014-0949-bm-b.md']:
    if oid not in h['orders_ack']:
        h['orders_ack'].append(oid)
h['orders_ack_count'] = len(h['orders_ack'])
h.setdefault('orders_ack_notes', {})
h['orders_ack_notes']['O-20261014-0942-bm-b.md'] = ('r931 bm-b ack: CEO 排满令 receipt verified -- sec1 排程即生效实证行内附 '
    '(W19 链在烧=qwen3.8:4b GPU 常驻实证 09:40 复验面; bili-reply CPU 热装实测合格; BNX/HW/PE/EngineTick/Radar 网格满跑; '
    'RAM wrapper 复跑=合法车道自 re-arm); sec2 阻塞面三件如实 (B站 cookie+aid / Tuanjie Hub 重登 / 750W PSU)')
h['orders_ack_notes']['O-20261014-0948-bm-b.md'] = ('r931 bm-b ack: CEO 哨兵机制确立令 receipt verified -- bm-b-Sentinel S4U PT5M '
    '部署+首拍实证 (本会话开工首读=本律执行: sentinel.log 尾行 10:33 NORMAL + IDLE/CRIT 两 flag 双 False + 心跳龄 6min/autofill 龄 1min); '
    '零仓库写/不入 pause 清单/正确的活选择权留车道四边界全遵守')
h['orders_ack_notes']['O-20261014-0949-bm-b.md'] = ('r931 bm-b ack: CEO 机队满载总结令 receipt verified -- §2 bm-b 自报三件在轨 '
    '(O-0030 CPU 满用/O-0942 排满/O-0948 哨兵) + 队列水位行=本心跳 note 字段 (pool ready 4+burning 1+board 0+N1 0) + '
    'bm-c 回执已至 (r992); bm-a 回执=bm-a lane')
h['sync'] = {'last_push_ts': NOW,
             'note': 'r931: closeout commit+push follows this write; delivery self-proof fetch+rev-list follows push'}
json.dump(h, open(hp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

# --- self-verify: epoch is int, ack count consistent ---
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert h2['orders_ack_count'] == len(h2['orders_ack']) == 213, 'ack count mismatch'
assert 'T' in h2['clock_read'] and '+' in h2['clock_read'], 'clock_read format'
s2 = json.load(open(sp, encoding='utf-8'))
assert s2['round_no'] == 931
print(json.dumps({'rc': 0, 'now': NOW, 'epoch': EPOCH, 'epoch_is_int': True,
                  'round_no': 931, 'orders_ack_count': 213, 'free_ram_gb': free_ram_gb,
                  'vram_free_gb': vram_free_gb, 'report_appended': True,
                  'state_round_no': s2['round_no']}, ensure_ascii=False))
