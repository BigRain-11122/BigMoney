# r91 bm-c S7 writebacks: round report append + state bump + heartbeat (r338bma pattern, EOL-preserved)
import json, time, io

now = time.strftime('%Y-%m-%dT%H:%M:%S') + time.strftime('%z')
iso = now[:-2] + ':' + now[-2:]

LINE = (
    "2026-09-27T17:15:xx+08:00｜R91 bm-c (dept:engineering+fleet)｜WM verdict: green (red=false; probe 17:10:49 py 0.6% legal-idle whitelist: "
    "board 0 open 30 all-claimed + bandit next_pick=claimed moneyflow-IC panel-wait + pool ready=0 supply-gap r90-disclosed no bm-c-claimable lane; "
    "audit v2.3 rc=0)｜did: (A) S0 stash-pop UU rescue on shared autofill ledger: stash-for-pull -> pop vs bm-a-r338 newer ledger = UU -> "
    "v1 blind-add marked worktree destroyed :2:/:3: stage blobs -> v2 dual-source canon (git show HEAD:+stash@{0}: sides -> whole-entry canonical-json "
    "dedup 48+48=50 distinct -> ts sort -> cap48 -> last_tick take-new 17:00->17:10) JSON-validated staged; tick 17:10:01 keepalive appended atop "
    "clean union (MM healthy; no tick commit = pool empty no-launch) + leftover r86-s7 stash (stale last_tick 15:10 two-line delta) content-verified "
    "DROPPED + S0.5 orders 96/96 zero-unacked (round-start) + decisions: no new rows past D-20260927-10 (r90-receipted D-06..10; BigMoney-face D-04 "
    "self-correction maintained + D-09 closed-by-r84 in-tree verified) + S1 smoke 25/25 + S2 board 0 open 30 all-claimed job_list empty + post_review "
    "REPORT-20260927 ✗0. (B) S6 33/33 rc=0 (_r91bmc_s6_chain.ps1 r89-lineage header-only delta; Sunday statutory no-op family + honest lane guards "
    "this=bm-c: repo/options/moneyflow/sina_mf/ths/ah/system_v1(bm-a) astock/sigexp/alloc(bm-b) fund_premium(weekend Mon-15:30); live legs green: "
    "regime ORANGE breadth-0.77 trigger shadow / clock CALL-2026-09-24 idempotent / fundamental 7.7h fresh skip / live.paper OK / t35v PASS zero-pending "
    "6 / t24 22/22 drift0 / promo 0/22 honest NOT-ELIGIBLE / aggr+grid idempotent at cutoff 09-24 / t35 export 09-24 / scorecard 6+28+7 cards / "
    "daily_report faces=4 token=1 / build_status 432combos 0pass 6 traders 5/7 milestones / token L2 1 leg). (C) S4 pitlaw r91 (S0 stash-pop shared-ledger "
    "UU dual-source union law: HEAD+stash sides not stage-blobs / resolve-before-add vs :X0:02 tick hazard / PS 'stash@{0}' single-quote) + 22nd-batch "
    "in-window archival (r338bma shared-JSON writer-format full 790B verbatim -> archive 二十二批节 + pointer line; CODELY 9962B<10KB hard line; "
    "zero-loss asserts x4 pass). (D) S7 checks: schtasks IterationLoop Running(this session)/Watchdog Ready 17:40 + precommit claw PRESENT+identical "
    "+ inbox zero-pending + S7 orders rescan 96/96 NONE unacked + stash list zero｜next: (1) Mon 09-28: T-91 s3 first-marks auto-fire 09:15 (bm-a lane) "
    "+ 15:30 fund_premium snapshot self-heal (bm-c lane) + new-bar full chain; (2) C-01 council window 09-29 12:00 seat-3 issued F-02; (3) r72/r84 "
    "stale-branch dedicated verify+GC (r90-deferred); (4) 10-01 month trio standing; (5) r95 5x HANDOVER check｜evidence: results/_r91bmc_resolve_autofill.py"
    "+_r91bmc_codeley_archive.py+_r91bmc_s7.py+_r91bmc_s6_chain.ps1 + smoke 25/25 + S6 33/33 rc=0 + CODELY 9962B + archive +985B [via bm-c]\n"
)
LINE = LINE.replace('17:15:xx', iso[11:19], 1)

def append_line(path, line):
    raw = open(path, 'rb').read()
    eol = '\r\n' if raw.count(b'\r\n') > 0 else '\n'
    seg = eol if raw.endswith(eol.encode()) or raw.endswith(b'\n') or raw.endswith(b'\r') else eol
    with io.open(path, 'a', encoding='utf-8', newline='') as f:
        f.write(line if line.endswith('\n') else line + eol)
    print('appended report line, eol=', repr(eol))

append_line('logs/iteration-loop/round_reports-bm-c.md', LINE)

# --- state-bm-c.json: round_no 90 -> 91 ---
sp = 'state-bm-c.json'
st_raw = open(sp, 'rb').read()
eol = '\r\n' if st_raw.count(b'\r\n') > 0 else '\n'
st = json.loads(st_raw.decode('utf-8'))
assert st['round_no'] == 90, f"unexpected round_no {st['round_no']}"
st['round_no'] = 91
st['updated'] = iso[:16]
st['note'] = ('r91: S0 stash-pop UU resolved dual-source union (_r91bmc_resolve_autofill v2: HEAD+stash sides, 48+48=50->cap48, last_tick 17:10) '
              '+ leftover r86 stash dropped + orders 96/96 double-scan + decisions no-new-past-D-10 (D-04/D-09 maintained) + smoke 25/25 + S6 33/33 '
              'Sunday no-op family + CODELY pitlaw r91 + 22nd-batch archival 9962B<10KB + next: (1) Mon 09-28 09:15 T-91 s3 auto-fire watch; '
              '(2) Mon 15:30 fund_premium self-heal bm-c lane; (3) C-01 window 09-29 12:00; (4) r72/r84 dedicated verify+GC; (5) 10-01 month trio')
st['last_round_ts'] = iso
s = json.dumps(st, ensure_ascii=False, indent=1)
tail = eol if st_raw.endswith((b'\n', b'\r')) else ''
out = (s.replace('\n', eol) + tail).encode('utf-8') if eol == '\r\n' else (s + tail).encode('utf-8')
open(sp, 'wb').write(out)
print('state round_no ->', json.load(open(sp, encoding='utf-8'))['round_no'])

# --- heartbeat fleet/machines/bm-c.json ---
hp = 'fleet/machines/bm-c.json'
h_raw = open(hp, 'rb').read()
heol = '\r\n' if h_raw.count(b'\r\n') > 0 else '\n'
h = json.loads(h_raw.decode('utf-8'))
h['last_seen'] = iso
h['current_task'] = ('R91 done: S0 stash-pop dual-source union resolve + S6 33/33 + 22nd-batch archival; next=Mon 09-28 T-91 s3 watch 09:15 '
                     '+ fund_premium self-heal 15:30 (bm-c lane) + C-01 window 09-29')
h['cpu_util_pct'] = 16.0
h['free_ram_gb'] = 4.8
h['gpu_free_vram_mb'] = 8174
h['cpu_pct'] = 0.6
h['verdict'] = ('legal idle: board 30 all-claimed 0 open, wm green red=false, pool 0-ready supply-gap disclosed r90 (no bm-c-claimable lane); '
                'r91=S0-union-resolve+S6 33/33+CODELY 22nd-batch archival all green')
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = iso
assert isinstance(h['heartbeat_epoch_utc'], int) and 'T' in h['clock_read']
s = json.dumps(h, ensure_ascii=False, indent=1)
tail = heol if h_raw.endswith((b'\n', b'\r')) else ''
out = (s.replace('\n', heol) + tail).encode('utf-8') if heol == '\r\n' else (s + tail).encode('utf-8')
open(hp, 'wb').write(out)
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int) and 'T' in h2['clock_read']
print('heartbeat: epoch', h2['heartbeat_epoch_utc'], 'clock', h2['clock_read'])
