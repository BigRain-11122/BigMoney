import sys, io, re, subprocess, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open(r'town.html', encoding='utf-8').read()

# canonical building names from org_chart.md v2 section AI-enable principle #5
canon = ['研究楼', '策略厂', '风控塔', '交易大厅', '数据塔', '机队码头', '工程部·地下机房',
         '组合调度中心', '总经理办公室', '资产组合研究部', 'ETF操作链研究所']

labels = re.findall(r"label\s*:\s*'([^']+)'", t)
print('labels on board: %d' % len(labels))
missing = [c for c in canon if c not in labels]
extra = [l for l in labels if l not in canon]
print('CANON-MISSING:', missing if missing else 'NONE')
print('EXTRA:', extra if extra else 'NONE')

# dept/mandate presence check (11 rows)
depts = re.findall(r"dept\s*:\s*'([^']+)'", t)
mandates = re.findall(r"mandate\s*:\s*'([^']+)'", t)
print('dept rows: %d, mandate rows: %d' % (len(depts), len(mandates)))

# org_chart mapping text consistency: office building name must appear in canvas text()
canvas_office = "text('总经理办公室'" in t
print('canvas-text office name aligned:', canvas_office)

# node syntax check on the inline <script> (r637 receipt pattern)
m = re.search(r'<script>\n(.*)</script>', t, re.S)
js = m.group(1) if m else ''
ok_js = True
if js:
    p = os.path.join(os.environ['TEMP'], 'town_inline_check.js')
    open(p, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['node', '--check', p], capture_output=True)
    print('node --check rc =', r.returncode)
    if r.returncode != 0:
        print(r.stderr.decode('utf-8', 'replace')[:600]); ok_js = False
else:
    print('no inline script found'); ok_js = False

verdict = (not missing) and (not extra) and len(depts) == 11 and canvas_office and ok_js
print('TOWN-ALIGN-ACCEPT VERDICT:', 'PASS' if verdict else 'FAIL')
