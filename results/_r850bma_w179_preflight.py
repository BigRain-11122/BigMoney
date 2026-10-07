"""r850 W179 pre-finalize gate: r752 three-identity gates (half-open convention per r839 W176 canon;
r846 W178 preflight bloodline adapted -- W179 bands from frozen prereg 6f14c35d5/ef540bf8f).

Gate 1: shard-total identity: A runs == 2000, B runs == 200, sum(audit.n_backtests) == 2200,
        per-shard audit.n_backtests == per-shard run count.
Gate 2: seed identity: A seed_rng unique=2000 sweep 408604..410603 EXACT (W179 prereg A band
        408_604..410_603 staircase 39th); B seed_rng_exit unique=200 sweep 410604..410803 EXACT
        (W179 prereg B band 410_604..410_803 own-A reservation); B seed_rng_entry inside A sweep.
Gate 3: half-open tiling: a_range spans tile [0,2000) contiguous, b_range spans tile [0,200) contiguous.
Plus r482: no duplicate shard ids; r708: no live finalize process of same runner;
freeze-face identity: n1 source carries W179 registration.
"""
import json, glob, subprocess

W = 'n1_w179'
files = sorted(glob.glob('results/p2cal_ext/%s/shard-*.json' % W), key=lambda f: int(f.split('shard-')[1].split('-')[0]))
assert len(files) == 12, 'expected 12 shards, got %d' % len(files)

a_seeds, b_exit, b_entry, ids, nbt_total = [], [], [], [], 0
spans_a, spans_b = [], []
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    assert d.get('audit', {}).get('n_backtests'), '%s: no audit (burn incomplete)' % f
    fa = d['families']['A_random_engine_exit']
    fb = d['families']['B_random_entry_random_exit']
    runs_total = len(fa['runs']) + len(fb['runs'])
    assert d['audit']['n_backtests'] == runs_total, '%s: audit nbt %s != runs %d' % (f, d['audit']['n_backtests'], runs_total)
    a_seeds += [r['seed_rng'] for r in fa['runs']]
    b_exit += [r['seed_rng_exit'] for r in fb['runs']]
    b_entry += [r['seed_rng_entry'] for r in fb['runs']]
    ids.append(d['shard'])
    spans_a.append(tuple(d['a_range']))
    spans_b.append(tuple(d['b_range']))
    nbt_total += d['audit']['n_backtests']

# Gate 1: totals (half-open: count = e - s)
n_a = sum(e - s for s, e in spans_a)
n_b = sum(e - s for s, e in spans_b)
print('Gate1 totals: A runs=%d (want 2000) B runs=%d (want 200) nbt=%d (want 2200)' % (len(a_seeds), len(b_exit), nbt_total))
ok1 = (len(a_seeds), len(b_exit), nbt_total) == (2000, 200, 2200)

# Gate 2: seed identity (W179 bands)
ua = sorted(set(a_seeds)); ub = sorted(set(b_exit))
print('Gate2 A: unique=%d min=%d max=%d' % (len(ua), ua[0], ua[-1]))
print('Gate2 B: unique=%d min=%d max=%d' % (len(ub), ub[0], ub[-1]))
ok2 = (len(ua) == 2000 and ua == list(range(408604, 410604))
       and len(ub) == 200 and ub == list(range(410604, 410804))
       and set(b_entry) <= set(ua))

# Gate 3: half-open tiling contiguous
def tiling_ok(spans, hi):
    spans = sorted(spans)
    if spans[0][0] != 0 or spans[-1][1] != hi:
        return False, 'endpoints (%d,%d)..(%d,%d) != [0,%d)' % (spans[0][0], spans[0][1], spans[-1][0], spans[-1][1], hi)
    cur = 0
    for s, e in spans:
        if s != cur or e <= s:
            return False, 'gap/overlap at %s (cur=%d)' % ((s, e), cur)
        cur = e
    return True, 'half-open contiguous [0,%d) PASS' % hi
ok3a, msg3a = tiling_ok(spans_a, 2000)
ok3b, msg3b = tiling_ok(spans_b, 200)
print('Gate3 A tiling:', ok3a, msg3a)
print('Gate3 B tiling:', ok3b, msg3b)

# r482 dup shard ids
ok4 = len(set(ids)) == 12
print('r482 dup shard ids:', 'none' if ok4 else sorted(ids))

# r708: no live finalize proc of same runner
ps = subprocess.run(['powershell', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | Select-Object -ExpandProperty CommandLine"],
    capture_output=True).stdout.decode('gbk', errors='replace')
live_fin = [l for l in ps.splitlines() if 'finalize' in l and W in l]
ok5 = not live_fin
print('r708 live same-runner processes:', live_fin if live_fin else 'none')

# freeze-face identity: W179 registration in n1 source + wave row count sanity
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8', errors='replace').read()
ok6 = 'WAVE_CONFIGS[179]' in src or "'179':" in src or '"179":' in src or '[179]' in src
print('freeze-face identity (n1 source has 179):', ok6)

verdict = ok1 and ok2 and ok3a and ok3b and ok4 and ok5 and ok6
print('PRE-FINALIZE VERDICT:', 'GREEN_FINALIZE_READY' if verdict else 'RED - DO NOT FINALIZE')
raise SystemExit(0 if verdict else 1)
