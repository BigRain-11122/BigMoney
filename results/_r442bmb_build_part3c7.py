"""r442 bm-b: fixup v7 -- dict close-brace + last metas std."""
SRC = open('results/_r442bmb_stage3c.py', encoding='utf-8').read()
lines = SRC.split('\n')
for i, l in enumerate(lines):
    if l == '             "mom_state": mom_state}':
        lines[i] = '             "mom_state": mom_state,'
        print('dict comma fix at', i + 1)
        break
# last metas site (3151) std insert
for i, l in enumerate(lines):
    if ('"amp_meta": amp_meta, "mom_meta": mom_meta,' in l
            and '"std_meta": std_meta,' not in lines[i + 1]):
        indent = len(l) - len(l.lstrip())
        lines.insert(i + 1, ' ' * indent + '"std_meta": std_meta,')
        print('std_meta inserted at', i + 2)
        break
open('results/_r442bmb_stage3c.py', 'w', encoding='utf-8').write(
    '\n'.join(lines))
