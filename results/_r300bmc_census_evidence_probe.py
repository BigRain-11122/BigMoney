import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import re
for path in ('scripts/census_fusion_s2_w2.py',):
    src = io.open(path, encoding='utf-8', errors='replace').read()
    hits = [(i + 1, l) for i, l in enumerate(src.splitlines())
            if re.search(r'run_cells_parallel|parallel_runner', l)]
    print(path, 'hits:', len(hits))
    for i, l in hits[:8]:
        print(f'L{i}: {l.strip()[:120]}')
