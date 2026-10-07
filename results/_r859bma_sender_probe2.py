import sys
sys.path.insert(0, r'Tools')
import inbox_guard

p = inbox_guard.SENDER_PAT.pattern
print('chars:', [(c, hex(ord(c))) for c in p[:10]])
b = open(r'Tools/inbox_guard.py', 'rb').read()
i = b.find(b'SENDER_PAT')
seg = b[i:i+120]
print('raw bytes:', seg)
