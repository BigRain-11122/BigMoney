# r674 bm-a S0 pre-alignment probe: shared dirty face crash_fuse.json local vs origin per-key freshness
import json, subprocess, sys

def git_show_blob(path):
    r = subprocess.run(['git', 'show', 'origin/main:' + path], capture_output=True)
    if r.returncode != 0:
        print('GIT_SHOW_FAIL', path, r.stderr.decode('utf-8', 'replace')[:200]); sys.exit(2)
    return r.stdout

local = json.load(open('results/crash_fuse.json', 'rb'))
origin = json.loads(git_show_blob('results/crash_fuse.json'))

keys = sorted(set(local) | set(origin))
local_newer, origin_newer, same, only_local, only_origin = [], [], [], [], []
for k in keys:
    lv, ov = local.get(k, None), origin.get(k, None)
    if k not in origin: only_local.append(k); continue
    if k not in local: only_origin.append(k); continue
    if lv == ov: same.append(k); continue
    # per-key ts compare (dict entries carry ts-ish fields)
    def ts(v):
        if isinstance(v, dict):
            for f in ('ts', 'last_crash_ts', 'cleared_ts', 'updated', 'time'):
                if f in v and isinstance(v[f], str): return v[f]
            return json.dumps(v, sort_keys=True)
        return str(v)
    lt, ot = ts(lv), ts(ov)
    if lt > ot: local_newer.append((k, lt, ot))
    elif ot > lt: origin_newer.append((k, lt, ot))
    else: same.append(k)

out = {
    'same': same, 'only_local': only_local, 'only_origin': only_origin,
    'local_newer': local_newer, 'origin_newer': origin_newer,
    'n_keys_local': len(local), 'n_keys_origin': len(origin),
}
open('results/_r674bma_s0_probe.json', 'wb').write(json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))
print(json.dumps(out, ensure_ascii=False)[:2000])
