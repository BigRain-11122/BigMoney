"""r414 bm-b: W6-JUDGE judge-0of1 shard done-flip (pit-89 burn-round-same-flip law).
Entry stays ready for judge-finalize (separate round work per frozen data_gates);
shard face flips done with burn receipt. Idempotent: re-run safe (checks status).
"""
import json
import sys

POOL = 'results/runnable_pool.json'
CKPT = 'results/trial_labor_w6/checkpoint/judge_shard_0of1.jsonl'

# verify checkpoint before flipping (fail-closed)
n, ids = 0, set()
with open(CKPT, encoding='utf-8') as fh:
    for ln in fh:
        if ln.strip():
            n += 1
            ids.add(json.loads(ln)['cell_id'])
screen = json.load(open('results/trial_labor_w6/w6_screen.json', encoding='utf-8'))
surv = list(screen['survivors'])
missing = [c for c in surv if 'JUDGE|' + c not in ids]
assert n == 293 and len(ids) == 293, f'checkpoint incomplete rows={n} ids={len(ids)}'
assert not missing, f'missing cells {missing[:3]}'
print(f'checkpoint verified: {n} rows / {len(ids)} distinct == survivors {len(surv)}')

d = json.load(open(POOL, encoding='utf-8'))
for e in d['entries']:
    if e['id'] != 'TRIAL-LABOR-W6-JUDGE':
        continue
    sh = e['shards'][0]
    if sh.get('status') == 'done':
        print('shard already done -- idempotent no-op')
        sys.exit(0)
    sh['status'] = 'done'
    sh['result_ref'] = (
        'results/trial_labor_w6/checkpoint/judge_shard_0of1.jsonl '
        '(293/293 cells, unique cell_id 293 == w6_screen survivors 293 verified r414 bm-b; '
        'burn 07:20:37->07:26:15 normal-exit 20 workers BelowNormal, runner log "judge shard 0of1 complete"; '
        'autofill tick claim 07:20:04 pid 14960 runner_sha 1d4083d2200afec1, legal stale-takeover per O-2100 s2.4 '
        '(prior owner bm-c claim 06:58:35 = 21.4min stale at tick, bm-c heartbeat 06:34:51); '
        'bm-c duplicate burn (if alive) = W1/W2 cross-kill contract harmless, finalize dedupes by cell_id)'
    )
    sh['note'] = (sh.get('note') or '') + (
        ' | r414 bm-b: shard burn complete + done-flip in burn-landing round (pit-89 law); '
        'judge-finalize = separate round work per frozen data_gates (entry face flips at finalize landing)'
    )
    print('shard flipped: done; entry status stays', e.get('status'))
    break

d['updated_at'] = '2026-09-29 07:33:00'  # autofill _now() space-format canon (MSG-0705: canonical writers use space format)
with open(POOL, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
# post-write verify
d2 = json.load(open(POOL, encoding='utf-8'))
e2 = [x for x in d2['entries'] if x['id'] == 'TRIAL-LABOR-W6-JUDGE'][0]
assert e2['shards'][0]['status'] == 'done'
assert e2['status'] == 'ready'
print('pool write verified: shard=done entry=ready')
