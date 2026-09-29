"""r442 bm-b: fixup v5 -- last metas site (post-shift)."""
SRC = open('results/_r442bmb_stage3c.py', encoding='utf-8').read()
lines = SRC.split('\n')
sites = [i + 1 for i, l in enumerate(lines)
         if '"amp_meta": amp_meta, "mom_meta": mom_meta,' in l]
print('remaining metas sites:', sites)
ln = sites[0]
l = lines[ln - 1]
assert '"amp_meta": amp_meta, "mom_meta": mom_meta,' in l, l
indent = len(l) - len(l.lstrip())
lines[ln:ln] = [' ' * indent + '"std_meta": std_meta,']
SRC = '\n'.join(lines)
open('results/_r442bmb_stage3c.py', 'w', encoding='utf-8').write(SRC)
print('inserted at', ln)
