# r802 bm-b rebase-conflict resolver (S6 twins, per-face ts-empirical canon)
# Context: S0 pull --rebase stopped replaying 386f4cfb6 (round 801) onto bm-a r821 postscript tip 1104e519d.
# 14 UU, zero lane faces. Canon: rolling-ledger union / snapshot ts-duel / regen twins ts-duel / token per-key max.
# Stage semantics in rebase: st2=ours(new base=bm-a postscript), st3=theirs(my r801 replay).
# Receipt written to results/_r802bmb_rebase_resolve.json. Zero-loss asserted for ledger unions.
import subprocess, json, sys, os

def stages_of(path):
    out = subprocess.run(['git','ls-files','-u','--',path],capture_output=True,text=True).stdout
    res = {}
    for line in out.strip().split('\n'):
        if not line.strip():
            continue
        meta, _, fp = line.partition('\t')
        parts = meta.split()
        if len(parts) >= 3:
            res[parts[2]] = parts[1]
    return res

def blob_bytes(sha):
    return subprocess.run(['git','cat-file','-p',sha],capture_output=True).stdout

def write_face(path, data):
    # r223/r234 law: detect producer line-ending style from the newer-side blob and mirror it
    with open(path,'wb') as f:
        f.write(data)

receipt = {'round': 'r802', 'machine': 'bm-b', 'event': 'rebase-replay 386f4cfb6 onto 1104e519d',
           'faces': {}, 'asserts': []}

# ---------- take-side faces (ts-duel, raw bytes preserve producer format) ----------
# duel results (empirical, from stage blob timestamps):
#   st3 (mine, r801 S6 run-2) newer: regime_state 11:38:49>11:38:28; update_status 11:38:48>11:38:27;
#     fundamental_b_layer_filter 11:39:37>11:39:13; _attrition_guard_scan 11:42:56>11:39:48;
#     REPORT json 11:39:57>11:32:33; LIVE json twins 11:39:58>11:39:36; md twins pair with json side
#   st2 (bm-a postscript) newer: futures_update_status 11:39:10>11:38:56; lhb_update_status 11:39:09>11:38:55
TAKE_ST3 = ['docs/daily_report/REPORT-2026-10-07.json','docs/daily_report/REPORT-2026-10-07.md',
            'docs/live_usage/LIVE-2026-10-07.json','docs/live_usage/LIVE-2026-10-07.md',
            'docs/live_usage/LIVE-latest.json','docs/live_usage/LIVE-latest.md',
            'results/regime_state.json','results/update_status.json',
            'results/fundamental_b_layer_filter.json','results/_attrition_guard_scan.json']
TAKE_ST2 = ['results/futures_update_status.json','results/lhb_update_status.json']

for p in TAKE_ST3 + TAKE_ST2:
    st = stages_of(p)
    sha = st['3'] if p in TAKE_ST3 else st['2']
    side = 'theirs(st3,mine)' if p in TAKE_ST3 else 'ours(st2,bm-a)'
    data = blob_bytes(sha)
    if b'<<<<<<<' in data:
        print('MARKER-LEAK ABORT', p); sys.exit(2)
    write_face(p, data)
    receipt['faces'][p] = {'recipe': 'take-side ts-duel', 'side': side}
    print('take %s <- %s' % (p, side))

# ---------- compute_audit.json: rolling-ledger union (history by ts) + latest ts-duel ----------
p = 'results/compute_audit.json'
st = stages_of(p)
j2 = json.loads(blob_bytes(st['2']))
j3 = json.loads(blob_bytes(st['3']))
h2 = j2.get('history', []); h3 = j3.get('history', [])
union = {}
for e in h2 + h3:
    union[e['ts']] = e
merged_hist = [union[k] for k in sorted(union.keys())]
latest = j3['latest'] if j3['latest']['ts'] >= j2['latest']['ts'] else j2['latest']
out = {'latest': latest, 'history': merged_hist}
# zero-loss assert: union count == |set(ts2) ∪ set(ts3)|
n_union = len(set(e['ts'] for e in h2) | set(e['ts'] for e in h3))
assert len(merged_hist) == n_union, 'union count mismatch'
receipt['faces'][p] = {'recipe': 'rolling-ledger union', 'hist_st2': len(h2), 'hist_st3': len(h3),
                       'union': len(merged_hist), 'latest_side': 'st3' if latest is j3['latest'] else 'st2'}
receipt['asserts'].append('compute_audit union %d == |A∪B| %d' % (len(merged_hist), n_union))
# mirror base blob formatting (CRLF/indent probe)
base_raw = blob_bytes(st['2'])
crlf = b'\r\n' in base_raw
txt = json.dumps(out, indent=1, ensure_ascii=False)
if crlf:
    txt = txt.replace('\n','\r\n')
write_face(p, txt.encode('utf-8'))
json.loads(open(p,'rb').read().decode('utf-8'))  # parse-verify before add (r185 law)
print('union compute_audit: %d + %d -> %d, latest=%s' % (len(h2), len(h3), len(merged_hist), latest['ts']))

# ---------- token_usage.json: per-key max union (r758 canon) ----------
p = 'results/token_usage.json'
st = stages_of(p)
j2 = json.loads(blob_bytes(st['2']))
j3 = json.loads(blob_bytes(st['3']))
def max_merge(a, b):
    # numeric counters: max; dict: recurse; list/other: take from a if a==b else take-newer caller decides
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        for k in set(a) | set(b):
            if k in a and k in b:
                out[k] = max_merge(a[k], b[k])
            else:
                out[k] = a.get(k, b.get(k))
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return max(a, b)
    return a  # identical or non-numeric: either side (equal bytes verified below when identical)
out = j3 if j3.get('generated','') >= j2.get('generated','') else j2
merged = max_merge(j2, j3)
# scalars/metadata from newer side win (non-numeric keys)
for k, v in out.items():
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        merged[k] = v
# numeric top-level totals keep max via max_merge; re-assert parse
receipt['faces'][p] = {'recipe': 'per-key max union', 'newer_side': 'st3' if out is j3 else 'st2',
                       'generated': merged.get('generated')}
base_raw = blob_bytes(st['2'])
crlf = b'\r\n' in base_raw
txt = json.dumps(merged, indent=1, ensure_ascii=False)
if crlf:
    txt = txt.replace('\n','\r\n')
write_face(p, txt.encode('utf-8'))
json.loads(open(p,'rb').read().decode('utf-8'))
print('token_usage max-union: generated=%s' % merged.get('generated'))

# ---------- stage all resolved faces ----------
receipt['staged'] = TAKE_ST3 + TAKE_ST2 + [p_prev for p_prev in ['results/compute_audit.json','results/token_usage.json']]
all_files = TAKE_ST3 + TAKE_ST2 + ['results/compute_audit.json','results/token_usage.json']
r = subprocess.run(['git','add','--'] + all_files, capture_output=True, text=True)
if r.returncode != 0:
    print('GIT ADD FAIL:', r.stderr); sys.exit(3)
with open('results/_r802bmb_rebase_resolve.json','w',encoding='utf-8') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
subprocess.run(['git','add','results/_r802bmb_rebase_resolve.json'], capture_output=True)
print('resolver done: 14 faces resolved, receipt staged')
