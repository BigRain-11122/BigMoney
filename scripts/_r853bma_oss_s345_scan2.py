# _r853bma_oss_s345_scan2.py -- round-2: canonical-name resolution (S3 404 cures) + wider S5 sentiment queries.
# Appends round2 faces into results/oss_eng_scan/s345-20261008.json (round1 evidence preserved under 'round2').
# rc: 0 = all searches returned; 1 = partial; 2 = mechanism failure.
import json, urllib.request, urllib.parse, os, sys, io, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'results', 'oss_eng_scan', 's345-20261008.json')
ALLOW = {'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'}
FORBID = {'AGPL-3.0', 'GPL-3.0', 'GPL-2.0', 'LGPL-3.0', 'LGPL-2.1'}

def search(q, per=8):
    u = ('https://api.github.com/search/repositories?q=' + urllib.parse.quote(q) +
         f'&sort=stars&order=desc&per_page={per}')
    req = urllib.request.Request(u, headers={'User-Agent': 'bm-a-oss-s345-scan'})
    d = json.loads(urllib.request.urlopen(req, timeout=25).read())
    out = []
    for r in d.get('items', []):
        lic = (r.get('license') or {}).get('spdx_id') or 'NONE'
        gate = 'PASS' if lic in ALLOW else ('FAIL(copyleft)' if lic in FORBID else
               ('PENDING(probe)' if lic == 'NOASSERTION' else 'REGISTRY-ONLY(nolic)'))
        try:
            days = (datetime.datetime.now(datetime.UTC) - datetime.datetime.strptime(r['pushed_at'][:10], '%Y-%m-%d')).days
        except Exception:
            days = None
        out.append(dict(repo=r['full_name'], stars=r['stargazers_count'], pushed_age_days=days,
                        license=lic, license_gate=gate, archived=r.get('archived'),
                        desc=(r.get('description') or '')[:150]))
    return d.get('total_count', 0), out

ev = json.load(io.open(OUT, encoding='utf-8'))
r2 = {'ts': datetime.datetime.now().isoformat(timespec='seconds') + '+08:00', 'errors': []}
r2['s3_canonical'] = {}
for label, q in [('gplearn', 'gplearn in:name'), ('PyPortfolioOpt', 'PyPortfolioOpt in:name'),
                 ('Riskfolio', 'Riskfolio in:name')]:
    try:
        total, items = search(q)
        r2['s3_canonical'][label] = dict(total=total, top=items[:3])
    except Exception as ex:
        r2['errors'].append(label + ' ' + str(ex)[:100])
r2['s5_more'] = {}
for q in ['A股情绪', '股票情绪指标', '涨停 连板', 'A股 量化 pythonstock']:
    try:
        total, items = search(q)
        r2['s5_more'][q] = dict(total=total, top=[i for i in items if (i['stars'] or 0) >= 50][:6])
    except Exception as ex:
        r2['errors'].append(q + ' ' + str(ex)[:100])
ev['round2'] = r2
ev['errors'] = ev.get('errors', []) + ['round2: ' + e for e in r2['errors']]
rc = 1 if r2['errors'] else 0
ev['rc'] = rc
with io.open(OUT, 'w', encoding='utf-8') as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print(json.dumps({'rc': rc, 'errors': r2['errors'],
                  'canonical': {k: [i['repo'] for i in v.get('top', [])] for k, v in r2['s3_canonical'].items()},
                  's5': {q: [(i['repo'], i['stars'], i['license']) for i in v.get('top', [])]
                         for q, v in r2['s5_more'].items()}}, ensure_ascii=False))
sys.exit(rc)
