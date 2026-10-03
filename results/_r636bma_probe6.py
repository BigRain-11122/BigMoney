import json

data = open(r'results\crash_fuse.json', 'rb').read()
print('CRLF:', data.count(b'\r\n'), '| LF:', data.count(b'\n'))
i = data.find(b'"scripts/fund_divlowvol_p1.py|run,--nulls"')
print('=== divlowvol pin block:')
print(data[i:i + 900].decode('utf-8', errors='replace'))
j = data.find(b'"scripts/fund_value_p1.py|run,--nulls"')
print('=== value sig block:')
print(data[j:j + 1400].decode('utf-8', errors='replace'))
cf = json.loads(data.decode('utf-8'))
print('parse OK; divlowvol sig:', json.dumps(cf['sigs'].get('scripts/fund_divlowvol_p1.py|run,--nulls'), ensure_ascii=False)[:200])
print('value sig:', json.dumps(cf['sigs'].get('scripts/fund_value_p1.py|run,--nulls'), ensure_ascii=False)[:400])
