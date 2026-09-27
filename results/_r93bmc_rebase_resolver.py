# r93 bm-c rebase UU resolver (18 files): canon union faces + take-new faces
# sides: ours=:2: (upstream bm-b r336), theirs=:3: (my round-93 commit)
import subprocess, json, sys
from pathlib import Path

def blob(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    if r.returncode != 0:
        sys.exit('blob fail: ' + ref)
    return r.stdout

def write_bytes(path, data):
    Path(path).write_bytes(data)

def probe_fmt(raw):
    indent = 2
    for line in raw.decode('utf-8', 'replace').splitlines()[:40]:
        s = line.lstrip(' ')
        if s.startswith('"'):
            indent = len(line) - len(s)
            break
    return indent, raw.endswith(b'\n')

TAKE_OURS = [
    'docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/heat_update_status.json', 'results/lhb_update_status.json',
    'results/regime_state.json', 'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/update_status.json',
]

resolved_log = []
for p in TAKE_OURS:
    write_bytes(p, blob(':2:' + p))
    resolved_log.append(p + ' -> ours-verbatim')

# ---------- x2_watch_log.jsonl: line union ----------
p = 'results/x2_watch_log.jsonl'
o_lines = blob(':2:' + p).decode('utf-8', 'replace').splitlines()
t_lines = blob(':3:' + p).decode('utf-8', 'replace').splitlines()
o_set = set(o_lines)
merged = o_lines + [l for l in t_lines if l.strip() and l not in o_set]
tail = '\n' if blob(':2:' + p).endswith(b'\n') else ''
Path(p).write_text('\n'.join(merged) + tail, encoding='utf-8')
resolved_log.append('%s -> line-union %d+%d->%d' % (p, len(o_lines), len(t_lines), len(merged)))

# ---------- token_usage.json: machines/rows union take-new ----------
p = 'results/token_usage.json'
o = json.loads(blob(':2:' + p)); t = json.loads(blob(':3:' + p))
if isinstance(o, dict) and isinstance(t, dict):
    for k, v in t.items():
        if k not in o:
            o[k] = v
        elif isinstance(v, dict) and isinstance(o[k], dict):
            for k2, v2 in v.items():
                if k2 not in o[k] or (isinstance(v2, (int, float)) and isinstance(o[k].get(k2), (int, float)) and v2 > o[k][k2]):
                    o[k][k2] = v2
        elif isinstance(v, list) and isinstance(o[k], list):
            seen = {json.dumps(x, sort_keys=True) for x in o[k]}
            o[k] = o[k] + [x for x in v if json.dumps(x, sort_keys=True) not in seen]
fmt = probe_fmt(blob(':2:' + p))
txt = json.dumps(o, indent=fmt[0], ensure_ascii=False) + ('\n' if fmt[1] else '')
Path(p).write_text(txt, encoding='utf-8')
resolved_log.append(p + ' -> dict-union')

# ---------- compute_audit.json: history union by ts ----------
p = 'results/compute_audit.json'
o = json.loads(blob(':2:' + p)); t = json.loads(blob(':3:' + p))
for k, v in t.items():
    if k == 'history' and isinstance(v, list):
        oh = o.get('history', [])
        keys = {h.get('ts') if isinstance(h, dict) else json.dumps(h, sort_keys=True) for h in oh}
        add = [h for h in v if (h.get('ts') if isinstance(h, dict) else json.dumps(h, sort_keys=True)) not in keys]
        o['history'] = oh + add
    elif k not in o:
        o[k] = v
fmt = probe_fmt(blob(':2:' + p))
txt = json.dumps(o, indent=fmt[0], ensure_ascii=False) + ('\n' if fmt[1] else '')
Path(p).write_text(txt, encoding='utf-8')
resolved_log.append(p + ' -> history-union')

# ---------- autofill_state.json: identity-key union (r93 law) ----------
p = 'results/autofill_state.json'
o = json.loads(blob(':2:' + p)); t = json.loads(blob(':3:' + p))
ik = lambda e: (e.get('ts'), e.get('machine'), e.get('entry'), e.get('shard'))
best = {}
for e in o.get('launches', []) + t.get('launches', []):
    k = ik(e)
    if k not in best or len([x for x in e.values() if x is not None]) > len([x for x in best[k].values() if x is not None]):
        best[k] = e
merged = sorted(best.values(), key=lambda e: e.get('ts') or '')
o['launches'] = merged[-48:] if len(merged) > 48 else merged
ots = (o.get('last_tick') or {}).get('ts', ''); tts = (t.get('last_tick') or {}).get('ts', '')
if tts and tts > ots:
    o['last_tick'] = t['last_tick']
fmt = probe_fmt(blob(':2:' + p))
txt = json.dumps(o, indent=fmt[0], ensure_ascii=False) + ('\n' if fmt[1] else '')
Path(p).write_text(txt, encoding='utf-8')
resolved_log.append('%s -> identity-union n=%d last_tick=%s' % (p, len(o['launches']), o['last_tick']['ts']))

# ---------- CODELY.md: line union (ours + theirs-unique) ----------
p = 'CODELY.md'
o_raw = blob(':2:' + p).decode('utf-8', 'replace')
t_raw = blob(':3:' + p).decode('utf-8', 'replace')
o_lines = o_raw.splitlines()
t_lines = [l for l in t_raw.splitlines() if l.strip()]
o_set = set(o_lines)
added = [l for l in t_lines if l not in o_set]
tail = '\n' if o_raw.endswith('\n') else ''
out = '\n'.join(o_lines + added) + tail
Path(p).write_text(out, encoding='utf-8')
size = Path(p).stat().st_size
resolved_log.append('CODELY.md -> line-union +%d lines size=%d' % (len(added), size))

# ---------- archive 202609.md: ours + theirs-unique tail section ----------
p = 'research/memory-archive/202609.md'
o_raw = blob(':2:' + p).decode('utf-8', 'replace')
t_raw = blob(':3:' + p).decode('utf-8', 'replace')
o_lines = o_raw.splitlines()
o_set = set(o_lines)
added = [l for l in t_raw.splitlines() if l.strip() and l not in o_set]
tail = '\n' if o_raw.endswith('\n') else ''
out = '\n'.join(o_lines + added) + tail
Path(p).write_text(out, encoding='utf-8')
resolved_log.append('archive 202609.md -> union +%d lines' % len(added))

print('\n'.join(resolved_log))
