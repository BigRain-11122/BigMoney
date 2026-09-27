# _r367bma_resolve.py -- R367 bm-a push-collision canonical resolution (rebase replay, 15 UU)
# Law refs: classifier-first (SKILL L1); snapshot deep-ts probe r100/R350 (wall-clock values only,
# key-EXCLUDE forbidden, probe STAGED blobs not worktree); twin coupling r327/r329 (md/js byte-copy
# same side as json winner); rolling-ledger union r188/r85 + r366 identity-per-face; mixed-dict+ledger
# autofill_state r322/r245 (compound-key dedup, cap50, re-sort asc, last_tick dict ts compare, tie->HEAD);
# js-wrapper R209 (whole bytes); mirror base blob newline/indent r223/r234; parse-verify before write r185.
import subprocess, json, io, re, sys

def blob(stage, path):
    b = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True).stdout
    if not b:
        return None
    return b

def jload(stage, path):
    return json.loads(blob(stage, path))

WALL = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def wallclock_max(obj):
    # R350: only values with time-of-day feed the max; date-only must not. No key exclusion lists.
    best = None
    def walk(v):
        nonlocal best
        if isinstance(v, dict):
            for x in v.values(): walk(x)
        elif isinstance(v, list):
            for x in v: walk(x)
        elif isinstance(v, str) and WALL.match(v):
            if best is None or v > best: best = v
    walk(obj)
    return best

def take_new_side(path, probe_key_hint=None):
    a, b = jload(2, path), jload(3, path)
    ma, mb = wallclock_max(a), wallclock_max(b)
    if ma is None and mb is None:
        side = 2  # no wall-clock anywhere -> tie -> HEAD (origin side, r140)
        why = 'no-wallclock-tie->HEAD'
    elif mb is None or (ma is not None and ma > mb):
        side = 2; why = 'origin-newer(%s>%s)' % (ma, mb)
    elif ma is None or mb > ma:
        side = 3; why = 'mine-newer(%s>%s)' % (mb, ma)
    else:
        side = 2; why = 'tie(%s)->HEAD' % ma
    data = blob(side, path)
    json.loads(data)  # parse-verify (r185)
    return side, why, data

def mirror_write(path, obj, base_bytes):
    # r223/r234: mirror base blob newline/indent
    txt = json.dumps(obj, ensure_ascii=False, indent=2)
    if b'\r\n' in base_bytes:
        txt = txt.replace('\n', '\r\n')
    if base_bytes.endswith(b'\n') and not txt.endswith('\n'):
        txt += '\n' if b'\r\n' not in base_bytes else '\r\n'
    if not base_bytes.endswith(b'\n') and txt.endswith('\n'):
        txt = txt[:-1]
    json.loads(txt.encode('utf-8').decode('utf-8-sig'))  # parse-verify
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(txt)

log = []

# ---------- 1) pure snapshots: take-new whole bytes ----------
SNAPS = ['results/update_status.json', 'results/token_usage.json',
         'results/futures_update_status.json', 'results/heat_update_status.json',
         'results/lhb_update_status.json', 'results/fundamental_b_layer_filter.json',
         'results/scorecard_v1.json', 'results/strategy_scorecard.json']
twin_src = {}
for p in SNAPS:
    side, why, data = take_new_side(p)
    with io.open(p, 'wb') as f:
        f.write(data)
    log.append((p, 'snapshot take-new', why))

# ---------- 2) twin pairs: json decides side, md/js byte-copy same side ----------
# REPORT twin (r329: md is not JSON -- byte copy, never json.loads)
p = 'docs/daily_report/REPORT-2026-09-28.json'
side, why, data = take_new_side(p)
with io.open(p, 'wb') as f: f.write(data)
md = blob(side, 'docs/daily_report/REPORT-2026-09-28.md')
with io.open('docs/daily_report/REPORT-2026-09-28.md', 'wb') as f: f.write(md)
log.append((p, 'twin json take-new', why))
log.append(('docs/daily_report/REPORT-2026-09-28.md', 'twin md byte-copy', 'same-side=%d' % side))

# dashboard twin (R209: js = wrapper, whole bytes, same side as json)
p = 'results/dashboard_status.json'
side, why, data = take_new_side(p)
with io.open(p, 'wb') as f: f.write(data)
js = blob(side, 'results/dashboard_status.js')
with io.open('results/dashboard_status.js', 'wb') as f: f.write(js)
log.append((p, 'snapshot take-new (twin src)', why))
log.append(('results/dashboard_status.js', 'js-wrapper byte-copy', 'same-side=%d' % side))

# ---------- 3) compute_audit: rolling-ledger union (identity=ts) + latest take-new ----------
p = 'results/compute_audit.json'
a, b = jload(2, p), jload(3, p)
ida = {r['ts'] for r in a['history']}
idb = {r['ts'] for r in b['history']}
union_ident = ida | idb
by = {}
for r in a['history'] + b['history']:
    k = r['ts']
    if k not in by: by[k] = r          # same-identity collision: first=origin(:2) side wins (older base order), honest
    else:
        # r366: same-identity new-side-wins is for per-face fresher rows; keep :2: first here and
        # verify content equality if both present
        if by[k] != r:
            by[k] = r                  # later (mine, :3:) row wins on true divergence
hist = sorted(by.values(), key=lambda r: r['ts'])
assert len(hist) == len(union_ident), 'compute_audit union identity-loss: %d vs %d' % (len(hist), len(union_ident))
assert len(hist) >= max(len(a['history']), len(b['history'])), 'union below max side = truncation'
latest = a['latest'] if (wallclock_max(a['latest']) or '') >= (wallclock_max(b['latest']) or '') else b['latest']
out = {'latest': latest, 'history': hist}
mirror_write(p, out, blob(1, p) or blob(2, p))
log.append((p, 'rolling-ledger union', 'hist %d+%d->%d identities=%d zero-loss; latest=%s' % (
    len(a['history']), len(b['history']), len(hist), len(union_ident), latest['ts'])))

# ---------- 4) regime_state: per-face identity (asof) union + flat take-new (r366) ----------
p = 'results/regime_state.json'
a, b = jload(2, p), jload(3, p)
def rs_union(ra, rb):
    # per-face identity: dict rows -> asof key; scalar rows -> the value itself (triggers are strings)
    ident = lambda r: r.get('asof') if isinstance(r, dict) else r
    ida = {ident(r) for r in ra}
    idb = {ident(r) for r in rb}
    by = {}
    for r in ra + rb:
        k = ident(r)
        if k not in by or by[k] != r: by[k] = r   # same-identity collision: later (new-side) wins
    return sorted(by.values(), key=lambda r: str(ident(r))), len(ida | idb)
uh, ui = rs_union(a.get('history', []), b.get('history', []))
ut, _ = rs_union(a.get('triggers', []), b.get('triggers', []))
un, _ = rs_union(a.get('transitions', []), b.get('transitions', []))
assert len(uh) == ui, 'regime_state history identity-loss'
base_new = a if (wallclock_max(a) or '') >= (wallclock_max(b) or '') else b
out = dict(base_new)
out['history'] = uh
if 'triggers' in a or 'triggers' in b: out['triggers'] = ut
if 'transitions' in a or 'transitions' in b: out['transitions'] = un
mirror_write(p, out, blob(1, p) or blob(2, p))
log.append((p, 'rolling-ledger per-face union', 'hist->%d trig->%d trans->%d flat=%s' % (
    len(uh), len(ut), len(un), base_new.get('updated'))))

# ---------- 5) autofill_state: mixed-dict+ledger r322/r245 ----------
p = 'results/autofill_state.json'
a, b = jload(2, p), jload(3, p)
KEY = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'), r.get('runner_sha256'), r.get('entry'), r.get('shard'))
by = {}
for r in a['launches'] + b['launches']:
    k = KEY(r)
    if k not in by:
        by[k] = r
    else:
        # r322: same-key pair -> field-set additive merge keep one; true divergence = flag, no silent dual-store
        sa, sb = set(by[k].keys()), set(r.keys())
        if sa == sb:
            if by[k] != r:
                by[k] = r  # field-equal keyset but content differs: keep later (new-side) honest
        else:
            merged = dict(by[k]); merged.update(r)
            by[k] = merged  # additive field-union merge, one record kept
launches = sorted(by.values(), key=lambda r: r['ts'], reverse=True)[:50]  # cap 50 newest (r322)
launches = sorted(launches, key=lambda r: r['ts'])  # write back re-sorted ASC (r245)
la, lb = a['last_tick'], b['last_tick']
assert isinstance(la, dict) and isinstance(lb, dict), 'last_tick must be dict'
last_tick = la if str(la.get('ts', '')) >= str(lb.get('ts', '')) else lb  # ts compare, tie->HEAD(:2:)=la
assert isinstance(last_tick, dict)
out = {'last_tick': last_tick, 'launches': launches}
mirror_write(p, out, blob(1, p) or blob(2, p))
log.append((p, 'mixed union', 'launches %d+%d->%d (dedup compound-key, cap50 asc) last_tick=%s@%s tie->HEAD-law' % (
    len(a['launches']), len(b['launches']), len(launches), last_tick.get('machine'), last_tick.get('ts'))))

# ---------- report ----------
for p, recipe, why in log:
    print('%-46s | %-28s | %s' % (p, recipe, why))
print('ALL RESOLVED: parse-verify passed, zero-loss assertions passed')
