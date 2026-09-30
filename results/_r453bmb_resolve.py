# r453 bm-b rebase collision resolver (push-rejection batch, bigmoney-conflict-resolve skill)
# Sides in REBASE: :2 = ours = origin/new-upstream (sibling machine), :3 = theirs = bm-b replayed commit.
# Recipes:
#  - snapshot faces (12): deep-ts probe -> newer internal ts wins; tie -> origin side (r140 tie->HEAD=onto side)
#  - rolling-ledger faces (2): history/transitions union zero-loss, then take-new top-level state fields
# All resolved JSONs must json.loads before write-back (r185 law). Zero-loss check for ledgers (|A U B| rows).
import json, subprocess, sys, io

def blob(stage, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode('utf-8', 'replace')

def deep_max_ts(obj, best=''):
    # recursive probe for max ISO-like ts string value
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) >= 10 and (v[:4].isdigit()) and (':' in v or '-' in v):
                kl = k.lower()
                if any(t in kl for t in ('ts', 'time', 'date', 'asof', 'generated', 'updated', 'written', 'seen', 'at')):
                    if v > best:
                        best = v
            else:
                best = deep_max_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_max_ts(v, best)
    return best

SNAPSHOTS = [
    'docs/daily_report/REPORT-2026-09-30.json',
    'docs/daily_report/REPORT-2026-09-30.md',
    'docs/live_usage/LIVE-2026-09-30.json',
    'docs/live_usage/LIVE-2026-09-30.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/token_usage.json',
    'results/update_status.json',
]
LEDGERS = ['results/compute_audit.json', 'results/regime_state.json']

def pick_snapshot(path, memo):
    # md twins inherit the decision of their json twin when present
    twin = None
    if path.endswith('.md'):
        cand = path[:-3] + '.json'
        if cand in memo:
            return memo[cand], 'twin-inherit'
    a_raw, b_raw = blob(2, path), blob(3, path)
    if a_raw is None and b_raw is not None:
        return 'theirs', 'origin-missing'
    if b_raw is None and a_raw is not None:
        return 'ours', 'bm-b-missing'
    ta = tb = ''
    try:
        ta = deep_max_ts(json.loads(a_raw))
        tb = deep_max_ts(json.loads(b_raw))
    except Exception:
        pass
    if not ta and not tb:
        try:
            ta = deep_max_ts(a_raw.replace("'", '"'))
            tb = deep_max_ts(b_raw.replace("'", '"'))
        except Exception:
            pass
    if tb > ta:
        side = 'theirs'  # bm-b side newer -> keep mine
    elif ta > tb:
        side = 'ours'    # origin side newer -> take sibling
    else:
        side = 'ours'    # tie -> HEAD/onto side (r140)
    return side, 'ts(%s vs %s)' % (ta or '?', tb or '?')

def resolve_ledger(path, union_keys):
    a = json.loads(blob(2, path))
    b = json.loads(blob(3, path))
    out = {}
    # take-new for non-ledger top fields by deep ts
    ta = deep_max_ts({k: v for k, v in a.items() if k not in union_keys})
    tb = deep_max_ts({k: v for k, v in b.items() if k not in union_keys})
    base, newr = (a, b) if ta >= tb else (b, a)
    for k, v in base.items():
        if k not in union_keys:
            out[k] = v
    for key in union_keys:
        av = base.get(key) or []
        bv = newr.get(key) or []
        seen = {}
        for row in list(av) + list(bv):
            if isinstance(row, dict):
                ident = json.dumps(row, sort_keys=True, ensure_ascii=False)
            else:
                ident = str(row)
            seen.setdefault(ident, row)
        merged = list(seen.values())
        merged.sort(key=lambda r: (r.get('ts', '') if isinstance(r, dict) else str(r)))
        out[key] = merged
        ida = set(json.dumps(x, sort_keys=True, ensure_ascii=False) if isinstance(x, dict) else str(x) for x in av)
        idb = set(json.dumps(x, sort_keys=True, ensure_ascii=False) if isinstance(x, dict) else str(x) for x in bv)
        print('  ledger %s %s: |A|=%d |B|=%d -> union=%d (zero-loss=%s)' % (path, key, len(av), len(bv), len(merged), len(merged) == len(ida | idb)))
    return out

memo = {}
print('== snapshot faces (deep-ts take-new) ==')
for p in SNAPSHOTS:
    side, why = pick_snapshot(p, memo)
    memo[p] = side
    print('%-52s -> %-6s (%s)' % (p, side, why))

print('== rolling-ledger faces (union) ==')
res_ledgers = {}
for p, keys in [(LEDGERS[0], ['history']), (LEDGERS[1], ['history', 'transitions', 'launches'])]:
    resolved = resolve_ledger(p, keys)
    res_ledgers[p] = resolved

# write back: snapshots by side, ledgers as resolved union
def write_bytes(path, data):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(data)

for p, side in memo.items():
    raw = blob(2 if side == 'ours' else 3, p)
    if p.endswith('.json'):
        json.loads(raw)  # r185 parse gate
    write_bytes(p, raw)
    print('written %s (side=%s)' % (p, side))

for p, obj in res_ledgers.items():
    raw = json.dumps(obj, ensure_ascii=False, indent=1)
    json.loads(raw)  # parse gate
    write_bytes(p, raw)
    print('written %s (union resolved)' % p)
print('RESOLVER DONE')
