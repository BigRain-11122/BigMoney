# r798 bm-b rebase conflict resolver (canon: bigmoney-conflict-resolve SKILL; r792 deep-ts probe lineage)
# 9 UU faces = dual-machine S6 same-window write collision (bm-a r811 in-flight)
# scorecard_v1/strategy_scorecard = take ours (:2 = bm-a host-authoritative per r378 single-writer law)
# other snapshots = take-new by deep ts probe; same-second tie -> ours per r140
import json, re, subprocess

def blob(stage, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None

UU = []
st = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, encoding='utf-8').stdout
for line in st.splitlines():
    if line.startswith('UU '):
        UU.append(line[3:].strip())

HOST_OURS = {'results/scorecard_v1.json', 'results/strategy_scorecard.json'}
TS_KEYS = ['ts', 'generated', 'generated_at', 'updated', 'scan_ts', 'written_at']

def deep_ts(raw):
    try:
        d = json.loads(raw.decode('utf-8'))
    except Exception:
        return None
    best = None
    def walk(v):
        nonlocal best
        if isinstance(v, dict):
            for k, x in v.items():
                if k in TS_KEYS and isinstance(x, str) and re.match(r'^\d{4}-\d{2}-\d{2}T', x):
                    if best is None or x > best:
                        best = x
                else:
                    walk(x)
        elif isinstance(v, list):
            for x in v[:5]:
                walk(x)
    walk(d)
    return best

resolved, log = {}, []
for p in UU:
    ours, theirs = blob(2, p), blob(3, p)
    if ours is None or theirs is None:
        resolved[p] = theirs if ours is None else ours
        log.append((p, 'single-side', 'theirs' if ours is None else 'ours'))
        continue
    if p in HOST_OURS:
        resolved[p] = ours
        log.append((p, 'host-authoritative-ours', 'r378 bm-a single-writer'))
        continue
    if p.endswith('.json'):
        to, tt = deep_ts(ours), deep_ts(theirs)
        if to and tt:
            if tt > to:
                resolved[p] = theirs; log.append((p, 'take-new-theirs', '%s > %s' % (tt, to)))
            else:
                resolved[p] = ours; log.append((p, 'take-new-ours-tie-or-newer', '%s >= %s' % (to, tt)))
            continue
    # .md twins and ts-less faces: side with newer byte length heuristic rejected -> follow json twin when present
    twin = p[:-3] + '.json' if p.endswith('.md') else None
    if twin and twin in resolved:
        resolved[p] = blob(2 if resolved[twin] == ours else 3, p)
        log.append((p, 'follow-json-twin', twin))
        continue
    resolved[p] = ours
    log.append((p, 'fallback-ours', 'no ts keys / no twin'))

for p, raw in resolved.items():
    if p.endswith('.json'):
        json.loads(raw.decode('utf-8'))  # parse-validate before write-back (r185)
    with open(p, 'wb') as f:
        f.write(raw)

with open('results/_r798bmb_rebase_resolve.json', 'w', encoding='utf-8') as f:
    json.dump({'faces': [{'path': p, 'recipe': r, 'note': n} for p, r, n in log]}, f, ensure_ascii=False, indent=1)
for row in log:
    print(row)
