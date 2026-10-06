# r772 bm-b merge resolver: 18-UU window (origin 6de9b69df absorbed mid-push, r759 phantom-delete law)
# 16 faces = ts-newer-wins -> git checkout --theirs (their S6 chain 10:49-10:52 newer than ours 10:46-10:48)
# 2 faces = rolling-ledger union (compute_audit history ts-key union + latest take-new;
#           regime_state history asof-key + transitions identity union, state fields base=theirs newer updated)
# Laws: r188/R208 union zero-loss, r140 same-second tie -> HEAD, r185 parse-verify before write,
#       r609 merge-window ours=HEAD: theirs=MERGE_HEAD:, assertion-form-matches-materialization (r611).
import subprocess, json

def blob(ref, path):
    r = subprocess.run(['git', 'show', ref + ':' + path], capture_output=True)
    assert r.returncode == 0, (ref, path, r.stderr[:200])
    return r.stdout

def detect(b):
    lines = b.split(b'\n')
    ind = (len(lines[1]) - len(lines[1].lstrip())) if len(lines) > 1 and lines[1].strip() else 1
    return ind, b.endswith(b'\n')

report = []

# ---- face 1: compute_audit.json (rolling-ledger union + latest take-new) ----
p = 'results/compute_audit.json'
ob, tb = blob('HEAD', p), blob('MERGE_HEAD', p)
o, t = json.loads(ob), json.loads(tb)
ind, tnl = detect(ob)
seen = {}
for e in o['history']:                      # ours first (r140 tie -> HEAD)
    seen[e['ts']] = e
for e in t['history']:
    if e['ts'] not in seen:
        seen[e['ts']] = e
merged_hist = sorted(seen.values(), key=lambda e: str(e['ts']))
latest = o['latest'] if str(o['latest'].get('ts', '')) >= str(t['latest'].get('ts', '')) else t['latest']
side = 'ours' if latest == o['latest'] else 'theirs'
out = json.dumps({'latest': latest, 'history': merged_hist}, ensure_ascii=False, indent=ind)
if tnl:
    out += '\n'
open(p, 'w', encoding='utf-8', newline='').write(out)
m2 = json.loads(open(p, encoding='utf-8').read())
assert len(m2['history']) == len(merged_hist), 'history roundtrip loss'
assert len(merged_hist) >= max(len(o['history']), len(t['history'])), 'union shrank'
report.append(f'{p}: history {len(o["history"])}+{len(t["history"])} -> {len(merged_hist)} ts-key union zero-loss; latest side={side} ts={latest.get("ts")}')

# ---- face 2: regime_state.json (state base=theirs newer; history/transitions union) ----
p = 'results/regime_state.json'
ob, tb = blob('HEAD', p), blob('MERGE_HEAD', p)
o, t = json.loads(ob), json.loads(tb)
assert str(t['updated']) >= str(o['updated']), 'theirs not newer -- recipe precondition violated'
merged = dict(t)                            # state fields take-new (base = theirs)
for k, keyfn in [('history', lambda e: e.get('asof')),
                 ('transitions', lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False))]:
    a, b = o.get(k, []), t.get(k, [])
    seen = {}
    for e in a + b:
        kk = keyfn(e)
        if kk not in seen:
            seen[kk] = e
    vals = list(seen.values())
    if k == 'history':
        vals = sorted(vals, key=lambda e: str(e.get('asof', '')))
    merged[k] = vals
    assert len(vals) >= max(len(a), len(b)), f'{k} union shrank'
ind, tnl = detect(tb)
out = json.dumps(merged, ensure_ascii=False, indent=ind)
if tnl:
    out += '\n'
open(p, 'w', encoding='utf-8', newline='').write(out)
m2 = json.loads(open(p, encoding='utf-8').read())
assert m2['updated'] == t['updated'], 'state field drift'
report.append(f'{p}: updated={t["updated"]} base=theirs; history {len(o.get("history",[]))}+{len(t.get("history",[]))} -> {len(merged["history"])}; transitions -> {len(merged["transitions"])}')

# ---- marker scan on resolved faces (r609: independent marker sweep, not --check) ----
import re
for p in ['results/compute_audit.json', 'results/regime_state.json']:
    raw = open(p, 'rb').read()
    for m in [b'<<<<<<<', b'=======', b'>>>>>>>']:
        assert m not in raw, f'leftover marker {m} in {p}'

print(json.dumps({'status': 'OK', 'report': report}, ensure_ascii=False, indent=1))
