# r736 bm-a merge resolver (r725 bm-a bloodline verbatim-adapted [r538 bm-c lineage], MERGE_MODE stage: 2=ours 3=theirs)
# Faces: 19 UU vs origin/main (bm-b r559 + bm-c r558 same-window waves; +scorecard_v1/strategy_scorecard vs r725 face set, +CODELY.md tail union)
# Decisions (canon): snapshot/derive faces = embedded-ts newer-wins (r709 law),
#   tie/missing -> theirs (r140); sides from index stages (:2:/:3:) per r515 law;
#   take-side faces get stage-blob CR-normalized readback assertion (r515/r704);
#   md twins follow their json twin (r708/r510 twin same-side law);
#   token_usage.json = machines per-key max-union (r456/r704 lineage);
#   compute_audit.json / regime_state.json = rolling-ledger union (r188/R208);
#   CODELY.md = append-only tail block-union, upstream-first, both entries verbatim (r506/r706 law).
import json, subprocess, sys, os, re

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
MERGE_TIP = subprocess.run(['git', 'rev-parse', 'origin/main'], capture_output=True, text=True, cwd=ROOT,
                           creationflags=0x08000000).stdout.strip()

def side(stage, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True, cwd=ROOT,
                       creationflags=0x08000000)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout

TS_KEYS = ('generated_at', 'updated', 'generated', 'now', 'ts', 'asof', 'as_of', 'last_run', 'scan_ts')

def norm_ts(s):
    return s.strip().replace(' ', 'T')

def probe_ts(obj, depth=0, max_depth=2):
    if not isinstance(obj, dict) or depth > max_depth:
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return norm_ts(v)
    for v in obj.values():
        if isinstance(v, dict):
            t = probe_ts(v, depth + 1, max_depth)
            if t:
                return t
    return None

ISO_RE = re.compile(r'20\d{2}-\d{2}-\d{2}[T ][0-9:.]+[0-9]')

def deep_ts(obj):
    best = None
    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
        elif isinstance(x, str):
            m = ISO_RE.search(x)
            if m:
                t = norm_ts(m.group(0))
                if best is None or t > best:
                    best = t
    walk(obj)
    return best

SNAPSHOTS = [
    'docs/daily_report/REPORT-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-latest.json',
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/update_status.json',
    'results/dashboard_status.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
]
TOKEN = 'results/token_usage.json'
MD_TWINS = {
    'docs/daily_report/REPORT-2026-10-05.md': 'docs/daily_report/REPORT-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.md': 'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-latest.md': 'docs/live_usage/LIVE-latest.json',
    'results/dashboard_status.js': 'results/dashboard_status.json',
}
UNION_LEDGERS = {
    'results/compute_audit.json': ['history'],
    'results/regime_state.json': ['history', 'transitions'],
}

receipt = {'round': 'r736 bm-a S0 integration merge', 'merge_head': MERGE_TIP, 'faces': {}, 'decisions': {}}
decisions = {}

def write_bytes(path, data):
    open(os.path.join(ROOT, path), 'wb').write(data)

def readback_assert(path, raw):
    rb = open(os.path.join(ROOT, path), 'rb').read()
    assert rb.replace(b'\r\n', b'\n') == raw.replace(b'\r\n', b'\n'), 'readback != stage blob: %s' % path

# ---- 1) snapshot faces: embedded-ts newer-wins; deep-ts audit fallback (r516-1)
for p in SNAPSHOTS:
    o_raw, t_raw = side(2, p), side(3, p)
    if t_raw is None and o_raw is None:
        sys.exit('both sides missing for %s (not a UU face?)' % p)
    if t_raw is None:
        decisions[p] = ('ours', 'theirs-missing'); write_bytes(p, o_raw); readback_assert(p, o_raw)
        receipt['faces'][p] = {'action': 'ours', 'why': 'theirs-missing'}; continue
    if o_raw is None:
        decisions[p] = ('theirs', 'ours-missing'); write_bytes(p, t_raw); readback_assert(p, t_raw)
        receipt['faces'][p] = {'action': 'theirs', 'why': 'ours-missing'}; continue
    try:
        o = json.loads(o_raw.decode('utf-8')); t = json.loads(t_raw.decode('utf-8'))
    except Exception as ex:
        decisions[p] = ('theirs', 'parse-fail=%s' % ex); write_bytes(p, t_raw); readback_assert(p, t_raw)
        receipt['faces'][p] = {'action': 'theirs', 'why': 'parse-fail'}; continue
    to, tt = probe_ts(o), probe_ts(t)
    mode = 'probe_ts'
    if to is None:
        to = deep_ts(o); mode = 'deep_ts'
    if tt is None:
        tt = deep_ts(t)
    if to and tt and to > tt:
        decisions[p] = ('ours', '%s %s>%s' % (mode, to, tt)); write_bytes(p, o_raw); readback_assert(p, o_raw)
    else:
        decisions[p] = ('theirs', '%s ours=%s theirs=%s -> newer/origin' % (mode, to, tt))
        write_bytes(p, t_raw); readback_assert(p, t_raw)
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    receipt['faces'][p] = {'action': decisions[p][0], 'why': decisions[p][1]}

# ---- 2) token_usage: machines per-key max-union (r456 lineage) + newer top-level
p = TOKEN
o_raw, t_raw = side(2, p), side(3, p)
o = json.loads(o_raw.decode('utf-8')); t = json.loads(t_raw.decode('utf-8'))
om, tm = o.get('machines') or {}, t.get('machines') or {}
merged = dict(om)
picked = 0
def tot(v):
    s = 0
    def walk(x):
        nonlocal s
        if isinstance(x, dict):
            for vv in x.values(): walk(vv)
        elif isinstance(x, (int, float)): s += x
    walk(v); return s
for k, tv in tm.items():
    ov = merged.get(k)
    if ov is None:
        merged[k] = tv; picked += 1
    elif tot(tv) > tot(ov):
        merged[k] = tv; picked += 1
if (probe_ts(t) or '') > (probe_ts(o) or ''):
    base = dict(t)
else:
    base = dict(o)
base['machines'] = merged
write_bytes(p, (json.dumps(base, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
decisions[p] = ('per-key-union', 'machines max-union picked_theirs=%d top ours=%s theirs=%s' % (
    picked, probe_ts(o), probe_ts(t)))
receipt['faces'][p] = {'action': 'per-key-union', 'picked_theirs': picked}

# ---- 3) twins follow their json twin (r708/r510 twin same-side law)
for p, twin in MD_TWINS.items():
    s, why = decisions[twin]
    raw = side(2 if s == 'ours' else 3, p)
    write_bytes(p, raw); readback_assert(p, raw)
    decisions[p] = (s, 'md-twin of %s (%s)' % (twin, why))
    receipt['faces'][p] = {'action': s, 'why': decisions[p][1]}

# ---- 4) rolling-ledger unions (r188/R208: history union + ours latest/state)
for p, keys in UNION_LEDGERS.items():
    o = json.loads(side(2, p).decode('utf-8'))
    t = json.loads(side(3, p).decode('utf-8'))
    for k in keys:
        a, b = o.get(k) or [], t.get(k) or []
        rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in a}
        for r in b:
            rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
        merged_rows = sorted(rows.values(), key=lambda r: str(r.get('ts', r.get('updated', ''))))
        o[k] = merged_rows
        assert len(merged_rows) >= max(len(a), len(b)), 'union loss %s %s' % (p, k)
        receipt['faces'][p] = {'action': 'union+' + k, 'ours_len': len(a), 'theirs_len': len(b), 'union_len': len(merged_rows)}
    write_bytes(p, (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    json.loads(open(os.path.join(ROOT, p), 'rb').read().decode('utf-8'))
    decisions[p] = ('union', 'rolling-ledger union, ours latest/state')

# ---- 5) CODELY.md append-only tail block-union (r506/r706 law: keep both sides' tail entries verbatim)
p = 'CODELY.md'
raw = open(os.path.join(ROOT, p), 'rb').read().decode('utf-8')
lines = raw.splitlines(keepends=True)
idx_open = [i for i, ln in enumerate(lines) if ln.startswith('<<<<<<< ')]
idx_mid = [i for i, ln in enumerate(lines) if ln.rstrip('\r\n') == '=======']
idx_close = [i for i, ln in enumerate(lines) if ln.startswith('>>>>>>> ')]
assert len(idx_open) == len(idx_close) == len(idx_mid) == 1, 'CODELY marker counts %s %s %s' % (idx_open, idx_mid, idx_close)
o_ix, m_ix, c_ix = idx_open[0], idx_mid[0], idx_close[0]
ours_block = lines[o_ix + 1:m_ix]
theirs_block = lines[m_ix + 1:c_ix]
out = lines[:o_ix] + theirs_block + ours_block + lines[c_ix + 1:]
text = ''.join(out)
for ln in out:
    assert not (ln.startswith('<<<<<<< ') or ln.startswith('>>>>>>> ') or ln.rstrip('\r\n') == '======='), 'marker residue line: %r' % ln[:40]
assert '[2026-10-05 17:1x r558 bm-c]' in text, 'theirs r558 entry lost'
assert '[2026-10-05 17:1x r735 bm-a]' in text, 'ours r735 entry lost'
open(os.path.join(ROOT, p), 'wb').write(text.encode('utf-8'))
rb = open(os.path.join(ROOT, p), 'rb').read()
assert rb.decode('utf-8') == text, 'CODELY readback mismatch'
decisions[p] = ('block-union', 'kept theirs r558 bm-c + ours r735 bm-a, upstream-first, %d+%d lines' % (len(theirs_block), len(ours_block)))
receipt['faces'][p] = {'action': 'block-union', 'ours_lines': len(ours_block), 'theirs_lines': len(theirs_block)}

receipt['decisions'] = {k: v[0] + ' | ' + v[1] for k, v in decisions.items()}
open(os.path.join(ROOT, 'results', '_r736bma_merge_resolve.json'), 'w', encoding='utf-8').write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
print('RESOLVED %d faces (merge_head=%s)' % (len(decisions), MERGE_TIP[:9]))
for k, v in sorted(decisions.items()):
    print('%-55s %-14s %s' % (k, v[0], v[1][:90]))
