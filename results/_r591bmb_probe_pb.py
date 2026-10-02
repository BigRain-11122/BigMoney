import io
t = io.open('research/shortline/SHORTLINE_PLAYBOOK.md', encoding='utf-8', errors='replace').read()
i = t.find('## ')
# print section 6 area
import re
ms = [(m.start(), m.group(0)[:80]) for m in re.finditer(r'^#{1,3} .*', t, re.M)]
for s, h in ms:
    print(s, '|', h)
