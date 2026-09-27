"""r357 bm-b: CENSUS-FUS-S2-W2B waiting->ready flip + TRIAL-LABOR-W1-JUDGE honest defer note.

W2B gates (frozen in entry):
(1) D8 transfer receipt: data/census_w2b/w2b_d8_faces.npz present, 60,418,563 bytes,
    sha256[:16]=9febb7b4b5fab260 == manifest w2b_d8_manifest.json expectation. VERIFIED.
(2) W2-A finalize: done r357 (clean exit, ledger 294,304, sidecars post-burn stable). VERIFIED.
-> flip ready. lane_owner=bm-b; next bm-b autofill tick claims+launches.

TRIAL-LABOR-W1-JUDGE gates:
(1) judge-prep: results/trial_labor_w1/judge_state.json verified this round:
    t18 g_manifest verdict PASS (48 members) + census_frozen L{1253,1127,875}/D{3104,2978,2726}
    exact match. MET.
(2) free RAM >= 4GB: 3-sample 12.74/13.29/13.36 GB (r354 law). MET *now*.
DEFER NOTE: flipping now would let the next tick stack the TRIAL judge burn
(~7-8GB pickled per-worker panels, worker_cap 12) on top of the W2B burn
(~15.5GB no-kill precedent from W2A) on a 23.9GB box that also hosts the
MiniGame company lanes (dual-company discipline) -> OOM risk. MASS judge
shards' frozen sec.9.1 CPU ordering puts the judge family BEHIND W2B.
Defer = physical RAM dependency, trace left in-entry (CEO immediate-law
sole legal defer clause). Flip window = post-W2B-landing round, same
3-sample RAM gate. CEO 48h clock 09-29 22:45 unaffected (W2B ~12h burn
lands ~16:00 today; judges ~minutes-scale on 12 workers after).
"""
import json

POOL = r'results\runnable_pool.json'
d = json.load(open(POOL, encoding='utf-8'))
items = d if isinstance(d, list) else d.get('entries', d.get('items', []))

w2b = judge = None
for e in items:
    if e.get('id') == 'CENSUS-FUS-S2-W2B':
        w2b = e
    elif e.get('id') == 'TRIAL-LABOR-W1-JUDGE':
        judge = e
assert w2b is not None and judge is not None, 'entries not found'

# --- W2B: waiting -> ready (both frozen gates verified this round)
assert w2b.get('status') == 'waiting', f"W2B status {w2b.get('status')} != waiting"
w2b['status'] = 'ready'
w2b['flip_note'] = ('r357 bm-b flip waiting->ready: D8 npz on-disk sha[:16]=9febb7b4b5fab260 '
                    '== manifest; W2-A finalize done r357 (clean exit, sidecars stable). '
                    'In-runner gates stay fail-closed (roster sha12 + D8 sha + join>=5000).')

# --- TRIAL-LABOR-W1-JUDGE: keep waiting, append defer trace (zero-loss, append-only)
assert judge.get('status') == 'waiting', f"judge status {judge.get('status')} != waiting"
judge['defer_note'] = ('r357 bm-b: gate(1) judge-prep VERIFIED (judge_state.json t18 PASS '
                       '48-member + census_frozen L1253/1127/875 D3104/2978/2726 exact); '
                       'gate(2) RAM 3-sample 12.74/13.29/13.36GB >=4GB MET at flip-check; '
                       'flip DEFERRED to post-W2B-landing window: physical RAM dependency '
                       '(W2B burn ~15.5GB no-kill precedent + judge ~7-8GB pickled panels '
                       'stacked = OOM risk on 23.9GB dual-company box; MASS sec.9.1 frozen '
                       'ordering puts judge family behind W2B). Auto-flip candidate next '
                       'bm-b round post-W2B with same 3-sample gate.')

with open(POOL, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

# self-verify
d2 = json.load(open(POOL, encoding='utf-8'))
items2 = d2 if isinstance(d2, list) else d2.get('entries', d2.get('items', []))
w2b2 = next(e for e in items2 if e.get('id') == 'CENSUS-FUS-S2-W2B')
j2 = next(e for e in items2 if e.get('id') == 'TRIAL-LABOR-W1-JUDGE')
assert w2b2['status'] == 'ready' and j2['status'] == 'waiting'
assert 'flip_note' in w2b2 and 'defer_note' in j2
print('OK: W2B -> ready (flip_note set); TRIAL-LABOR-W1-JUDGE -> waiting kept (defer_note set)')
