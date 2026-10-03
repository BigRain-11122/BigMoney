# r650 bm-a rebase conflict resolver (manual faces per bigmoney-conflict-resolve skill)
# Faces: fundamental_b_layer_filter (snapshot take-new deep-ts), post_review.jsonl (append union),
#         twin families REPORT-2026-10-04 + LIVE-2026-10-04 + LIVE-latest (json probe -> md byte-copy same side),
#         post_review/REPORT-20261004.md (UNKNOWN -> manual classify + decide)
import subprocess, json, re, sys

def stage_blob(stage, path):
    return subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout

def probe_ts(obj, keys=('generated_at', 'generated', 'updated', 'ts')):
    # deep scan nested layers (r311/D-20260927-09)
    found = []
    def walk(o, depth):
        if depth > 6 or o is None: return
        if isinstance(o, dict):
            for k, v in o.items():
                kk = k.lower().replace('_', '').replace('-', '')
                if isinstance(v, str) and re.match(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}', v):
                    for pref in keys:
                        if kk.startswith(pref.lower().replace('_', '').replace('-', '')):
                            found.append(v); break
                walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o[:400]: walk(v, depth + 1)
    walk(obj, 0)
    return max(found) if found else None

report = {}

# 1) fundamental_b_layer_filter.json -- snapshot take-new by updated
p = 'results/fundamental_b_layer_filter.json'
a, b = stage_blob(2, p), stage_blob(3, p)
da, db = json.loads(a), json.loads(b)
ta, tb = probe_ts(da, ('updated', 'generated_at')), probe_ts(db, ('updated', 'generated_at'))
side = 3 if (tb or '') >= (ta or '') else 2
open(p, 'wb').write(a if side == 2 else b)
report[p] = {'ts_origin': ta, 'ts_mine': tb, 'took': ('origin' if side == 2 else 'mine')}
print(f'[fundamental_b_layer_filter] origin={ta} mine={tb} -> took {"origin" if side==2 else "mine"}')

# 2) post_review.jsonl -- append-log line-level union zero loss
p = 'results/post_review.jsonl'
a, b = stage_blob(2, p).decode('utf-8'), stage_blob(3, p).decode('utf-8')
la, lb = [x for x in a.splitlines() if x.strip()], [x for x in b.splitlines() if x.strip()]
seen, out = set(), []
for line in la + lb:
    key = line.strip()
    if key in seen: continue
    seen.add(key); out.append(line)
# stable order: try ts sort if every line parses with a ts field, else keep union order
def lts(line):
    try: return probe_ts(json.loads(line), ('ts', 'at', 'reviewed_at', 'generated_at')) or ''
    except Exception: return ''
if all(lts(x) for x in out):
    out.sort(key=lts)
nla, nlb = len(la), len(lb)
open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + ('\n' if out else ''))
report[p] = {'lines_origin': nla, 'lines_mine': nlb, 'lines_union': len(out)}
print(f'[post_review.jsonl] origin={nla} mine={nlb} union={len(out)} (zero-loss assert: {len(out)}>=max={max(nla,nlb)})')
assert len(out) >= max(nla, nlb)

# 3) twin families: json probe decides side, md byte-copies from same side
families = {
    'docs/daily_report/REPORT-2026-10-04': ['json', 'md'],
    'docs/live_usage/LIVE-2026-10-04': ['json', 'md'],
    'docs/live_usage/LIVE-latest': ['json', 'md'],
}
live_side = None
for base, exts in families.items():
    jp = base + '.json'
    a, b = stage_blob(2, jp), stage_blob(3, jp)
    try:
        ta = probe_ts(json.loads(a), ('generated_at', 'generated', 'asof', 'updated'))
        tb = probe_ts(json.loads(b), ('generated_at', 'generated', 'asof', 'updated'))
    except Exception as e:
        ta, tb = None, None
        print(f'[{jp}] parse issue {e}; falling back to raw-text regex probe')
        ma = re.search(rb'"(?:generated_at|generated)"\s*:\s*"([^"]+)"', a)
        mb = re.search(rb'"(?:generated_at|generated)"\s*:\s*"([^"]+)"', b)
        ta = ma.group(1).decode() if ma else None
        tb = mb.group(1).decode() if mb else None
    side = 3 if (tb or '') >= (ta or '') else 2
    if 'LIVE' in base and live_side is None:
        live_side = side
    elif 'LIVE' in base:
        assert side == live_side, f'LIVE twins took different sides! {base}: {side} vs {live_side}'
    for ext in exts:
        fp = f'{base}.{ext}'
        blob = stage_blob(side, fp)
        open(fp, 'wb').write(blob)
    report[base] = {'ts_origin': ta, 'ts_mine': tb, 'took': ('origin' if side == 2 else 'mine')}
    print(f'[{base}] origin={ta} mine={tb} -> took {"origin" if side==2 else "mine"} (both twins)')

# 4) UNKNOWN: results/post_review/REPORT-20261004.md -- inspect both sides for ts markers
p = 'results/post_review/REPORT-20261004.md'
a, b = stage_blob(2, p).decode('utf-8', errors='replace'), stage_blob(3, p).decode('utf-8', errors='replace')
tsa = re.findall(r'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', a)
tsb = re.findall(r'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', b)
print(f'[post_review/REPORT-20261004.md] origin ts markers={tsa[:3]} mine ts markers={tsb[:3]}')
print(f'  origin lines={len(a.splitlines())} mine lines={len(b.splitlines())}')
report[p] = {'origin_ts': tsa[:3], 'mine_ts': tsb[:3], 'origin_lines': len(a.splitlines()), 'mine_lines': len(b.splitlines())}

json.dump(report, open('results/_r650bma_resolve_report.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('resolver report -> results/_r650bma_resolve_report.json')
