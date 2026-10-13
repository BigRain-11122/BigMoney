import subprocess, json, sys

GIT = r'C:\Program Files\Git\cmd\git.exe'


def run(args, check=True):
    r = subprocess.run([GIT] + args, capture_output=True, encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        print('GIT FAIL', args, (r.stderr or '')[:200])
        sys.exit(2)
    return r.stdout


def stage_shas(path):
    d = {}
    for line in run(['ls-files', '-u', '--', path]).strip().splitlines():
        p = line.split()
        d[int(p[2])] = p[1]
    return d


def blob(path, stage):
    shas = stage_shas(path)
    if stage not in shas:
        print(f'MISSING stage {stage} for {path}')
        sys.exit(2)
    return json.loads(run(['cat-file', '-p', shas[stage]]))


def wjson(path, obj):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


# rebase window stage semantics (r782 law): stage3 = pick side (our r921 commit), stage2 = onto side (origin lineage)
P1 = 'results/_attrition_guard_scan.json'
a2, a3 = blob(P1, 2), blob(P1, 3)
w1 = a3 if a3.get('ts', '') >= a2.get('ts', '') else a2
wjson(P1, w1)
print(f'{P1}: pick(st3) ts={a3.get("ts")} vs onto(st2) ts={a2.get("ts")} -> newer-wins ts={w1.get("ts")}')

P2 = 'results/compute_audit.json'
o, t = blob(P2, 2), blob(P2, 3)


def row_key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)


union, seen = [], set()
for r in t.get('history', []) + o.get('history', []):
    k = row_key(r)
    if k not in seen:
        seen.add(k)
        union.append(r)
latest = t['latest'] if t['latest'].get('ts', '') > o['latest'].get('ts', '') else o['latest']
wjson(P2, {'latest': latest, 'history': union})
print(f'{P2}: union {len(o.get("history", []))}+{len(t.get("history", []))} -> {len(union)}, latest ts={latest.get("ts")} (r921 resolve2 pattern)')

P3 = 'results/token_usage.json'
u2, u3 = blob(P3, 2), blob(P3, 3)
g2, g3 = u2.get('generated', ''), u3.get('generated', '')
w3 = u3 if g3 >= g2 else u2
wjson(P3, w3)
print(f'{P3}: pick generated={g3} vs onto generated={g2} -> newer-wins={g3 if g3 >= g2 else g2}')

for p in (P1, P2, P3):
    txt = open(p, encoding='utf-8').read()
    json.loads(txt)
    for m in ('<<<<<<<', '=======', '>>>>>>>'):
        if m in txt:
            print('MARKER PRESENT', p, m)
            sys.exit(2)
print('RESOLVE OK: 3 faces explicit blob-merged, JSON-valid, marker-free')
