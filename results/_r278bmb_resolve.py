# r278 bm-b rebase collision resolver (vs bm-a r276 6e12a6e0, same-window S6 product family)
# 15-UU classified per bigmoney-conflict-resolve skill; recipes:
#  - compute_audit.json: rolling-ledger -> top-level take-new (mine 23:04 sample) + history identity-union (ours 203 base + mine extras, ts asc) [r188/R208]
#  - regime_state.json: only 'updated' differs (identity-equal otherwise) -> take mine (newer) [R208]
#  - autofill_state.json: launches 49==49 identical; last_tick same-second tie 23:00:01 -> HEAD=ours per r140 [r203/r245]
#  - dashboard pair: take-new by meta.generated_at wall-clock explicit key (mine 23:05:38 > 23:01:05; r265 future-constant hijack law -> explicit producer key only) [r267/r277]
#  - *_status.json / blf / token_usage / daily_report twin / scorecards: same-producer regenerated snapshots, take-new by internal ts [R208]
# Byte-face law: take-side files written as verbatim blob bytes (zero format drift); re-serialized file (compute_audit) mirrors indent/newline/trailing-nl of base blob.
import subprocess, json, sys

def blob(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'blob fetch failed {rev} {path}: {r.stderr[:200]}')
    return r.stdout

TAKE_MINE = [
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/update_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/token_usage.json',
    'results/dashboard_status.json',
    'results/dashboard_status.js',
    'docs/daily_report/REPORT-2026-09-26.json',
    'docs/daily_report/REPORT-2026-09-26.md',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/regime_state.json',
]
TAKE_OURS = ['results/autofill_state.json']

def main():
    report = []
    # ---- verbatim take-side files (zero format drift) ----
    for f in TAKE_MINE:
        b = blob(':3', f)
        open(f, 'wb').write(b)
        report.append(f'{f}: take-mine (verbatim {len(b)}B)')
    for f in TAKE_OURS:
        b = blob(':2', f)
        open(f, 'wb').write(b)
        report.append(f'{f}: take-ours (verbatim {len(b)}B)')

    # ---- compute_audit.json: top take-mine + history identity-union ----
    f = 'results/compute_audit.json'
    raw_o, raw_m = blob(':2', f), blob(':3', f)
    o, m = json.loads(raw_o), json.loads(raw_m)
    ho, hm = o['history'], m['history']
    ident = lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False)
    seen = {ident(e) for e in ho}
    extras = [e for e in hm if ident(e) not in seen]
    union = ho + extras
    union.sort(key=lambda e: e.get('ts', ''))  # producer order = ts asc (append)
    top = {k: v for k, v in m.items() if k != 'history'}  # top-level = newest sample (mine)
    merged = dict(top)
    merged['history'] = union
    # byte-face mirror: indent from base blob line 2, newline mode, trailing newline
    line2 = raw_o.split(b'\n')[1] if b'\n' in raw_o else b''
    indent = len(line2) - len(line2.lstrip(b' '))
    crlf = b'\r\n' in raw_o
    trailing = b'\n' if raw_o.endswith(b'\n') else b''
    text = json.dumps(merged, ensure_ascii=False, indent=indent or 1)
    if crlf:
        text = text.replace('\n', '\r\n')
    open(f, 'wb').write(text.encode('utf-8') + trailing)
    report.append(f'{f}: top=mine, history union {len(ho)}+{len(extras)}->{len(union)} (ts asc, zero-loss)')

    # ---- parse-verify + zero-loss audit ----
    for f in TAKE_MINE + TAKE_OURS + [f]:
        if f.endswith('.js'):
            t = open(f, encoding='utf-8').read()
            assert t.lstrip().startswith('window.DASH_DATA') and t.rstrip().endswith('};'), f'js wrapper broken {f}'
            inner = t[t.index('{'):t.rindex('}') + 1]
            json.loads(inner)
        elif f.endswith('.md'):
            open(f, encoding='utf-8').read()
        else:
            d = json.loads(open(f, encoding='utf-8').read())
            if f == 'results/autofill_state.json':
                assert len(d['launches']) == 49 and isinstance(d['last_tick'], dict), 'autofill face broken'
                assert d['last_tick']['machine'] == 'bm-a', 'tie->HEAD=ours violated'
            if f == 'results/regime_state.json':
                assert d['updated'] == '2026-09-26 23:04:14', 'regime take-new violated'
            if f == 'results/dashboard_status.json':
                assert d['meta']['generated_at'] == '2026-09-26T23:05:38', 'dashboard take-new violated'
    ca = json.loads(open('results/compute_audit.json', encoding='utf-8').read())
    assert len(ca['history']) == len(ho) + len(extras), 'union count mismatch'
    assert ca['latest']['ts'] == '2026-09-26 23:04:04', 'top take-new violated'
    print('RESOLVED 15/15, parse-verify ALL PASS')
    for line in report:
        print(' -', line)

if __name__ == '__main__':
    main()
