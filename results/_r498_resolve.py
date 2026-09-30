# r498 rebase conflict resolver (canonical recipes per bigmoney-conflict-resolve SKILL.md)
# Batch 1: applying 3d71169 (r497) onto 3a318a952 (bm-b origin head). Re-runnable per conflict batch.
# ALL_FACES union already handled by scripts/merge_lane_views.py resolve (ran separately).
# This script handles: twin-regen-md (daily report), LIVE family, dashboard pair,
# snapshot take-new (fundamental_b_layer_filter, scorecard_v1, strategy_scorecard,
# _attrition_guard_scan), append-log union (pool_core_samples.jsonl), AA shards assert+take-:2:.
# Laws: r188 line-union, r140 same-second tie -> HEAD(:2:), r100/R350 hardened ts probe,
# r329 md-twin-copies-side-bytes, r209 js-wrapper take-side whole bytes, r471 adoption.
import subprocess, json, sys, re, io

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def normkey(k):
    return k.replace('_', '').replace('-', '').lower()

TS_SHAPE = re.compile(r'^20\d{2}-')
HAS_TOD = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

PROBE_PREFIXES = ('generated', 'updated', 'ts', 'asof', 'clockread', 'timestamp')

def collect_probe(obj, out, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_SHAPE.match(v) and HAS_TOD.match(v):
                nk = normkey(k)
                if any(nk.startswith(p) for p in PROBE_PREFIXES):
                    out.append((nk, v))
            collect_probe(v, out, path + '/' + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            collect_probe(v, out, path + '/' + str(i))

def probe_side(obj):
    cands = []
    collect_probe(obj, cands)
    if not cands:
        return None
    cands.sort(key=lambda x: x[1])
    return cands[-1][1]

log = []

def resolve_twin_side(pair_paths, probe_path_idx=0, tag=''):
    """Decide winner side by ts probe on the JSON member; write ALL members from that side's blob bytes."""
    a2, a3 = blob(2, pair_paths[probe_path_idx]), blob(3, pair_paths[probe_path_idx])
    if a2 is None or a3 is None:
        log.append(f'{tag}: no conflict stages present -> SKIP (not conflicted this batch)')
        return None
    j2, j3 = json.loads(a2), json.loads(a3)
    p2, p3 = probe_side(j2), probe_side(j3)
    if p2 is None and p3 is None:
        log.append(f'{tag}: NO PROBE BOTH SIDES -> fail-closed, take :2: (HEAD tie law r140)')
        side = 2
    elif p3 is None or (p2 is not None and p2 >= p3):
        side = 2 if p2 != p3 else 2  # tie or newer -> HEAD per r140
        log.append(f'{tag}: probe2={p2} probe3={p3} -> take :2: ({"tie" if p2 == p3 else "newer"})')
    else:
        side = 3
        log.append(f'{tag}: probe2={p2} probe3={p3} -> take :3: (newer)')
    for p in pair_paths:
        data = blob(side, p)
        with open(p, 'wb') as fh:
            fh.write(data)
        if p.endswith('.json'):
            json.loads(open(p, 'rb').read())  # parse-verify
        log.append(f'  wrote {p} from :{side}: ({len(data)}B)')
    return side

def resolve_snapshot_ts(path, tag=''):
    a2, a3 = blob(2, path), blob(3, path)
    if a2 is None or a3 is None:
        log.append(f'{tag or path}: no conflict stages present -> SKIP (not conflicted this batch)')
        return None
    j2, j3 = json.loads(a2), json.loads(a3)
    p2, p3 = probe_side(j2), probe_side(j3)
    if p2 is None and p3 is None:
        side = 2
        log.append(f'{tag or path}: no probes both sides -> :2: fail-closed')
    elif p3 is None or (p2 is not None and p2 >= p3):
        side = 2
        log.append(f'{tag or path}: p2={p2} p3={p3} -> :2:')
    else:
        side = 3
        log.append(f'{tag or path}: p2={p2} p3={p3} -> :3:')
    data = blob(side, path)
    open(path, 'wb').write(data)
    json.loads(open(path, 'rb').read())
    return side

def resolve_jsonl_union(path):
    a2, a3 = blob(2, path), blob(3, path)
    if a2 is None or a3 is None:
        log.append(f'{path}: no conflict stages present -> SKIP (not conflicted this batch)')
        return None
    # normalize mixed EOLs (producer appends vary CRLF/LF) to LF for split+dedup, exact-line dedup only
    t2 = a2.decode('utf-8').replace('\r\n', '\n')
    t3 = a3.decode('utf-8').replace('\r\n', '\n')
    l2 = [l for l in t2.split('\n') if l.strip()]
    l3 = [l for l in t3.split('\n') if l.strip()]
    set2 = set(l2)
    union = l2 + [l for l in l3 if l not in set2]
    out = '\n'.join(union) + '\n'
    for l in union:
        json.loads(l)  # parse-verify every line
    open(path, 'wb').write(out.encode('utf-8'))
    log.append(f'{path}: line-union |A|={len(l2)} |B|={len(l3)} |A∪B|={len(union)} (r188 zero-loss, EOL normalized LF)')
    return len(union)

def resolve_aa_shards(paths):
    todo = [p for p in paths if blob(2, p) is not None and blob(3, p) is not None]
    if not todo:
        log.append('aa_shards: no conflict stages present -> SKIP (not conflicted this batch)')
        return True
    for p in todo:
        a2, a3 = blob(2, p), blob(3, p)
        j2, j3 = json.loads(a2), json.loads(a3)
        # assert science payload identical (all keys except audit envelope)
        sci2 = {k: v for k, v in j2.items() if k != 'audit'}
        sci3 = {k: v for k, v in j3.items() if k != 'audit'}
        if sci2 != sci3:
            log.append(f'{p}: SCIENCE PAYLOAD DIFFERS -> ABORT this file, manual adjudication needed')
            return False
        open(p, 'wb').write(a2)
        log.append(f'{p}: AA science-payload identical (audit envelope only diff) -> took :2: (origin/pool-flip basis)')
    return True

def main():
    # 1. daily report twin (json decides, md copies same side) - r329
    resolve_twin_side(['docs/daily_report/REPORT-2026-10-01.json', 'docs/daily_report/REPORT-2026-10-01.md'],
                      probe_path_idx=0, tag='daily_report_twin')
    # 2. LIVE family - all 4 from same side
    resolve_twin_side(['docs/live_usage/LIVE-2026-10-01.json', 'docs/live_usage/LIVE-2026-10-01.md',
                       'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'],
                      probe_path_idx=0, tag='live_usage_family')
    # 3. dashboard pair - json decides, js copies same side whole bytes (r209)
    resolve_twin_side(['results/dashboard_status.json', 'results/dashboard_status.js'],
                      probe_path_idx=0, tag='dashboard_pair')
    # 4. snapshots
    resolve_snapshot_ts('results/fundamental_b_layer_filter.json')
    resolve_snapshot_ts('results/scorecard_v1.json')
    resolve_snapshot_ts('results/strategy_scorecard.json')
    resolve_snapshot_ts('results/_attrition_guard_scan.json')  # manual UNKNOWN: rc=0 both, ts probe decides
    # 5. append-log union
    resolve_jsonl_union('results/pool_core_samples.jsonl')
    # 6. AA shards
    shards = [f'results/p2cal_ext/n1_w2/shard-{i}-of-12.json' for i in range(2, 12)]
    ok = resolve_aa_shards(shards)
    print('\n'.join(log))
    return 0 if ok else 2

if __name__ == '__main__':
    sys.exit(main())
