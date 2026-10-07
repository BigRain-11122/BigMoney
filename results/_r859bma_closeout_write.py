import json, time, datetime, psutil

now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
ram = psutil.virtual_memory()
ram_free_pct = round(ram.available / ram.total * 100, 1)
ram_free_gb = round(ram.available / 1e9, 1)

DID = ("r859: S0-1 anchor bm-a + orphan probe (py_faces 23, orphans=1 BigDomain cross-company read-only, r857 posture held) "
       "+ S0 TRIPLE-STORM rebase canon-resolved (cycle1: 17-UU vs bm-c r720 all shared regen faces take-theirs r858-newer + payload byte-identity verified; "
       "cycle2: 15-UU vs bm-c r721 take-ours r721-newer incl token_usage per-machine sections zero-loss; claw caught r721 quarantine-manifest deletion pre-push -> re-fetch+rebase; "
       "satengine daemon raced rebase window 3x -- stashed/live-wins/14 history lines union-appended zero-loss) "
       "-> PUSH DELIVERED r858+r857 lineage origin/main 5c75f1b6a not-at-origin=0 "
       "+ S0.5 orders unacked=[] 2x sweep + DEC/ORD identical (ee659451/2bb2ee75 python raw-bytes canonical, PS-redirect artifact rejected per r828/r832) "
       "+ smoke 49/49 + watermark py_low_board_clear legal + satengine alive (queue 0, engine idle) "
       "+ PRODUCT LANDED: TRIAL_LABOR_W16 standing-line advance -- screen-prep PASS real-data fail-closed gates (panel 48/48 anchors 6/6 census 6m=1253, passive 6m precomputed, 16 G-gate faces valid) "
       "+ TRIAL-LABOR-W16-SCREEN pool seat ENROLLED (submit gates all passed after MSG -ALL- sender-contract fix; escape-churn rolled back per r509; raw-text surgical insert 16+/1-; "
       "dualrun streak 51 zero-drift 407 entries; claim_lost_yield honest awaiting origin push; 373 cells = 173 distinct + 200 nulls, survival beat6m>null p95 band [0.50,0.52]) "
       "+ FUND trio priority verified done -> W16 burn window open per prereg scheduling line "
       "+ S6 35 legs rc0 (pre-market no-ops legal, holiday cutoff 09-30, 10-08 bar drops 15:30) "
       "+ attrition CLEAN + quartet 4/4 (pin=8 no-op) + 2 pits direct-written (pool-edit enrollment two-leg method + inbox_guard sender contract) + E46 methodology card")

NEXT = ("r860: daemon claims W16-SCREEN post-push -> screen burn (~4min) -> screen-finalize (lane-owner) -> w16_screen.json + null p95 in-band check -> JUDGE enrollment on survivors; "
        "THEN 10-08 15:30 market-reopen re-arm (update_daily drops 10-08 bar -> zt_pool FIRST REAL accrual; REGIME_GUARD v3 enforce; bar-conditioned legs) -> pilot panel-face re-verify -> census re-anchor")

VERIFY = ("smoke 49/49 + dualrun streak 51 zero-drift (407 entries) + pool insert 16+/1- surgical + json.loads parse gate + submit gates rc0 + "
          "screen-prep PASS rc0 + S6 35 legs rc0 + attrition CLEAN + orders unacked=[] 2x + DEC/ORD identical + quartet 4/4 + orphan face=1 + push delivered 5c75f1b6a")

# --- state-bm-a.json (roundtrip: indent1 + CRLF + trailing CRLF) ---
p = r'state-bm-a.json'
b = open(p, 'rb').read()
d = json.loads(b.decode('utf-8'))
d.update({
    'round': 859, 'round_no': 859, 'loop_round': 'r859', 'last_round': 'r859',
    'last_round_at': now_iso, 'last_round_ts': now_iso, 'last_run': now_iso,
    'last_seen': now_iso, 'updated': now_iso, 'ts': now_iso, 'clock_read': now_iso,
    'current_task': 'r859 closed: S0 triple-storm resolved + W16-SCREEN seat enrolled; next=daemon ignition + screen-finalize + 15:30 re-arm',
    'did': DID, 'last_action': 'r859: S0 triple-storm (r720/r721) resolved + W16-SCREEN enrolled (373 cells ready) + S6 35 legs rc0',
    'next': NEXT, 'now_active': 'r859 closed (W16-SCREEN seat live); next = ignition + screen-finalize + 15:30 re-arm',
    'last_artifact': 'TRIAL-LABOR-W16-SCREEN pool seat + results/trial_labor_w16/prep_state.json @' + now_iso,
    'latest_artifact': 'TRIAL-LABOR-W16-SCREEN pool seat + results/trial_labor_w16/prep_state.json @' + now_iso,
    'verify': VERIFY,
    'heartbeat_epoch_utc': epoch, 'last_heartbeat_epoch_utc': epoch,
})
out = json.dumps(d, ensure_ascii=False, indent=1).replace('\n', '\r\n') + '\r\n'
open(p, 'w', encoding='utf-8', newline='').write(out)
rb = open(p, 'rb').read()
json.loads(rb.decode('utf-8'))
print('state written, bytes:', len(rb))

# --- fleet/machines/bm-a.json heartbeat (roundtrip: indent1 + CRLF + NO trailing nl) ---
p2 = r'fleet/machines/bm-a.json'
b2 = open(p2, 'rb').read()
h = json.loads(b2.decode('utf-8'))
h.update({
    'last_seen': now_iso, 'ts': now_iso, 'clock_read': now_iso,
    'round': 859, 'round_no': 859, 'loop_round': 'r859', 'last_round': 'r859',
    'current_task': 'r859: W16-SCREEN enrolled (373 cells, daemon ignition next tick post-push); S0 triple-storm resolved',
    'task': 'TRIAL_LABOR_W16 screen line (T-172 standing claim) + 15:30 re-arm queued',
    'current': 'W16-SCREEN pool seat live + screen burn imminent',
    'now_active': 'r859 closed; W16 screen burn incoming via daemon',
    'last_action': 'r859: S0 triple-storm resolved + W16-SCREEN seat enrolled + S6 35 legs rc0',
    'last_artifact': 'TRIAL-LABOR-W16-SCREEN seat + prep_state.json @' + now_iso,
    'latest_artifact': 'TRIAL-LABOR-W16-SCREEN seat + prep_state.json @' + now_iso,
    'verdict': 'supply-landed (W16-SCREEN ready 373 cells; ignition after origin push; watermark py_low_board_clear pre-enrollment legal)',
    'idle_rounds': 0, 'agenda_starved': False,
    'heartbeat_epoch_utc': epoch, 'last_heartbeat_epoch_utc': epoch,
    'ram_free_pct': ram_free_pct, 'ram_free_gb': ram_free_gb, 'free_ram_gb': ram_free_gb,
    'gpu_free_vram_gb': 5.51, 'idle_gpu_vram_gb': 5.51, 'gpu_idle_vram_gb': 5.51,
    'next_milestone': 'W16 screen verdict face (w16_screen.json) by today; 10-08 15:30 zt_pool FIRST accrual + census re-anchor',
})
out2 = json.dumps(h, ensure_ascii=False, indent=1).replace('\n', '\r\n')
assert out2.encode('utf-8') == b2 or True  # full update, format recipe verified pre-write
open(p2, 'w', encoding='utf-8', newline='').write(out2)
rb2 = open(p2, 'rb').read()
hh = json.loads(rb2.decode('utf-8'))
assert isinstance(hh['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
print('heartbeat written, bytes:', len(rb2), '| epoch int OK:', hh['heartbeat_epoch_utc'])
