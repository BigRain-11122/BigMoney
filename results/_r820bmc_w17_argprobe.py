import re, sys

src = open('scripts/trial_labor_w17.py', encoding='utf-8').read()
m = re.search(r"add_parser\([\"']screen", src)
if m:
    seg = src[m.start():m.start()+2600]
    for line in seg.splitlines():
        ls = line.strip()
        if 'add_argument' in ls or 'add_parser' in ls:
            print(ls[:160])
else:
    print('screen subparser not found')
for mm in re.finditer(r'CKPT_DIR[^\n]*', src):
    print('CKPT:', mm.group(0)[:160])
for mm in re.finditer(r'(nproc|cpu_count|NPROC|max_workers|processes\s*=)[^\n]{0,80}', src):
    print('CPU:', mm.group(0)[:120])
