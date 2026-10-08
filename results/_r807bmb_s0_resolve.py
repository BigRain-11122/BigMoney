# r807 bm-b S0 rebase UU resolver (canonical recipes per bigmoney-conflict-resolve SKILL.md)
# Conflicts: pick 762069faa (r806) replay onto origin de1ad11f9 (bm-c r784 window)
# 1. results/fund_divlowvol_p1/nulls.jsonl  (append-log)  -> key-unique union == theirs (probe-verified superset)
# 2. results/compute_audit.json             (rolling-ledger) -> history ts-union + latest take-new(ours)
# 3. results/update_status.json             (snapshot)    -> take-new whole doc (ours, deep ts probe)
# 4. fleet/backlog.md                       (UNKNOWN->manual: claim collision) -> HEAD side per fleet/README.md S4
#    (bm-a claim 10-07T22:33 landed origin first via 84badf07d; bm-b r806 self-claim 10-08 23:30 later-comer yields)
import json, subprocess, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
receipt = {}

def blob_bytes(stage, path):
    r = subprocess.run(['git', '-C', REPO, 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'blob read fail {stage}:{path}: {r.stderr[:200]}')
    return r.stdout

def write_bytes(path, data):
    with open(REPO + '\\' + path.replace('/', '\\'), 'wb') as f:
        f.write(data)

# ---------- 1) nulls.jsonl: key-unique union ----------
p = 'results/fund_divlowvol_p1/nulls.jsonl'
ours_b, theirs_b = blob_bytes(2, p), blob_bytes(3, p)
ol = [l for l in ours_b.decode('utf-8').splitlines() if l.strip()]
tl = [l for l in theirs_b.decode('utf-8').splitlines() if l.strip()]
seen = {}
for l in ol + tl:  # ours first; later identical lines collapse; probe showed zero content diffs
    seen[l] = True
union_lines = list(seen.keys())
# canonical order: sort by k numeric embedded in key field
def knum(l):
    d = json.loads(l)
    return int(d.get('k') if d.get('k') is not None else d['key'].split('|')[1])
union_lines.sort(key=knum)
out = ('\n'.join(union_lines) + '\n').encode('utf-8')
write_bytes(p, out)
receipt[p] = {'recipe': 'append-log key-unique union', 'ours_lines': len(ol), 'theirs_lines': len(tl),
              'union_unique': len(union_lines), 'note': 'probe: ours 183 intra-dups + missing null|1972; theirs=2000/2000 healed dual-flip verified superset'}
assert len(union_lines) == 2000, f'expect 2000, got {len(union_lines)}'
for l in union_lines:
    json.loads(l)

# ---------- 2) compute_audit.json: rolling-ledger ----------
p = 'results/compute_audit.json'
ours = json.loads(blob_bytes(2, p).decode('utf-8'))
theirs = json.loads(blob_bytes(3, p).decode('utf-8'))
oh, th = ours['history'], theirs['history']
by_ts = {}
for e in th + oh:  # theirs older range first, ours newer range after
    by_ts[e['ts']] = e
union_hist = [by_ts[k] for k in sorted(by_ts.keys())]
latest_new = 'ours' if ours['latest']['ts'] >= theirs['latest']['ts'] else 'theirs'
merged = {'history': union_hist, 'latest': ours['latest'] if latest_new == 'ours' else theirs['latest']}
txt = json.dumps(merged, indent=2, ensure_ascii=False)
# mirror producer trailing-newline style of ours blob
trailer = '\n' if blob_bytes(2, p).endswith(b'\n') else ''
write_bytes(p, (txt + trailer).encode('utf-8'))
receipt[p] = {'recipe': 'rolling-ledger history ts-union + latest take-new', 'ours_hist': len(oh), 'theirs_hist': len(th),
              'union': len(union_hist), 'latest_side': latest_new, 'latest_ts': merged['latest']['ts']}
# verify round-trip
assert json.loads(open(REPO + '\\' + p.replace('/', '\\'), 'rb').read().decode('utf-8')) == merged

# ---------- 3) update_status.json: snapshot take-new ----------
p = 'results/update_status.json'
ours_b, theirs_b = blob_bytes(2, p), blob_bytes(3, p)
o_ts = json.loads(ours_b.decode('utf-8')).get('updated')
t_ts = json.loads(theirs_b.decode('utf-8')).get('updated')
winner = 'ours' if o_ts >= t_ts else 'theirs'
write_bytes(p, ours_b if winner == 'ours' else theirs_b)
receipt[p] = {'recipe': 'snapshot take-new', 'ours_updated': o_ts, 'theirs_updated': t_ts, 'winner': winner}
json.loads(open(REPO + '\\' + p.replace('/', '\\'), 'rb').read().decode('utf-8'))

# ---------- 4) fleet/backlog.md: HEAD-side (claim collision, later-comer yields) ----------
p = 'fleet/backlog.md'
work = open(REPO + '\\fleet\\backlog.md', 'rb').read().decode('utf-8')
lines = work.split('\n')
outl, mode = [], 'copy'
for ln in lines:
    if ln.startswith('<<<<<<< HEAD'):
        mode = 'head'; continue
    if ln.startswith('======') and mode == 'head':
        mode = 'skip'; continue
    if ln.startswith('>>>>>>>'):
        mode = 'copy'; continue
    if mode == 'skip':
        continue
    outl.append(ln)
write_bytes(p, ('\n'.join(outl)).encode('utf-8'))
receipt[p] = {'recipe': 'UNKNOWN->manual claim-collision, HEAD side (fleet/README.md S4 later-comer yields)',
              'note': 'bm-a claim 10-07T22:33 origin-first (84badf07d) wins; bm-b r806 self-claim 10-08 23:30 yields; T-94 ownership=bm-a'}
txt = open(REPO + '\\fleet\\backlog.md', 'rb').read().decode('utf-8')
assert '<<<<<<<' not in txt and '>>>>>>>' not in txt and 'bm-b@2026-10-08 23:30' not in txt

# ---------- receipt ----------
rec_path = REPO + r'\results\_r807bmb_s0_resolve_receipt.json'
with open(rec_path, 'w', encoding='utf-8') as f:
    json.dump({'round': 'r807-bm-b S0', 'rebase': 'pick 762069faa onto de1ad11f9', 'files': receipt}, f, indent=2, ensure_ascii=False)
print('RESOLVE-OK')
for k, v in receipt.items():
    print(k, '->', v['recipe'], {kk: vv for kk, vv in v.items() if kk != 'recipe' and kk != 'note'})
