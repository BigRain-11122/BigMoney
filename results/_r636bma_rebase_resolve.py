"""r636 bm-a: rebase UU resolution (4 files) per conflict canon.

- nulls.jsonl: take OURS (origin side = bm-b canonical; my 25 illegal rows drop
  out of the replayed housekeeping commit entirely -- r622 discard precedent).
- _r633bma rehearsal JSONs: take THEIRS (mine -- bm-a own products, newer ts).
- pool_core_samples.jsonl: exact-line union ours+theirs (append-only, r294/r630).
"""
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                         errors='replace')


# 1) nulls.jsonl: ours (origin canonical)
r = run(['git', 'checkout', '--ours', 'results/fund_value_p1/nulls.jsonl'])
print('nulls take-ours rc:', r.returncode, r.stderr.strip()[:120])

# 2) rehearsal JSONs: theirs (mine, newer)
for fp in ('results/_r633bma_finalize_rehearsal_fund_quality_p1.json',
           'results/_r633bma_finalize_rehearsal_fund_value_p1.json'):
    r = run(['git', 'checkout', '--theirs', fp])
    print(f'{fp.split(chr(92))[-1]} take-theirs rc:', r.returncode, r.stderr.strip()[:80])

# 3) pool_core_samples.jsonl: exact-line union
r2 = subprocess.run(['git', 'show', ':2:results/pool_core_samples.jsonl'],
                    capture_output=True)
r3 = subprocess.run(['git', 'show', ':3:results/pool_core_samples.jsonl'],
                    capture_output=True)
ours = r2.stdout.decode('utf-8', errors='replace').splitlines()
theirs = r3.stdout.decode('utf-8', errors='replace').splitlines()
seen = set()
merged = []
for line in ours + theirs:
    if line.strip() and line not in seen:
        seen.add(line)
        merged.append(line)
open('results/pool_core_samples.jsonl', 'w', encoding='utf-8', newline='').write(
    '\n'.join(merged) + ('\n' if merged else ''))
print(f'pool_core_samples union: ours={len(ours)} theirs={len(theirs)} merged={len(merged)} '
      f'(dedup {len(ours) + len(theirs) - len(merged)})')

# verify no conflict markers anywhere in the 4 files
import re
pat = re.compile(r'^(<{7}|={7}$|>{7}|\|{7})', re.M)
for fp in ('results/fund_value_p1/nulls.jsonl',
           'results/_r633bma_finalize_rehearsal_fund_quality_p1.json',
           'results/_r633bma_finalize_rehearsal_fund_value_p1.json',
           'results/pool_core_samples.jsonl'):
    txt = open(fp, encoding='utf-8', errors='replace').read()
    m = pat.findall(txt)
    print(fp.split(chr(92))[-1], 'markers:', len(m))

# sanity: nulls row count + my illegal k absent
import json
rows = [json.loads(l) for l in open('results/fund_value_p1/nulls.jsonl', encoding='utf-8') if l.strip()]
ks = set(r['k'] for r in rows)
print('nulls rows after resolution:', len(rows), '| max k:', max(ks))
sys.exit(0)
