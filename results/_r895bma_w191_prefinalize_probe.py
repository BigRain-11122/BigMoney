"""W191 pre-finalize three-gate probe (r831 half-open engine-ignited wave semantics).

Mirrors r892 W190 probe one wave later (r891 W189 precedent). Gates per
pit-engine-finalize r752/r831/r482/r708/r807:
  G1 sum: sum(A n)==2000, sum(B n)==200, sum(audit.n_backtests)==2200
  G2 half-open tiling: A first x0==0, last x1==2000, adjacent y0==prev x1; B same to 200
  G3 seed continuity: A seed_rng set == 435_004..437_003 (2000 unique, FIFTY-FIRST
     E36 staircase A-hops-prior-B, hops=1 past W190 B band); B exit set ==
     437_004..437_203 (200 unique, own-A tail+1, hops=1 reserved walk); B entry
     subset of own-wave A band; zero dup across shards (r482 id-level zero-dup)
  G4 idempotence (r538): finalize output results/perpetual_faces/n1_w191_results.json
     must NOT exist (no self-produced uncommitted wave product in prev derive face)
  G5 live process (r708): no running perpetual_faces_n1.py finalize/aggregator process
  G6 chain head (r807): science_gates ledger_head() total == 831,336 = registry-prose
     post-W190 head 825,328 + 6,008 bm-b r807 FUND-trio append-style re-anchor
     (head_file must be fund_trio_p1_ledger_reanchor.json; re-anchor landed origin
     01:1x per pit-protocol-judge r807 law -- live data-driven head is canonical)
Output: results/_r895bma_w191_prefinalize_probe.json (machine-suffixed D-20261008-02)
"""
import glob, json, subprocess, sys

SHARDS = sorted(glob.glob('results/p2cal_ext/n1_w191/shard-*.json'))
A_LO, A_HI = 435004, 437003   # W191 A band (inclusive) -- FIFTY-FIRST E36 staircase
B_LO, B_HI = 437004, 437203   # W191 B band (inclusive) -- own-A tail+1, hops=1
N_A, N_B, N_TOT = 2000, 200, 2200
OUT = 'results/perpetual_faces/n1_w191_results.json'
EXPECTED_HEAD = 831336  # 825,328 (registry prose) + 6,008 bm-b r807 FUND-trio re-anchor

recs = []
sum_a = sum_b = sum_bt = 0
a_seeds, b_exit, b_entry = set(), set(), set()
for f in SHARDS:
    d = json.load(open(f, encoding='utf-8'))
    fam = d['families']
    nA = fam['A_random_engine_exit']['n']
    nB = fam['B_random_entry_random_exit']['n']
    sum_a += nA; sum_b += nB; sum_bt += d['audit']['n_backtests']
    a_seeds |= {r['seed_rng'] for r in fam['A_random_engine_exit']['runs']}
    b_exit |= {r['seed_rng_exit'] for r in fam['B_random_entry_random_exit']['runs']}
    b_entry |= {r['seed_rng_entry'] for r in fam['B_random_entry_random_exit']['runs']}
    recs.append({'shard': d['shard'], 'a_range': d['a_range'], 'b_range': d['b_range'],
                 'nA': nA, 'nB': nB, 'n_bt': d['audit']['n_backtests']})

g1 = (sum_a == N_A and sum_b == N_B and sum_bt == N_TOT)

def tiling(key_range, total):
    rs = [r[key_range] for r in sorted(recs, key=lambda x: x[key_range][0])]
    ok = rs[0][0] == 0 and rs[-1][1] == total
    for p, q in zip(rs, rs[1:]):
        if q[0] != p[1]:
            ok = False
    return ok, rs

g2a, a_rs = tiling('a_range', N_A)
g2b, b_rs = tiling('b_range', N_B)
g2 = g2a and g2b

g3 = (a_seeds == set(range(A_LO, A_HI + 1)) and b_exit == set(range(B_LO, B_HI + 1))
      and b_entry <= set(range(A_LO, A_HI + 1))
      and len(a_seeds) == sum_a and len(b_exit) == sum_b)

g4 = not glob.glob(OUT)

try:
    procs = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match 'perpetual_faces_n1\\.py (finalize|aggregate)'} | Select-Object -ExpandProperty ProcessId"],
        capture_output=True, text=True)
    live_pids = [p.strip() for p in procs.stdout.split() if p.strip()]
except Exception:
    live_pids = ["PROBE_ERROR"]
g5 = live_pids == []

sys.path.insert(0, 'scripts')
sys.path.insert(0, '.')
import science_gates
head = science_gates.ledger_head()
g6 = head.get('total') == EXPECTED_HEAD

out = {
    'probe': 'W191 pre-finalize six-gate (r831 half-open + r708 live-proc + r807 head)',
    'shards': len(SHARDS),
    'G1_sums': {'sum_A': sum_a, 'sum_B': sum_b, 'sum_backtests': sum_bt, 'pass': g1},
    'G2_tiling_halfopen': {'pass': g2, 'A_ranges': a_rs, 'B_ranges': b_rs},
    'G3_seed_continuity': {'pass': g3, 'A_min': min(a_seeds) if a_seeds else None,
                           'A_max': max(a_seeds) if a_seeds else None,
                           'A_unique': len(a_seeds),
                           'B_exit_min': min(b_exit) if b_exit else None,
                           'B_exit_max': max(b_exit) if b_exit else None,
                           'B_exit_unique': len(b_exit),
                           'B_entry_in_band': (max(b_entry) <= A_HI and min(b_entry) >= A_LO) if b_entry else False},
    'G4_output_absent': g4,
    'G5_no_live_finalize_proc': {'pass': g5, 'pids': live_pids},
    'G6_chain_head': {'pass': g6, 'head_total': head.get('total'),
                      'expected_prev': EXPECTED_HEAD, 'head_file': head.get('file')},
    'VERDICT': 'GREEN_FINALIZE_READY' if (g1 and g2 and g3 and g4 and g5 and g6) else 'RED_BLOCKED',
}
json.dump(out, open('results/_r895bma_w191_prefinalize_probe.json', 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(json.dumps({'G1': g1, 'G2': g2, 'G3': g3, 'G4': g4, 'G5': g5, 'G6': g6,
                  'VERDICT': out['VERDICT'], 'sum': [sum_a, sum_b, sum_bt],
                  'head': head.get('total'), 'shards': len(SHARDS)}))
