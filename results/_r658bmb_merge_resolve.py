"""r658 bm-b rebase UU resolver (13 faces, r652/r657 recipes).
HEAD = origin side (bm-c r455 union product + waves, ts 08:39-41)
REBASE_HEAD = my r658 wave (S6 regen, ts 08:45-46, newer)
Recipes:
  - 12 regen faces: honest-ts take-MINE (newer)
  - compute_audit.json: history exact-row-dedup union zero-loss, latest=mine(newest)
Surgery only -- no add/commit here (r657 law: surgery decoupled from chains).
"""
import subprocess, json, os

HEAD = 'e1dd04ac62fa3f7f2a3e70b2be36ba4504cbe0aa'
MINE = 'fb4f59899bdd6731d4275ab7e224b11407e52229'

def gv(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    assert r.returncode == 0, f'show failed {rev}:{path}'
    return r.stdout

TAKE_MINE = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

report = []

# --- 1. plain take-mine faces (raw bytes) ---
for p in TAKE_MINE:
    b = gv(MINE, p)
    if p.endswith('.json'):
        json.loads(b.decode('utf-8'))  # reparse guard
    open(p, 'wb').write(b)
    report.append(f"take-mine: {p} ({len(b)}B)")

# --- 2. compute_audit union (zero-loss, exact-row dedup, sort by ts) ---
ca_path = 'results/compute_audit.json'
o = json.loads(gv(HEAD, ca_path).decode('utf-8'))
m = json.loads(gv(MINE, ca_path).decode('utf-8'))
oh, mh = o.get('history', []), m.get('history', [])
seen = set()
union = []
for row in oh + mh:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(row)
union.sort(key=lambda r: r.get('ts', ''))
# containment evidence: every origin row and every mine row present
o_set = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in oh}
m_set = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in mh}
u_set = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in union}
assert o_set <= u_set and m_set <= u_set, 'union containment FAILED'
out = {
    'latest': union[-1],
    'history': union,
    'machines': o.get('machines', {}),
    'ts': m.get('latest', {}).get('ts', o.get('ts')),
}
blob = json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8')
json.loads(blob.decode('utf-8'))  # reparse guard
open(ca_path, 'wb').write(blob)
report.append(
    f"compute_audit union: origin={len(oh)} mine={len(mh)} -> union={len(union)} "
    f"(o_contained={len(o_set & u_set)}/{len(o_set)}, m_contained={len(m_set & u_set)}/{len(m_set)}), "
    f"latest ts={union[-1].get('ts')}")

# --- 3. conflict-marker zero check on all touched files (line-start per r657 law) ---
MARKERS = ('<<<<<<<', '=======', '>>>>>>>')
bad = []
for p in TAKE_MINE + [ca_path]:
    with open(p, 'rb') as f:
        for ln in f:
            s = ln.lstrip()
            if any(s.startswith(mk.encode()) for mk in MARKERS):
                bad.append(p)
                break
if bad:
    raise SystemExit('MARKERS REMAIN: ' + ','.join(bad))
report.append('conflict-marker scan: 13/13 line-start clean')

for ln in report:
    print(ln)
ev = os.path.join('results', '_r658bmb_merge_resolve.txt')
with open(ev, 'a', encoding='utf-8') as f:
    f.write('=== r658 rebase UU resolve ===\n' + '\n'.join(report) + '\n')
print('RESOLVE DONE (surgery only; add/continue run separately)')
