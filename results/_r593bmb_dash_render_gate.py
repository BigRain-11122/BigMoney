# r593 bm-b: dashboard engine_wave face end-to-end verification
# 1) full build() payload (pure call, guarded faces untouched)
# 2) temp html+js pair under results/ (private test artifacts)
# 3) Edge headless dump-dom -> assert N1 wave row renders with live numbers
import io, json, os, shutil, subprocess, sys, re

sys.path.insert(0, r'.')
sys.path.insert(0, r'scripts')
from monitor import build_status as bs

payload = bs.build()
ew = (payload.get('data') or {}).get('engine_wave') or {}
assert ew.get('present') is True, 'engine_wave missing from build() payload'
assert ew['chain_head'] == 610948 and ew['k'] == 244320, (ew.get('chain_head'), ew.get('k'))
print('build() OK: engine_wave present, chain_head', ew['chain_head'], 'K', ew['k'])

js_path = os.path.abspath(r'results\_r593bmb_dash_test_status.js')
with open(js_path, 'w', encoding='utf-8') as f:
    f.write('window.DASH_DATA = ' + json.dumps(payload, ensure_ascii=False) + ';\n')

html = io.open(r'dashboard.html', encoding='utf-8').read()
old = '<script src="results/dashboard_status.js"></script>'
new = '<script src="_r593bmb_dash_test_status.js"></script>'
assert old in html
test_html = os.path.abspath(r'results\_r593bmb_dash_test.html')
io.open(test_html, 'w', encoding='utf-8').write(html.replace(old, new))

edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(edge):
    edge = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
assert os.path.exists(edge), 'msedge not found'
r = subprocess.run([edge, '--headless', '--disable-gpu', '--dump-dom',
                    'file:///' + test_html.replace('\\', '/')],
                   capture_output=True, timeout=90,
                   encoding='utf-8', errors='replace')
dom = r.stdout
checks = {
    'N1 row title': 'N1 波链 · 常供产线' in dom,
    'chain head 610948': '610948' in dom,
    'K 244320': '244320' in dom,
    'registered tail W113': '注册尾 W113' in dom,
    'W112 landed': 'W112✓610948' in dom,
    'W113 shards 12/12': 'W113 12/12片 账待落' in dom,
    'ahead seat W114 bm-a': '前席 W114 bm-a' in dom,
    'next seatable W115': '下一可席 W115' in dom,
    'status chip': ('账待落' in dom),
}
bad = [k for k, v in checks.items() if not v]
for k, v in checks.items():
    print(('PASS ' if v else 'FAIL ') + k)
if bad:
    print('DOM CHECK FAILURES:', bad)
    sys.exit(1)
print('DASHBOARD RENDER ALL PASS')
