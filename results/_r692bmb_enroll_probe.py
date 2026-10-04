# r692 bm-b probe3: which shard key did bm-a's enroll script write
src = open('results/_r694bma_n2_gen_enroll.py', encoding='utf-8').read()
for pat in ('n2-w15-generate-0of1', 'generate-0of1', 'shard', 'refuse-if-exists'):
    print('PAT', pat, 'count', src.count(pat))
# show first 30 lines around shard creation
lines = src.splitlines()
for i, ln in enumerate(lines):
    if 'generate-0of1' in ln or 'shard' in ln.lower():
        print(i, ln.strip()[:150])
