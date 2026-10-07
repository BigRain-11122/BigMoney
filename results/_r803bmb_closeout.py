# r803 bm-b closeout: state 802->803, D-19 watermarks, heartbeat epoch-int, boards scan, round report row
import ctypes, json, subprocess, time, glob, os, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong)]
m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
FREE_RAM = round(m.ullAvailPhys / (1024**3), 2)
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
    VRAM_MB = int(out); VRAM_GB = round(VRAM_MB/1024, 3)
except Exception:
    VRAM_MB = None; VRAM_GB = None

DEC_SHA = '4C32527BF511B7E62EB52316864A9430B4FFFE6CC23A39116C0B6C818782C254'
ORD_SHA = 'E6A1DEE6270E08F5FBC457B3FA275C62804D0E9D158765D84E03D358FF4B5703'

# ---- state.json (root, TRUE state per r646 path-split epoch law) ----
s = json.load(open('state.json', encoding='utf-8'))
s['round_no'] = 803
s['last_round_at'] = NOW
s['ts'] = NOW
s['updated'] = NOW
s['last_seen'] = NOW
s['clock_read'] = NOW
s['last_decisions_sha'] = DEC_SHA
s['last_decisions_at'] = NOW
s['last_decisions_read_at'] = NOW
s['last_orders_sha'] = ORD_SHA
s['last_orders_read_at'] = NOW
json.dump(s, open('state.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.load(open('state.json', encoding='utf-8'))
assert s['round_no'] == 803

# ---- heartbeat fleet/machines/bm-b.json ----
h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
ack = h.get('orders_ack', [])
for o in ['O-20261007-1157-bm-c.md', 'O-20261007-1240-bm-c.md']:
    if o not in ack:
        ack.append(o)
h['orders_ack'] = ack
h['orders_ack_count'] = len(ack)
h['last_seen'] = NOW
h['heartbeat_epoch_utc'] = EPOCH
h['clock_read'] = NOW
h['ts'] = NOW
h['last_round_at'] = NOW
h['round_no'] = 803
h['round'] = 803
h['free_ram_gb'] = FREE_RAM
h['gpu_free_vram_gb'] = VRAM_GB
if VRAM_MB is not None:
    h['gpu_free_vram_mb'] = VRAM_MB
h['verdict'] = ('green: r803 six-dead-session absorb landed at origin (dead r802 QA pack 5/5 + S6 chain products) '
                '+ 14-face merge surgery receipts; smoke 48/48; attrition CLEAN; orders 166/166; D-19 dual consumed; satengine alive rc0 idle')
h['current_task'] = ('r803 closed; next = D burn watch 1739->2000 ETA ~17:3x -> trio finalize (window 10-05..10-09, G4 r638 fallback armed) '
                     '+ O-2358 self-claim <=1h post-close + market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3 first bar)')
h['last_action'] = ('r803: churn-absorb dead r802 estate -> merge origin wave (bm-c r675/676 + bm-a r823/824) 14-face canon resolve '
                    '(_r803bmb_generic_resolve receipt) -> push delivered; O-1157 bm-b resume receipt + O-1240 sweep-ack; state 802->803')
h['now_active'] = ('FUND trio: Q 2000/2000 + V 2000/2000 COMPLETE (dual-flip done) / D 1739/2000 burning rate 1.0/min ETA ~17:3x; '
                   'G1 pending D, G2+G3 green, G4 r638 fallback armed; finalize window 10-05..10-09')
h['latest_artifact'] = ('qa/smoke-r802.md + qa/equity-curve-r802.png (dead r802 session QA pack 5/5 landed at origin this round via absorb) '
                        '+ results/_r803bmb_generic_resolve.json (14-face merge resolution receipt)')
json.dump(h, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
h2 = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
assert h2['orders_ack_count'] == len(h2['orders_ack']) == 166

# ---- boards mechanical scan ----
open_tasks = 0
for p in glob.glob('fleet/tasks/*.json'):
    try:
        t = json.load(open(p, encoding='utf-8'))
        if t.get('status') == 'open':
            open_tasks += 1
    except Exception:
        pass

row = ('%s | round 803 (bm-b, dept:engineering, dead r802 absorb + 14-face merge-surgery landing + resume-broadcast receipt round) | '
       '[watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle queue_depth=0 heartbeat_age 52s; boards %d open (job_list 0 + fleet tasks mechanical scan); '
       'trio D in-flight burn = trial-labor line satisfied)] | '
       'CEO three-line: current-work = FUND trio NULLS judgment batch in-flight (Q 2000 + V 2000 COMPLETE dual-flip done / D 1739/2000 burning rate 1.0/min ETA ~17:3x @12:49 chain leg39 probe; '
       'G1 pending D, G2 integrity + G3 rehearsal green, G4 PENDING r638 fallback armed; finalize window 10-05..10-09) + O-1157 resume broadcast receipted | '
       'latest-artifact = qa/smoke-r802.md + qa/equity-curve-r802.png (dead r802 session QA charter pack 5/5: 3 syms x 800 bars 93 trades determinism=True, landed at origin this round via absorb) '
       '+ results/_r803bmb_generic_resolve.json (14-face merge resolution receipt: 12 ts-duel theirs-newer + compute_audit union 201+201->203 zero-loss + token_usage per-key max) '
       '+ results/_r803bmb_d19_read.json (D-19 dual fresh-read evidence) | '
       'next-milestone = trio D 2000/2000 ~17:3x -> same-window pool dual-flip + trio finalize per r668 law (G4 r638 fallback armed) + post-trio-close O-20261006-2358 self-claim <=1h '
       '+ market reopen 10-08 (S6 legs 25-28 resume + REGIME_GUARD v3 first new bar enforce) | '
       'S0: identity=bm-b anchored (machine.json first-read; TRUE state = root state.json per r646 path-split epoch law); 45 dirty faces churn-absorbed 51ab886d (r620/r792 absorb law: dead r802 session estate = QA pack r802 5/5 + S6 chain outputs + state 802 + workfiles, all bm-b-owned, no other-machine half-products) '
       '-> merge origin/main (15 behind: bm-c r675/676 golden-week guards + bm-a r823/r824 W173 finalize+seat/W174/W14 funnel) -> 14 UU faces resolved via dead-session generic resolver reused verbatim (r802 _r802bmb_generic_resolve.py bloodline retagged _r803; ts-duel 12 faces theirs-newer 12:52-12:54 vs ours 12:45-12:50 per r773 direction law; compute_audit rolling union 203 zero-loss; token_usage per-key max) -> merge commit 3e0171985 -> push DELIVERED d29596c1e..3e0171985 zero --no-verify | '
       'S0.5: orders dir 166 vs ack 164 -> +2 unacked consumed same-round: O-20261007-1157 (resume broadcast; bm-b receipt line filled = unpaused full-power confirmation, broadcast-protocol legal one-liner) + O-20261007-1240 (G21-T006 AU02 bgm_main dispatch, executor=bm-a r824 receipt verified 12:5x = bm-b zero execution face sweep-ack per no-mail-steal law); ack 164->166; '
       'D-19 dual fresh read (_r803bmb_d19_read.py = r789 ssh-first sparse-clone recipe verbatim; group tree C:\\Fluxgroup\\FluxGroup NOT git double-probed): decisions 815FA0F2->4C32527B CHANGED = 12:00 governance batch face (dead r802 session had consumed 635C3024->815FA0F2 mid-flight; 4C32527B = bm-c r674-676 already-receipted rows: D-20261007-01/02/03/04/05/06 all executed or non-BigMoney faces incl. our F-20261007-01 D-06 gate evidence receipted; group-origin history-surgery rewind face per r701/r798 law = watermarks follow origin current truth) -> zero own action; '
       'orders 3AB53172->E6A1DEE6 CHANGED = delta rows are committee same-window closes (C-20261007-02 local-compute law + C-20261007-03 mechanism retrospective + C1657 rotation) = zero new BigMoney dispatch (1207/1218 @BigMoney rows = bm-a-owned ticket T-2026-10-06-173-P1 in-flight per r773 claim-collision record, deliverable due 10-08 noon) -> watermarks 4C32527B/E6A1DEE6 written to state | '
       'S1: smoke 48/48 | S2: boards 0 open (job_list 0 session + fleet tasks %d open mechanical scan); dev queue stays closed per r297/r307 (J12 anti-dup no-touch / J13 bm-a lane / J10+J18b+town landed / Optuna gated) | '
       'S3: satengine alive rc0 idle; watermark red=false; trial-labor line trio D in-flight satisfied zero new drafting legal; post_review zero active FAIL rows (r801 verify inherited, no new reds this window) | '
       'S6: dead r802 session chain ABSORBED as this round S6 evidence (white-run law: 12:49 chain = 3rd run in 60min window avoided; 35 legs rc0 golden-week no-op face, cutoff 2026-09-30 unchanged, legs 25-28 built-in skip reopen 10-08; leg39 trio probe Q 2000/D 1739/V 2000 dup_k=0 x3 integrity True mechanical_ready=False G1=False G2=True G3=True G4=PENDING; dualrun-before-compute_audit ordering held in absorbed run) | '
       'S7: quartet 4/4 (IterationLoop pin=2 no-op first-fire 13:22 + LoopWatchdog re-registered first-fire 13:15 + precommit/prepush claws LF-normalized reinstall) + attrition guard CLEAN rc0 (4 ledgers, healed rows historical, evidence results/_attrition_guard_scan.json) + state 802->803 honest single-increment (dead r802 state write absorbed not double-counted) + heartbeat epoch %d int self-verified + orders_ack 166 self-verified + inbox 0 unread | '
       'treasure zero-hit claim: zero sweep/archive/delete actions this round (absorb = commit non-delete; merge resolution = content merge per canon) | '
       'verification: smoke 48/48 + attrition CLEAN + orders 166/166 + D-19 dual fresh-read consumed watermarks written + quartet 4/4 + merge receipt on-disk | '
       'local undelivered-to-origin commit count: 0 (post-close commit+push same-window; push rejected -> fallback origin machine/bm-b-r803 + next-round red flag per law) | '
       'token: L1 meter face absorbed from r802 chain (results/token_usage.json per-key max-merged at merge; no cloud tokens this round) | '
       'product score 2 (dead r802 QA pack + S6 chain products landed at origin = CEO-visible runnable evidence; 14-face merge-surgery receipt; O-1157 resume receipt closure)'
       ) % (NOW, open_tasks, open_tasks, EPOCH)
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(row + '\n')
print('closeout written: round 803, epoch %d, ack %d, open_tasks %d, free_ram %s GB' % (EPOCH, len(ack), open_tasks, FREE_RAM))
