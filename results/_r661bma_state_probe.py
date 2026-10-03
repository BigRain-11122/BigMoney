import re

raw = open(r'state-bm-a.json', 'rb').read()
txt = raw.decode('utf-8', errors='replace')
print('size:', len(raw))
for key in ['"round_no"', '"did"', '"verify"', '"next"', '"last_round_at"', '"current_task"']:
    m = re.search(re.escape(key) + r'.', txt)
    print(key, 'at offset', m.start() if m else None)
print('--- tail 500B (ascii-safe) ---')
print(raw[-500:].decode('utf-8', errors='replace').encode('ascii', errors='replace').decode())
