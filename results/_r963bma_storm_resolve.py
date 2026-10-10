import subprocess, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GIT = r"C:\Program Files\Git\cmd\git.exe"

def blob(rev):
    r = subprocess.run([GIT, 'show', rev], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace')

uu = subprocess.run([GIT, 'diff', '--name-only', '--diff-filter=U'],
                    capture_output=True, text=True).stdout.split()
print("UU files:", len(uu))

THEIRS = {  # bm-b-owned lane faces (R31 owner-side) + bm-b legacy report
    'fleet/machines/bm-b.json', 'logs/iteration-loop/round_reports.md',
    'results/autofill_state.bm-b.json', 'results/compute_audit.bm-b.json',
    'results/astock_daily_update_status.json', 'results/etf_daily_pull_status.json',
    'results/futures_update_status.bm-b.json', 'results/idle_trigger_state.bm-b.json',
    'results/lhb_update_status.bm-b.json', 'results/regime_state.bm-b.json',
    'results/saturation_engine/face_bm-b.json', 'results/saturation_engine/state_bm-b.json',
    'results/saturation_engine/history_bm-b.jsonl', 'results/token_usage.bm-b.json',
    'results/update_status.bm-b.json', 'state.json',
}
JSONL_UNION = {  # append-only lanes: union dedup
    'results/post_review.jsonl', 'results/pool_dualrun.bm-b.jsonl',
    'results/saturation_engine/history_bm-b.jsonl',
}
TS_KEYS = ('ts', 'updated_at', 'generated_at', 'last_run', 'asof', 'now')

resolved = 0
for f in uu:
    if f in THEIRS:
        content = blob(':3:' + f)
        mode = 'theirs'
    elif f in JSONL_UNION:
        ours = [l for l in blob(':2:' + f).splitlines() if l.strip()]
        theirs = [l for l in blob(':3:' + f).splitlines() if l.strip()]
        seen, out = set(), []
        for l in ours + theirs:
            if l not in seen:
                seen.add(l); out.append(l)
        content = '\n'.join(out) + '\n'
        mode = f'union({len(ours)}+{len(theirs)}->{len(out)})'
    else:
        # JSON snapshot: newer top-level ts wins; unparseable/failure -> theirs
        try:
            o = json.loads(blob(':2:' + f))
            t = json.loads(blob(':3:' + f))
            ot = next((o[k] for k in TS_KEYS if isinstance(o, dict) and o.get(k)), '')
            tt = next((t[k] for k in TS_KEYS if isinstance(t, dict) and t.get(k)), '')
            if str(tt) >= str(ot):
                content, mode = blob(':3:' + f), f'newer-theirs({ot} vs {tt})'
            else:
                content, mode = blob(':2:' + f), f'newer-ours({ot} vs {tt})'
        except Exception as e:
            content, mode = blob(':3:' + f), f'theirs-fallback({e.__class__.__name__})'
    with open(f, 'w', encoding='utf-8', newline='') as fh:
        fh.write(content)
    r = subprocess.run([GIT, 'add', '--', f], capture_output=True)
    resolved += 1
    print(f"  {f}: {mode}")
print("resolved:", resolved)
