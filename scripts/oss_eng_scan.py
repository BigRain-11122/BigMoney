# oss_eng_scan.py -- O-20261007-2245 bm-c lane: engineering-class OSS scan probe.
# Four families (backtest-engine benchmark / data pipeline / scheduling-monitoring /
# broker gateway), five-gate CPH4 evaluation (fit / dup-check vs attrition+in-service /
# license / health / cost). Auto faces read live from api.github.com (the proven
# reliable channel); manual faces (fit/cost) are first-pass judgment, disclosed.
# Verdicts are scan evidence only -- adoption still requires the full gate chain
# (borrow-law iron face: external claims = unverified hypotheses, lai-na != mian-jian).
# rc: 0 = all fetched; 1 = partial fetch errors (disclosed); 2 = mechanism failure.
import json, time, urllib.request, urllib.error, os, sys, io, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, 'results', 'oss_eng_scan')
ALLOW_LICENSES = {'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'}
FORBID_LICENSES = {'AGPL-3.0', 'AGPL-2.0', 'GPL-3.0', 'GPL-2.0', 'LGPL-3.0', 'LGPL-2.1'}
HEALTH_STARS_MIN = 500
HEALTH_PUSH_DAYS = 365

# registry: family, id, repo (owner/name or None=non-GitHub), why_fit (first-pass),
# cost_h (initial-screen budget hours, <=8h rule), dup_tags (for attrition/in-service cross-check)
CANDIDATES = [
    # F1 backtest-engine benchmark (self-engine gap reference)
    dict(family='F1-backtest-engine', id='E1', repo='mementum/backtrader',
         why='event-driven engine; order/exit-stack reference for our self-engine gap analysis',
         cost_h=8, dup_tags=['backtest-engine']),
    dict(family='F1-backtest-engine', id='E2', repo='polakowo/vectorbt',
         why='vectorized grid scan; N1 band-burn throughput reference',
         cost_h=8, dup_tags=['backtest-engine', 'grid-scan']),
    dict(family='F1-backtest-engine', id='E3', repo='nautechsystems/nautilus_trader',
         why='prod-grade engine; live-execution architecture reference',
         cost_h=8, dup_tags=['backtest-engine', 'live-exec']),
    dict(family='F1-backtest-engine', id='E4', repo='stefan-jansen/zipline-reloaded',
         why='pipeline-style engine; point-in-time data discipline reference',
         cost_h=8, dup_tags=['backtest-engine']),
    dict(family='F1-backtest-engine', id='E5', repo='ricequant/rqalpha',
         why='A-share native T+1 engine; fee/board-rule caliber comparison face',
         cost_h=8, dup_tags=['backtest-engine', 'a-share-native']),
    # F2 data pipeline
    dict(family='F2-data-pipeline', id='D1', repo='akfamily/akshare',
         why='in-service (sina channel via direct endpoints); cost/robustness ledger face',
         cost_h=2, dup_tags=['data-pipeline'], in_service=True),
    dict(family='F2-data-pipeline', id='D2', repo='wadefu/tushare',
         why='pro API already CEO-token-authorized; backup channel for daily/fundamental faces',
         cost_h=4, dup_tags=['data-pipeline'], in_service=True),
    dict(family='F2-data-pipeline', id='D3', repo='shidenggui/easyquotation',
         why='lightweight realtime quote lib; intraday-marks channel candidate',
         cost_h=4, dup_tags=['data-pipeline', 'intraday']),
    # F3 scheduling / monitoring
    dict(family='F3-sched-monitor', id='G1', repo='agronholm/apscheduler',
         why='in-process python scheduler; Windows-fleet loop hardening candidate',
         cost_h=4, dup_tags=['scheduler']),
    dict(family='F3-sched-monitor', id='G2', repo='healthchecks/healthchecks',
         why='self-hosted dead-man cron monitor; fleet silence-law watchdog face',
         cost_h=4, dup_tags=['monitor']),
    dict(family='F3-sched-monitor', id='G3', repo='louislam/uptime-kuma',
         why='self-hosted uptime monitor; machine/daemon liveness dashboard candidate',
         cost_h=4, dup_tags=['monitor']),
    dict(family='F3-sched-monitor', id='G4', repo='PrefectHQ/prefect',
         why='heavyweight DAG scheduler; control-plane reference only (fits git-plane fleet poorly)',
         cost_h=6, dup_tags=['scheduler']),
    # F4 broker gateway
    dict(family='F4-broker-gateway', id='B1', repo='vnpy/vnpy',
         why='gateway + CTA templates; strategy face already S2; engineering face = broker API adapter',
         cost_h=8, dup_tags=['broker-gateway', 'cta-template'], in_flight_note='CTA_P1 in-flight (O-2215-2): harvest templates only, no verdict import'),
    dict(family='F4-broker-gateway', id='B2', repo='shidenggui/easytrader',
         why='retail broker-client automation; A-share order-route candidate for paper->live bridge',
         cost_h=8, dup_tags=['broker-gateway']),
    dict(family='F4-broker-gateway', id='B3', repo=None,
         why='xtquant/QMT official SDK: vendor-distributed (no canonical GitHub repo); register as non-GitHub vendor face, gates pending vendor docs',
         cost_h=8, dup_tags=['broker-gateway', 'vendor-sdk']),
]

def load_attrition_tokens():
    tokens = set()
    for fn in ('gate_attrition.json', 'gate_attrition.bm-a.json',
               'gate_attrition.bm-b.json', 'gate_attrition.bm-c.json'):
        p = os.path.join(REPO, 'results', fn)
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        stack = [data]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                for k, v in cur.items():
                    if isinstance(k, str) and len(k) < 64:
                        tokens.add(k.lower())
                    stack.append(v)
            elif isinstance(cur, list):
                stack.extend(cur)
            elif isinstance(cur, str) and len(cur) < 64:
                tokens.add(cur.lower())
    return tokens

def gh_fetch(repo):
    url = 'https://api.github.com/repos/' + repo
    req = urllib.request.Request(url, headers={
        'User-Agent': 'bigmoney-oss-scan', 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    attr = load_attrition_tokens()
    ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    date = datetime.date.today().strftime('%Y%m%d')
    rows, ok, fail = [], 0, 0
    for c in CANDIDATES:
        row = dict(c)
        row['dup_hits_attrition'] = [t for t in c['dup_tags'] if t in attr]
        if c['repo'] is None:
            row.update(stars=None, pushed_at=None, license=None, archived=None,
                      open_issues=None, fetch='non-github-vendor', url=None,
                      gate_license='PENDING', gate_health='PENDING')
            rows.append(row)
            continue
        try:
            d = gh_fetch(c['repo'])
            lic = (d.get('license') or {}).get('spdx_id') or 'None'
            row.update(stars=d.get('stargazers_count'), pushed_at=d.get('pushed_at'),
                       license=lic, archived=d.get('archived'),
                       open_issues=d.get('open_issues_count'),
                       fetch='ok', url=d.get('html_url'))
            if lic in FORBID_LICENSES:
                row['gate_license'] = 'FORBIDDEN'
            elif lic in ALLOW_LICENSES:
                row['gate_license'] = 'PASS'
            else:
                row['gate_license'] = 'PENDING'
            try:
                days = (datetime.datetime.now(datetime.timezone.utc) -
                        datetime.datetime.strptime(d.get('pushed_at', ''),
                                                    '%Y-%m-%dT%H:%M:%SZ').replace(
                                                    tzinfo=datetime.timezone.utc)).days
            except Exception:
                days = 99999
            row['push_age_days'] = days
            row['gate_health'] = ('PASS' if (d.get('stargazers_count', 0) >= HEALTH_STARS_MIN
                                              and days <= HEALTH_PUSH_DAYS
                                              and not d.get('archived')) else 'FAIL')
            ok += 1
        except urllib.error.HTTPError as e:
            row.update(stars=None, pushed_at=None, license=None, archived=None,
                       open_issues=None, fetch='HTTP-%d' % e.code, url=None,
                       gate_license='UNVERIFIED', gate_health='UNVERIFIED', push_age_days=None)
            fail += 1
        except Exception as e:
            row.update(stars=None, pushed_at=None, license=None, archived=None,
                       open_issues=None, fetch='ERR-' + str(e)[:40], url=None,
                       gate_license='UNVERIFIED', gate_health='UNVERIFIED', push_age_days=None)
            fail += 1
        rows.append(row)
        time.sleep(0.6)
    out = dict(scan_ts=ts, round=706, machine='bm-c', order='O-20261007-2245-bm-c',
               source='api.github.com /repos endpoint, live fetch, no hand-typed numbers',
               thresholds=dict(health_stars_min=HEALTH_STARS_MIN,
                               health_push_days=HEALTH_PUSH_DAYS,
                               forbid=list(sorted(FORBID_LICENSES))),
               attrition_tokens_loaded=len(attr), fetched_ok=ok, fetched_fail=fail,
               candidates=rows)
    path = os.path.join(OUT_DIR, 'scan-%s.json' % date)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('OSS-ENG-SCAN %s ok=%d fail=%d attr_tokens=%d' % (ts, ok, fail, len(attr)))
    print('| id | family | repo | stars | license | health | lic-gate | fit | cost_h | dup |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        dup = 'HIT:' + ','.join(r['dup_hits_attrition']) if r['dup_hits_attrition'] else 'clean'
        if r.get('in_service'):
            dup += ' /in-service'
        print('| %s | %s | %s | %s | %s | %s | %s | %s | %sh | %s |' % (
            r['id'], r['family'], r['repo'] or '(vendor)', r['stars'],
            r['license'], r['gate_health'], r['gate_license'],
            r['why'][:38], r['cost_h'], dup))
    print('EVIDENCE ' + path)
    if ok == 0:
        print('MECHANISM FAILURE: zero fetches')
        return 2
    return 0 if fail == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
