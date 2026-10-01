import io, sys
base = 'K:/Fluxgroup/FluxGroup/quant/bigmoney/'

# ---- CODELY.md: union = HEAD block + mine-unique (r312) line ----
p = base + 'CODELY.md'
raw = open(p, encoding='utf-8', newline='').read()
lines = raw.split('\n')
try:
    i_h = next(i for i,l in enumerate(lines) if l.startswith('<<<<<<<'))
    i_b = next(i for i,l in enumerate(lines) if l.startswith('|||||||'))
    i_s = next(i for i,l in enumerate(lines) if l.strip() == '=======')
    i_e = next(i for i,l in enumerate(lines) if l.startswith('>>>>>>>'))
except StopIteration:
    print('CODELY markers not found -- abort'); sys.exit(1)
head_block = lines[i_h+1:i_b]
base_block = lines[i_b+1:i_s]
theirs_block = lines[i_s+1:i_e]
# unique-to-theirs lines (not present verbatim in base or head)
head_set = set(l for l in head_block)
mine_unique = [l for l in theirs_block if l not in head_set and l not in base_block]
resolved = lines[:i_h] + head_block + mine_unique + lines[i_e+1:]
open(p, 'w', encoding='utf-8', newline='').write('\n'.join(resolved))
print('CODELY: head entries=%d base=%d theirs=%d mine_unique=%d -> total lines=%d' % (len(head_block), len(base_block), len(theirs_block), len(mine_unique), len(resolved)))
assert not any(l.startswith(('<<<<<<<','>>>>>>>','|||||||')) or l.strip()=='=======' for l in resolved), 'markers remain'

# ---- pool_core_samples.jsonl: line-union, origin first, dedupe exact ----
p2 = base + 'results/pool_core_samples.jsonl'
raw2 = open(p2, encoding='utf-8', newline='').read()
l2 = raw2.split('\n')
i_h2 = next(i for i,l in enumerate(l2) if l.startswith('<<<<<<<'))
i_b2 = next(i for i,l in enumerate(l2) if l.startswith('|||||||'))
i_s2 = next(i for i,l in enumerate(l2) if l.strip()=='=======')
i_e2 = next(i for i,l in enumerate(l2) if l.startswith('>>>>>>>'))
head2 = [x for x in l2[i_h2+1:i_b2] if x.strip()]
theirs2 = [x for x in l2[i_s2+1:i_e2] if x.strip()]
seen = set(head2)
extra = [x for x in theirs2 if x not in seen]
resolved2 = l2[:i_h2] + head2 + extra + l2[i_e2+1:]
open(p2, 'w', encoding='utf-8', newline='').write('\n'.join(resolved2))
print('SAMPLES: head=%d theirs=%d extra_appended=%d -> total_lines=%d' % (len(head2), len(theirs2), len(extra), len([x for x in resolved2 if x.strip()])))
assert not any(x.startswith(('<<<<<<<','>>>>>>>','|||||||')) or x.strip()=='=======' for x in resolved2), 'markers remain'
print('BOTH-RESOLVED-OK')
