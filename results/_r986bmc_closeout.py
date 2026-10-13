import json, time, os
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

R = 'r986'
NEXT = 'r987'

did = ("r986: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 zero-kill; S0 fetch 0/0 clean "
       "(x6 daemon live-faces legit dirty, no rebase owed); (2) S0.5 dual-delta FALSE both scans (opening + S7 tail; "
       "ord content-sha1 348eaf34 == live per r977 pinned method / dec raw-blob sha256 86187eff == live; unacked=0; "
       "local orders full-scan: O-20261014-0312 acked receipt-line present, two 004x bm-b orders = FYI-only faces; "
       "METHOD-FACE DIVERGENCE healed: heartbeat last_orders_sha held stale r537 blob-sha face 53582389 vs state "
       "content-sha 348eaf34 -- both FALSE vs live by own method, zero rows owed, heartbeat normalized to pinned "
       "content-sha face this window to kill the r977-saga recurrence vector); (3) S1 smoke 49/49; (4) S3: satengine "
       "ALIVE rc0 (queue empty, burns none; W236=bm-a chain in-flight prereg 67ade8314 landed 05:1x, splice/burn/"
       "finalize theirs per seat-first; absorb criteria NOT met -- bm-a commits landing) + wm red=false healthy "
       "wait-state (next_pick=claimed MF-IC-P1 parked source-blocked) + post_review YES=45 NO=0 WAIT=5 zero-x + "
       "jobs=0 + pool ready=0 + P2 tech queue all-done + P3 explore closed + idle green_idle=false RAM 1.8pct "
       "honest not-claim-eligible (GPU lane=MV V3 burn window protected per O-20261014-0312 sec.2); (5) WAIT-STATE "
       "faces verified not merely re-declared: MF panel confirmed ABSENT on bm-c (data/moneyflow dir nonexistent -> "
       "R31 collector lane = bm-a, batch execution = panel holder per lane-ruling-4; relay MSG-0512 standing in "
       "inbox addressed to bm-a) + bm-a shared-face heartbeat ts 22:22 stale BUT chain alive via commits (prereg "
       "landed 05:1x) -> no takeover; (6) S6 light: dualrun ZERO-DRIFT streak 51 + compute_audit FLAG "
       "pool_starvation/supply_floor structural (ready 0<floor 3, answered-by-chain W236 + RW-5 freeze legal) + "
       "token delta=0 L2 legs 0 today; (7) S7: attrition 4 CLEAN + pin=5 no-op + watchdog re-registered + both "
       "claws installed + tail dual-scan FALSE; counter 986->987")

verdict = ("green: wait-state window honestly held (10-14 bars not due until 15:30; W236=bm-a active chain yield "
           "per seat-first, prereg landed 05:1x; MF-IC-P1 parked 22d source-blocked upstream, panel absent locally "
           "verified; pool ready=0 + RW-5 freeze supply legally chained to W236 finalize [bm-a]; idle RAM-gated "
           "1.8pct honest) + watermark method-face divergence healed at heartbeat (both deltas FALSE vs live, zero "
           "rows owed) + smoke 49/49 + S6 light zero-drift + S7 quad green + post_review zero-x")

nxt = (f"{NEXT}: (1) W236 chain watch continues -- bm-a in-flight (prereg landed 05:1x; splice/burn/finalize theirs; "
       "absorb ONLY if their window dies post-seat per seat-first law); (2) 10-14 bars re-probe after 15:30 -> "
       "papers full chain when new bar lands (10-13 papers debt zero per r985 verify); (3) MF collector fix watch "
       "-- if bm-a panel completes, MF-IC-P1 S2 completion gate check (execution machine = panel holder); "
       "(4) MV V3 director rulings watch per ORD rows; closeout scripts: canonical report path MANDATORY (r750 law)")

closeout_note = ("r986: clean continuation window (state round_no=986 at open, executed r986, advanced 986->987 so "
                 f"next={NEXT}); zero absorb owed (r985 closeout 165150f66 landed clean, zero dead window between); "
                 "zero double-count: S0.5 dual-delta FALSE both scans (opening + S7 tail), unacked=0 both scans; "
                 "wait-state window #4 held per one-line law with verification-not-rescan of wait objects "
                 "(MF panel absent locally + bm-a chain alive via commits); heartbeat ORD watermark method-face "
                 "normalized to r977 pinned content-sha (stale r537 blob-sha face dropped, divergence disclosed, "
                 "zero rows owed under both methods)")

# ---- 1. canonical round report row ----
row = (f"{now_iso} | {R} | bm-c wait-state window #4 close (bars not due 15:30 + W236=bm-a in-flight yield + "
       f"MF-IC-P1 parked 22d panel-absent-locally verified + pool 0 + RW-5 freeze) + ORD watermark method-face heal "
       f"(heartbeat blob-sha face 53582389 -> pinned content-sha 348eaf34; both FALSE vs live, zero rows owed; r977 "
       f"saga recurrence vector killed) | smoke 49/49 + s05 dual FALSE x2 (probe results/_r986bmc_s05_probe.py) + "
       f"dualrun ZERO-DRIFT streak 51 + attrition 4 CLEAN + S7 quad (pin=5/watchdog/claws) + post_review 0-x "
       f"(YES45/WAIT5) + orphan face=2 zero-kill | {NEXT}: W236 bm-a chain watch (absorb only if window dies "
       f"post-seat) + 15:30 bars re-probe -> papers chain + MF panel watch -> S2 gate + MV V3 rulings watch + "
       f"canonical report path MANDATORY")
with open('logs/iteration-loop/round_reports-bm-c.md', 'a', encoding='utf-8') as f:
    f.write(row + '\n')
print('ledger row appended (canonical path)')

# ---- 2. state file update ----
d = json.load(open('state-bm-c.json', encoding='utf-8'))
d['round_no'] = 987
d['loop_round'] = 986
d['last_round'] = 986
d['last_round_label'] = R
d['round_no_label'] = R
d['last_round_at'] = now_iso
d['last_round_closed'] = now_iso
d['last_round_ts'] = epoch
d['did'] = did
d['verdict'] = verdict
d['next'] = nxt
d['next_pointer'] = nxt
d['r986_closeout_note'] = closeout_note
d['r986_absorb_note'] = ''
d['current_task'] = f'{R} wait-state window #4 close (W236 yield watch + MF panel watch + bars pre-15:30 + ORD method-face heal)'
d['current_task_at'] = now_iso
d['current_task_ts'] = epoch
d['activity_now'] = f"2026-10-14 06:1x | {R} | bm-c: wait-state close + ORD watermark method-face heal | counter 986->987"
d['now_active'] = d['activity_now']
d['last_action'] = f'{R} closeout (wait-state window #4 + heartbeat ORD method-face normalize + S6 light + S7 quad)'
d['last_action_at'] = now_iso
d['last_round_summary'] = (f'{R}: wait-state window #4 (W236=bm-a in-flight yield prereg landed 05:1x + bars not due + '
                           f'MF-IC-P1 parked 22d panel-absent-locally + pool 0 + RW-5 freeze) + heartbeat ORD '
                           f'watermark method-face normalized (r977 pin, zero rows owed) + smoke 49/49 + S0.5 dual '
                           f'FALSE x2 + S6 light zero-drift streak 51 + S7 quad green; counter 986->987')
d['last_round_summary_at'] = now_iso
d['latest_artifact'] = 'wait-state window #4 (no new artifact; watch faces verified: MF panel absent locally, bm-a chain alive; heartbeat ORD method-face heal)'
d['last_artifact'] = d['latest_artifact']
d['recent_artifact'] = d['latest_artifact']
d['next_milestone'] = '10-14 bars post-15:30 papers chain + W236 finalize watch (bm-a) + MF panel completion -> MF-IC-P1 unpark'
d['orphan_face'] = 2
d['orphan_faces'] = 2
d['idle_rounds'] = 0
d['agenda_starved'] = False
d['orders_ack_receipt'] = f'{R}: zero unacked both scans; group ORD/DEC dual-delta FALSE both (ord 348eaf34 content-sha / dec 86187eff hold); zero bm-c execution owed'
d['orders_ack_ts'] = now_iso
d['prod_lanes'] = ("CPU=N1 W236: bm-a chain in-flight (prereg 67ade8314 landed 05:1x; splice/burn/finalize theirs; "
                   "bm-c yielded per seat-first); MF-IC-P1: parked 22d source-blocked (panel absent on bm-c verified; "
                   "bm-a collector lane, relay MSG-0512 standing); GPU=MV V3: burn window protected per O-20261014-0312 sec.2")
for k in ('ts', 'updated', 'updated_at', 'last_seen', 'last_seen_at'):
    d[k] = now_iso
d['heartbeat_epoch_utc'] = epoch
d['last_ts'] = epoch
d['last_pulled_at'] = now_iso
d['last_orders_read_at'] = now_iso
d['last_orders_seen'] = now_iso
d['last_orders_at'] = now_iso
d['last_decisions_read_at'] = now_iso
d['last_decisions_seen'] = now_iso
d['last_decisions_at'] = now_iso
json.dump(d, open('state-bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state written: round_no=987')

# ---- 3. heartbeat update ----
h = json.load(open('fleet/machines/bm-c.json', encoding='utf-8'))
h['round_no'] = 987
h['round_no_label'] = R
h['last_round'] = 986
h['last_round_at'] = now_iso
h['did'] = did
h['verdict'] = verdict
h['next'] = nxt
h['next_pointer'] = nxt
h['current_task'] = d['current_task']
h['current_task_at'] = now_iso
h['latest_artifact'] = d['latest_artifact']
h['last_artifact'] = d['latest_artifact']
h['recent_artifact'] = d['latest_artifact']
h['next_milestone'] = d['next_milestone']
h['activity_now'] = d['activity_now']
h['now_active'] = d['activity_now']
h['last_action'] = d['last_action']
h['last_action_at'] = now_iso
h['last_round_summary'] = d['last_round_summary']
h['last_round_summary_at'] = now_iso
h['last_round_closed'] = now_iso
h['last_round_ts'] = epoch
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now_iso
for k in ('ts', 'last_seen', 'last_seen_at', 'updated', 'updated_at', 'last_pulled_at', 'orders_ack_ts'):
    h[k] = now_iso
h['last_ts'] = epoch
h['current_task_ts'] = epoch
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['orphan_face'] = 2
h['orphan_faces'] = 2
h['prod_lanes'] = d['prod_lanes']
h['orders_ack_receipt'] = d['orders_ack_receipt']
h['last_round_label'] = R
# ORD watermark method-face normalization (r977 pin: content-bytes sha1)
h['last_orders_sha'] = '348eaf34abef14ca3ec84139144d883b04d45826'
h['last_orders_at'] = now_iso
h['last_orders_read_at'] = now_iso
h['last_orders_seen'] = now_iso
h['ord_sha_method'] = ("python content-bytes sha1 of git show origin/main:docs/orders.md (r977 ROOT-CAUSE FIX pin: "
                       "watermark MUST use probe method content-bytes sha1 for ORD; heartbeat previously held stale "
                       "r537 blob-sha face 53582389 -- normalized r986, both methods were FALSE vs live so zero rows "
                       "owed/lost; raw-blob sha256 for DEC unchanged)")
h['last_decisions_read_at'] = now_iso
h['last_decisions_at'] = now_iso
h['last_decisions_seen'] = now_iso
# live RAM snapshot
try:
    import psutil
    vm = psutil.virtual_memory()
    h['free_ram_gb'] = round(vm.available / 1024**3, 1)
    h['ram_free_gb'] = h['free_ram_gb']
    h['idle_ram_gb'] = h['free_ram_gb']
    cpu = psutil.cpu_percent(interval=1)
    h['cpu_pct'] = cpu
    h['cpu_util_pct'] = cpu
    h['cpu_idle_pct'] = round(100 - cpu, 1)
except Exception:
    pass
json.dump(h, open('fleet/machines/bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# post-write self-verify
h2 = json.load(open('fleet/machines/bm-c.json', encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in h2['clock_read'], 'clock_read must be T-separated'
print('heartbeat written + self-verified (epoch int, clock T-separated, free_ram', h2.get('free_ram_gb'), 'GB)')
print('CLOSEOUT WRITES DONE')
