"""r555 helper: locate summary tail with looser anchors."""
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
import re
for m in re.finditer(r'exempt', src):
    print(m.start(), repr(src[m.start() - 60:m.start() + 60]))
print('---')
i = src.find('law sec.2 pre-claim')
print('pre-claim idx:', i)
print(repr(src[i - 300:i + 200]) if i > 0 else 'not found')
