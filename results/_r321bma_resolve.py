# r321 bm-a rebase conflict resolver (push-collision batch, bigmoney-conflict-resolve canon)
# 2 UU per classifier: results/autofill_state.json (mixed-dict+ledger) + results/compute_audit.json (rolling-ledger)
# Stage mapping in rebase: :2: = origin/base (HEAD during replay) -- bm-c tick commits; :3: = ours (r321 being replayed)
# Laws: launches key-union (ts,machine,entry,shard,pid) r317; cap50 desc->resort asc r245; last_tick inner-ts whole-dict r203;
#       compute_audit history ts-key union zero-loss r188 + latest take-new with ts probe DEEP-SCAN (D-20260927-09) + path-existence first (r319)
import json, subprocess

def stage(side, path):
    return subprocess.run(['git', 'show', f':{side}:{path}'], capture_output=True, check=True).stdout.decode('utf-8')

def load(side, path):
    txt = stage(side, path)
    return json.loads(txt)

def probe_ts(obj, *keys):
    """Deep-scan nested ts with per-level existence probing (r319: missing key = silently-False compare)."""
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur if isinstance(cur, str) else None

# --- autofill_state.json ---
A = load(2, 'results/autofill_state.json')   # origin/base side
B = load(3, 'results/autofill_state.json')   # ours (r321)
la, lb = A.get('launches', []), B.get('launches', [])
key = lambda e: (e.get('ts'), e.get('machine'), e.get('entry'), e.get('shard'), e.get('pid'))
ka, kb = {key(e) for e in la}, {key(e) for e in lb}
union = {}
for e in la: union.setdefault(key(e), e)
for e in lb: union.setdefault(key(e), e)
assert len(union) == len(ka | kb), f'launches zero-loss violated: {len(union)} != {len(ka | kb)}'
launches = sorted(union.values(), key=lambda e: e.get('ts') or '', reverse=True)[:50]  # cap50 keep-newest (R215)
launches = sorted(launches, key=lambda e: e.get('ts') or '')  # write-back ts-asc producer order (r245)
lta, ltb = A.get('last_tick'), B.get('last_tick')
ta, tb = probe_ts(A, 'last_tick', 'ts'), probe_ts(B, 'last_tick', 'ts')
if ta is not None and tb is not None:
    last_tick = lta if ta >= tb else ltb   # newer inner ts wins whole-dict; tie -> base/HEAD side (r140)
elif ta is not None: last_tick = lta
elif tb is not None: last_tick = ltb
else: last_tick = lta or ltb
assert isinstance(last_tick, dict), 'last_tick must stay dict (r203)'
merged_a = dict(A); merged_a['launches'] = launches; merged_a['last_tick'] = last_tick
with open('results/autofill_state.json', 'w', encoding='utf-8', newline='') as f:
    f.write(json.dumps(merged_a, ensure_ascii=False, indent=1).replace('\n', '\r\n'))
print(f'autofill_state: launches {len(la)}+{len(lb)} -> union {len(union)} (assert |A|B|={len(ka|kb)}) -> cap50 {len(launches)} ts-asc; last_tick ts base={ta} ours={tb} -> took {"base" if ta>=tb and tb else "ours"}')

# --- compute_audit.json ---
A = load(2, 'results/compute_audit.json')
B = load(3, 'results/compute_audit.json')
ha, hb = A.get('history', []), B.get('history', [])
hkey = lambda e: e.get('ts')
hu = {}
for e in ha: hu.setdefault(hkey(e), e)
for e in hb: hu.setdefault(hkey(e), e)
assert len(hu) == len({hkey(e) for e in ha} | {hkey(e) for e in hb}), 'history zero-loss violated'
history = sorted(hu.values(), key=lambda e: e.get('ts') or '')
ta, tb = probe_ts(A, 'latest', 'ts'), probe_ts(B, 'latest', 'ts')
latest = (B if (tb or '') > (ta or '') else A)['latest'] if (ta or tb) else (A.get('latest') or B.get('latest'))
merged_c = dict(A)  # base-side top-level shell; overwrite unioned/newer faces
merged_c['history'] = history
merged_c['latest'] = latest
# preserve any other top-level keys from the newer side (shallow newest-wins)
newer = B if (tb or '') > (ta or '') else A
for k, v in newer.items():
    if k not in ('history', 'latest'):
        merged_c[k] = v
with open('results/compute_audit.json', 'w', encoding='utf-8', newline='') as f:
    f.write(json.dumps(merged_c, ensure_ascii=False, indent=1).replace('\n', '\r\n'))
print(f'compute_audit: history {len(ha)}+{len(hb)} -> union {len(history)} ts-key zero-loss; latest ts base={ta} ours={tb} -> took {"ours" if (tb or "")>(ta or "") else "base"}')

# re-verify both files parse (r185 law)
for p in ('results/autofill_state.json', 'results/compute_audit.json'):
    json.loads(open(p, encoding='utf-8').read())
    assert '<<<<<<<' not in open(p, encoding='utf-8').read(), 'marker residue'
print('parse-verify both: OK, zero marker residue')
