b = open('research/PERPETUAL_N1_W96_PREREG.md', 'rb').read()
s = b.decode('utf-8')
i7 = s.find('\u00a77')
i8 = s.find('\u00a78')
seg = s[i7-3:i8+40]
import json
print(json.dumps(seg, ensure_ascii=True))
