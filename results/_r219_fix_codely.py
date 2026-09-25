# R219: fix backtick artifact in CODELY.md entry (literal, no shell escaping)
p = 'CODELY.md'
t = open(p, encoding='utf-8').read()
old_l = '①技能实跑前先 ' + chr(92) + '--selftest' + chr(92) + ' 计数'
new_l = '①技能实跑前先 ' + chr(96) + '--selftest' + chr(96) + ' 计数'
assert old_l in t, 'pattern not found'
t = t.replace(old_l, new_l)
open(p, 'w', encoding='utf-8', newline='').write(t)
i = t.find('技能实跑前先')
print('verified:', repr(t[i:i+42]))
