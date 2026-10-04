# r710 bm-a judge-finalize pre-flight dup probe (r482 zero-dup-id law, read-only zero-ledger)
# 12/12 shard ckpt vs JUDGE_STATE kept set: unique ids, 0 dup, 0 missing, 0 poison (grammar sanity).
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'results', 'n2_w15')
CKPT = os.path.join(RES, 'checkpoint')

state = json.load(open(os.path.join(RES, 'n2_w15_judge_state.json'), encoding='utf-8'))
kept = sorted(state['collapse']['kept'])
n_judge = state['n_judge_cells']

shards = sorted(f for f in os.listdir(CKPT)
                if f.startswith('n2_w15_judge_shard_') and f.endswith('.jsonl'))
rows = []
for f in shards:
    with open(os.path.join(CKPT, f), encoding='utf-8') as fh:
        for ln in fh:
            if ln.strip():
                rows.append(json.loads(ln))

ids = [r.get('cell_id') for r in rows]
dups = [i for i in set(ids) if ids.count(i) > 1]
kept_set = set(kept)
seen = set(ids)
missing = [c for c in kept if ('JUDGE|%s' % c) not in seen]
extra = [c for c in seen if c.split('JUDGE|', 1)[-1] not in kept_set and c not in kept_set]

# poison scan: each row must be a dict with cell_id + numeric fields parseable
poison = []
for r in rows:
    if not isinstance(r, dict) or 'cell_id' not in r:
        poison.append(str(r)[:60])
        continue
    for k in ('ret_cAGR6', 'ret_cAGR12', 'ret_cAGR24', 'sharpe6', 'sharpe12', 'sharpe24'):
        v = r.get(k)
        if v is not None and not isinstance(v, (int, float)):
            poison.append('%s:%s' % (r['cell_id'], k))

verdict = {
    'probe': 'judge-finalize pre-flight dup probe (r482 law)',
    'n_shard_files': len(shards), 'n_rows': len(rows),
    'n_kept_expected': len(kept), 'n_judge_state_field': n_judge,
    'n_unique_ids': len(seen), 'n_dup_ids': len(dups),
    'n_missing_vs_kept': len(missing), 'n_extra_beyond_kept': len(extra),
    'n_poison_rows': len(poison),
    'shard_files': shards,
    'dup_ids_sample': sorted(dups)[:5], 'missing_sample': missing[:5],
    'poison_sample': poison[:5],
}
ok = (len(shards) == 12 and len(rows) == len(kept) == n_judge
      and not dups and not missing and not extra and not poison)
verdict['verdict'] = 'GREEN_FINALIZE_READY' if ok else 'RED_HOLD'
json.dump(verdict, open(os.path.join(ROOT, 'results', '_r710bma_judge_dup_probe.json'), 'w',
                        encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
os.write
print(json.dumps(verdict, ensure_ascii=False)[:400])
sys.exit(0 if ok else 2)
