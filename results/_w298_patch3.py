import io
p = 'results/_r1181bmc_gen_w298_sixgate.py'
t = io.open(p, encoding='utf-8', newline='').read()
old = "rep('expect 1,077,741 / 651,320', 'expect 1,077,741 / 651,320')\n"
assert t.count(old) == 1, t.count(old)
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, ''))
print('removed no-op rep')