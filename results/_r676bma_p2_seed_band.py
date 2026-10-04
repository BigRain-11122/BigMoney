# _r676bma_p2_seed_band.py -- THEME-JUDGE-P2 nulls seed band disjoint scan (pre-freeze gate)
# Registers nothing; pure scan + receipt. Registration happens in science_gates at freeze.
import sys, json
sys.path.insert(0, 'scripts')
sys.path.insert(0, '.')
import science_gates

CAND_BASE = 20589000  # candidate band start for theme_judge_p2_nulls
BAND_W = 2000

reg = science_gates.SEED_REGISTRY
def band_of(v):
    # registry values are band BASES; bands are [base, base+2000) per P1 precedent
    return (v, v + 2000)

clashes = []
min_gap = None
for k, v in reg.items():
    if not isinstance(v, (int, float)):
        continue
    lo, hi = band_of(int(v))
    gap = max(lo - (CAND_BASE + BAND_W), CAND_BASE - hi)
    if min_gap is None or gap < min_gap:
        min_gap = gap; nearest = k
    if gap < 2000:
        clashes.append((k, int(v), gap))

cand_lo, cand_hi = CAND_BASE, CAND_BASE + BAND_W
receipt = {
    'batch': 'THEME-JUDGE-P2',
    'seed_key': 'theme_judge_p2_nulls',
    'band': [cand_lo, cand_hi],
    'band_width': BAND_W,
    'registry_size': len(reg),
    'clashes_lt_2000': clashes,
    'min_gap': min_gap,
    'nearest_entry': nearest if min_gap is not None else None,
    'verdict': 'ADMIT' if not clashes else 'REJECT',
}
open('results/theme_judge_p2_seed_band_receipt.json', 'w', encoding='utf-8').write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print('verdict:', receipt['verdict'], '| min_gap:', min_gap, '| nearest:', receipt['nearest_entry'])
