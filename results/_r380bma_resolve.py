# r380 bm-a push-storm resolver: 3 snapshot faces (REPORT twins same-side coupling + fundamental_b_layer_filter take-new)
# Laws: r98/r99/r100 twins, r329 md byte-copy same-side, R216 fundamental take-new, R350 probe STAGED blobs (not worktree),
#       r100 key-normalize probe, r185 parse-verify before write, r209 no-PS-redirect (subprocess bytes).
import subprocess, json, re, sys

def stage_blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'stage {stage} missing for {path}: {r.stderr[:200]}')
    return r.stdout

def deep_ts_probe(obj, pat=r'^20\d{2}-'):
    # R350/r100 hardened probe: normalize keys stripping '_'/'-'; only values matching wall-clock shape; recurse nested.
    best = None
    def norm(k): return re.sub(r'[_\-]', '', k).lower()
    def walk(o, path):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                nk = norm(k)
                if isinstance(v, str) and re.match(pat, v) and ('ts' in nk or 'generated' in nk or 'updated' in nk or 'asof' in nk):
                    # wall-clock value must carry time-of-day for freshness ranking (R350)
                    if len(v) >= 16 and (':' in v):
                        if best is None or v > best[0]:
                            best = (v, path + [k])
                walk(v, path + [k])
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + [str(i)])
    walk(obj, [])
    return best

out = []

# 1) REPORT twins: json probe generated_at -> pick side; md byte-copy SAME side (r98/r99/r100 + r329)
jp = 'docs/daily_report/REPORT-2026-09-28.json'
mp = 'docs/daily_report/REPORT-2026-09-28.md'
o2 = stage_blob(2, jp); o3 = stage_blob(3, jp)
p2 = deep_ts_probe(json.loads(o2.decode('utf-8')))
p3 = deep_ts_probe(json.loads(o3.decode('utf-8')))
side = 2 if (p2 and (not p3 or p2[0] >= p3[0])) else 3
jbytes = stage_blob(side, jp); mbytes = stage_blob(side, mp)
json.loads(jbytes.decode('utf-8'))  # parse-verify r185
open(jp, 'wb').write(jbytes); open(mp, 'wb').write(mbytes)
out.append(f'REPORT twins -> side :{side}: json ts={ (p2 if side==2 else p3)[0] } vs other={ (p3 if side==2 else p2) and (p3 if side==2 else p2)[0] }; md byte-copy same side; parse-verified')

# 2) fundamental_b_layer_filter.json: take-new by updated ts (R216), probe both staged blobs
fp = 'results/fundamental_b_layer_filter.json'
f2 = stage_blob(2, fp); f3 = stage_blob(3, fp)
q2 = deep_ts_probe(json.loads(f2.decode('utf-8')))
q3 = deep_ts_probe(json.loads(f3.decode('utf-8')))
fside = 2 if (q2 and (not q3 or q2[0] >= q3[0])) else 3
fb = stage_blob(fside, fp)
json.loads(fb.decode('utf-8'))
open(fp, 'wb').write(fb)
out.append(f'fundamental_b_layer_filter -> side :{fside}: ts={ (q2 if fside==2 else q3)[0] } vs other={ (q3 if fside==2 else q2) and (q3 if fside==2 else q2)[0] }; parse-verified')

# marker scan on all 3 written files (zero unresolved conflict markers)
for p in (jp, mp, fp):
    b = open(p, 'rb').read()
    assert b.count(b'<<<<<<<') == 0 and b.count(b'>>>>>>>') == 0, f'markers remain in {p}'
out.append('marker-scan: 3/3 clean')

for line in out:
    print(line)
