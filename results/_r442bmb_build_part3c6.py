"""r442 bm-b: fixup v6 -- worker-dict indent + duplicate std_meta."""
SRC = open('results/_r442bmb_stage3c.py', encoding='utf-8').read()
lines = SRC.split('\n')
# fix 1: worker dict indent (14 -> 13)
for i, l in enumerate(lines):
    if l == '              "std_state": std_state}':
        lines[i] = '             "std_state": std_state}'
        print('fixed worker dict indent at', i + 1)
        break
# fix 2: duplicate std_meta after metas line
for i, l in enumerate(lines):
    if ('"amp_meta": amp_meta, "mom_meta": mom_meta,' in l
            and '"std_meta": std_meta,' in lines[i + 1]
            and '"std_meta": std_meta,' in lines[i + 2]):
        del lines[i + 2]
        print('removed duplicate std_meta at', i + 3)
        break
# verify remaining metas site got std
n = 0
for i, l in enumerate(lines):
    if '"amp_meta": amp_meta, "mom_meta": mom_meta,' in l:
        has_std = '"std_meta": std_meta,' in lines[i + 1]
        print('metas site', i + 1, 'std follows:', has_std)
        n += 1
print('total metas sites:', n)
open('results/_r442bmb_stage3c.py', 'w', encoding='utf-8').write(
    '\n'.join(lines))
