# -*- coding: utf-8 -*-
"""r84 bm-c probe: autofill_state.json rebase collision (S0 re-land of f01947ff onto dd34727b).

Rebase stages: :1 = base (f01947ff^ = bb8befda), :2 = ours (origin tip dd34727b),
:3 = theirs (f01947ff round-84 pre-pull tick). Pure measurement face; zero-loss probe.
"""
import json, subprocess

def stage(n):
    b = subprocess.run(['git', 'show', f':{n}:results/autofill_state.json'],
                       capture_output=True, check=True).stdout
    txt = b.decode('utf-8')
    return json.loads(txt), b

K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
               r.get('runner_sha256'), r.get('entry'), r.get('shard'))

base, base_b = stage(1)
ours, ours_b = stage(2)
theirs, theirs_b = stage(3)

for name, d, b in (('base', base, base_b), ('ours(dd34727b)', ours, ours_b),
                   ('theirs(f01947ff)', theirs, theirs_b)):
    print(f"{name}: launches={len(d['launches'])} last_tick={d['last_tick']} "
          f"crlf={b.count(b'\r\n')} lf={b.count(b'\n')}")

ok, tk = {}, {}
for r in ours['launches']:
    ok.setdefault(K(r), []).append(r)
for r in theirs['launches']:
    tk.setdefault(K(r), []).append(r)

only_ours = [k for k in ok if k not in tk]
only_theirs = [k for k in tk if k not in ok]
print(f"only_ours={len(only_ours)} only_theirs={len(only_theirs)}")
for k in only_ours:
    print('  OURS-ONLY:', k, 'cc=', ok[k][0].get('crash_counted'))
for k in only_theirs:
    print('  THEIRS-ONLY:', k, 'cc=', tk[k][0].get('crash_counted'))

same_key_diff = []
for k in sorted(set(ok) & set(tk)):
    o, t = ok[k][0], tk[k][0]
    diff = {f for f in set(o) | set(t) if o.get(f) != t.get(f)}
    if diff:
        same_key_diff.append((k, sorted(diff)))
print(f"same-key content diffs: {len(same_key_diff)}")
for k, d in same_key_diff:
    print('  DIFF:', k, d)

# in-side duplicate check (r322 composite-key law)
for name, m in (('ours', ok), ('theirs', tk)):
    dups = {k: len(v) for k, v in m.items() if len(v) > 1}
    print(f"{name} in-side dups: {dups if dups else 0}")

# what changed vs base per side (context for verdict)
for name, d in (('ours', ours), ('theirs', theirs)):
    bk = {K(r) for r in base['launches']}
    added = [k for k in {K(r) for r in d['launches']} if k not in bk]
    print(f"{name} vs base: +{len(added)} {added[:3]} last_tick_delta={d['last_tick'] != base['last_tick']}")
