# r501 bm-b rebase UU resolver (3 files): classifier recipes (rolling-ledger x2 + snapshot)
# sides: ours=:2: (upstream origin), theirs=:3: (my r501 S6 commit 15d674e46)
import subprocess, json, sys, re
from pathlib import Path

def blob(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    if r.returncode != 0:
        sys.exit('blob fail: ' + ref)
    return r.stdout

def probe_fmt(raw):
    indent = 2
    for line in raw.decode('utf-8', 'replace').splitlines()[:40]:
        s = line.lstrip(' ')
        if s.startswith('"'):
            indent = len(line) - len(s)
            break
    return indent, raw.endswith(b'\n')

def deep_ts(obj, best=''):
    # r100/R350: deep-scan nested layers for ^20xx- timestamps, no key excludes
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and re.match(r'^20\d{2}-', v) and 'T' in v or \
               (isinstance(v, str) and re.match(r'^20\d{2}-\d{2}-\d{2}[ T]', v)):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for x in obj:
            best = deep_ts(x, best)
    return best

log = []

# ---------- compute_audit.json: history union by ts, state fields take-new(deep ts) ----------
p = 'results/compute_audit.json'
o = json.loads(blob(':2:' + p)); t = json.loads(blob(':3:' + p))
oh = o.get('history', []); th = t.get('history', [])
keys = {h.get('ts') for h in oh if isinstance(h, dict)}
add = [h for h in th if isinstance(h, dict) and h.get('ts') not in keys]
merged = oh + add
new_base, my_base = dict(o), dict(t)
if deep_ts(my_base) > deep_ts(new_base):
    new_base, my_base = my_base, new_base
new_base['history'] = merged
fmt = probe_fmt(blob(':2:' + p))
Path(p).write_text(json.dumps(new_base, indent=fmt[0], ensure_ascii=False) + ('\n' if fmt[1] else ''), encoding='utf-8')
log.append('%s -> history-union %d+%d->%d, state ts=%s' % (p, len(oh), len(th), len(merged), deep_ts(new_base)))

# ---------- regime_state.json: transitions union, state fields take-new(deep ts) ----------
p = 'results/regime_state.json'
o = json.loads(blob(':2:' + p)); t = json.loads(blob(':3:' + p))
lk = [k for k in ('transitions', 'history') if isinstance(o.get(k), list) and isinstance(t.get(k), list)]
new_base, my_base = dict(o), dict(t)
for k in lk:
    ok_ = {(e.get('ts') or e.get('date') or json.dumps(e, sort_keys=True)) for e in o[k]}
    add = [e for e in t[k] if (e.get('ts') or e.get('date') or json.dumps(e, sort_keys=True)) not in ok_]
    new_base[k] = o[k] + add
if deep_ts(my_base) > deep_ts(new_base):
    for k in new_base:
        if k not in lk:
            new_base[k] = my_base.get(k, new_base[k])
fmt = probe_fmt(blob(':2:' + p))
Path(p).write_text(json.dumps(new_base, indent=fmt[0], ensure_ascii=False) + ('\n' if fmt[1] else ''), encoding='utf-8')
log.append('%s -> %s union + take-new ts=%s' % (p, '/'.join(lk), deep_ts(new_base)))

# ---------- update_status.json: snapshot take-new (deep ts) ----------
p = 'results/update_status.json'
o = json.loads(blob(':2:' + p)); t = json.loads(blob(':3:' + p))
pick = t if deep_ts(t) > deep_ts(o) else o
fmt = probe_fmt(blob(':2:' + p))
Path(p).write_text(json.dumps(pick, indent=fmt[0], ensure_ascii=False) + ('\n' if fmt[1] else ''), encoding='utf-8')
log.append('%s -> take-new ts=%s' % (p, deep_ts(pick)))

print('\n'.join(log))
