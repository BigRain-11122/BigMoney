# r335 bm-b S0 fold inspection: dump both-side blobs for 30-UU batch (rebase pick a8cf7330 onto 1558405c)
# Sides: stage2=HEAD=upstream(bm-a r338 close), stage3=REBASE_HEAD=bm-b r334. Read git objects via subprocess bytes (r209: no PS redirection).
import json, subprocess, difflib, sys

def blob(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def eol(b):
    if b is None: return '?'
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    return 'CRLF' if crlf >= lf and crlf > 0 else ('LF' if lf > 0 else 'none')

def brief(v, n=90):
    s = json.dumps(v, ensure_ascii=False, default=str) if not isinstance(v, str) else v
    return s[:n] + ('…' if len(s) > n else '')

UU = """CODELY.md
docs/daily_report/REPORT-2026-09-27.json
docs/daily_report/REPORT-2026-09-27.md
research/memory-archive/202609.md
results/autofill_state.json
results/compute_audit.json
results/daily_scorecard.json
results/dashboard_status.js
results/dashboard_status.json
results/fundamental_b_layer_filter.json
results/futures_update_status.json
results/heat_update_status.json
results/lhb_update_status.json
results/paper/COMPOSITE-CE-01_paper.json
results/paper/COMPOSITE-CE-02_paper.json
results/paper/DROUGHT-CE-01_paper.json
results/paper/ENGULF-CE-01_paper.json
results/paper/NEEDLE-DE-01_paper.json
results/paper/VOLATILITY-CE-01_paper.json
results/paper_export/export-2026-09-24.json
results/paper_export/latest.json
results/prospect_paper/_summary.json
results/prospect_promotion/_summary.json
results/regime_state.json
results/scorecard_v1.json
results/strategy_scorecard.json
results/t35_open_fill_verify.json
results/token_usage.json
results/update_status.json
results/x2_watch_log.jsonl""".splitlines()

for path in UU:
    a, b = blob('HEAD', path), blob('REBASE_HEAD', path)
    print(f'\n===== {path} | A(HEAD)={len(a) if a else -1}B {eol(a)} | B(REB)={len(b) if b else -1}B {eol(b)}')
    if path.endswith('.jsonl'):
        la, lb = a.decode('utf-8').splitlines(), b.decode('utf-8').splitlines()
        sa, sb = set(la), set(lb)
        print(f'  lines A={len(la)} B={len(lb)} Aonly={len(sa-sb)} Bonly={len(sb-sa)}')
        for x in sorted(sa - sb)[:3]: print('   A+', brief(x, 110))
        for x in sorted(sb - sa)[:3]: print('   B+', brief(x, 110))
        continue
    if path.endswith('.md'):
        la, lb = a.decode('utf-8').splitlines(), b.decode('utf-8').splitlines()
        base = blob('HEAD~1', path)  # informational only
        # try common prefix/suffix
        pre = 0
        while pre < min(len(la), len(lb)) and la[pre] == lb[pre]: pre += 1
        suf = 0
        while suf < min(len(la), len(lb)) - pre and la[-1-suf] == lb[-1-suf]: suf += 1
        print(f'  md lines A={len(la)} B={len(lb)} common_prefix={pre} common_suffix={suf}')
        print('  A-suffix:', *[f'   |{x[:100]}' for x in la[pre:len(la)-suf][:8]])
        print('  B-suffix:', *[f'   |{x[:100]}' for x in lb[pre:len(lb)-suf][:8]])
        continue
    if path.endswith('.js'):
        print('  A head:', brief(a.decode('utf-8'), 200)); print('  B head:', brief(b.decode('utf-8'), 200))
        continue
    try:
        da, db = json.loads(a.decode('utf-8')), json.loads(b.decode('utf-8'))
    except Exception as ex:
        print('  PARSE FAIL', ex); continue
    if isinstance(da, dict) and isinstance(db, dict):
        print('  keys:', sorted(da.keys()))
        for k in sorted(set(da) | set(db)):
            va, vb = da.get(k, '<absent>'), db.get(k, '<absent>')
            if va == vb: continue
            if isinstance(va, list) and isinstance(vb, list):
                print(f'  [{k}] LIST A={len(va)} B={len(vb)}', end='')
                ja, jb = json.dumps(va), json.dumps(vb)
                if ja == jb: print('(json-equal)')
                else:
                    pre = 0
                    while pre < min(len(va), len(vb)) and va[pre] == vb[pre]: pre += 1
                    print(f' diverge@{pre}')
                    for x in va[pre:pre+2]: print('    A*', brief(x, 130))
                    for x in vb[pre:pre+2]: print('    B*', brief(x, 130))
                    if len(va) > pre+2: print(f'    A..{len(va)-pre-2} more')
                    if len(vb) > pre+2: print(f'    B..{len(vb)-pre-2} more')
            elif isinstance(va, dict) and isinstance(vb, dict):
                sub = {kk: (va.get(kk, '<abs>'), vb.get(kk, '<abs>')) for kk in set(va) | set(vb) if va.get(kk, '<abs>') != vb.get(kk, '<abs>')}
                print(f'  [{k}] DICT-diff keys={list(sub)[:6]}')
                for kk, (x1, x2) in list(sub.items())[:4]:
                    print(f'    .{kk}: A={brief(x1,80)} B={brief(x2,80)}')
            else:
                print(f'  [{k}] A={brief(va,80)} | B={brief(vb,80)}')
    else:
        print('  A type', type(da).__name__, 'B type', type(db).__name__)
print('\nINSPECT DONE')
