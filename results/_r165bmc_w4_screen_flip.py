# r165 bm-c: TRIAL-LABOR-W4-SCREEN pool done-flip + TRIAL-LABOR-W4-JUDGE entry (parked waiting)
# evidence script per _r395bma_close_out / r381 byte-style law (CRLF + no trailing newline + indent=2 + ensure_ascii=False)
import json, time, datetime

POOL = 'results/runnable_pool.json'
now = datetime.datetime.now()
ts = now.strftime('%Y-%m-%d %H:%M:%S')

raw = open(POOL, 'rb').read()
tail_before = raw[-1:]
pool = json.loads(raw.decode('utf-8'))

entries = pool['entries']
scr = None
for e in entries:
    if e.get('id') == 'TRIAL-LABOR-W4-SCREEN':
        scr = e
        break
assert scr is not None, 'W4-SCREEN entry missing'
assert scr['status'] == 'ready', f"unexpected status {scr['status']}"
# finalize products must exist (single-shot completion markers)
w4s = json.load(open('results/trial_labor_w4/w4_screen.json', encoding='utf-8'))
assert w4s['n_distinct'] == 3810 and w4s['k_nulls'] == 200 and w4s['n_survivors'] == 461
assert w4s['grammar_sha256'] == 'd498e9343ee57460'
assert w4s['evidence_cutoff'] == '2026-09-22' and w4s['batch_cells'] == 4010

# --- 1. W4-SCREEN done-flip (tick relaunch stops; W3 r395 precedent) ---
sh = scr['shards'][0]
sh['status'] = 'done'
sh['done_at'] = ts
sh['note'] = (sh['note'] +
    ' | burn r165 finalize: 4010/4010 cells (autofill claim 13:00:01 pid 23908 12 workers ~12.3min), '
    'null p95 0.5164, survivors 461/3810 = 12.10%')
scr['status'] = 'done'
scr['done_at'] = ts
scr['result_ref'] = 'results/trial_labor_w4/w4_screen.json (+ w4_screen_cells.csv)'
scr['note_done'] = (
    'r165 bm-c finalize: burn 13:00:01 autofill claim (pid 23908, 12 workers, ~12.3min) -> checkpoint 4010/4010; '
    'finalize: null p95 0.5164 (prereg sec.5 band [0.42,0.62] PASS), distinct 3810 (band [2800,4600] PASS), '
    'survivors 461/3810 = 12.10% (band [2%,15%] PASS; count 461 in [100,750] PASS); '
    'vol segmented {calm 61/1226=4.98%, none 140/1311=10.68%, wild 260/1273=20.42%} -- '
    'sec.5 pred-4 VOL direction prior (calm>=none>=wild) FALSIFIED opposite order, prereg anticipated two-way martyrdom, '
    'batch-end sec.8 reconciliation carries it; gate x vol interaction top bear|wild 156/434=35.94%; '
    'ledger TRIAL_LAB_W4_SCREEN +4,010 chain total 305,190; '
    'survivors feed TRIAL-LABOR-W4-JUDGE (parked waiting entry same round, queued behind W2/W3-JUDGE per prereg sec.0 '
    'physical-order gate bm-b r369 ruling; judge-prep+judge+judge-finalize trio on deep-panel machine per W1 r346 precedent)')

# --- 2. TRIAL-LABOR-W4-JUDGE entry parked waiting (W1 r121 / W3 r370 precedent shapes) ---
have_judge = any(e.get('id') == 'TRIAL-LABOR-W4-JUDGE' for e in entries)
assert not have_judge, 'W4-JUDGE entry already exists'
judge = {
    "id": "TRIAL-LABOR-W4-JUDGE",
    "ticket_ref": ("T-2026-09-28-98 WAVE-4 judge slice (CEO O-20260927-2245 thousand-trader order + "
                   "O-20260927-2250 standing law; prereg FROZEN r396 commit 3aec0868; runner full-slice built bm-a r397 "
                   "selftest 84/84 hermetic -- judge trio CLI already in-tree unlike W3 later-build; "
                   "screen-finalize LANDED bm-c r165: 4010/4010 cells, null p95 0.5164, survivors 461/3810 "
                   "-- judge physical dep satisfied)"),
    "prereg_ref": ("research/TRIAL_LABOR_W4_PREREG.md FROZEN sec.0 TRIAL_LAB_W4_JUDGE (s3 full judgment batch: "
                   "batch_trials = survivors 461 judged cells; dual nulls B/P resampling face = not ledger +0 per prereg "
                   "sec.0, census sec.9.2 NAV derivation precedent) + sec.0 W4-JUDGE physical-order gate (bm-b r369 "
                   "ruling adopted, ticket-logged: judge face queued BEHIND W2/W3-JUDGE + other in-flight judge faces; "
                   "RAM r354 three-sample gate + serial flip discipline auto-realizes; 48h CEO report clock starts at "
                   "judge-finalize) + sec.4 (g1_prime_v2/g2_registration_v2 shared lib zero hand-copy; DSR n_trials = "
                   "live chain head cross-wave no-reset, r396 freeze-time read 301,180 + W4 SCREEN +4,010 -> run-time "
                   "live read governs; E[FP]=0.05*N_judged; family PBO CSCV 8 blocks family=strategy-module)"),
    "runner": "scripts/trial_labor_w4.py",
    "runner_args": ["judge", "--shard", "0", "--shards", "1"],
    "lane_owner": None,
    "priority": 1,
    "status": "waiting",
    "entered_at": ts,
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal",
        "priority": "BelowNormal",
        "note": ("judge initargs carry BOTH leg panels + per-leg ATR20 + per-leg gate/vol state faces = heaviest "
                 "per-worker state in the fleet (worker_cap RAM guard applies); dual-leg x {6m,12m,24m} x cost "
                 "{base x1, x2=CostPatch(2)} engine curves per judged cell WITH gate+vol+stop overlays + dual nulls "
                 "B/P resampling ~4-6x screen-cell weight; W2/W3 judge same-machinery precedent; flip executor = "
                 "deep-panel machine round (bm-b) post queue-position + judge-prep + RAM 3-sample gate "
                 "(W1-JUDGE r357 defer precedent)")
    },
    "data_gates": ("WAITING DEPS (flip to ready upon ALL, W1-JUDGE r346 precedent): (1) serial queue ahead per prereg "
                   "sec.0 physical-order gate (bm-b r369 ruling): TRIAL-LABOR-W2-JUDGE + TRIAL-LABOR-W3-JUDGE + "
                   "MASS-TRIAL-W1-JUDGE-SHARD-0..3 ahead/in-flight; (2) judge-prep run on the deep-panel machine "
                   "(physical = bm-b t18 sidecar family; cache-less machines exit-2 honest per W1 precedent) -> "
                   "judge_state.json manifest verdict PASS; (3) machine free RAM >= 4GB three-sample across >=30s "
                   "(r354 law; census W2B burn on bm-b gates it until finalize). IN-RUNNER fail-closed: "
                   "judge_state/w4_screen absent exit 2; grammar sha != d498e9343ee57460 refuse; zero-survivor "
                   "vacuous face = judge no-op lawful (not this wave: 461 survivors). After shards: judge-finalize = "
                   "separate round work (ledger TRIAL_LAB_W4_JUDGE batch_trials=survivors literal + w4_judge.json "
                   "G1/G2/DSR/PBO/E[FP] judgment summary + gate x vol segmented disclosure; intake slice lands next "
                   "per prereg sec.6; 48h CEO report clock starts)"),
    "shards": [
        {
            "key": "judge-0of1",
            "status": "waiting",
            "owner": None,
            "owner_since": None,
            "checkpoint": "results/trial_labor_w4/checkpoint/judge_shard_0of1.jsonl (row-level done-set resume, cross-kill W1 law)",
            "note": ("single shard W1/W2/W3-JUDGE precedent; multi-shard i%shards split legal per shard law on partial "
                     "claim; cell enumeration = sorted survivors global index i = dual-nulls seed binding face "
                     "(stable across shard counts)")
        }
    ],
    "entered_by": "bm-c r165",
    "note": ("r165 bm-c entry post-screen-finalize (461 survivors); parked waiting NOT ready: serial queue behind "
             "W2/W3-JUDGE + MASS W1 judge shards per prereg sec.0 physical-order gate (bm-b r369 ruling) + RAM r354 "
             "sequencing gate (census W2B burn on bm-b until finalize ~15:00 ETA per r164 watch); judge-prep + judge + "
             "judge-finalize chain on deep-panel machine per physical-dep law O-1730 family")
}
entries.append(judge)
pool['updated_at'] = ts

out = json.dumps(pool, ensure_ascii=False, indent=2)
out = out.replace('\n', '\r\n')  # r381 law: restore CRLF
with open(POOL, 'wb') as f:
    f.write(out.encode('utf-8'))  # no trailing newline (r381 law)

# --- self-verify ---
raw2 = open(POOL, 'rb').read()
assert raw2[-1:] == tail_before, 'tail byte changed'
assert raw2.count(b'\r\n') == raw2.count(b'\n'), 'mixed line endings'
chk = json.loads(raw2.decode('utf-8'))
s2 = [e for e in chk['entries'] if e['id'] == 'TRIAL-LABOR-W4-SCREEN'][0]
j2 = [e for e in chk['entries'] if e['id'] == 'TRIAL-LABOR-W4-JUDGE'][0]
assert s2['status'] == 'done' and s2['shards'][0]['status'] == 'done'
assert j2['status'] == 'waiting'
print('W4-SCREEN flipped done @', s2['done_at'])
print('W4-JUDGE entered waiting, entered_at', j2['entered_at'])
print('byte-style: CRLF', raw2.count(b'\r\n'), 'tail', raw2[-1:], 'size', len(raw2))
