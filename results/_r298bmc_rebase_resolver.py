# r298-started rebase conflict resolver, continued by r299 (re-runnable per batch)
# Current batch: r296 pick (a29817802) onto origin head -- 2 UU faces:
#   CODELY.md               -> line-union HEAD-block + ours-block (origin canon order first, ours appended)
#   results/x2_watch_log.jsonl -> conflict-region line-union, ts-sorted (ledger tail = latest truth;
#                              dedupe domain = conflict region ONLY per r294; both files pure CRLF per probe)
# Laws: r188 line-union / r140 tie->HEAD / r294 region-only dedupe / r289 CRLF byte fidelity
import json, sys, subprocess

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

def load_lines(path):
    b = open(path, 'rb').read()
    lines = b.split(b'\r\n')
    trailing = lines[-1] == b''
    if trailing:
        lines = lines[:-1]
    return lines, trailing

def save_lines(path, lines, trailing):
    data = b'\r\n'.join(lines)
    if trailing:
        data += b'\r\n'
    open(path, 'wb').write(data)

def parse_conflicts(lines):
    """Return list of (start_idx, head_lines, our_lines, end_idx) 0-based, markers excluded."""
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith(b'<<<<<<<'):
            j_head = i
            k_base = None
            k_sep = None
            k_end = None
            for j in range(i + 1, len(lines)):
                if lines[j].startswith(b'|||||||') and k_base is None:
                    k_base = j
                elif lines[j].rstrip(b'\r') == b'=======' and k_sep is None and k_base is not None:
                    k_sep = j
                elif lines[j].startswith(b'>>>>>>>') and k_sep is not None:
                    k_end = j
                    break
            if k_end is None:
                raise SystemExit(f'malformed conflict block starting line {i+1}')
            head_lines = lines[j_head + 1:k_base]
            our_lines = lines[k_sep + 1:k_end]
            out.append((i, head_lines, our_lines, k_end))
            i = k_end + 1
        else:
            i += 1
    return out

def jsonl_ts(line):
    try:
        return json.loads(line.decode('utf-8')).get('ts', '')
    except Exception:
        return ''

def resolve(path, mode):
    lines, trailing = load_lines(path)
    blocks = parse_conflicts(lines)
    if not blocks:
        print(f'{path}: no conflict markers -> nothing to do')
        return False
    # rebuild from tail to head so indices stay valid
    for (start, head_lines, our_lines, end) in reversed(blocks):
        if mode == 'union':
            merged = head_lines + our_lines
        elif mode == 'union-ts':
            seen = set()
            merged = []
            for ln in head_lines + our_lines:
                if ln not in seen:  # dedupe domain = conflict region only (r294)
                    seen.add(ln)
                    merged.append(ln)
            merged.sort(key=jsonl_ts)  # ledger tail = latest truth
        else:
            raise SystemExit(f'unknown mode {mode}')
        lines[start:end + 1] = merged
    save_lines(path, lines, trailing)
    print(f'{path}: resolved {len(blocks)} block(s), union size={sum(1 for _ in open(path, "rb"))} lines-ish')
    return True

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

AUDIT_KEYS = {'audit', 'elapsed_sec', 'workers', 'machine', 'hostname', 'cpu_parallel', 'generated', 'generated_at', 'ts'}

def strip_audit(obj):
    if isinstance(obj, dict):
        return {k: strip_audit(v) for k, v in obj.items() if k not in AUDIT_KEYS}
    if isinstance(obj, list):
        return [strip_audit(v) for v in obj]
    return obj

def resolve_batch2():
    """r297 pick batch: 7 cells jsonl (set-equal AA) + 3 n1_w2 shards (equal-except-audit AA)
    + attrition scan snapshot (probe-newer UU). All -> take :2: origin canon per r498/r140."""
    import subprocess as sp
    st = sp.run(['git', 'status', '--porcelain=v1'], capture_output=True, text=True, encoding='utf-8').stdout
    conflicted = [ln[3:].strip() for ln in st.splitlines()
                  if ln[:2] in ('UU', 'AA', 'DU', 'UD', 'AU', 'UA', 'DD')]
    if not conflicted:
        print('batch2: no conflicted faces')
        return
    for path in conflicted:
        b2, b3 = blob(2, path), blob(3, path)
        if path.endswith('cells_LA-') or '/cells_LA-' in path:
            l2 = sorted(b2.decode('utf-8').splitlines())
            l3 = sorted(b3.decode('utf-8').splitlines())
            assert l2 == l3, f'{path}: sorted payload NOT equal -- fail-closed, escalate'
            open(path, 'wb').write(b2)
            print(f'{path}: AA set-equal verified ({len(l2)} lines) -> take :2:')
        elif path.endswith('.json') and 'shard-' in path:
            j2, j3 = json.loads(b2), json.loads(b3)
            assert strip_audit(j2) == strip_audit(j3), f'{path}: payload differs beyond audit -- fail-closed'
            open(path, 'wb').write(b2)
            print(f'{path}: AA equal-except-audit verified -> take :2:')
        elif '_attrition_guard_scan' in path:
            j2, j3 = json.loads(b2), json.loads(b3)
            p2, p3 = j2.get('ts', ''), j3.get('ts', '')
            winner = 2 if p2 >= p3 else 3
            open(path, 'wb').write(b2 if winner == 2 else b3)
            print(f'{path}: probe p2={p2} p3={p3} -> take :{winner}:')
        else:
            raise SystemExit(f'UNHANDLED conflict face: {path} -- inspect manually')

def resolve_batch3():
    """autostash pop conflict: results/crash_fuse.json = keyed registry (sigs/cleared dicts).
    Union of keys; common key -> newer last_crash_ts/cleared_ts wins, tie/missing -> HEAD (r140).
    Serialized exactly like Tools/autofill.py _save_fuse: ensure_ascii=False, indent=1, CRLF."""
    import subprocess as sp
    path = 'results/crash_fuse.json'
    def ref_blob(rev, p):
        r = sp.run(['git', 'show', f'{rev}:{p}'], capture_output=True)
        return r.stdout if r.returncode == 0 else None
    b2 = ref_blob('HEAD', path)
    b3 = ref_blob('stash@{0}', path)
    assert b2 is not None and b3 is not None, 'missing blob sides'
    h, s = json.loads(b2), json.loads(b3)
    merged = {}
    stats = {'sigs': [0, 0, 0], 'cleared': [0, 0, 0]}  # [head-only, stash-only, common]
    for section in ('sigs', 'cleared'):
        hd, sd = h.get(section, {}), s.get(section, {})
        out = {}
        for k, v in hd.items():
            out[k] = v
        for k, v in sd.items():
            if k not in out:
                out[k] = v
                stats[section][1] += 1
            else:
                stats[section][2] += 1
                tk = 'last_crash_ts' if section == 'sigs' else 'cleared_ts'
                t2, t3 = out[k].get(tk, ''), v.get(tk, '')
                if t3 and (not t2 or t3 > t2):
                    out[k] = v
        stats[section][0] = len(hd) - stats[section][2]
        merged[section] = out
    data = json.dumps(merged, ensure_ascii=False, indent=1).replace('\n', '\r\n')
    open(path, 'wb').write(data.encode('utf-8'))
    print(f'{path}: keyed-union sigs={stats["sigs"]} cleared={stats["cleared"]} '
          f'-> merged sigs={len(merged["sigs"])} cleared={len(merged["cleared"])}')
    # byte-fidelity assert vs HEAD for shared keys would be noisy; sanity: valid json + no markers
    json.loads(open(path, 'rb').read().decode('utf-8'))
    assert b'<<<<<<<' not in open(path, 'rb').read()
    print('ASSERT PASS: crash_fuse.json merged, valid, marker-free')

def resolve_batch4():
    """r299 pick replay onto newer origin: crash_fuse.json UU from stages :2: (origin) / :3: (ours).
    Same keyed-union law as batch3 (per-key newer last_crash_ts/cleared_ts, tie->origin)."""
    b2, b3 = blob(2, 'results/crash_fuse.json'), blob(3, 'results/crash_fuse.json')
    assert b2 is not None and b3 is not None, 'missing stage sides'
    h, s = json.loads(b2), json.loads(b3)
    merged = {}
    stats = {'sigs': [0, 0, 0], 'cleared': [0, 0, 0]}  # [origin-only, ours-only, common]
    for section in ('sigs', 'cleared'):
        hd, sd = h.get(section, {}), s.get(section, {})
        out = {}
        for k, v in hd.items():
            out[k] = v
        for k, v in sd.items():
            if k not in out:
                out[k] = v
                stats[section][1] += 1
            else:
                stats[section][2] += 1
                tk = 'last_crash_ts' if section == 'sigs' else 'cleared_ts'
                t2, t3 = out[k].get(tk, ''), v.get(tk, '')
                if t3 and (not t2 or t3 > t2):
                    out[k] = v
        stats[section][0] = len(hd) - stats[section][2]
        merged[section] = out
    data = json.dumps(merged, ensure_ascii=False, indent=1).replace('\n', '\r\n')
    open('results/crash_fuse.json', 'wb').write(data.encode('utf-8'))
    print(f'crash_fuse.json: keyed-union sigs={stats["sigs"]} cleared={stats["cleared"]} '
          f'-> merged sigs={len(merged["sigs"])} cleared={len(merged["cleared"])}')
    json.loads(open('results/crash_fuse.json', 'rb').read().decode('utf-8'))
    assert b'<<<<<<<' not in open('results/crash_fuse.json', 'rb').read()
    print('ASSERT PASS: crash_fuse.json merged, valid, marker-free')

if __name__ == '__main__':
    import os
    os.chdir(ROOT)
    if '--batch4' in sys.argv:
        resolve_batch4()
        sys.exit(0)
    if '--batch3' in sys.argv:
        resolve_batch3()
        sys.exit(0)
    if '--batch2' in sys.argv:
        resolve_batch2()
        sys.exit(0)
    jobs = [
        ('CODELY.md', 'union'),
        ('results/x2_watch_log.jsonl', 'union-ts'),
    ]
    for path, mode in jobs:
        resolve(path, mode)
    # post-assert: no markers remain, line counts sane
    for path, _ in jobs:
        b = open(path, 'rb').read()
        for m in (b'<<<<<<<', b'>>>>>>>', b'|||||||'):
            if m in b:
                raise SystemExit(f'ASSERT FAIL: {m} still in {path}')
    print('ASSERT PASS: no conflict markers remain')
