"""r273 bm-b closing writes: heartbeat + state.json + round report line.
Byte-face law: mirror each file's probed faces (BOM/EOL/indent/ensure_ascii/trailing-nl)."""
import json, time, datetime, psutil, io

# ---- probe faces ------------------------------------------------------------
def face(p):
    b = open(p, 'rb').read()
    return {'bom': b[:3] == b'\xef\xbb\xbf', 'crlf': b.count(b'\r\n'),
            'trailing_nl': b.endswith(b'\n'), 'bytes': len(b), 'raw': b}

HB = r'fleet/machines/bm-b.json'
ST = r'logs/iteration-loop/state.json'
RR = r'logs/iteration-loop/round_reports.md'
fh, fs, fr = face(HB), face(ST), face(RR)
for n, f in (('hb', fh), ('state', fs), ('rr', fr)):
    assert not f['bom'], f'{n} BOM violation'
print('faces: hb crlf=%d trail=%s | state crlf=%d trail=%s | rr crlf=%d trail=%s' % (
    fh['crlf'], fh['trailing_nl'], fs['crlf'], fs['trailing_nl'], fr['crlf'], fr['trailing_nl']))

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec='seconds')          # T-separator law (R262)
epoch = int(time.time())                           # JSON int law (R170/R178)

cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
gfree = None
try:
    import pynvml
    pynvml.nvmlInit()
    h = pynvml.nvmlDeviceGetHandleByIndex(0)
    mi = pynvml.nvmlDeviceGetMemoryInfo(h)
    gfree = round((mi.total - mi.used) / 1048576.0, 0)
    pynvml.nvmlShutdown()
except Exception:
    gfree = None

# ---- heartbeat (mirror: indent=1, raw utf-8, no trailing newline) ------------
hb = json.loads(fh['raw'].decode('utf-8'))
hb['last_seen'] = clock
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock
hb['current_task'] = ('r273 done: O-20260926-2000-bm-c migration executor built+DryRun-validated (19/19 task XMLs) '
                      '+ ARMED detached (journal C:\\Users\\Administrator\\fluxgroup-migration-journal.log); '
                      'next round expects NEW ROOT E:\\Fluxgroup\\FluxGroup\\quant\\bigmoney; window <=09-29 12:00')
hb['cpu_util_pct'] = cpu
hb['cpu_pct'] = cpu
hb['round_no'] = 273
hb['free_ram_gb'] = round(vm.available / 1073741824.0, 1)
hb['idle_ram_gb'] = hb['free_ram_gb']
hb['idle_ram_mb'] = int(hb['free_ram_gb'] * 1024)
if gfree is not None:
    hb['gpu_free_vram_gb'] = round(gfree / 1024.0, 1)
    hb['gpu_free_vram_mb'] = int(gfree)
    hb['gpu_idle_vram_gb'] = hb['gpu_free_vram_gb']
    hb['gpu_idle_vram_mb'] = int(gfree)
hb['verdict'] = ('healthy r273: migration executor armed (O-20260926-2000-bm-c six-step, fail-closed gates, '
                 'DryRun 19/19); smoke 25/25; S6 25 legs exit 0; orders 84/84; CODELY recompile r273 49.3KB')
out = json.dumps(hb, ensure_ascii=False, indent=1)
assert out == json.dumps(json.loads(out), ensure_ascii=False, indent=1)
open(HB, 'wb').write(out.encode('utf-8'))          # no trailing newline (mirror)
b2 = open(HB, 'rb').read()
j2 = json.loads(b2.decode('utf-8'))
assert isinstance(j2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in j2['clock_read'], 'clock_read must be T-separated'
print('heartbeat written: epoch int OK, T-sep OK, %d bytes' % len(b2))

# ---- state.json (mirror faces) ------------------------------------------------
st = json.loads(fs['raw'].decode('utf-8'))
st['round_no'] = 273
st['did'] = ('r273: O-20260926-2000-bm-c migration executor (discovery 245-scan 19 hits + robocopy/verify gates + '
             'DryRun 19/19) armed detached + SIBLINGS dual-root probe + CODELY recompile r273 + S6 25 legs exit 0')
st['verdict'] = 'green'
st['next'] = ('r274 EXPECTS NEW ROOT E:\\Fluxgroup\\FluxGroup\\quant\\bigmoney: assemble five receipts (tree snapshot '
              'nine-item table / tasks before-after / per-line ignition / git HEAD / root_path already registered) '
              '+ delete old-root backup after ignition + repair failed redefinitions + user-level memory pointer update')
st['last_round_ts'] = clock
st['last_result'] = 'ok'
out = json.dumps(st, ensure_ascii=False, indent=1)
if fs['crlf'] > 0:
    out = out.replace('\n', '\r\n')           # mirror CRLF face (per-file probe law)
if fs['trailing_nl'] and not out.endswith('\r\n' if fs['crlf'] > 0 else '\n'):
    out += '\r\n' if fs['crlf'] > 0 else '\n'
open(ST, 'wb').write(out.encode('utf-8'))
print('state.json written round_no=273 (crlf_face=%s)' % (fs['crlf'] > 0))

# ---- round report line --------------------------------------------------------
line = (clock + ' | r273 (bm-b) | dept:工程/舰队 | WM-VERDICT: GREEN py_low_board_clear (probe 20:31 py 0.7% '
        'board 0 open / pool 49/49 done / bandit MF_IC parked bm-a-lane; red=false) | did: S0 tick-discard stash-dance '
        '(autofill_state, R252 recipe) + pull (bm-a r267 migration executor family landed); S0.5 orders 84/84 diff empty '
        '(both scans) + DECISIONS.md no new lines (last r239 face) + inbox 0; smoke 25/25; S2 board 28-claimed/0-open '
        '+ post_review latest 0 NO (11 NO all historical re-anchored r270 family); S3 MAIN = O-20260926-2000-bm-c '
        'MIGRATION EXECUTION LEG: canon v2.0 read zero-touch (git show 7d75a7e1, origin/master still v1.0), '
        'discovery scan ALL 245 schtasks XMLs -> 19 tasks reference old roots (3 Bigmoney trio + 16 MiniGame face) '
        'zero variants zero dump-fails (results/_r273bmb_migration_discovery.json), live-code face fixed '
        'monitor/build_status.py _SIBLINGS -> old+new dual-candidate probe (verified 4 lines alive pre-move), '
        'executor results/_r273bmb_fluxgroup_migration.ps1 built per bm-a r267 pattern + bm-b specifics '
        '(robocopy C:->E: cross-volume + HEAD/clean/filecount verify gates + ollama kill + plastic services '
        'stop/restart + HKCU PATH ffmpeg entry repoint + Bee clear + gaming\\MiniGame junction + nine-item skeleton '
        '+ fail-closed: failed-redefinition tasks stay disabled), DryRun self-caught x2 (Join-Path positional-binding '
        'bug inherited verbatim from bm-a line + CJK-in-ANSI regex hazard -> [char]-code fix) then 19/19 pre-validated '
        'exit 0, ignition faces spot-checked (wscript/new-path XMLs); S4 pit-law appended (CODELY 51257B crossed 50KB '
        '-> hot-cold recompile r273 batch: 1 flow line moved, 50456B 49.3KB, multiset/verbatim/face gates PASS); '
        'S6 ~25 legs all exit 0 weekend no-op family (audit FLAG pool_starvation=supply-gap legal idle per O-1137 '
        'adjudication r266/r272; watermark py_low_board_clear; daily 0 rows cutoff 09-24; regime ORANGE shadow; '
        'clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0; scorecard 6/28/7 12.2s; lhb 30min guard; heat '
        'weekend; futures cutoff-covered; options/mf/sina_mf/ths/ah bm-a-lane + fp bm-c-lane honest no-ops; '
        'fundamental 23.4h fresh; blf pass; aggr/alloc/grid marks no-ops; t35 export 09-24; dsc 6 traders; daily '
        'report REPORT-2026-09-26 faces=4 token=1; monitor 432combos/0pass 5/7 milestones; token delta 0 L2 1 '
        'watchdog retro) | evidence: DryRun 19/19 exit 0 journal + discovery JSON + task-status probe txt + '
        'recompile gates PASS + S6 exit codes in transcript + smoke 25/25 | next: r274 EXPECTS NEW ROOT '
        'E:\\Fluxgroup\\FluxGroup\\quant\\bigmoney (armed executor: quiesce->disable 19->rename E:\\Minigame->'
        'E:\\Fluxgroup\\MiniGame->robocopy Bigmoney->verify->skeleton->junction->PATH->Bee->XML apply->re-enable->'
        'receipt marker; journal C:\\Users\\Administrator\\fluxgroup-migration-journal.log): five-receipt assembly + '
        'old-root backup deletion after ignition verified + failed-redef repair via register recipes + user-level '
        'memory pointer updates; HQ ledger flip = group collection face (no local write)')
nl = '\r\n' if fr['crlf'] > 0 else '\n'
with open(RR, 'ab') as f:
    f.write((line + nl).encode('utf-8'))
print('round report line appended (%d chars, nl=%r)' % (len(line), nl))
