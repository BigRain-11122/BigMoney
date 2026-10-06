# r780 bm-b rebase UU resolver: results/pool_core_samples.jsonl (append-log, r188/r217 union law)
# rebase window: stage2 = onto side (origin tip), stage3 = replayed bm-b commit (r782/r764 stage-semantics law)
# r758 law: jsonl independent observation events -> union dedup + stable ts sort when ts key present
import subprocess, json, sys

P = 'results/pool_core_samples.jsonl'

def blob(stage_ref):
    r = subprocess.run(['git', 'show', stage_ref], capture_output=True)
    if r.returncode != 0:
        print('FAIL: git show', stage_ref, r.stderr.decode('utf-8', 'replace')[:200]); sys.exit(2)
    return r.stdout.decode('utf-8')

a_raw = blob(':2:' + P)
b_raw = blob(':3:' + P)
a, b = a_raw.splitlines(), b_raw.splitlines()

seen, out = set(), []
for l in a + b:
    if l.strip() and l not in seen:
        seen.add(l); out.append(l)

# parse-verify each line (r185 law) and collect ts if universally present
ts_list = []
for l in out:
    try:
        obj = json.loads(l)
    except Exception as e:
        print('FAIL: non-json line:', repr(l[:120])); sys.exit(2)
    ts = None
    if isinstance(obj, dict):
        for k in ('ts', 'timestamp', 'time', 'utc'):
            v = obj.get(k)
            if isinstance(v, (int, float)):
                ts = v; break
            if isinstance(v, str) and len(v) >= 10:
                ts = v; break
    ts_list.append((ts, l))

if all(t is not None for t, _ in ts_list):
    ts_list.sort(key=lambda x: x[0])  # stable sort
    out = [l for _, l in ts_list]
    print('ts stable-sort applied')

nl = '\r\n' if a_raw.endswith('\r\n') or '\r\n' in a_raw[:2000] else '\n'
data = nl.join(out) + nl
# write-back mirror newline translation (r223/r234: detect producer format)
with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(data)

# post-verify: reparse whole file
with open(P, 'r', encoding='utf-8') as f:
    lines = [x for x in f.read().splitlines() if x.strip()]
for l in lines:
    json.loads(l)
assert len(lines) == len(out), 'line count drift'
print('union OK: |onto|=%d |replay|=%d -> union=%d (dedup removed %d)' % (len(a), len(b), len(out), len(a) + len(b) - len(out)))
