# -*- coding: utf-8 -*-
"""r83 bm-c resolver #2: autofill_state.json rebase-replay UU (push-collision batch).

Rebase context: my S0-receipt commit (85d63ee0) replaying onto origin/main 6afba45c
(bm-b r326). Stage mapping per r323 rebase-inversion: stage2(ours)=origin/new
(bm-b r326: 44 launches, 38 cc, last_tick bm-b 13:30:02), stage3(theirs)=mine
(44 launches, 44 cc, last_tick bm-a 13:20:02). Base(stage1)=pre-rebase 50-launch
legacy with 6 dup pairs.

Canon (SKILL.md mixed-dict+ledger recipe incl. this-round dedup step):
  launches: union -> same-composite-key content-identity verify (field-set diff
            must be additive-only -> field-union merge keep-one; real divergence =
            escalate, never silent double-store) -> ts desc cap50 -> re-sort asc.
            Here both sides deduped to the SAME 44 unique keys; 6 records differ
            only by crash_counted (absent vs true) = additive field -> union true.
  last_tick: internal-ts compare, newer wins -> bm-b 13:30:02 (no tie this time).
"""
import io, json, subprocess

P = 'results/autofill_state.json'
K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
               r.get('runner_sha256'), r.get('entry'), r.get('shard'))

def stage(n):
    b = subprocess.run(['git', 'show', f':{n}:{P}'], capture_output=True, check=True)
    return json.loads(b.stdout.decode('utf-8'))

base, ours, theirs = stage(1), stage(2), stage(3)
ko, kt = {K(r) for r in ours['launches']}, {K(r) for r in theirs['launches']}
assert ko == kt, 'key-set divergence would need escalation'
assert len(ours['launches']) == len(theirs['launches']) == 44

merged_keys = []
n_union_cc = 0
for k in sorted(kt):  # ts asc via tuple sort (ts is first element)
    a = next(r for r in ours['launches'] if K(r) == k)
    b = next(r for r in theirs['launches'] if K(r) == k)
    diff = {f for f in set(a) | set(b) if a.get(f) != b.get(f)}
    if diff:
        assert diff == {'crash_counted'}, (k, sorted(diff))
        # additive field-union: true supersedes absent (crash already counted on
        # the producing machine bm-c; true side prevents double-count)
        assert b.get('crash_counted') is True and 'crash_counted' not in a, (k, a, b)
        rec = dict(a); rec['crash_counted'] = True
        n_union_cc += 1
    else:
        rec = dict(a)
    merged_keys.append(rec)

# cap50 (44 < 50, no-op by count) + already ts-asc sorted
assert len(merged_keys) == 44

# last_tick: internal ts compare, newer wins
lo, lt = ours['last_tick'], theirs['last_tick']
last = lo if lo['ts'] >= lt['ts'] else lt
assert last == {'ts': '2026-09-27 13:30:02', 'machine': 'bm-b',
                'py_cpu_pct': 0.0, 'verdict': 'pool_empty_or_busy'}

out = {'launches': merged_keys, 'last_tick': last}
io.open(P, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, ensure_ascii=False, indent=1) + '\n')

# strict re-verify
d = json.loads(io.open(P, encoding='utf-8').read())
ks = [K(r) for r in d['launches']]
assert len(ks) == len(set(ks)) == 44, 'dup residue'
assert all(r.get('crash_counted') is True for r in d['launches']), 'cc gap'
assert d['last_tick']['machine'] == 'bm-b' and d['last_tick']['ts'] == '2026-09-27 13:30:02'
assert [r['ts'] for r in d['launches']] == sorted(r['ts'] for r in d['launches']), 'order'
print(f'UNION2-OK launches=44(44 cc, {n_union_cc} field-union) last_tick=bm-b 13:30:02 (newer-wins)')
