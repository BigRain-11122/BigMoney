# -*- coding: utf-8 -*-
"""r325 bm-a rebase resolver #2 -- 25-UU vs bm-c r82 (probe _r325bma_probe2.py).
Recipes per bigmoney-conflict-resolve skill:

  16 snapshot files        : S3 (bm-a 13:14-15) newer on frozen ts paths
                             -> git checkout --theirs whole bytes
  compute_audit.json       : history union by (ts, machine) + content-identity
                             verify on collisions (r319/r322); latest take S3
  regime_state.json       : asof-key union + content check; state fields S3
  x2_watch_log.jsonl       : append-log line-level union zero-loss (r188)
  autofill_state.json     : launches union -> ts desc cap 50 -> RE-SORT ASC
                             before write (bm-b r245 law); last_tick compare by
                             internal ts, tie -> HEAD/stage2 (r140); isinstance
                             dict assert (r220)
  daily_scorecard.json + t35_open_fill_verify.json : deep-diff locate differing
                             fields -> newer-ts side wins whole bytes; fail-closed
                             if non-ts differences appear
"""
import json
import subprocess
import sys


def stage_bytes(path, n):
    return subprocess.run(['git', 'show', ':%d:%s' % (n, path)],
                          capture_output=True).stdout


def write_bytes(path, b):
    with open(path, 'wb') as fh:
        fh.write(b)


def write_json(path, doc):
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    json.loads(s)
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(s)
    assert open(path, 'rb').read().decode('utf-8') == s


TAKE_THEIRS = [
    'docs/daily_report/REPORT-2026-09-27.json',
    'docs/daily_report/REPORT-2026-09-27.md',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/update_status.json',
    'results/token_usage.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-24.json',
    'results/paper_export/latest.json',
]


def resolve_compute_audit():
    p = 'results/compute_audit.json'
    d2, d3 = json.loads(stage_bytes(p, 2)), json.loads(stage_bytes(p, 3))
    union, coll = {}, 0
    for e in d2['history'] + d3['history']:
        k = (e.get('ts'), e.get('machine'))
        if k in union:
            coll += 1
            assert json.dumps(union[k], sort_keys=True) == json.dumps(e, sort_keys=True), \
                'content-diff on key %r (r322 escalation)' % (k,)
        else:
            union[k] = e
    merged = sorted(union.values(), key=lambda e: e.get('ts') or '')
    doc = dict(d3)
    doc['history'] = merged
    write_json(p, doc)
    return 'compute_audit: union %d+%d -> %d (collisions %d content-identical), latest S3 13:14:03' % (
        len(d2['history']), len(d3['history']), len(merged), coll)


def resolve_regime():
    p = 'results/regime_state.json'
    d2, d3 = json.loads(stage_bytes(p, 2)), json.loads(stage_bytes(p, 3))
    union = {}
    for e in (d2.get('history') or []) + (d3.get('history') or []):
        k = e.get('asof')
        if k in union:
            assert json.dumps(union[k], sort_keys=True) == json.dumps(e, sort_keys=True), k
        else:
            union[k] = e
    doc = dict(d3)
    doc['history'] = sorted(union.values(), key=lambda e: e.get('asof') or '')
    write_json(p, doc)
    return 'regime_state: asof-union -> %d (content-identical), state take S3 13:14:12' % len(doc['history'])


def resolve_x2log():
    p = 'results/x2_watch_log.jsonl'
    l2 = [ln for ln in stage_bytes(p, 2).decode('utf-8').splitlines() if ln.strip()]
    l3 = [ln for ln in stage_bytes(p, 3).decode('utf-8').splitlines() if ln.strip()]
    seen, out = set(), []
    for ln in l2 + l3:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    # chronological re-order by embedded ts (append-log union keeps zero loss)
    def ts_of(ln):
        try:
            return json.loads(ln).get('ts') or ''
        except Exception:
            return ''
    out.sort(key=ts_of)
    body = '\n'.join(out) + '\n'
    json.dumps([json.loads(ln) for ln in out])          # every line parses
    write_bytes(p, body.encode('utf-8'))
    return 'x2_watch_log: line union %d+%d -> %d zero-loss (sorted by ts)' % (
        len(l2), len(l3), len(out))


def resolve_autofill():
    p = 'results/autofill_state.json'
    d2, d3 = json.loads(stage_bytes(p, 2)), json.loads(stage_bytes(p, 3))
    l2, l3 = d2.get('launches') or [], d3.get('launches') or []
    seen, merged = set(), []
    for e in l2 + l3:
        k = json.dumps(e, sort_keys=True)
        if k not in seen:
            seen.add(k)
            merged.append(e)
    merged.sort(key=lambda e: e.get('ts') or '', reverse=True)
    merged = merged[:50]                    # cap 50 newest (cap = keep-newest)
    merged.sort(key=lambda e: e.get('ts') or '')   # re-sort ASC before write (r245)
    lt2, lt3 = d2.get('last_tick'), d3.get('last_tick')
    t2 = (lt2 or {}).get('ts') if isinstance(lt2, dict) else None
    t3 = (lt3 or {}).get('ts') if isinstance(lt3, dict) else None
    if t2 is None and t3 is not None:
        last_tick = lt3
    elif t3 is None and t2 is not None:
        last_tick = lt2
    elif t2 is not None and t3 is not None:
        last_tick = lt2 if str(t2) >= str(t3) else lt3   # tie -> HEAD/stage2 (r140)
    else:
        last_tick = None
    doc = dict(d3)
    doc['launches'] = merged
    if last_tick is not None:
        doc['last_tick'] = last_tick
        assert isinstance(doc['last_tick'], dict)
    write_json(p, doc)
    return 'autofill_state: launches union %d+%d -> %d cap50 asc-sorted, last_tick ts %s (tie->HEAD law)' % (
        len(l2), len(l3), len(merged), (last_tick or {}).get('ts'))


def diff_sides(p):
    b2, b3 = stage_bytes(p, 2), stage_bytes(p, 3)
    d2, d3 = json.loads(b2), json.loads(b3)
    diffs = []

    def walk(a, b, path=''):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in set(a) | set(b):
                if k not in a or k not in b:
                    diffs.append((path + '.' + str(k), 'MISSING-ONE-SIDE'))
                else:
                    walk(a[k], b[k], path + '.' + str(k))
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                diffs.append((path + '[len]', '%d vs %d' % (len(a), len(b))))
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, path + '[%d]' % i)
        elif a != b:
            diffs.append((path, '%r vs %r' % (a, b)))

    walk(d2, d3)
    return diffs


def resolve_diffpick(p, ts_key):
    diffs = diff_sides(p)
    tsdiffs = [d for d in diffs if d[0].endswith(ts_key)]
    assert tsdiffs, '%s: no %s diff found; raw diffs=%s' % (p, ts_key, diffs[:5])
    nonts = [d for d in diffs if not d[0].endswith(ts_key)]
    assert not nonts, '%s: NON-TS DIFFS fail-closed: %s' % (p, nonts[:5])
    d2, d3 = json.loads(stage_bytes(p, 2)), json.loads(stage_bytes(p, 3))
    v2 = _get(d2, ts_key)
    v3 = _get(d3, ts_key)
    win = 3 if str(v3) > str(v2) else 2
    write_bytes(p, stage_bytes(p, win))
    return '%s: deep-diff %d fields all ts-class (%s: %r vs %r) -> side S%d whole bytes' % (
        p, len(diffs), ts_key, v2, v3, win)


def _get(d, dotted):
    cur = d
    for part in dotted.split('.'):
        cur = cur[part]
    return cur


def main():
    report = []
    report.append(resolve_compute_audit())
    report.append(resolve_regime())
    report.append(resolve_x2log())
    report.append(resolve_autofill())
    # daily_scorecard + t35_open_fill_verify: locate the differing ts field first
    for p in ['results/daily_scorecard.json', 'results/t35_open_fill_verify.json']:
        diffs = diff_sides(p)
        paths = sorted({d[0] for d in diffs})
        print('DIFFPATHS %s -> %s' % (p, paths))
    report.append(resolve_diffpick('results/t35_open_fill_verify.json', 'ts'))
    for p in TAKE_THEIRS:
        r = subprocess.run(['git', 'checkout', '--theirs', p], capture_output=True)
        if r.returncode != 0:
            print('CHECKOUT FAIL', p, r.stderr.decode('utf-8', 'replace'))
            return 2
    for line in report:
        print(line)
    print('resolver2: %d union/ledger + %d take-theirs + t35 resolved; daily_scorecard pending diff print' % (
        4, len(TAKE_THEIRS)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
