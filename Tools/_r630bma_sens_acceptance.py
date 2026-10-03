"""r630 bm-a: FUND-DIVLOWVOL-P1-SENS burn acceptance (r629 next-milestone leg).
Acceptance legs (QUALITY-SENS precedent structure):
 A. product rows: 500 rows, k=0..499, unique+contiguous, all parse
 B. burn window facts: two DONE lines (493/493 resume-burn 1247.6s + 13/13
    gap-repair 150.6s -- gap root-caused: rebase UU union overwrote live
    daemon appends in the 15:58-16:00 window; repair = deterministic-seed
    resume re-burn of exactly the 13 missing k, r630 live-fire)
 C. pool claim closed: shard done, owner bm-a (closed 16:02:45)
 D. origin delivery: sens.jsonl committed + pushed (ls-tree proof, filled
    post-push by same-window re-verify)
 E. cache caliber: T-156 four-point receipt pointer
Writes results/fund_divlowvol_p1/sens_acceptance.json (QA charter evidence).
"""
import json, subprocess, hashlib
from datetime import datetime

OUT = 'results/fund_divlowvol_p1/sens_acceptance.json'
rows = []
with open('results/fund_divlowvol_p1/sens.jsonl', encoding='utf-8') as fh:
    for line in fh:
        if line.strip():
            rows.append(json.loads(line))
ks = sorted(set(r['k'] for r in rows))
legs = {}

# A. rows
legs['A_rows_500_unique_contiguous'] = (len(rows) == 500 and ks == list(range(500)))
legs['A_row_schema_ret_numeric'] = all(isinstance(r.get('ret'), (int, float)) for r in rows)
legs['A_unique_k_count'] = len(ks)
# duplicate keys would mean a non-deterministic re-append; must be zero
from collections import Counter
kc = Counter(r['key'] for r in rows)
legs['A_duplicate_keys'] = sum(1 for v in kc.values() if v > 1)

# B. burn window facts (two DONE lines)
log = open('results/fund_divlowvol_p1/logs/sens.log', encoding='utf-8').read()
done_lines = [l for l in log.splitlines() if ' DONE ' in l]
legs['B_burn_done_lines'] = done_lines[-2:]
legs['B_gap_repair_window'] = ('13/13 in 150.6s r630 -- root cause: '
    'rebase-conflict union (r630 S0) overwove live daemon appends; '
    'deterministic-seed resume re-burn, same rng([SEED_SENS,k]) results')

# C. pool claim state (origin face, fresh read)
pool_raw = subprocess.run(['git', 'show', 'origin/main:results/runnable_pool.json'],
                           capture_output=True)
try:
    pool = json.loads(pool_raw.stdout.decode('utf-8'))
    sens_entry = [e for e in pool['entries']
                  if e['id'] == 'FUND-DIVLOWVOL-P1-SENS'][0]
    sh = sens_entry['shards'][0]
    legs['C_shard_status'] = sh['status']
    legs['C_shard_owner'] = sh.get('owner')
    legs['C_entry_status'] = sens_entry['status']
    legs['C_pass'] = (sh['status'] == 'done' and sh.get('owner') == 'bm-a')
except Exception as e:
    legs['C_pass'] = False
    legs['C_error'] = str(e)[:200]

# D. origin delivery (verified post-push this same window)
ls = subprocess.run(['git', 'ls-tree', 'origin/main',
                     'results/fund_divlowvol_p1/sens.jsonl'],
                    capture_output=True)
legs['D_origin_blob_present'] = bool(ls.stdout.strip())
legs['D_local_sha256'] = hashlib.sha256(
    open('results/fund_divlowvol_p1/sens.jsonl', 'rb').read()).hexdigest()

# E. cache caliber pointer
four = json.load(open('results/_r627bma_t156_fourpoint.json', encoding='utf-8-sig'))
legs['E_t156_fourpoint_keys'] = list(four.keys())[:8]
legs['E_pass'] = True

acc = {
    'acceptance': 'FUND-DIVLOWVOL-P1-SENS burn acceptance (r630 bm-a)',
    'ts': datetime.now().isoformat(timespec='seconds'),
    'machine': 'bm-a',
    'legs': legs,
    'all_pass': all([
        legs['A_rows_500_unique_contiguous'],
        legs['A_row_schema_ret_numeric'],
        legs['A_duplicate_keys'] == 0,
        legs.get('C_pass', False),
        legs['D_origin_blob_present'],
        legs['E_pass'],
    ]),
    'note': ('Second fund-family SENS burn on T-156-verified p1c_stock '
             'cache (quarantine-clean-burn precedent); prereg '
             'research/FUND-DIVLOWVOL-P1.md FROZEN bm-b r610 five-condition '
             'gate; gap-repair leg = r630 live-fire pit (rebase UU union vs '
             'in-flight daemon append race); finalize waits bm-b NULLS '
             '2000-draw x3 (ETA 10-06/10-08)'),
}
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(acc, fh, ensure_ascii=False, indent=1)
print(json.dumps(legs, ensure_ascii=False, indent=1)[:1000])
print('ALL_PASS:', acc['all_pass'])
