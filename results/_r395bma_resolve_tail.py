# r395 bm-a tail resolver: fundamental_b_layer_filter (snapshot take-new by deep-ts) + daily_report twins
# (json face generated_at deep-probe ts-diffpick whole-bytes; md face copy bytes from SAME side blob; r327/r329 law)
# fail-closed: any anomaly -> print + exit 2, no blind writes.
import subprocess, json, sys, re

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'blob read fail {stage} {path}: {r.stderr[:200]}')
    return r.stdout

TS_RE = re.compile(rb'^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}')

def deep_probe_ts(obj, best=b''):
    # recursive newest-ts probe over bytes values (r311/D-09 law: ts lives in nested layers)
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_probe_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_probe_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj.encode()):
        if obj.encode() > best:
            best = obj.encode()
    return best

def resolve_snapshot(path):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a), json.loads(b)
    ta, tb = deep_probe_ts(ja), deep_probe_ts(jb)
    if not ta or not tb:
        raise SystemExit(f'{path}: ts probe empty ours={ta} theirs={tb} -- fail-closed')
    side = 2 if ta >= tb else 3
    pick = a if side == 2 else b
    json.loads(pick)  # parse-verify r185
    with open(path, 'wb') as f:
        f.write(pick)
    print(f'{path}: ours_ts={ta.decode()} theirs_ts={tb.decode()} -> take {"ours(:2)" if side==2 else "theirs(:3)"} whole-face')

def resolve_twins(json_path, md_path):
    a, b = blob(2, json_path), blob(3, json_path)
    ja, jb = json.loads(a), json.loads(b)
    ta, tb = deep_probe_ts(ja), deep_probe_ts(jb)
    if not ta or not tb:
        raise SystemExit(f'{json_path}: generated ts probe empty ours={ta} theirs={tb}')
    side = 2 if ta >= tb else 3
    jpick = a if side == 2 else b
    json.loads(jpick)
    with open(json_path, 'wb') as f:
        f.write(jpick)
    md = blob(side, md_path)  # same-side bytes直拷 (r329: md twin is not JSON, no json.loads)
    with open(md_path, 'wb') as f:
        f.write(md)
    print(f'twins: json ours_ts={ta.decode()} theirs_ts={tb.decode()} -> side {"ours(:2)" if side==2 else "theirs(:3)"}; md copied same-side bytes ({len(md)}B)')

resolve_snapshot('results/fundamental_b_layer_filter.json')
resolve_twins('docs/daily_report/REPORT-2026-09-28.json', 'docs/daily_report/REPORT-2026-09-28.md')
print('tail resolver done')
