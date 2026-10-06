# r780 bm-b V-gap refill verification (P0 fact-check, read-only)
# r779 diagnosis: 14 missing ks [280,281,282,347,419,1738,1744,1803,1854,1929,1930,1931,1995,1996]
import json

MISSING = [280, 281, 282, 347, 419, 1738, 1744, 1803, 1854, 1929, 1930, 1931, 1995, 1996]
ks = {}
dups = []
with open('results/fund_value_p1/nulls.jsonl', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        k = obj.get('k', obj.get('draw', obj.get('idx')))
        if k in ks:
            dups.append((k, ks[k], i))
        ks[k] = i

present = sorted(ks)
n = len(present)
full = set(range(1, 2001))
have = set(present)
gaps = sorted(full - have)
extra = sorted(have - full)
filled = [k for k in MISSING if k in have]
still = [k for k in MISSING if k not in have]
print(json.dumps({
    'lines': sum(1 for _ in open('results/fund_value_p1/nulls.jsonl', encoding='utf-8')),
    'unique_ks': n,
    'dup_count': len(dups),
    'dup_examples': dups[:5],
    'missing_ks_now': gaps,
    'out_of_range': extra,
    'r779_targets_filled': filled,
    'r779_targets_still_missing': still,
    'range_1_2000_complete': n == 2000 and not gaps,
}, ensure_ascii=False))
