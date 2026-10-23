import io, re
t = io.open('results/_r1180bmc_w297_sixgate.py', encoding='utf-8').read()
print('len', len(t))
pats = [
    r'PRE-FINALIZE[^\n]{0,70}',
    r'clone lineage[^\n]{0,70}',
    r'\d+th consecutive',
    r'"wave": \d+',
    r'SPLICE = .*',
    r'1075541|649120|1077741|651320|1073341|646920',
    r"'a_seed_base_\d+'",
    r"'b_exit_seed_base_\d+'",
    r'law sec\.4 W\d+ [AB]: \d{3}_\d{3}\.\.[\d_]+',
    r"if '\d+: \{' in seg",
    r"_set_wave\(\d+\)",
    r'_r11\d+bmc_prereg_derive_w\d+',
    r"_r11\d+bmc_w\d+_sixgate",
]
for p in pats:
    print('%-45s %r' % (p, sorted(set(re.findall(p, t)))[:10]))
print('--- rel/abs band tokens:', sorted(set(re.findall(r'\b\d{3}_\d{3}\b', t)))[:20])
print('--- counts 1075541/649120:', t.count('1075541'), t.count('649120'))
print('--- head:'); print(t[:600])