# -*- coding: utf-8 -*-
"""r84 bm-c resolver: results/autofill_state.json S0 rebase collision
(re-land of unpushed f01947ff r84-pre-pull tick onto origin dd34727b).

Probe (_r84bmc_probe.py) verdict:
  both sides 44 launches, key sets IDENTICAL (zero add/del, zero in-side dups);
  only divergence = crash_counted on 6 bm-c T19-PHANTOM-P1 records
  (ours/dd34727b = None -- stripped by remote-side sweep-in 80a57a54 bm-b r327;
   theirs/f01947ff = True, inherited from post-r83-resolve base bb8befda);
  last_tick same-second tie 13:40:02 (ours bm-b vs theirs bm-c).

Canon applied:
  r322 composite-key field-union (None vs True -> True, additive fact);
  r140/r325 last_tick same-second tie -> HEAD (= ours, the side rebased onto);
  r245 re-sort ts ascending before write-back; base blob line-ending mirror
  (base=LF crlf=0, indent=1); r185 parse-verify before add.
"""
import io, json, subprocess

def stage(n):
    b = subprocess.run(['git', 'show', f':{n}:results/autofill_state.json'],
                       capture_output=True, check=True).stdout
    return json.loads(b.decode('utf-8')), b

ours, ours_b = stage(2)
theirs, theirs_b = stage(3)
base, base_b = stage(1)

K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
               r.get('runner_sha256'), r.get('entry'), r.get('shard'))

ok = {K(r): r for r in ours['launches']}
tk = {K(r): r for r in theirs['launches']}
assert len(ok) == len(ours['launches']) == 44, 'ours key uniqueness broken'
assert len(tk) == len(theirs['launches']) == 44, 'theirs key uniqueness broken'
assert set(ok) == set(tk), 'probe said identical key sets -- changed?'
assert base_b.count(b'\r\n') == 0, 'base expected LF (probe)'

merged = {}
cc_restored = 0
for k in ok:
    o, t = ok[k], tk[k]
    rec = dict(o)
    for f, v in t.items():
        if f not in rec or rec.get(f) != v:
            if f == 'crash_counted' and v is True:
                rec[f] = v          # r322 field-union: additive fact wins
                cc_restored += 1
            else:
                raise AssertionError(f'true divergence at {k}: {f} '
                                     f'{rec.get(f)!r} vs {v!r}')
    merged[k] = rec
assert cc_restored == 6, f'expected 6 cc restorations, got {cc_restored}'
assert len(merged) == 44

# r245: producer=append order; write back must be ts ascending (stable for ties)
launches = sorted(merged.values(), key=lambda r: r['ts'])

# r140/r325: last_tick same-second tie -> HEAD (ours = side rebased onto)
lo, lt = ours['last_tick'], theirs['last_tick']
assert lo['ts'] == lt['ts'] == '2026-09-27 13:40:02', (lo, lt)
last = dict(lo)
assert isinstance(last, dict)

out = {'launches': launches, 'last_tick': last}
io.open('results/autofill_state.json', 'w', encoding='utf-8',
        newline='\n').write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')

# r185 strict re-verify
d = json.loads(io.open('results/autofill_state.json', encoding='utf-8').read())
assert len(d['launches']) == 44
keys = [K(r) for r in d['launches']]
assert len(set(keys)) == 44, 'dup residue'
assert all(r.get('crash_counted') is True for r in d['launches']), 'cc gap'
assert d['last_tick'] == {'ts': '2026-09-27 13:40:02', 'machine': 'bm-b',
                          'py_cpu_pct': 0.0, 'verdict': 'pool_empty_or_busy'}
assert [r['ts'] for r in d['launches']] == sorted(r['ts'] for r in d['launches'])
print(f'UNION-OK launches=44 (keysets identical, zero add/del) cc_restored=6 '
      f'(None->True r322 field-union; stripped face originated in remote '
      f'80a57a54 sweep-in, evidence for bm-b self-audit) last_tick=bm-b '
      f'13:40:02 (same-sec tie->HEAD per r140/r325) LF mirror base, ts-asc r245')
