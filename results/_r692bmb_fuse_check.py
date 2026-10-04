# r692 bm-b probe6: crash fuse keepblock alignment for N2 generate (r626d-1 timing law)
# r691 edited scripts/perpetual_faces_n2.py at 20:05:52 -- fuse sig must == current file sha16
import json, hashlib, subprocess

out = {}
# current file sha16
with open('scripts/perpetual_faces_n2.py', 'rb') as f:
    sha = hashlib.sha256(f.read()).hexdigest()[:16]
out['current_runner_sha16'] = sha

# fuse faces (shared + lane)
for p in ('results/crash_fuse.json', 'results/crash_fuse.bm-b.json'):
    try:
        d = json.load(open(p, encoding='utf-8'))
        # find n2-related fuse records
        hits = {}
        def scan(obj, path=''):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if 'n2' in str(k).lower() or 'perpetual_faces_n2' in str(v)[:100] if not isinstance(v, (dict, list)) else False:
                        hits[path + '/' + k] = str(v)[:150]
                    scan(v, path + '/' + k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    scan(v, f'{path}[{i}]')
        scan(d)
        out[p] = hits if hits else {'top_keys': list(d.keys())[:12]}
    except Exception as ex:
        out[p] = {'err': str(ex)}

with open('results/_r692bmb_fuse_check.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:2000])
