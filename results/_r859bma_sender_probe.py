import sys
sys.path.insert(0, r'Tools')
import inbox_guard

txt = open(r'fleet/inbox/MSG-2026-10-08-0330-bma-w16screen-seat.md', encoding='utf-8', errors='replace').read()
p = inbox_guard.SENDER_PAT
print('pattern repr:', repr(p.pattern))
m = p.search(txt)
print('sender match:', m.group(1) if m else None)
import re
# find what the CJK word actually is
cjk = re.findall(r'[\u4e00-\u9fff]+[:\uff1a]', p.pattern)
print('pattern cjk token:', cjk)
# check with the observed-passing w169 seat msg
t2 = open(r'fleet/inbox/processed/MSG-2026-10-07-0547-bma-w169-seat.md', encoding='utf-8', errors='replace').read()
m2 = p.search(t2)
print('w169 sender match:', m2.group(1) if m2 else None)
