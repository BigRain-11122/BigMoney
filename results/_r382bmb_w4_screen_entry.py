"""r382 bm-b: TRIAL-LABOR-W4-SCREEN pool entry creation (W2 r360 / W3 r150 precedent) + byte-style law."""
import json, subprocess

POOL = 'results/runnable_pool.json'
raw = open(POOL, 'rb').read()
crlf = raw.count(b'\r\n'); trailing = raw[-1:]
assert b'\r\n' in raw and trailing != b'\n'

d = json.loads(raw.decode('utf-8'))
assert not any(x['id'] == 'TRIAL-LABOR-W4-SCREEN' for x in d['entries'])
gen = next(x for x in d['entries'] if x['id'] == 'TRIAL-LABOR-W4-GENERATE')
assert gen['status'] == 'done'

entry = {
    "id": "TRIAL-LABOR-W4-SCREEN",
    "ticket_ref": ("T-2026-09-28-98 WAVE-4 screen slice (CEO O-2026-09-27-2245 thousand-trader order + "
                   "O-2026-09-27-2250 standing law; prereg FROZEN r396 commit 3aec0868 + seeds R250 "
                   "same-commit 20289500/20290000/20290500; runner full-slice built bm-a r397 selftest "
                   "84/84 hermetic; G-VOL raw-face law fix bm-b r381 commit 61f81785 production-validated "
                   "through real-fire landing 12:27:41 n=3810 distinct; screen-prep PASS r382 12:30:56)"),
    "prereg_ref": ("research/TRIAL_LABOR_W4_PREREG.md FROZEN sec.3 s2 (each distinct candidate = "
                   "legacy-axis leg-L 6m full-history backtest, W1 13bp base, T+1, initial-stop + "
                   "regime-gate + VOL-gate faces carried per cell, frozen composition order "
                   "filter->timing->GATE->VOL->STOP per MSG-0440 E1 mapping; beat6m >= passive over "
                   "1253 frozen starts, comparison operator per frozen sec.3 text; null family K=200 "
                   "seven-tuple axis R/X/S/T/STOP/GATE/VOL seed trial_labor_w4_scrnull=20290000; "
                   "survival line = beat6m > null p95 program-frozen via tl2._finalize_math import = "
                   "W2/W3 identical law; finalize refuses missing cells, checkpoint retained; ledger "
                   "TRIAL_LAB_W4_SCREEN batch = distinct 3810 + 200 nulls literal per sec.3; products "
                   "w4_screen.json + w4_screen_cells.csv + vol-gate segmented survival stats per "
                   "prereg sec.6)"),
    "runner": "scripts/trial_labor_w4.py",
    "runner_args": ["screen", "--shard", "0", "--shards", "1"],
    "lane_owner": None,
    "priority": 1,
    "status": "waiting",
    "entered_at": "2026-09-28 12:31:30",
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal (16-core bm-b: 12 observed; 32-core bm-c: <=25)",
        "priority": "BelowNormal",
        "note": ("W2-SCREEN 3,124 cells minutes-level pool batch (r389 06:50-06:52) + W3-SCREEN 3,752 "
                 "cells 4.6min (r395) same cell weight + vectorized gate+vol overlays -> 4,010 cells "
                 "(3,810 distinct + 200 nulls) est minutes-level; per-cell jsonl checkpoint "
                 "cross-kill resume (W1 law); prereg sec.0 worst-case anchor stands as ceiling"),
    },
    "data_gates": ("WAITING DEPS (flip to ready upon ALL, W1/W2/W3-JUDGE r346 precedent): (1) "
                   "TRIAL-LABOR-W4-GENERATE done -- LANDED r382 12:27:41, w4_candidates.json n=3810 "
                   "single-shot completion marker in-repo; (2) screen-prep PASS -- prep_state.json "
                   "12:30:56 gates G-PANEL 48/48 + G-ANCHOR registered-six replay faithful on the W4 "
                   "seven-tuple identity face + G-CENSUS leg-L {1253,1127,875} frozen-match + G-EXCLUDE "
                   "sources disclosed + G-VOL raw-face anchors {first-valid 519, calm 1523, wild 1441} "
                   "re-verified live; (3) machine free RAM >= 4GB three-sample across >=30s (r354 law; "
                   "autofill has no RAM gate so waiting status is the ONLY protection; census W2B "
                   "slow-tail burn gates bm-b until finalize -- flip executor = any machine per r203 "
                   "law, bm-a/bm-c RAM-open windows lawful; SCREEN face = CPU pool face per prereg "
                   "sec.0 r369 disposition). IN-RUNNER fail-closed exit 2: prep/candidates/grammar "
                   "absent, grammar sha != d498e9343ee57460 refuse, free RAM three-sample < 4GB "
                   "honest refuse. After all shards: screen-finalize = separate round work (ledger "
                   "TRIAL_LAB_W4_SCREEN + w4_screen.json + w4_screen_cells.csv; survivors feed the "
                   "judge face next slice; W2 r362 / W3 r150 precedent)"),
    "shards": [
        {
            "key": "screen-0of1",
            "status": "waiting",
            "owner": None,
            "owner_since": None,
            "checkpoint": "results/trial_labor_w4/checkpoint/screen_shard_0of1.jsonl (append-per-cell; finalize gate refuses missing cells)",
            "note": ("single shard; worker_cap() parallelism inside the shard (W2/W3-SCREEN same "
                     "shape); multi-shard i%shards split legal per shard law on partial claim"),
        }
    ],
    "entered_by": "bm-b r382",
}
d['entries'].append(entry)

out = json.dumps(d, ensure_ascii=False, indent=2).replace('\n', '\r\n')
if trailing != b'\n':
    out = out.rstrip('\r\n')
open(POOL, 'wb').write(out.encode('utf-8'))

v = open(POOL, 'rb').read()
assert v.count(b'\r\n') >= crlf
d2 = json.loads(v.decode('utf-8'))
e2 = next(x for x in d2['entries'] if x['id'] == 'TRIAL-LABOR-W4-SCREEN')
assert e2['status'] == 'waiting' and e2['shards'][0]['status'] == 'waiting'
print('W4-SCREEN entry appended OK; entries=%d' % len(d2['entries']))
r = subprocess.run(['git', 'diff', '--stat', '--', POOL], capture_output=True, text=True)
print(r.stdout.strip())
