# -*- coding: utf-8 -*-
# r595 bm-b S0 surgery: unwind unpushed r594 commit (accidental deletions of bm-a estate),
# restore deletions, take origin-canonical for non-owned faces, pure-FF realign, rebase-free.
# Laws applied: r589 (unwind-FF-recommit loop), r585 (per-face checkout), r593 (execution-time rev-parse),
# r380 (porcelain per-line parse), r580 (python subprocess argv), r570 (jsonl dict-gate union), r381 (twin-yield origin-verbatim).
import subprocess, sys, io

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r

def die(msg):
    print("ABORT:", msg); sys.exit(1)

# 0) sanity: HEAD must be 3000e02a0 (parent of the unwound commit)
r = run(['git', 'rev-parse', 'HEAD'])
head = r.stdout.strip()
if not head.startswith('3000e02a0'):
    die('HEAD is %s, expected 3000e02a0 (reset already applied?)' % head)
print('step0 HEAD ok:', head)

# 1) restore the 9 accidentally-deleted bm-a estate files from index (=3000e02a0 versions)
RESTORE9 = [
 'results/_r592bma_s6_stderr.txt', 'results/_r592bma_s6_stdout.txt',
 'results/_r592bma_takeorigin.txt', 'results/_r592bma_w114_anchor.py',
 'results/_r592bma_w114_band_gate.py', 'results/_r592bma_w114_freeze_edits.py',
 'results/_r592bma_w114_prereg_gen.py', 'results/_r592bma_w114_probe.py',
 'results/_r593bma_s6_chain.py']
r = run(['git', 'checkout', '--'] + RESTORE9)
if r.returncode != 0: die('restore9 failed rc=%s %s' % (r.returncode, r.stderr))
print('step1 restored 9 bm-a estate files from index')

# 2) fresh fetch + execution-time target
r = run(['git', 'fetch', 'origin'])
if r.returncode != 0: die('fetch failed rc=%s %s' % (r.returncode, r.stderr))
r = run(['git', 'rev-parse', 'origin/main'])
TARGET = r.stdout.strip()
if len(TARGET) != 40: die('bad target sha %r' % TARGET)
print('step2 execution-time origin/main =', TARGET)

# 3) shared append-only jsonl faces: relation probe before overwrite (r570 dict-gate union for shared,
#    origin-verbatim for other-machine-owned evidence per r381 twin-yield)
def probe_jsonl(path, union_if_local_dict_extra):
    r = run(['git', 'show', 'origin/main:%s' % path])
    if r.returncode != 0:
        print('  jsonl probe %s: not in origin tree (leave local as-is)' % path); return
    origin_bytes = r.stdout.encode('utf-8', 'surrogateescape')
    try:
        with open(path, 'rb') as f: local_bytes = f.read()
    except FileNotFoundError:
        print('  jsonl probe %s: not on local disk' % path); return
    origin_lines = [l for l in origin_bytes.decode('utf-8', 'replace').split('\n') if l.strip()]
    local_lines = [l for l in local_bytes.decode('utf-8', 'replace').split('\n') if l.strip()]
    import json
    local_only = [l for l in local_lines if l not in origin_lines]
    dict_extra = []
    for l in local_only:
        try:
            if isinstance(json.loads(l), dict): dict_extra.append(l)
        except Exception:
            pass
    print('  jsonl %s: origin=%d lines local=%d lines local_only=%d (dict-gated=%d)' % (path, len(origin_lines), len(local_lines), len(local_only), len(dict_extra)))
    if union_if_local_dict_extra and dict_extra:
        merged = origin_lines + dict_extra
        eol = '\r\n' if b'\r\n' in origin_bytes else '\n'
        data = eol.join(merged) + eol
        with open(path, 'wb') as f: f.write(data.encode('utf-8'))
        print('  -> union written: origin verbatim + %d local dict lines' % len(dict_extra))
    else:
        with open(path, 'wb') as f: f.write(origin_bytes)
        print('  -> origin verbatim (local extras discarded: %d non-dict or owned-elsewhere)' % len(local_only))

print('step3 jsonl faces:')
probe_jsonl('results/x2_watch_log.jsonl', True)          # shared face -> dict-gate union
probe_jsonl('results/pool_dualrun.bm-a.jsonl', False)    # bm-a-owned evidence -> origin verbatim (r381)

# 4) per-face checkout: KEEP whitelist = bm-b-owned + r594 product faces; ALL other tracked M faces take origin
KEEP = set([
 'scripts/daily_report.py',
 'docs/daily_report/REPORT-2026-10-02.json',
 'docs/daily_report/REPORT-2026-10-02.md',
 'logs/iteration-loop/round_reports.md',
 'state.json',
 'results/_r594bmb_integrate.py', 'results/_r594bmb_rr_tail.txt',
 'results/_r594bmb_s6_extract.txt', 'results/_r594bmb_s6_runner.ps1',
 'results/_r594bmb_wrap.py', 'results/_r594bmb_pit.py', 'results/_r594bmb_pushfix.py',
 'results/pool_dualrun.bm-b.jsonl',
 'results/token_usage.bm-b.json', 'results/update_status.bm-b.json',
 'results/lhb_update_status.bm-b.json', 'results/futures_update_status.bm-b.json',
 'results/autofill_state.bm-b.json', 'results/compute_audit.bm-b.json',
 'results/regime_state.bm-b.json',
 'results/saturation_engine/face_bm-b.json', 'results/saturation_engine/history_bm-b.jsonl',
 'results/saturation_engine/state_bm-b.json',
 'results/astock_daily_update_status.json', 'results/etf_daily_pull_status.json',
 'results/p1d_gates.json',
])

# 5) pure-FF realign: CAS update-ref (old = current HEAD) + reset --mixed at TARGET (r593/r578 laws)
r = run(['git', 'update-ref', 'refs/heads/main', TARGET, head])
if r.returncode != 0: die('update-ref CAS failed rc=%s %s' % (r.returncode, r.stderr))
r = run(['git', 'reset', '--mixed', TARGET])
if r.returncode != 0: die('reset --mixed failed rc=%s %s' % (r.returncode, r.stderr))
print('step5 FF realigned main ->', TARGET)

# 6) status-driven worktree sync: D faces (origin files missing on disk) -> checkout; M faces not in KEEP -> checkout origin
r = run(['git', 'status', '--porcelain'])
if r.returncode != 0: die('status failed')
lines = r.stdout.split('\n')
d_paths, m_foreign, m_keep = [], [], []
for ln in lines:
    if not ln.strip(): continue
    if len(ln) < 4: continue
    xy, path = ln[:2], ln[3:]
    if xy == ' D' or xy == 'D ':
        d_paths.append(path)
    elif xy == ' M' or xy == 'M ':
        (m_keep if path in KEEP else m_foreign).append(path)
if d_paths:
    for p in d_paths: print('  D-face restore:', p)
    r = run(['git', 'checkout', '--'] + d_paths)
    if r.returncode != 0: die('checkout D faces failed rc=%s %s' % (r.returncode, r.stderr))
if m_foreign:
    print('step6 foreign M faces -> take origin (%d):' % len(m_foreign))
    for p in m_foreign: print('   ', p)
    r = run(['git', 'checkout', '--'] + m_foreign)
    if r.returncode != 0: die('checkout foreign M failed rc=%s %s' % (r.returncode, r.stderr))
print('step6 KEEP faces left dirty (%d):' % len(m_keep))
for p in sorted(m_keep): print('   ', p)

# 7) final verification: no deletions remain anywhere
r = run(['git', 'status', '--porcelain'])
final = [l for l in r.stdout.split('\n') if l.strip()]
bad = [l for l in final if l.startswith(' D') or l.startswith('D ') or l.startswith('DD') or l.startswith('AD')]
print('step7 final status lines=%d deletions=%d' % (len(final), len(bad)))
for b in bad: print('  STILL-D:', b)
if bad: die('deletions remain')
print('SURGERY OK: tree now = origin + bm-b payload only, zero deletions')
