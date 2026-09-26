import json, time, datetime
now = datetime.datetime.now()
ts_iso = now.isoformat()
epoch = int(time.time())
clock = now.astimezone().isoformat()

# --- state file ---
sp = 'state-bm-a.json'
st = json.load(open(sp, encoding='utf-8-sig'))
st['round_no'] = 286
st['did'] = ("R286: R285 dead-session residue adopted (9ebdd06f, R279 law) + T-86 s2 CENSUS_FUS_S2_W1 prereg FROZEN e51e55e0 (exploration face, wave-1 core48 29 faces x 4060 combos + 58 control + 400 nulls N=4518, seed census_fusion_s2=20274500 same-commit R250 law, registry v1.1 G-row lowamp20 amendment, wave-2 rule frozen T-87-gated) + S6 22 legs rc=0 + smoke 25/25 + science_gates selftest 37/37")
st['verdict'] = 'ok'
st['next'] = ("census runner build + pool entry (CENSUS-FUS-S2-W1) per frozen prereg; CN-TREND finalize harvest when product lands (three-piece r244 law + cross-family leg vs CN-SOE)")
st['ts'] = ts_iso
st['last_round_ts'] = now.strftime('%Y-%m-%d %H:%M:%S')
st['updated_at'] = now.strftime('%Y-%m-%d %H:%M:%S')
st['current_task'] = "R286 done: census prereg frozen; CN-TREND burn in flight (harvest next); census runner build next"
st['last_run'] = now.strftime('%Y-%m-%d %H:%M:%S')
st['last_round_at'] = now.strftime('%Y-%m-%d %H:%M:%S')
st['last_round'] = 285
st['updated'] = now.strftime('%Y-%m-%d %H:%M:%S')
st['last_seen'] = ts_iso
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- round report (trailing-newline probe per R281 law) ---
rp = 'logs/iteration-loop/round_reports-bm-a.md'
raw = open(rp, 'rb').read()
line = ("2026-09-27 %s | R286 bm-a | WM=AMBER-legal py_low_with_work_cands (batch alive: CN-TREND nulls phase burning owner=bm-a local_batch_running=true py 13.9%%; supply opened same round = census prereg frozen) | S0.5 orders double-scan 89/89 acked zero unacked + zero new group-decision lines (D-20260927-04/05 already receipted) | S0 rebase clean; R285 dead-session residue ADOPTED per R279 law (9ebdd06f: post-slice-b tail = CODELY hot-cold archive move + R285 harvest-closure law + S6 regen panels; proof = state stale 284 + no R285 report line + 4min quiescence) | MAIN: T-86 s2 CENSUS_FUS_S2_W1 prereg FROZEN e51e55e0 pre-runner (R99 chain): exploration face per ticket spec (zero judgment/zero paper eligibility, feeds T-23 intake funnel only); wave-1 core48 = A-row 28 + G-row lowamp20 (registry v1.1 append-only amendment, spec-mandated lowamp/trend coverage, scratch formula non-recoverable disclosed) = 29 faces -> 406 pairs + 3654 triples + 58 control pairs + K=400 combo nulls, N=4518, V2+x2 cost weekly tercile blend + rank-IC + dual-sort conditional + per-year IC; seed census_fusion_s2=20274500 (band 20274500..20274900, rg zero hits, registered same commit R250 one-step law); science_gates selftest 37/37 post-SEED edit (R256 checker-edit law); F-04 MSG-20260927-0230-bm-a declared; wave-2 wide-universe enumeration rule frozen (T-87 panel gate + B-layer mask + wave-2 addendum freeze BEFORE run, R99 per wave) | S6 22 legs rc=0 (audit CLEAN v2.3 pool-supply-gap py 19.9%% burn, WM probe batch-alive, daily no-op cutoff 09-24, regime ORANGE shadow breadth 0.77, 3-cards 6/28/7 best VOLATILITY-CE-01 87.0, clock CALL-2026-09-24 ORANGE_COOL 4 sleeves 0 activated, data lanes weekend no-ops/throttles honest, b_layer mask regen gates all pass, live.paper family skipped no-new-bar, scorecard O1600 6 rows, report REPORT-2026-09-27 regen, monitor, token delta 0) | smoke 25/25 | next: census runner build + pool entry; CN-TREND harvest three-piece (r244/r285 law: judgment + attrition + prereg s7/s8 + post_review row + cross-family leg vs CN-SOE) when finalize lands [via bm-a]" % now.strftime('%H:%M:%S'))
add_nl = b'' if raw.endswith(b'\n') else b'\n'
open(rp, 'ab').write(add_nl + line.encode('utf-8') + b'\n')

# --- heartbeat ---
hp = 'fleet/machines/bm-a.json'
hb = json.load(open(hp, encoding='utf-8-sig'))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().available / 2**30
except Exception:
    cpu, ram = 0.0, 0.0
hb['last_seen'] = ts_iso
hb['current_task'] = st['current_task']
hb['task'] = st['current_task']
hb['cpu_cores'] = 32
hb['cpu_pct'] = cpu
hb['free_ram_gb'] = round(ram, 1)
hb['verdict'] = 'py_low_with_work_cands_batch_alive'
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock
hb['round_no'] = 286
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
h = json.load(open(hp, encoding='utf-8-sig'))
assert isinstance(h['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in h['clock_read'], 'clock_read must be T-sep'
print('wrap ok; epoch', epoch, 'clock', clock, 'cpu', cpu, 'ram', round(ram, 1))
