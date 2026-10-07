# oss_license_probe.py -- O-20261007-2245 bm-c lane: NOASSERTION license verification probe.
# For repos where api.github.com reports license NOASSERTION, read the /license endpoint
# raw file (base64) and classify the HEAD TEXT -- overlay/dual restriction clauses are
# matched FIRST because plain-Apache keywords must not shadow them (live catch r707:
# vectorbt LICENSE.md head = Commons Clause v1.0 overlay; rqalpha LICENSE head = Chinese
# dual grant, Apache-2.0 for non-commercial use only). Gate buckets:
#   PASS (MIT/Apache/BSD/ISC) / FORBIDDEN (GPL/AGPL/LGPL family) /
#   CONDITIONAL-REF-ONLY (Commons Clause overlay, dual non-commercial grants:
#   reference-only reading stays lawful; embedding/redistribution/productization does not
#   -- group harvest-mechanism ruling required) / PENDING (unrecognized).
# Evidence-only scan face: verdicts feed OSS_HARVEST_LEDGER rows; adoption still requires
# the full gate chain (lai-na != mian-jian). Idempotent: same-day rerun overwrites the
# dated evidence file with fresh live data (no hand-typed numbers).
# rc: 0 = all resolved; 1 = partial fetch errors (disclosed); 2 = mechanism failure.
import json, base64, urllib.request, urllib.error, os, sys, io, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, 'results', 'oss_eng_scan')
ALLOW = {'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'}
FORBID = {'AGPL-3.0', 'AGPL-2.0', 'GPL-3.0', 'GPL-2.0', 'LGPL-3.0', 'LGPL-2.1'}
# append here when new scan rows report NOASSERTION (id, owner/name)
TARGETS = [('E2', 'polakowo/vectorbt'), ('E5', 'ricequant/rqalpha')]

def current_round():
    try:
        st = json.load(open(os.path.join(REPO, 'state-bm-c.json'), encoding='utf-8'))
        return st.get('round_no')
    except Exception:
        return None

def classify_head(text):
    t = text[:4000]
    # overlay/dual restrictions FIRST -- plain-Apache keyword must not shadow them
    # (live catch r707: vectorbt head IS Commons Clause, rqalpha head IS a Chinese
    #  dual-license grant; naive Apache-first matching mis-flags both as PASS)
    if 'Commons Clause' in t:
        return 'Apache-2.0+Commons-Clause(v1.0)'
    if ('非商业用途' in t or '商业授权' in t) and 'Apache' in t:
        return 'Dual:Apache-2.0(non-commercial)/commercial-written-license'
    if 'GNU AFFERO GENERAL PUBLIC LICENSE' in t or 'GNU LESSER GENERAL PUBLIC LICENSE' in t:
        return 'LGPL-3.0-family' if 'LESSER' in t else 'AGPL-family'
    if 'GNU GENERAL PUBLIC LICENSE' in t:
        return 'GPL-family'
    if 'Apache License' in t and 'Version 2.0' in t:
        return 'Apache-2.0'
    if 'Apache License' in t:
        return 'Apache-family'
    if 'MIT License' in t or 'Permission is hereby granted, free of charge' in t:
        return 'MIT'
    if 'Redistribution and use in source and binary forms' in t:
        return 'BSD-family'
    return 'UNRECOGNIZED'

def gh_license(repo):
    url = 'https://api.github.com/repos/%s/license' % repo
    req = urllib.request.Request(url, headers={
        'User-Agent': 'bigmoney-oss-scan', 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    date = datetime.date.today().strftime('%Y%m%d')
    rnd = current_round()
    rows, ok, fail = [], 0, 0
    for tid, repo in TARGETS:
        row = dict(id=tid, repo=repo, source='api.github.com /license endpoint live fetch')
        try:
            d = gh_license(repo)
            spdx = (d.get('license') or {}).get('spdx_id') or 'None'
            name = (d.get('license') or {}).get('name') or 'None'
            path = d.get('path')
            head = base64.b64decode(d.get('content', '')).decode('utf-8', 'replace')
            head_class = classify_head(head)
            verdict_spdx = spdx if spdx not in ('NOASSERTION', 'None') else head_class
            if verdict_spdx in FORBID or verdict_spdx in ('AGPL-family', 'GPL-family', 'LGPL-3.0-family'):
                gate = 'FORBIDDEN'
            elif 'Commons-Clause' in verdict_spdx or verdict_spdx.startswith('Dual:'):
                # source-available/dual licenses: not in the MIT/Apache/BSD allow bucket;
                # reference-only (read/compare) remains lawful, embedding/redistribution
                # or productization does not -- group harvest-mechanism ruling required.
                gate = 'CONDITIONAL-REF-ONLY'
            elif verdict_spdx in ALLOW or verdict_spdx in ('Apache-family', 'BSD-family'):
                gate = 'PASS'
            else:
                gate = 'PENDING'
            row.update(api_spdx=spdx, api_name=name, path=path, size=d.get('size'),
                       head_sha=d.get('sha'), head_class=head_class,
                       verdict=verdict_spdx, gate_license=gate, fetch='ok')
            row['head_excerpt'] = ' | '.join(
                l.strip() for l in head.splitlines() if l.strip())[:400]
            ok += 1
        except urllib.error.HTTPError as e:
            row.update(fetch='HTTP-%d' % e.code, gate_license='UNVERIFIED')
            fail += 1
        except Exception as e:
            row.update(fetch='ERR-' + str(e)[:60], gate_license='UNVERIFIED')
            fail += 1
        rows.append(row)
    out = dict(probe_ts=ts, round=rnd, machine='bm-c', order='O-20261007-2245-bm-c',
               purpose='NOASSERTION license verification (E2/E5 first batch)',
               allow=sorted(ALLOW), forbid=sorted(FORBID), fetched_ok=ok,
               fetched_fail=fail, results=rows)
    path = os.path.join(OUT_DIR, 'license-%s.json' % date)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('OSS-LICENSE-PROBE %s round=%s ok=%d fail=%d' % (ts, rnd, ok, fail))
    for r in rows:
        print('%s %s api_spdx=%s head_class=%s verdict=%s gate=%s path=%s fetch=%s' % (
            r['id'], r['repo'], r.get('api_spdx'), r.get('head_class'),
            r.get('verdict'), r.get('gate_license'), r.get('path'), r.get('fetch')))
        if r.get('head_excerpt'):
            print('  HEAD: %s' % r['head_excerpt'][:260])
    print('EVIDENCE ' + path)
    if ok == 0:
        return 2
    return 0 if fail == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
