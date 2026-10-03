import io, re, subprocess, sys
c = io.open('town.html', encoding='utf-8').read()
res = {}
# expected KPI faces per building (org_chart v2/v5/v6 table)
expected = {
    'lab': '正交成员供给数', 'fac': '成员稳定准入率', 'risk': '红线零违例',
    'hall': '唯一计分板', 'pf': 'SPM 全维判决面', 'data': '新鲜度 · 零污染',
    'alloc': '配置面四指标', 'etfops': '交易级胜率', 'dock': 'SLA 达标',
    'office': '月报按期', 'bunker': '轮健康度',
}
# building object bodies by brace matching from BUILDS = [ to ];
start = c.index('const BUILDS = [')
seg = c[start:c.index('function findBuild')]
n_ok = 0
for bid, needle in expected.items():
    m = re.search(r"\{ id:'" + bid + r"'", seg)
    if not m:
        res[bid] = 'MISSING BUILD'
        continue
    # brace-match the object
    i = m.start(); depth = 0
    while True:
        if seg[i] == '{': depth += 1
        elif seg[i] == '}':
            depth -= 1
            if depth == 0: break
        i += 1
    body = seg[m.start():i]
    res[bid] = 'KPI-OK' if needle in body else 'KPI-MISSING'
    n_ok += res[bid] == 'KPI-OK'
# JS syntax check: extract script and node --check
js = re.search(r'<script>(.*)</script>', c, re.S).group(1)
io.open(r'C:\Users\Administrator\AppData\Local\Temp\town_check.js', 'w', encoding='utf-8').write(js)
node = subprocess.run(['node', '--check', r'C:\Users\Administrator\AppData\Local\Temp\town_check.js'],
                      capture_output=True, text=True)
print('buildings KPI face: %d/11 OK' % n_ok)
print('node --check rc=', node.returncode, node.stderr[:300])
ok = n_ok == 11 and node.returncode == 0
out = {'kpi_faces': res, 'n_ok': n_ok, 'node_check_rc': node.returncode,
       'verdict': 'PASS' if ok else 'FAIL', 'bytes': len(c.encode('utf-8'))}
io.open('results/_r639bmb_town_align_report.json', 'w', encoding='utf-8', newline='\n').write(
    __import__('json').dumps(out, ensure_ascii=False, indent=1))
sys.exit(0 if ok else 1)
