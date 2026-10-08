"""W188 pre-finalize three-gate probe (r831 half-open engine-ignited wave semantics).

Gates (per pit-engine-finalize r752/r831/r482):
  G1 sum: sum(A n)==2000, sum(B n)==200, sum(audit.n_backtests)==2200
  G2 half-open tiling: A first x0==0, last x1==2000, adjacent y0==prev x1; B same to 200
  G3 seed continuity: A seed_rng set == 428404..430403 (2000 unique);
     B exit set == 430404..430603 (200 unique); B entry subset of A band; zero dup across shards
Output: results/_r889bma_w188_prefinalize_probe.json
"""
import json, glob

SHARDS = sorted(glob.glob('results/p2cal_ext/n1_w188/shard-*.json'))
A_LO, A_HI = 428404, 430403   # A staircase band (inclusive) -- FORTY-EIGHTH E36
B_LO, B_HI = 430404, 430603   # B own-A reserved W141 leg2 band (inclusive)
N_A, N_B, N_TOT = 2000, 200, 2200

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

def tiling(key_range, key_n, total):
    rs = [r[key_range] for r in sorted(recs, key=lambda x: x[key_range][0])]
    ok = rs[0][0] == 0 and rs[-1][1] == total
    for p, q in zip(rs, rs[1:]):
        if q[0] != p[1]:
            ok = False
    return ok, rs

g2a, a_rs = tiling('a_range', 'nA', N_A)
g2b, b_rs = tiling('b_range', 'nB', N_B)
g2 = g2a and g2b

g3 = (a_seeds == set(range(A_LO, A_HI + 1)) and b_exit == set(range(B_LO, B_HI + 1))
      and b_entry <= set(range(A_LO, A_HI + 1))
      and len(a_seeds) == sum_a and len(b_exit) == sum_b)

out = {
    'probe': 'W188 pre-finalize three-gate (r831 half-open)',
    'shards': len(SHARDS),
    'G1_sums': {'sum_A': sum_a, 'sum_B': sum_b, 'sum_backtests': sum_bt,
                'pass': g1},
    'G2_tiling_halfopen': {'pass': g2, 'A_ranges': a_rs, 'B_ranges': b_rs},
    'G3_seed_continuity': {'pass': g3, 'A_min': min(a_seeds), 'A_max': max(a_seeds),
                           'A_unique': len(a_seeds),
                           'B_exit_min': min(b_exit), 'B_exit_max': max(b_exit),
                           'B_exit_unique': len(b_exit),
                           'B_entry_in_band': max(b_entry) <= A_HI and min(b_entry) >= A_LO},
    'VERDICT': 'GREEN_FINALIZE_READY' if (g1 and g2 and g3) else 'RED_BLOCKED',
}
json.dump(out, open('results/_r889bma_w188_prefinalize_probe.json', 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(json.dumps({'G1': g1, 'G2': g2, 'G3': g3, 'VERDICT': out['VERDICT'],
                  'sum': [sum_a, sum_b, sum_bt], 'A_rng': a_rs, 'B_rng': b_rs}))
