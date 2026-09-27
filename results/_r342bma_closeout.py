# -*- coding: utf-8 -*-
# r342 bm-a closeout: state + round report + heartbeat (single-writer faces; epoch JSON int R170/R178)
import json, time, os

ST = 'state-bm-a.json'
RP = 'logs/iteration-loop/round_reports-bm-a.md'
HB = 'fleet/machines/bm-a.json'

now = time.time()
off = time.strftime('%z', time.localtime(now))
clock = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(now)) + off[:3] + ':' + off[3:]

did = ("R342: S0 FOLD-LANDING FIRST-DUTY COMPLETE -- pull--rebase stop-1 2-UU vs bm-c r93 chain resolved via _r342bma_resolve.py "
       "(compute_audit rolling-ledger union base201/ours204/theirs229 -> 230 rows zero-loss: ours-only 17:53:14 bmc-audit + theirs-only 26 "
       "09-26-morning rows + shared-2 content-equal; latest canonical-equal take-ours; CRLF+indent2 face mirror r223/r234; re-sort ts asc "
       "r245) + memory-archive/202609.md append-union both-keep (HEAD=bm-c r93 二十五批 2 lines + mine 二十六批+续 66 lines, second-25th "
       "同象双存 per r85 勘注; content from LF stage blobs not CRLF worktree per r329/r239) -> staged -c core.autocrlf=false (CRLF blob "
       "preserved) -> rebase --continue 2/2 clean -> push 52a26db4..7ff30da4 origin/main LANDED -> machine/bm-a-r341 branch GC-deleted "
       "(content-anchor = resolver zero-loss asserts, r336 GC precedent) + S0.5 orders 96/96 double-scan zero-unacked + decisions "
       "no-new-past-D-10 + smoke 25/25 + S6 29/29 rc=0 Sunday no-op family (moneyflow rank-pass + ah_panel detached refresh spawned "
       "by-design; post-union producer window 230->201 r85 滚动窗截留 survival-check PASS, git-history保全)")
verify = ("resolver all-asserts PASS (rows 230 == |A∪B|, md 1058 lines membership-zero-loss, staged-blob verify CRLF face + "
          "marker-free) + r85 window survival check PASS (30 dropped all older than boundary 09-26 13:33:21) + schtasks both tasks "
          "present + claw CR-normalized byte-match True + heartbeat epoch-int/clock-T self-verified")
nxt = ("(1) T-91 s3 auto-fires Mon 09-28 09:15 first-marks; (2) W2-A bm-b finalize window ~18:10-21:10 watch + UNC follow-up sec.9.3; "
       "(3) bm-b dual-evidence watch continues (git-silent+still-stale -> takeover canon r341 pitlaw); (4) next 5x = R345 HANDOVER "
       "check; (5) 10-01 month-first round trio (science_audit/monthly_briefing/self_review)")

# --- state (full-face rewrite: round_no advances, did/verify/next replaced) ---
json.dump({'round_no': 342, 'did': did, 'verify': verify, 'next': nxt,
           'last_round_at': time.strftime('%Y-%m-%d %H:%M', time.localtime(now)),
           'current_task': 'r342 done: fold-landing landed main + escape branch GC; T-91 armed Mon 09:15; W2-A watch ~21:10'},
          open(ST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- round report line (append-only own file; EOL mirror) ---
rb = open(RP, 'rb').read()
eol = '\r\n' if rb.count(b'\r\n') > (rb.count(b'\n') - rb.count(b'\r\n')) else '\n'
line = (f"{clock} | R342 bm-a (dept:工程+舰队) | WM first-line verdict: green (red=false lane healthy @18:12:31 probe, "
        "py_low_board_clear legal-idle: board 0 open/96 claimed + pool ready=1 CENSUS-FUS-S2-W2A lane_owner=bm-b R31 in-flight "
        "ETA~21:10 + bandit claimed-await-panel; audit v2.3 CLEAN flags=[] @18:12:25) | did: (A) " + did.replace('R342: ', '') +
        " | verify: " + verify + " | next: " + nxt)
with open(RP, 'ab') as f:
    sep = eol.encode('utf-8') if rb.endswith(b'\n') else b''
    f.write(sep + line.encode('utf-8') + eol.encode('utf-8'))

# --- heartbeat (single-writer own file; mirror r335 pattern) ---
d = json.load(open(HB, encoding='utf-8'))
try:
    import psutil
    cpu_pct = psutil.cpu_percent(interval=1)
    free_ram_gb = round(psutil.virtual_memory().available / (1024**3), 2)
except Exception:
    cpu_pct, free_ram_gb = 0.0, 0.0
try:
    import subprocess as sp
    out = sp.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                 capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    gpu_free = round(float(out[0]) / 1024, 2)
except Exception:
    gpu_free = d.get('gpu_free_vram_gb', 0.0)
d['last_seen'] = clock
d['current_task'] = ('r342 done: fold-landing LANDED origin/main (7ff30da4) + escape branch machine/bm-a-r341 GC; '
                     'compute_audit union 230 rows + archive md append-union landed; W2-A watch ~21:10; T-91 Mon 09:15')
d['cpu_pct'] = cpu_pct
d['free_ram_gb'] = free_ram_gb
d['gpu_free_vram_gb'] = gpu_free
d['verdict'] = 'healthy'
d['heartbeat_epoch_utc'] = int(now)
d['clock_read'] = clock
d['round_no'] = 342
d['task'] = 'idle-round-done'
json.dump(d, open(HB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- self-verification (smoke F7 face) ---
v = json.load(open(HB, encoding='utf-8'))
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in v['clock_read'] and '+' in v['clock_read'], 'clock T-sep + offset'
assert json.load(open(ST, encoding='utf-8'))['round_no'] == 342
assert open(RP, 'rb').read().endswith(eol.encode('utf-8'))
print('closeout ok:', clock, '| cpu', cpu_pct, '| ram', free_ram_gb, '| gpu', gpu_free, '| epoch', v['heartbeat_epoch_utc'])
