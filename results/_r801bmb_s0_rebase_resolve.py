# r801 bm-b S0 rebase conflict resolver (bigmoney-conflict-resolve skill)
# Replay of 54aff4cac (r800) onto origin tip df749d5bb hit 16 UU faces.
# Recipes per classifier: snapshot take-new by deep wall-clock ts probe (probe
# STAGED blobs :2:/:3:, value-shape adjudication only per R350), rolling-ledger
# union zero row loss, twins take SAME side. UNKNOWN file: diagnose only here.
import json, re, subprocess, sys

TS_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def git_bytes(*args):
    r = subprocess.run(['git'] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s rc=%d %s' % (args, r.returncode, r.stderr[:300]))
    return r.stdout

def probe_ts(obj):
    """Deep scan for max wall-clock timestamp (date + time-of-day required, R350)."""
    best = None
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for v in o.values():
                if isinstance(v, str) and TS_RE.match(v):
                    if best is None or v > best:
                        best = v
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return best

def side_json(path, stage):
    return json.loads(git_bytes('show', ':%d:%s' % (stage, path)).decode('utf-8-sig'))

def detect_indent(raw):
    lines = raw.decode('utf-8-sig').splitlines()
    for ln in lines[1:4]:
        if ln.startswith('  ') or ln.startswith('\t'):
            return '\t' if ln[0] == '\t' else 2
    return 2

LEDGER_KEYS = ('history', 'transitions', 'launches', 'records')
TIE_TAKE_STAGE = 2  # same-second tie -> HEAD (ours = origin base in rebase), r140 law

def resolve_snapshot(path, group_probe_paths=None):
    """Whole-doc take-new by max wall-clock ts across probe paths (same side for twins)."""
    probe_paths = group_probe_paths or [path]
    ts = {2: None, 3: None}
    for st in (2, 3):
        cands = []
        for p in probe_paths:
            try:
                cands.append(probe_ts(side_json(p, st)))
            except Exception as e:
                print('  probe fail %s :%d: %s' % (p, st, e))
        cands = [c for c in cands if c]
        ts[st] = max(cands) if cands else None
    if ts[3] and (ts[2] is None or ts[3] > ts[2]):
        take = 3
    elif ts[2] is None and ts[3] is None:
        take = TIE_TAKE_STAGE  # no clock either side -> HEAD tie rule
    else:
        take = 2
    print('%s: ts2=%s ts3=%s -> take :%d:' % (path, ts[2], ts[3], take))
    return take

def resolve_ledger(path):
    a = side_json(path, 2)
    b = side_json(path, 3)
    ta, tb = probe_ts(a), probe_ts(b)
    base_stage = 2 if (ta and (tb is None or ta >= tb)) else 3
    base = a if base_stage == 2 else b
    other = b if base_stage == 2 else a
    out = json.loads(json.dumps(base))  # deep copy
    for key in LEDGER_KEYS:
        la = base.get(key)
        lb = other.get(key)
        if isinstance(la, list) and isinstance(lb, list):
            seen, union = set(), []
            for ent in la + lb:
                sig = json.dumps(ent, sort_keys=True, ensure_ascii=False)
                if sig not in seen:
                    seen.add(sig)
                    union.append(ent)
            def ent_ts(e):
                if isinstance(e, dict):
                    for v in e.values():
                        if isinstance(v, str) and TS_RE.match(v):
                            return v
                return ''
            try:
                union.sort(key=ent_ts)
            except Exception:
                pass
            out[key] = union
            print('%s: %s union |%d|+%d -> %d rows (dedup full-entry)' % (path, key, len(la), len(lb), len(union)))
    print('%s: ledger base :%d: (ta=%s tb=%s)' % (path, base_stage, ta, tb))
    raw2 = git_bytes('show', ':2:%s' % path)
    indent = detect_indent(raw2)
    data = json.dumps(out, indent=indent, ensure_ascii=False).encode('utf-8')
    if raw2.endswith(b'\n') and not data.endswith(b'\n'):
        data += b'\n'
    return data

def main():
    rep = subprocess.run(['git', 'ls-files', '-u'], capture_output=True, text=True).stdout
    uu = set()
    for line in rep.splitlines():
        f = line.split('\t')
        if len(f) == 2:
            uu.add(f[1])
    print('UU set (%d):' % len(uu))
    for p in sorted(uu):
        print('  ' + p)

    report_group = ['docs/daily_report/REPORT-2026-10-07.json', 'docs/daily_report/REPORT-2026-10-07.md']
    live_group = ['docs/live_usage/LIVE-2026-10-07.json', 'docs/live_usage/LIVE-2026-10-07.md',
                  'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md']
    unknown_paths = []
    resolved = []

    for p in sorted(uu):
        if p in report_group:
            take = resolve_snapshot(p, group_probe_paths=['docs/daily_report/REPORT-2026-10-07.json'])
            for q in report_group:
                open(q, 'wb').write(git_bytes('show', ':%d:%s' % (take, q)))
                resolved.append(q)
        elif p in live_group:
            take = resolve_snapshot(p, group_probe_paths=['docs/live_usage/LIVE-2026-10-07.json', 'docs/live_usage/LIVE-latest.json'])
            for q in live_group:
                open(q, 'wb').write(git_bytes('show', ':%d:%s' % (take, q)))
                resolved.append(q)
        elif p in ('results/compute_audit.json', 'results/regime_state.json'):
            data = resolve_ledger(p)
            open(p, 'wb').write(data)
            json.loads(data.decode('utf-8'))  # parse-validate before add (r185)
            resolved.append(p)
        elif p.endswith('.jsonl'):
            # append-log (r188 law): line-level union, order-preserving, zero loss
            a = git_bytes('show', ':2:%s' % p).decode('utf-8-sig').splitlines()
            b = git_bytes('show', ':3:%s' % p).decode('utf-8-sig').splitlines()
            seen, union = set(), []
            for ln in a + b:
                if ln not in seen:
                    seen.add(ln)
                    union.append(ln)
            raw2 = git_bytes('show', ':2:%s' % p)
            nl = b'\r\n' if b'\r\n' in raw2 else b'\n'
            data = nl.join(l.encode('utf-8') for l in union)
            if raw2.endswith((b'\n', b'\r\n')):
                data += nl
            open(p, 'wb').write(data)
            print('%s: append-log union |%d|+%d -> %d lines' % (p, len(a), len(b), len(union)))
            resolved.append(p)
        elif p == 'results/_attrition_guard_scan.json':
            # r801 manual classification (fail-closed discharge): per-run scan verdict
            # snapshot {ts, files, active_loss, rc} regenerated whole per scan ->
            # snapshot take-new by wall-clock ts, tie -> HEAD (:2:), r140 law.
            take = resolve_snapshot(p)
            open(p, 'wb').write(git_bytes('show', ':%d:%s' % (take, p)))
            json.loads(git_bytes('show', ':%d:%s' % (take, p)).decode('utf-8-sig'))
            resolved.append(p)
        else:
            take = resolve_snapshot(p)
            open(p, 'wb').write(git_bytes('show', ':%d:%s' % (take, p)))
            json.loads(git_bytes('show', ':%d:%s' % (take, p)).decode('utf-8-sig'))  # validate chosen side
            resolved.append(p)

    # unknown diagnosis (fail-closed, no write)
    for p in unknown_paths:
        for st in (2, 3):
            try:
                o = side_json(p, st)
                keys = list(o.keys()) if isinstance(o, dict) else type(o).__name__
                lens = {k: len(v) for k, v in o.items() if isinstance(v, (list, dict))} if isinstance(o, dict) else {}
                print('UNKNOWN %s :%d: top_keys=%s lens=%s ts=%s' % (p, st, keys, lens, probe_ts(o)))
            except Exception as e:
                print('UNKNOWN %s :%d: parse fail %s' % (p, st, e))

    seen = sorted(set(resolved))
    if seen:
        r = subprocess.run(['git', 'add'] + seen, capture_output=True)
        print('git add rc=%d paths=%d' % (r.returncode, len(seen)))
        if r.returncode != 0:
            print(r.stderr.decode('utf-8', 'replace')[:500])
    print('REMAINING UU after resolve: re-run ls-files -u to confirm attrition file only')

if __name__ == '__main__':
    main()
