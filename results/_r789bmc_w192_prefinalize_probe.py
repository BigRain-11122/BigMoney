"""W192 pre-finalize six-gate probe (r381 recovery-round-first-action law:
bm-c-owned wave 12/12 delivered 03:48, finalize same-window per
pit-engine-finalize r381/r752/r482/r708/r807 -- clone of r895 W191 probe one
wave later; G5 live-proc face switched to psutil (zero-window law, same
r708 semantics).  Gates:
  G1 sum: sum(A n)==2000, sum(B n)==200, sum(audit.n_backtests)==2200
  G2 half-open tiling: A first x0==0, last x1==2000, adjacent y0==prev x1; B same to 200
  G3 seed continuity: A seed_rng set == 437_204..439_203 (2000 unique, E36
     staircase A-hops-prior-B FIFTY-SECOND, W191 B tail+1); B exit set ==
     439_204..439_403 (200 unique, own-A tail+1, W141 same-freeze leg2); B
     entry subset of own-wave A band; zero dup across shards (r482)
  G4 idempotence (r538): results/perpetual_faces/n1_w192_results.json must NOT exist
  G5 live process (r708): no running perpetual_faces_n1.py finalize/aggregate proc
  G6 chain head (r807 live-data-driven): science_gates ledger_head() total ==
     834,545 = W191 n1 landed 833,536 + bm-a r899 F1-BULL-COND-P1 1,009 EXACT
Output: results/_r789bmc_w192_prefinalize_probe.json (machine-suffixed)
"""
import glob, json, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SHARDS = sorted(glob.glob('results/p2cal_ext/n1_w192/shard-*.json'))
A_LO, A_HI = 437204, 439203   # W192 A band (inclusive) -- FIFTY-SECOND E36 staircase
B_LO, B_HI = 439204, 439403   # W192 B band (inclusive) -- own-A tail+1, W141 leg2
N_A, N_B, N_TOT = 2000, 200, 2200
OUT = 'results/perpetual_faces/n1_w192_results.json'
EXPECTED_HEAD = 834545  # 833,536 (W191) + 1,009 (bm-a r899 F1-BULL-COND-P1)

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
    import psutil
    live_pids = []
    for p in psutil.process_iter(['pid', 'cmdline']):
        try:
            cl = p.info['cmdline'] or []
        except Exception:
            continue
        j = ' '.join(cl)
        if 'perpetual_faces_n1.py' in j and ('finalize' in j or 'aggregate' in j):
            live_pids.append(p.info['pid'])
except Exception:
    live_pids = ["PROBE_ERROR"]
g5 = live_pids == []

sys.path.insert(0, 'scripts')
sys.path.insert(0, '.')
import science_gates
head = science_gates.ledger_head()
g6 = head.get('total') == EXPECTED_HEAD

out = {
    'probe': 'W192 pre-finalize six-gate (r381 recovery-first + r708 live-proc psutil + r807 live head)',
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
json.dump(out, open('results/_r789bmc_w192_prefinalize_probe.json', 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(json.dumps({'G1': g1, 'G2': g2, 'G3': g3, 'G4': g4, 'G5': g5, 'G6': g6,
                  'VERDICT': out['VERDICT'], 'sum': [sum_a, sum_b, sum_bt],
                  'head': head.get('total'), 'shards': len(SHARDS)}))
