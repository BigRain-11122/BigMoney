"""r831 W175 pre-finalize gate: r752 three-identity gate + r482 dup probe + r708 live-process check (leg A).

Gate 1: dual selftest (n1 engine + pf law bands) -- run separately (mutating runner faces).
Gate 2: shard-total identity: sum(A spans) == 2000, sum(B spans) == 200, sum(n_backtests) == 2200.
Gate 3: cross-shard seed continuity: A spans tile [0..1999] seamlessly (+1 joins), B spans tile [0..199].
Plus r482: no duplicate shard ids; r708: no live finalize/process of same runner.
"""
import json, glob, os, subprocess

files = sorted(glob.glob('results/p2cal_ext/n1_w178/shard-*.json'), key=lambda f: int(f.split('shard-')[1].split('-')[0]))
assert len(files) == 12, f'expected 12 shards, got {len(files)}'

spans_a, spans_b, ids, nbts = [], [], [], 0
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    assert d.get('audit', {}).get('n_backtests'), f'{f}: no audit (burn incomplete)'
    a0, a1 = d['a_range']
    b0, b1 = d['b_range']
    spans_a.append((a0, a1))
    spans_b.append((b0, b1))
    ids.append(d['shard'])
    nbts += d['audit']['n_backtests']

# Gate 2: totals
n_a = sum(e - s + 1 for s, e in spans_a)
n_b = sum(e - s + 1 for s, e in spans_b)
print(f'Gate2 totals: A seeds={n_a} (want 2000), B seeds={n_b} (want 200), n_backtests={nbts} (want 2200)')
ok2 = (n_a, n_b, nbts) == (2000, 200, 2200)

# Gate 3: seamless tiling
def tiling_ok(spans, lo, hi):
    spans = sorted(spans)
    if spans[0][0] != lo or spans[-1][1] != hi:
        return False, f'endpoints {spans[0]}..{spans[-1]} != [{lo},{hi}]'
    for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
        if s2 != e1 + 1:
            return False, f'gap/overlap at {e1}->{s2}'
    return True, 'seamless'

ok3a, msg_a = tiling_ok(spans_a, 0, 1999)
ok3b, msg_b = tiling_ok(spans_b, 0, 199)
print(f'Gate3 A tiling: {ok3a} ({msg_a})')
print(f'Gate3 B tiling: {ok3b} ({msg_b})')

# r482 dup probe
dup = len(ids) != len(set(ids))
print(f'r482 dup shard ids: {"DUP!" if dup else "none"} ({sorted(ids)})')

# scientific face identity across all 12 (freeze fields identical)
ref = json.load(open(files[0], encoding='utf-8'))
face_keys = ['batch', 'preregistered_doc', 'law_ref', 'evidence_cutoff', 'nshards']
face_mismatch = []
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    for k in face_keys:
        if d.get(k) != ref.get(k):
            face_mismatch.append((f, k))
print(f'freeze-face identity: {"PASS" if not face_mismatch else face_mismatch}')

# r708 live-process check (finalize/aggregator same-runner probe)
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                   "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
                   "Where-Object {$_.CommandLine -match 'perpetual_faces_n1' -or $_.CommandLine -match 'finalize'} | "
                   "Select-Object ProcessId,CommandLine | ConvertTo-Json"], capture_output=True, text=True)
out = (r.stdout or '').strip()
live = [ln for ln in out.splitlines() if 'perpetual_faces_n1' in ln or 'finalize' in ln]
print(f'r708 live same-runner processes: {"NONE" if not live else live[:3]}')

all_ok = ok2 and ok3a and ok3b and not dup and not face_mismatch
print(f'\nPRE-FINALIZE VERDICT: {"GREEN" if all_ok else "RED - DO NOT FINALIZE"}')
