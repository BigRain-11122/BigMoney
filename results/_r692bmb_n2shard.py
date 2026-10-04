# r692 bm-b probe: N2-W15 dual-shard full detail + pool diff since HEAD~1 + autofill state
import json, subprocess

out = {}
d = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in d.get('entries', []):
    if e.get('id') == 'PERPETUAL-N2-W15-GENERATE':
        out['n2_entry_core'] = {k: e.get(k) for k in ('status', 'owner', 'owner_since', 'owner_note', 'note') if k in e}
        sh = e.get('shards')
        out['n2_shards_full'] = sh

# what did origin change in runnable_pool.json (merge brought bm-a r695)
r = subprocess.run(['git', 'diff', 'HEAD~3', 'HEAD', '--', 'results/runnable_pool.json'],
                   capture_output=True, text=True, encoding='utf-8')
out['pool_diff_since_merge_base'] = (r.stdout or '')[:1800]

# my autofill daemon state
try:
    a = json.load(open('results/autofill_state.bm-b.json', encoding='utf-8'))
    out['autofill_bm_b'] = {k: a.get(k) for k in list(a.keys())[:14]}
except Exception as ex:
    out['autofill_bm_b_err'] = str(ex)

with open('results/_r692bmb_n2shard.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:2600])
