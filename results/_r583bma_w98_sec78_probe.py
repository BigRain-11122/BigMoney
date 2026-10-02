# r583 bm-a: W98 prereg sec7/8 mechanical backfill (bytes-safe, LF preserved)
import json

P = 'research/PERPETUAL_N1_W98_PREREG.md'
b = open(P, 'rb').read()
assert b.count(b'\r\n') == 0, 'expected pure LF file, got CRLF'
s = b.decode('utf-8')

# probe exact placeholder text
i7 = s.find('\u00a77')
i8 = s.find('\u00a78')
probe = s[i7-3:i8+60]
print('PROBE:', json.dumps(probe, ensure_ascii=True))
