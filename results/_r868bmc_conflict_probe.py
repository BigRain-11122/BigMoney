import io, re
t = io.open('results/update_status.json', encoding='utf-8', errors='replace').read()
lines = t.splitlines()
for i, ln in enumerate(lines):
    if ln.startswith(('<<<<<<<', '=======', '>>>>>>>')):
        print('MARK', ln, '-> ctx:', lines[i+1][:100] if i+1 < len(lines) else '')
ts = re.findall(r'"(?:ts|updated|updated_at|generated)"\s*:\s*"([^"]+)"', t)
print('timestamps found:', ts[:6])
