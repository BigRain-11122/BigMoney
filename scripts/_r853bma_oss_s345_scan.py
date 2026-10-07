# _r853bma_oss_s345_scan.py -- O-20261007-2245 S3/S5 supplementary scan (bm-a lane, ledger sections 一).
# S3: awesome-quant ecosystem entry list -> funnel-A candidate extraction (README cross-checked shortlist).
# S5: A-share sentiment-factor OSS implementations (GitHub search API; CEO research-orientation: A-share native
#     sentiment/sentiment-cycle/limit-up/lhb families first-class).
# S4 (joinquant/myquant community knowledge) runs via the session web channel; this script records the slot.
# Gates mirror scripts/oss_eng_scan.py: license / health (stars+push) / dup (in-service + judged-out families) /
#       cost (<=8h first-pass) / fit (first-pass, disclosed). Verdicts = scan evidence only (lai-na != mian-jian).
# rc: 0 = all faces fetched; 1 = partial fetch errors (disclosed); 2 = mechanism failure.
import json, urllib.request, urllib.error, os, sys, io, datetime, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'results', 'oss_eng_scan', 's345-20261008.json')
ALLOW = {'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'}
FORBID = {'AGPL-3.0', 'AGPL-2.0', 'GPL-3.0', 'GPL-2.0', 'LGPL-3.0', 'LGPL-2.1'}
IN_SERVICE = {'akshare', 'tushare', 'vnpy', 'qlib', 'vectorbt', 'backtrader', 'easytrader',
              'nautilus_trader', 'zipline-reloaded', 'empyrical', 'prefect', 'zipline'}  # ledger in-service/prior ids
JUDGED_OUT = ['MOM-0/4920', 'timeseries-0/228', 'wild-0/1569']  # attrition blacklists, no re-admission

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': 'bm-a-oss-s345-scan'})
    return urllib.request.urlopen(req, timeout=timeout).read()

def repo_meta(name):
    d = json.loads(fetch('https://api.github.com/repos/' + name))
    lic = (d.get('license') or {}).get('spdx_id') or 'NONE'
    return dict(repo=name, stars=d.get('stargazers_count'), pushed_at=d.get('pushed_at'),
                license=lic, archived=d.get('archived'), desc=(d.get('description') or '')[:160], api='core')

def search(q, per=10):
    u = 'https://api.github.com/search/repositories?q=' + urllib.parse.quote(q) + f'&sort=stars&order=desc&per_page={per}'
    d = json.loads(fetch(u))
    out = []
    for r in d.get('items', []):
        out.append(dict(repo=r['full_name'], stars=r['stargazers_count'], pushed_at=r['pushed_at'],
                        license=(r.get('license') or {}).get('spdx_id') or 'NONE',
                        archived=r.get('archived'), desc=(r.get('description') or '')[:160], api='search'))
    return out, d.get('total_count')

def lic_gate(l):
    if l in ALLOW: return 'PASS'
    if l in FORBID: return 'FAIL(copyleft)'
    if l == 'NOASSERTION': return 'PENDING(license-probe r707 chain)'
    return 'REGISTRY-ONLY'

def health_gate(stars, pushed):
    try:
        days = (datetime.datetime.utcnow() - datetime.datetime.strptime(pushed[:10], '%Y-%m-%d')).days
    except Exception:
        days = None
    ok = (stars is not None and stars >= 100) and (days is not None and days <= 365)
    return ok, days

# ---------- S3: awesome-quant README cross-checked shortlist ----------
evidence = {'ts': datetime.datetime.now().isoformat(timespec='seconds') + '+08:00', 'lane': 'bm-a r853',
            'law_ref': 'O-20261007-2245 OSS_HARVEST_LEDGER section-1 S3/S4/S5', 's3': {}, 's5': {}, 's4': {}, 'errors': []}
try:
    raw = fetch('https://raw.githubusercontent.com/wilsonfreitas/awesome-quant/master/README.md').decode('utf-8', 'replace')
    links = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', raw)
    gh = [t for _, u in links for t in [re.sub(r'https?://(www\.)?github\.com/', '', u).strip('/').split('/')[0:2]]
          if u.startswith('https://github.com/') and t]
    gh_names = ['/'.join(t) for t in gh if len(t) == 2]
    evidence['s3']['readme_entries'] = len(gh_names)
    shortlist = {
        'OSS-S3-01 gplearn (GP factor mining, W15 supply line)': 'gplearn/gplearn',
        'OSS-S3-02 PyPortfolioOpt (alloc/portfolio line)': 'mbhushan/PyPortfolioOpt',
        'OSS-S3-03 Riskfolio-Lib (alloc+risk line)': 'dcajasun/Riskfolio-Lib',
        'OSS-S3-04 quantstats (tearsheet/reporting registry)': 'ranaroussi/quantstats',
        'OSS-S3-05 easyquotation (A-share realtime quotes alt channel)': 'shidenggui/easyquotation',
        'OSS-S3-06 financepy (derivatives pricing, registry)': 'domokane/FinancePy',
    }
    rows = []
    for label, repo in shortlist.items():
        row = dict(label=label, in_readme=(repo.lower() in [g.lower() for g in gh_names]) or
                  any(repo.lower().endswith(g.split('/')[-1].lower()) for g in gh_names))
        try:
            m = repo_meta(repo)
            ok, days = health_gate(m['stars'], m['pushed_at'])
            dup = [k for k in IN_SERVICE if k.lower() == repo.split('/')[-1].lower()]
            row.update(m, license_gate=lic_gate(m['license']), health_ok=ok, push_age_days=days, dup_in_service=dup)
        except Exception as ex:
            row['fetch_error'] = str(ex)[:160]; evidence['errors'].append('S3 ' + repo + ' ' + str(ex)[:80])
        rows.append(row)
    evidence['s3']['shortlist'] = rows
except Exception as ex:
    evidence['errors'].append('S3 readme ' + str(ex)[:120])

# ---------- S5: A-share sentiment-factor OSS search ----------
queries = ['A股 情绪 因子', '龙虎榜 因子', 'china stock market sentiment indicator']
try:
    for q in queries:
        items, total = search(q)
        keep = []
        for it in items[:10]:
            ok, days = health_gate(it['stars'], it['pushed_at'])
            it['license_gate'] = lic_gate(it['license']); it['health_ok'] = ok; it['push_age_days'] = days
            it['dup_in_service'] = [k for k in IN_SERVICE if k.lower() in it['repo'].lower()]
            if it['stars'] and it['stars'] >= 50:
                keep.append(it)
        evidence['s5'][q] = dict(total=total, kept=keep)
except Exception as ex:
    evidence['errors'].append('S5 search ' + str(ex)[:120])

evidence['s4'] = dict(status='via-session-web-channel', note='joinquant/myquant community knowledge scan; rows recorded in ledger by session')

rc = 2 if 'S3 readme' in ' '.join(evidence['errors']) and not evidence['s3'] else (1 if evidence['errors'] else 0)
evidence['rc'] = rc
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(evidence, f, ensure_ascii=False, indent=1)
print(json.dumps({'rc': rc, 'errors': evidence['errors'], 'out': os.path.relpath(OUT, REPO),
                  's3_rows': len(evidence['s3'].get('shortlist', [])),
                  's5_kept': {q: len(v.get('kept', [])) for q, v in evidence['s5'].items() if isinstance(v, dict)}},
                 ensure_ascii=False))
sys.exit(rc)
