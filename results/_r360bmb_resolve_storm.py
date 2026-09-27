"""_r360bmb_resolve_storm -- push-storm cherry-pick 16-UU batch resolution.

Storm: bm-b r360 cherry-pick onto origin (bm-a r382 + revived bm-c r136
in-window). Classifier 16/16 GREEN 0 UNKNOWN. Recipes per SKILL.md:
snapshot take-new by deep-ts probe (r350/R208); rolling-ledger ts-key
union no-cap + latest take-new (compute_audit r188/R208; regime asof-union);
mixed-dict+ledger (autofill_state r203/r215/r245); memory-union (CODELY
r208/r212); anchor-insert (HANDOVER R210: origin-first keeps position,
latecomer inserts before the latest-核对 anchor line); js twin-bound whole
bytes same-side as json (R209); daily twins same-side (r98); token_usage
machines-union + top take-new (r123 family). Parse-verify before write-back
(r185); take-whole faces written as verbatim stage bytes (zero format drift).
"""
import json
import subprocess

def blob(stage, path):
    return subprocess.run(['git', 'show', f':{stage}:{path}'],
                           capture_output=True).stdout

def jload(stage, path):
    return json.loads(blob(stage, path).decode('utf-8-sig'))

def write_bytes(path, data):
    with open(path, 'wb') as fh:
        fh.write(data)

def write_text_mirror(path, text, ref_bytes):
    crlf = b'\r\n' in ref_bytes[:400]
    with open(path, 'wb') as fh:
        fh.write(text.replace('\n', '\r\n' if crlf else '\n')
                 .encode('utf-8'))

def probe_ts(d, keys=('ts', 'generated', 'generated_at', 'updated',
                      'updated_at', 'asof')):
    for k in keys:
        if isinstance(d, dict) and k in d:
            return str(d[k])
    return ''

def take_newer(path, ts2=None, ts3=None):
    """snapshot recipe: deep-ts probe both stage blobs, take newer whole
    (verbatim bytes). Returns chosen side."""
    d2, d3 = jload(2, path), jload(3, path)
    t2 = ts2 or probe_ts(d2)
    t3 = ts3 or probe_ts(d3)
    side = 3 if t3 > t2 else 2          # newer ts wins; tie -> ours(2) r140
    write_bytes(path, blob(side, path))
    print(f'  {path}: ours={t2!r} theirs={t3!r} -> side {side}')
    json.loads(open(path, 'rb').read().decode('utf-8-sig'))   # parse-verify

log = []

# ---- snapshot take-new faces (each probes its own ts) ----
for p in ('results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json',
          'results/lhb_update_status.json',
          'results/scorecard_v1.json',
          'results/strategy_scorecard.json',
          'results/update_status.json'):
    take_newer(p)

# ---- daily twins same-side (r98): probe .json, apply to both ----
rj = 'docs/daily_report/REPORT-2026-09-28.json'
rm = 'docs/daily_report/REPORT-2026-09-28.md'
d2, d3 = jload(2, rj), jload(3, rj)
side = 3 if probe_ts(d3) > probe_ts(d2) else 2
for p in (rj, rm):
    write_bytes(p, blob(side, p))
    if p.endswith('.json'):
        json.loads(open(p, 'rb').read().decode('utf-8-sig'))
print(f'  daily twins -> side {side} (ts ours={probe_ts(d2)!r} '
      f'theirs={probe_ts(d3)!r})')

# ---- dashboard twins: probe meta deep-ts, same side both (R209) ----
dj = 'results/dashboard_status.json'
ds = 'results/dashboard_status.js'
m2 = jload(2, dj).get('meta', {})
m3 = jload(3, dj).get('meta', {})
side = 3 if probe_ts(m3) > probe_ts(m2) else 2
for p in (dj, ds):
    write_bytes(p, blob(side, p))
json.loads(open(dj, 'rb').read().decode('utf-8-sig'))
print(f'  dashboard twins -> side {side} (meta ours={probe_ts(m2)!r} '
      f'theirs={probe_ts(m3)!r})')

# ---- token_usage: machines union + top take-new ----
tp = 'results/token_usage.json'
t2, t3 = jload(2, tp), jload(3, tp)
base, other = (t2, t3) if probe_ts(t2) >= probe_ts(t3) else (t3, t2)
merged = dict(base)
for mk, mv in other.get('machines', {}).items():
    merged.setdefault('machines', {})
    if mk not in merged['machines']:
        merged['machines'][mk] = mv
write_text_mirror(tp, json.dumps(merged, ensure_ascii=False, indent=1) + '\n',
                  blob(2, tp))
json.loads(open(tp, 'rb').read().decode('utf-8-sig'))
print(f'  token_usage: top ts={probe_ts(merged)!r} machines='
      f'{sorted(merged["machines"])}')

# ---- compute_audit: history ts-key union no-cap + latest take-new ----
cp = 'results/compute_audit.json'
c2, c3 = jload(2, cp), jload(3, cp)
latest = c2['latest'] if probe_ts(c2['latest']) >= probe_ts(c3['latest']) \
    else c3['latest']
rows = {}
for src in (c2, c3):
    for r in src.get('history', []):
        rows[probe_ts(r) or json.dumps(r, sort_keys=True, default=str)] = r
hist = sorted(rows.values(), key=probe_ts)
merged = {'latest': latest, 'history': hist}
write_text_mirror(cp, json.dumps(merged, ensure_ascii=False, indent=1) + '\n',
                  blob(2, cp))
json.loads(open(cp, 'rb').read().decode('utf-8-sig'))
print(f'  compute_audit: history {len(c2["history"])}U{len(c3["history"])} '
      f'-> {len(hist)} no-cap; latest ts={probe_ts(latest)!r}')

# ---- regime_state: state take-new + history/transitions union ----
rp = 'results/regime_state.json'
r2, r3 = jload(2, rp), jload(3, rp)
base = r2 if probe_ts(r2) >= probe_ts(r3) else r3
other = r3 if base is r2 else r2
merged = dict(base)
for key in ('history', 'transitions'):
    seen, rows = set(), []
    for src in (base, other):
        for r in src.get(key, []):
            k = json.dumps(r, sort_keys=True, default=str)
            if k not in seen:
                seen.add(k)
                rows.append(r)
    rows.sort(key=probe_ts)
    merged[key] = rows
write_text_mirror(rp, json.dumps(merged, ensure_ascii=False, indent=1) + '\n',
                  blob(2, rp))
json.loads(open(rp, 'rb').read().decode('utf-8-sig'))
print(f'  regime_state: updated={merged.get("updated")!r} asof='
      f'{merged.get("asof")!r} history {len(merged["history"])} '
      f'transitions {len(merged["transitions"])}')

# ---- autofill_state: mixed-dict+ledger (r203/r215/r245) ----
ap = 'results/autofill_state.json'
a2, a3 = jload(2, ap), jload(3, ap)
lt2, lt3 = a2['last_tick'], a3['last_tick']
last_tick = lt3 if str(lt3.get('ts', '')) > str(lt2.get('ts', '')) else lt2
seen, rows = set(), []
for src in (a2, a3):
    for r in src.get('launches', []):
        k = json.dumps(r, sort_keys=True, default=str)
        if k not in seen:
            seen.add(k)
            rows.append(r)
rows.sort(key=lambda r: str(r.get('ts', '')), reverse=True)
rows = rows[:50]
rows.sort(key=lambda r: str(r.get('ts', '')))
merged = {'last_tick': last_tick, 'launches': rows}
assert isinstance(merged['last_tick'], dict)
write_text_mirror(ap, json.dumps(merged, ensure_ascii=False, indent=1) + '\n',
                  blob(2, ap))
back = json.loads(open(ap, 'rb').read().decode('utf-8-sig'))
assert isinstance(back['last_tick'], dict)
print(f'  autofill_state: last_tick ts={back["last_tick"]["ts"]} '
      f'launches={len(back["launches"])} (cap 50 asc)')

# ---- CODELY.md: memory-union (stage2 verbatim + mine-only lines append) ----
kb2, kb3 = blob(2, 'CODELY.md'), blob(3, 'CODELY.md')
l2 = kb2.decode('utf-8-sig').splitlines()
l3 = kb3.decode('utf-8-sig').splitlines()
set2 = set(l2)
mine_only = [x for x in l3 if x not in set2]
merged_lines = l2 + mine_only
crlf = b'\r\n' in kb2[:400]
text = '\n'.join(merged_lines) + '\n'
with open('CODELY.md', 'wb') as fh:
    fh.write(text.replace('\n', '\r\n' if crlf else '\n').encode('utf-8'))
print(f'  CODELY.md: stage2 {len(l2)} lines + mine-only {len(mine_only)} '
      f'appended (union)')

# ---- HANDOVER.md: anchor-insert (R210: insert before latest-核对 anchor) ----
hb2, hb3 = blob(2, 'research/HANDOVER.md'), blob(3, 'research/HANDOVER.md')
h2 = hb2.decode('utf-8-sig').splitlines()
h3 = hb3.decode('utf-8-sig').splitlines()
mine = [x for x in h3 if x.startswith('> bm-b round 360 五倍数核对')
        and x not in set(h2)]
anchor_idx = next((i for i, x in enumerate(h2)
                   if x.startswith('> bm-a round 380 五倍数核对')), 0)
for line in mine:
    h2.insert(anchor_idx, line)
    anchor_idx += 1
crlf = b'\r\n' in hb2[:400]
text = '\n'.join(h2) + '\n'
with open('research/HANDOVER.md', 'wb') as fh:
    fh.write(text.replace('\n', '\r\n' if crlf else '\n').encode('utf-8'))
print(f'  HANDOVER.md: inserted {len(mine)} line(s) before bm-a-380 anchor')

# ---- final marker scan (r153 law) ----
import os
bad = []
for root, _, fns in os.walk('.'):
    if '.git' in root or '__pycache__' in root:
        continue
    for fn in fns:
        p = os.path.join(root, fn)
        try:
            with open(p, 'rb') as fh:
                head = fh.read(6)
        except OSError:
            continue
        if head in (b'<<<<<<<', b'>>>>>>') or head.startswith(b'<<<<<<<'):
            bad.append(p)
print('marker scan:', bad if bad else 'CLEAN')
print('STORM RESOLUTION COMPLETE')
