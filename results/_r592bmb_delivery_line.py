# -*- coding: utf-8 -*-
# byte-level insertion of delivery segment into the r592 round-report line (r530 bytes-in-bytes-out law)
p = r'logs\iteration-loop\round_reports.md'
raw = open(p, 'rb').read()
anchor = '| next: CEO visibility'.encode('utf-8')
seg = ' | delivery: \u672c\u5730\u672a\u8fbe origin commit \u6570=0 (post-push fetch+ls-tree self-check)'.encode('utf-8')
i = raw.rfind(anchor)
assert i > 0, 'anchor not found'
# idempotence: skip if delivery segment already present just before anchor
if raw[max(0, i-220):i].find(b'delivery') >= 0:
    print('already inserted, no-op')
else:
    raw = raw[:i] + seg + raw[i:]
    open(p, 'wb').write(raw)
    print('inserted at byte', i, 'new len', len(raw))
# verify the line now contains the delivery face
t = raw.decode('utf-8', errors='replace')
j = t.rfind('delivery')
print('context:', t[j-40:j+120].replace('\r', '').replace('\n', ' '))
