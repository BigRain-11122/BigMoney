# r941 bm-a rebase resolver (E42 one-breath window; 31 UU at pick dfc5af570)
# Laws honored: r185 parse-verify, r140 tie->:2:(HEAD-at-replay), r100/R350 hardened deep-ts probe,
# r327/r329 twin-side coupling (json decides side, md byte-copy same side), r188 x2 line union,
# R209 js-wrapper whole-byte, r223/r234 byte-verbatim take-side (no re-serialization).
# Stages: :2: = origin/upstream side, :3: = local/replayed-commit side (r351 directional law).
import subprocess, json, re, sys, io

GIT = r'C:\Program Files\Git\cmd\git.exe'

def git_bytes(*a):
    r = subprocess.run([GIT] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %r rc=%d %s' % (a, r.returncode, r.stderr.decode('utf-8', 'replace')[:300]))
    return r.stdout

def stage_blob(stage, path):
    return git_bytes('cat-file', 'blob', stage + path)

WALLCLOCK_RE = re.compile(r'[T ]\d{2}:\d{2}')
TSVAL_RE = re.compile(r'^20\d{2}-')
KEY_RE = re.compile(r'(asof|ts$|_ts|time|updated|generated|cutoff|scan|lastrun|lastseen|as_at|_at$)')

def _norm_key(k):
    return k.replace('_', '').replace('-', '').lower()

def deep_ts_probe(obj):
    """Return (wallclock_max, dateonly_max) over timestamp-shaped values under qualified keys."""
    wall, date = [], []
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                nk = _norm_key(k)
                if isinstance(v, str) and TSVAL_RE.match(v):
                    if KEY_RE.search(nk) or nk.endswith('ts') or nk.endswith('at') or 'date' in nk or 'updated' in nk:
                        if WALLCLOCK_RE.search(v):
                            wall.append(v)
                        else:
                            date.append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return (max(wall) if wall else None, max(date) if date else None)

def probe_side(path):
    """Decide side for a snapshot json via staged-blob deep-ts probe. tie -> :2: (r140, HEAD at replay)."""
    probes = {}
    for stage in (':2:', ':3:'):
        b = stage_blob(stage, path)
        try:
            probes[stage] = deep_ts_probe(json.loads(b.decode('utf-8', 'replace')))
        except Exception as e:
            probes[stage] = ('PARSE_FAIL', str(e)[:80])
    p2, p3 = probes[':2:'], probes[':3:']
    # wall-clock bucket preferred (R350); fall back to date-only bucket
    for idx in (0, 1):
        v2, v3 = p2[idx], p3[idx]
        if v2 is None and v3 is None:
            continue
        if v2 is None:
            return ':3:', probes
        if v3 is None:
            return ':2:', probes
        if v2 != v3:
            return (':2:' if v2 > v3 else ':3:'), probes
    return ':2:', probes  # tie -> :2: per r140

def take_side_whole(path, side, verify_json=True):
    b = stage_blob(side, path)
    if verify_json:
        json.loads(b.decode('utf-8', 'replace'))
    with io.open(path, 'wb') as f:
        f.write(b)
    return len(b)

def resolve_twin(json_path, md_path, receipt):
    side, probes = probe_side(json_path)
    n1 = take_side_whole(json_path, side)
    n2 = take_side_whole(md_path, side, verify_json=False)
    receipt.append({'path': json_path, 'recipe': 'twin-json-decides', 'side': side, 'probe': {k: list(v) if isinstance(v, tuple) else v for k, v in probes.items()}, 'bytes': [n1, n2]})

def resolve_snapshot(path, receipt, label='snapshot-take-new'):
    side, probes = probe_side(path)
    n = take_side_whole(path, side)
    receipt.append({'path': path, 'recipe': label, 'side': side, 'probe': {k: list(v) if isinstance(v, tuple) else v for k, v in probes.items()}, 'bytes': n})

def _verify_jsonl_line(ln):
    try:
        json.loads(ln)
        return True
    except Exception:
        # legacy joined-pair defect (present once in base/origin/local alike): two valid objects concatenated on one line
        i = ln.find('}{')
        if i < 0:
            return False
        try:
            json.loads(ln[:i + 1])
            json.loads(ln[i + 1:])
            return True
        except Exception:
            return False

def resolve_jsonl_union(path, receipt):
    b2 = stage_blob(':2:', path).decode('utf-8', 'replace').splitlines()
    b3 = stage_blob(':3:', path).decode('utf-8', 'replace').splitlines()
    seen, out = set(), []
    for ln in b2 + b3:  # origin-first = chronological here (origin batch 04:08 predates local 04:23)
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    # parse-verify every non-empty line (r185; legacy joined-pair verified by split)
    legacy = 0
    for ln in out:
        if ln.strip():
            try:
                json.loads(ln)
            except Exception:
                if _verify_jsonl_line(ln):
                    legacy += 1
                else:
                    raise RuntimeError('union line fails parse: %s' % ln[:150])
    assert legacy <= 1, 'unexpected joined-line count %d' % legacy
    nl = '\r\n' if b'\r\n' in stage_blob(':2:', path) else '\n'
    body = nl.join(out) + (nl if out else '')
    with io.open(path, 'wb') as f:
        f.write(body.encode('utf-8'))
    receipt.append({'path': path, 'recipe': 'append-log-line-union', 'origin_lines': len(b2), 'local_lines': len(b3), 'union_lines': len(out), 'legacy_joined_line_verified': legacy})

def main():
    receipt = []
    # 1) twin pairs (json decides side; md byte-copy same side) - r327/r329
    resolve_twin('docs/daily_report/REPORT-2026-10-10.json', 'docs/daily_report/REPORT-2026-10-10.md', receipt)
    resolve_twin('docs/live_usage/LIVE-2026-10-10.json', 'docs/live_usage/LIVE-2026-10-10.md', receipt)
    resolve_twin('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md', receipt)
    # paper_export pair: export json decides, latest.json same side (same generation run)
    side, probes = probe_side('results/paper_export/export-2026-10-09.json')
    n1 = take_side_whole('results/paper_export/export-2026-10-09.json', side)
    n2 = take_side_whole('results/paper_export/latest.json', side)
    receipt.append({'path': 'results/paper_export/export-2026-10-09.json', 'recipe': 'paper-export-pair', 'side': side, 'bytes': [n1, n2]})
    # dashboard pair: json decides side; js = whole-byte same side (R209: never json.dumps rewrite)
    side, probes = probe_side('results/dashboard_status.json')
    n1 = take_side_whole('results/dashboard_status.json', side)
    b = stage_blob(side, 'results/dashboard_status.js')
    assert b'window.DASH_DATA' in b, 'js wrapper missing DASH_DATA marker'
    with io.open('results/dashboard_status.js', 'wb') as f:
        f.write(b)
    receipt.append({'path': 'results/dashboard_status.json', 'recipe': 'dashboard-pair-json-decides', 'side': side, 'js_bytes': len(b)})
    # 2) plain snapshots
    for p in [
        'results/daily_scorecard.json',
        'results/scorecard_v1.json',
        'results/strategy_scorecard.json',
        'results/t35_open_fill_verify.json',
        'results/prospect_paper/_summary.json',
        'results/prospect_promotion/_summary.json',
        'results/fundamental_b_layer_filter.json',  # not an ALL_FACES member (face=fundamental_status is a different file) -> snapshot per classifier
        'results/paper/COMPOSITE-CE-01_paper.json',
        'results/paper/COMPOSITE-CE-02_paper.json',
        'results/paper/DROUGHT-CE-01_paper.json',
        'results/paper/ENGULF-CE-01_paper.json',
        'results/paper/NEEDLE-DE-01_paper.json',
        'results/paper/VOLATILITY-CE-01_paper.json',
    ]:
        resolve_snapshot(p, receipt)
    # 3) hand-classified unknown: _attrition_guard_scan.json = guard-scan receipt snapshot, newest scan wins
    resolve_snapshot('results/_attrition_guard_scan.json', receipt, label='hand-classified-snapshot (guard scan receipt)')
    # 4) append-log union
    resolve_jsonl_union('results/x2_watch_log.jsonl', receipt)
    with io.open('results/_r941bma_rebase_resolver.json', 'w', encoding='utf-8', newline='') as f:
        json.dump({'round': 'r941', 'machine': 'bm-a', 'files': receipt}, f, ensure_ascii=False, indent=1)
    print('resolver done: %d files, receipt written' % len(receipt))

if __name__ == '__main__':
    main()
