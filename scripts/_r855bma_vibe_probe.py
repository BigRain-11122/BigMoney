# _r855bma_vibe_probe.py -- OSS admission experiment S5-01 vibe-astock probe (bm-a lane, r855).
# Target: github.com/simonlin1212/vibe-astock (A-share short-line review dashboard; REGIME-5 sentiment supply
#         candidate #1 per OSS_HARVEST_LEDGER section-6; consumer = O-20261001-2103 R2 feature engineering leg).
# Faces: (1) repo meta re-verify (stars/license/push re-read, no hand-copied numbers);
#        (2) recursive file tree -> indicator-module identification by keyword funnel;
#        (3) raw fetch of key source files (size-capped) -> data-channel inventory (akshare/API call regex)
#            + emotion-indicator formula extraction (literal needles, disclosed as claims=unverified);
#        (4) local data-readiness cross-check: which channels our in-repo S6 chain already covers.
# Gates: admission verdict = probe evidence only (lai-na != mian-jian; adaptation still requires prereg chain).
# rc: 0 = all faces fetched; 1 = partial fetch errors (disclosed); 2 = mechanism failure.
import json, urllib.request, urllib.parse, urllib.error, os, sys, io, re, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'results', 'oss_eng_scan', 'vibe-probe-20261008.json')
REPO_NAME = 'simonlin1212/vibe-astock'
UA = {'User-Agent': 'bm-a-oss-vibe-probe'}

IND_KEYS = ['情绪', '涨停', '连板', '梯队', '晋级', '赚钱', '龙虎', '炸板', '周期', 'sentiment',
            'emotion', 'zt', 'pool', 'lhb', 'timeline', 'space', 'review']
CHANNEL_PAT = re.compile(r'(?:akshare\s+as\s+ak[\s\S]{0,120}?ak\.\w+|ak\.\w+|tushare\.\w+'
                          r'|api\.pico\.ai\w*|efinance\.\w+| requests\.(?:get|post)\([^)]{0,120})')
FETCH_CAP_BYTES = 120_000
MAX_FILES = 8

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()

def try_fetch(url, timeout=25):
    try:
        return fetch(url, timeout), None
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'

def main():
    ts = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    ev = {'ts': ts, 'lane': 'bm-a r855', 'law_ref': 'O-20261007-2245 ledger S5-01 admission probe; O-20261001-2103 R2 leg',
          'repo': REPO_NAME, 'faces': {}}
    rc = 0

    # face 1: repo meta
    body, err = try_fetch(f'https://api.github.com/repos/{REPO_NAME}')
    if err:
        ev['faces']['meta'] = {'fetch_error': err}; rc = 1
        meta = {}
    else:
        d = json.loads(body)
        meta = dict(stars=d.get('stargazers_count'), license=(d.get('license') or {}).get('spdx_id') or 'NONE',
                    pushed_at=d.get('pushed_at'), archived=d.get('archived'), default_branch=d.get('default_branch'),
                    language=d.get('language'), size_kb=d.get('size'))
        ev['faces']['meta'] = meta

    branch = meta.get('default_branch') or 'main'
    br = urllib.parse.quote(branch)

    # face 2: recursive tree
    body, err = try_fetch(f'https://api.github.com/repos/{REPO_NAME}/git/trees/{br}?recursive=1')
    if err:
        ev['faces']['tree'] = {'fetch_error': err}; rc = max(rc, 1)
        files = []
    else:
        t = json.loads(body)
        files = [e['path'] for e in t.get('tree', []) if e.get('type') == 'blob']
        ev['faces']['tree'] = {'n_files': len(files), 'truncated': t.get('truncated', False)}

    # indicator-module funnel
    cand = []
    for p in files:
        pl = p.lower()
        if not pl.endswith(('.py', '.js', '.ts', '.vue', '.md')):
            continue
        hits = [k for k in IND_KEYS if k in pl]
        if hits:
            cand.append({'path': p, 'keys': hits})
    cand.sort(key=lambda x: -len(x['keys']))
    ev['faces']['modules'] = {'n_candidates': len(cand), 'top': cand[:20]}

    # face 3: raw fetch key files
    srcs, channels = [], set()
    for c in cand[:MAX_FILES]:
        body, err = try_fetch(f'https://raw.githubusercontent.com/{REPO_NAME}/{br}/{urllib.parse.quote(c["path"])}')
        if err or len(body or b'') > FETCH_CAP_BYTES:
            srcs.append({'path': c['path'], 'fetch_error': err or 'size-cap-skip'})
            rc = max(rc, 1)
            continue
        try:
            txt = body.decode('utf-8', errors='replace')
        except Exception as e:
            srcs.append({'path': c['path'], 'fetch_error': f'decode: {e}'}); continue
        found_ch = sorted(set(m.group(0)[:60] for m in CHANNEL_PAT.finditer(txt)))
        channels.update(found_ch)
        srcs.append({'path': c['path'], 'bytes': len(body), 'data_calls': found_ch[:40],
                     'akshare_calls': sorted(set(re.findall(r'ak\.(stock_\w+|zhit\w+|fund_\w+)', txt)))[:40],
                     'indicator_needles': sorted(set(k for k in IND_KEYS if k in txt))})
    ev['faces']['sources'] = srcs
    ev['faces']['channel_inventory'] = sorted(channels)[:80]

    # face 4: README for claimed feature surface
    body, err = try_fetch(f'https://raw.githubusercontent.com/{REPO_NAME}/{br}/README.md')
    if err:
        ev['faces']['readme'] = {'fetch_error': err}; rc = max(rc, 1)
    else:
        rtxt = body.decode('utf-8', errors='replace')
        ev['faces']['readme'] = {'bytes': len(body),
                                 'claimed_features': sorted(set(k for k in IND_KEYS if k in rtxt)),
                                 'head_excerpt': rtxt[:600]}

    # face 4b: local data-readiness cross-check (in-repo channel registry, no network)
    readiness = {'akshare_installed': None, 'akshare_version': None, 'zt_pool_api': None, 'lhb_in_chain': None}
    try:
        import akshare as ak
        readiness['akshare_installed'] = True
        readiness['akshare_version'] = getattr(ak, '__version__', None)
        readiness['zt_pool_api'] = hasattr(ak, 'stock_zt_pool_em')
        readiness['zt_strength_api'] = hasattr(ak, 'stock_zt_pool_strong_em')
        readiness['lhb_api'] = hasattr(ak, 'stock_lhb_detail_em')
    except Exception as e:
        readiness['akshare_installed'] = f'ERROR: {e}'
        readiness['lhb_in_chain'] = 'in-chain: scripts/update_lhb.py (S6 R18)'
        ev['faces']['local_readiness'] = readiness
        rc = max(rc, 1)
    else:
        readiness['lhb_in_chain'] = 'in-chain: scripts/update_lhb.py (S6 R18)'
        ev['faces']['local_readiness'] = readiness

    ev['rc'] = rc
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print(f'vibe-probe rc={rc} modules={ev["faces"].get("modules", {}).get("n_candidates", 0)} '
          f'channels={len(ev["faces"].get("channel_inventory", []))} out={os.path.relpath(OUT, REPO)}')
    return rc

if __name__ == '__main__':
    sys.exit(main())
