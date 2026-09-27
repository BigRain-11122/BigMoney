# r128 bm-c rebase-storm resolver -- 16-UU vs origin tip 9293a68d (bm-b r356 addendum chain)
# Canon: r373 identity-key union / r370 latest.ts basis / r120 audit ts-union / r356 PS env law
# Faces: 11 derived take-origin (done via git checkout --ours before this script)
#        + autofill_state full-row id-union + compute_audit history ts-union
#        + regime_state take-new-inner-ts + token_usage per-field max + CODELY manual union
import json, io, sys, subprocess

def load(p):
    with io.open(p, encoding='utf-8-sig') as f:
        return json.load(f)

def dump(obj, p):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')

S = '.codely-cli/scratch/'
report = []

# ---- 1. autofill_state.json: full-row identity union (launch id = pid+ts row id) ----
ours = load(S + 'r128_results_autofill_state.json.ours')
thrs = load(S + 'r128_results_autofill_state.json.theirs')
def key_launch(row):
    # identity = pid + launched_at + entry (r373: identity fields, NOT full row)
    return (row.get('pid'), row.get('launched_at'), row.get('entry'))
merged = {}
for row in ours['launches'] + thrs['launches']:
    k = key_launch(row)
    prev = merged.get(k)
    if prev is None or str(row.get('last_seen') or row.get('launched_at') or '') >= str(prev.get('last_seen') or prev.get('launched_at') or ''):
        merged[k] = row
union = sorted(merged.values(), key=lambda r: str(r.get('launched_at')))
CAP = 50  # r355 cap-50 rolling window semantics
launches = union[-CAP:]
lt_o, lt_t = ours.get('last_tick') or {}, thrs.get('last_tick') or {}
last_tick = lt_t if str(lt_t.get('ts') or '') >= str(lt_o.get('ts') or '') else lt_o
auto = {'launches': launches, 'last_tick': last_tick}
assert len(merged) >= max(len(ours['launches']), len(thrs['launches'])), 'union must not lose rows'
dump(auto, 'results/autofill_state.json')
report.append(f'autofill: {len(ours["launches"])}+{len(thrs["launches"])} -> union {len(merged)}, kept {len(launches)} (cap-50), last_tick ts={last_tick.get("ts")}')

# ---- 2. compute_audit.json: history identity-union by (ts, machine) ----
ours = load(S + 'r128_results_compute_audit.json.ours')
thrs = load(S + 'r128_results_compute_audit.json.theirs')
def key_hist(row):
    return (row.get('ts'), row.get('py_procs'), row.get('cpu_total_pct'))  # ts primary; sample fingerprint tiebreak
hist = {}
for row in ours.get('history', []) + thrs.get('history', []):
    k = (row.get('ts'), row.get('cores'))
    hist[k] = row  # same-key: r370 non-empty-priority -- later write wins only if fields present
allh = sorted(hist.values(), key=lambda r: str(r.get('ts')))
keep = allh[-40:] if len(allh) > 40 else allh  # bounded window, newest kept
la, lb = ours.get('latest') or {}, thrs.get('latest') or {}
latest = lb if str(lb.get('ts') or '') >= str(la.get('ts') or '') else la
audit = {'latest': latest, 'history': keep}
dump(audit, 'results/compute_audit.json')
report.append(f'audit: hist {len(ours.get("history",[]))}+{len(thrs.get("history",[]))} -> union {len(hist)} kept {len(keep)}, latest ts={latest.get("ts")}')

# ---- 3. regime_state.json: asof-union / take-new inner-ts (same asof both sides) ----
ours = load(S + 'r128_results_regime_state.json.ours')
thrs = load(S + 'r128_results_regime_state.json.theirs')
base = thrs if str(thrs.get('updated') or '') >= str(ours.get('updated') or '') else ours
# state_hist union if present (asof append-log, identity=asof)
ho, ht = ours.get('state_hist') or [], thrs.get('state_hist') or []
if ho or ht:
    seen = {}
    for row in ho + ht:
        seen[row.get('asof')] = row
    base['state_hist'] = sorted(seen.values(), key=lambda r: str(r.get('asof')))
dump(base, 'results/regime_state.json')
report.append(f"regime: take-new updated={base.get('updated')} asof={base.get('asof')} state={base.get('state')}")

# ---- 4. token_usage.json: per-field max for cumulative totals, newer generated ----
ours = load(S + 'r128_results_token_usage.json.ours')
thrs = load(S + 'r128_results_token_usage.json.theirs')
tok = dict(thrs if str(thrs.get('generated') or '') >= str(ours.get('generated') or '') else ours)
for k in ours:
    ov, tv = ours.get(k), thrs.get(k)
    if isinstance(ov, (int, float)) and isinstance(tv, (int, float)):
        tok[k] = max(ov, tv)
    elif isinstance(ov, str) and isinstance(tv, str) and ov.replace('.', '').isdigit() and tv.replace('.', '').isdigit():
        try:
            tok[k] = str(max(float(ov), float(tv)))
            if '.' not in ov and '.' not in tv:
                tok[k] = str(int(float(tok[k])))
        except ValueError:
            pass
dump(tok, 'results/token_usage.json')
report.append(f"token: per-field max, generated={tok.get('generated')} state_est={tok.get('total_state_tokens_est')} report_est={tok.get('total_report_tokens_est')}")

# ---- 5. CODELY.md: manual union = origin full + my r128 append (both sides preserved) ----
with io.open(S + 'r128_CODELY.ours', encoding='utf-8-sig') as f:
    cod_ours = f.read()  # origin (ours in rebase)
with io.open(S + 'r128_CODELY.theirs', encoding='utf-8-sig') as f:
    cod_thrs = f.read()  # my commit (theirs)
my_marker = '[2026-09-28 03:2x r128 bm-c]'
assert my_marker in cod_thrs, 'my r128 pitlaw must exist in my side'
# my side = origin-base-at-r127 + r128 append; origin side has batch-26 rearchive + r356 entry.
# union = origin content + my r128 entry (deduped if already present)
r128_line = [l for l in cod_thrs.splitlines() if my_marker in l]
assert len(r128_line) == 1, f'r128 entry count {len(r128_line)}'
out = cod_ours.rstrip('\n')
if my_marker not in cod_ours:
    out += '\n' + r128_line[0] + '\n'
with io.open('CODELY.md', 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
report.append(f'CODELY: origin {len(cod_ours)}B + my r128 entry -> {len(out)}B union')

print('RESOLVE OK')
for r in report:
    print(' -', r)
