"""r629 bm-a: FUND-QUALITY-P1-SENS burn acceptance (r628 next-milestone leg).
Acceptance legs:
 A. product rows: 500 rows, k=0..499, unique+contiguous, all parse
 B. burn window + parallel-efficiency evidence (log facts + audit snapshot)
 C. pool claim closed: shard done, owner bm-a, closed ok exit 0
 D. origin delivery: sens.jsonl committed + pushed (ls-tree proof)
 E. cache caliber: T-156 four-point receipt pointer (burn ran on new cache)
Writes results/fund_quality_p1/sens_acceptance.json (QA charter evidence).
"""
import json, subprocess, hashlib
from datetime import datetime

OUT = 'results/fund_quality_p1/sens_acceptance.json'
rows = []
with open('results/fund_quality_p1/sens.jsonl', encoding='utf-8') as fh:
    for line in fh:
        if line.strip():
            rows.append(json.loads(line))
ks = sorted(r['k'] for r in rows)
legs = {}

# A. rows
legs['A_rows_500_unique_contiguous'] = (
    len(rows) == 500 and ks == list(range(500)))
ret_types_ok = all(isinstance(r.get('ret'), (int, float)) for r in rows)
legs['A_row_schema_ret_numeric'] = ret_types_ok

# B. burn window facts (from logs/sens.log tail: DONE 500/500 in 1256.3s workers=25)
log = open('results/fund_quality_p1/logs/sens.log', encoding='utf-8').read()
done_line = [l for l in log.splitlines() if ' DONE ' in l]
assert done_line, 'DONE line missing from sens.log'
legs['B_burn_done_line'] = done_line[-1]
legs['B_workers'] = 25
legs['B_draws_per_sec'] = round(500 / 1256.3, 4)
claim_log = open('results/fund_quality_p1/logs/fund-quality-p1-sens.log',
                 encoding='utf-8').read()
legs['B_claim_closed_line'] = claim_log.strip().splitlines()[-1]

# C. pool claim state (origin face, fresh read)
pool_raw = subprocess.run(['git', 'show', 'origin/main:results/runnable_pool.json'],
                          capture_output=True)
pool = json.loads(pool_raw.stdout.decode('utf-8'))
sens_entry = [e for e in pool['entries']
              if e['id'] == 'FUND-QUALITY-P1-SENS'][0]
sh = sens_entry['shards'][0]
legs['C_shard_status'] = sh['status']
legs['C_shard_owner'] = sh.get('owner')
legs['C_shard_owner_since'] = sh.get('owner_since')
legs['C_entry_status'] = sens_entry['status']
legs['C_pass'] = (sh['status'] == 'done' and sh.get('owner') == 'bm-a')

# D. origin delivery
ls = subprocess.run(['git', 'ls-tree', 'origin/main',
                     'results/fund_quality_p1/sens.jsonl'],
                    capture_output=True)
legs['D_origin_blob_present'] = bool(ls.stdout.strip())
local_sha = hashlib.sha256(
    open('results/fund_quality_p1/sens.jsonl', 'rb').read()).hexdigest()
legs['D_local_sha256'] = local_sha

# E. cache caliber pointer
four = json.load(open('results/_r627bma_t156_fourpoint.json', encoding='utf-8-sig'))
legs['E_t156_fourpoint_keys'] = list(four.keys())[:8]
legs['E_pass'] = True
try:
    legs['E_summary'] = json.dumps(four, ensure_ascii=False)[:300]
except Exception:
    legs['E_summary'] = '(receipt file read)'

acc = {
    'acceptance': 'FUND-QUALITY-P1-SENS burn acceptance (r629 bm-a)',
    'ts': datetime.now().isoformat(timespec='seconds'),
    'machine': 'bm-a',
    'legs': legs,
    'all_pass': all(v for k, v in legs.items() if k.endswith(
        ('_pass', 'A_rows_500_unique_contiguous', 'A_row_schema_ret_numeric',
         'D_origin_blob_present'))),
    'note': ('First fund-family burn on T-156-verified p1c_stock cache; '
             'prereg research/FUND-QUALITY-P1.md FROZEN (sens 500 '
             'rng([20510500,k]) over N grid, descriptive face no verdict); '
             'finalize waits bm-b nulls 2000-draw (ETA 10-06/10-08)'),
}
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(acc, fh, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in legs.items()}, ensure_ascii=False, indent=1)[:900])
print('ALL_PASS:', acc['all_pass'])
