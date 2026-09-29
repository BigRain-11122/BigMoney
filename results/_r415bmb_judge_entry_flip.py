"""r415 bm-b: W6-JUDGE entry done-flip at judge-finalize landing (pit-89 law:
finalize landing round MUST flip entry face same-round; shard already done r414).
Fail-closed: refuses unless w6_judge.json product is on disk and coherent.
Idempotent: re-run safe (checks status)."""
import json
import sys
import time

POOL = 'results/runnable_pool.json'
JUDGE = 'results/trial_labor_w6/w6_judge.json'

# fail-closed product verification before flipping
j = json.load(open(JUDGE, encoding='utf-8'))
n = j['n_judged_cells']
elig = j.get('n_eligible_g2')
ledger = j.get('trials_ledger') or {}
assert n == 293, f'judged cells {n} != 293 survivors'
assert ledger.get('file') == 'w6_judge.json', 'ledger face mismatch: ' + str(ledger)
print(f'w6_judge.json verified: {n} judged, E[FP]={j["n_wave_disclosure"]["E_FP_nominal_5pct"]}, '
      f'G2 eligible {elig}, ledger total {ledger.get("total")}')

d = json.load(open(POOL, encoding='utf-8'))
for e in d['entries']:
    if e['id'] != 'TRIAL-LABOR-W6-JUDGE':
        continue
    if e.get('status') == 'done':
        print('entry already done -- idempotent no-op')
        sys.exit(0)
    assert e['shards'][0].get('status') == 'done', 'shard not done (inconsistent)'
    e['status'] = 'done'
    e['finished_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
    e['note'] = (e.get('note') or '') + (
        ' | r415 bm-b: judge-finalize LANDED (w6_judge.json 293 judged cells, E[FP] '
        + str(j['n_wave_disclosure']['E_FP_nominal_5pct'])
        + ', G2 eligible ' + str(elig)
        + ', trials ledger total ' + str(ledger.get('total'))
        + ' cross-wave cumulative no-reset); entry done-flip same round per pit-89 law '
        '(shard done r414 burn round; 48h CEO report clock starts at this finalize).'
    )
    print('entry flipped: done @', e['finished_at'])
    break

d['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')  # autofill _now() space-format canon (MSG-0705)
with open(POOL, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
# post-write verify
d2 = json.load(open(POOL, encoding='utf-8'))
e2 = [x for x in d2['entries'] if x['id'] == 'TRIAL-LABOR-W6-JUDGE'][0]
assert e2['status'] == 'done' and e2['shards'][0]['status'] == 'done'
print('pool write verified: entry=done shard=done')
