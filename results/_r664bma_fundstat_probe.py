import json, os, glob

# fund statement backfill status (T-166, my lane)
raw = open('results/fund_statement_update_status.json', 'rb').read()
d = json.loads(raw.decode('utf-8', errors='replace'))
print('=== fund_statement_update_status ===')
print(json.dumps(d, ensure_ascii=False, indent=1)[:1800])
