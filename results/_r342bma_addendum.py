# -*- coding: utf-8 -*-
# r342 bm-a addendum: storm-receipt three-face update (valve note per D-20260925-01iii; report/state/heartbeat)
import json, time

now = time.time()
off = time.strftime('%z', time.localtime(now))
clock = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(now)) + off[:3] + ':' + off[3:]

ST, RP, HB = 'state-bm-a.json', 'logs/iteration-loop/round_reports-bm-a.md', 'fleet/machines/bm-a.json'

# state: fold did/next faces updated with final landing receipt
d = json.load(open(ST, encoding='utf-8'))
d['did'] = (d['did'] +
    ' || ADDENDUM in-round storm: push-reject wave-2 (bm-c r94 chain 13-UU same-window S6 family -> resolver2 _r342bma_resolve2.py: '
    '12 faces take-new byte-verbatim by deep-ts probe all mine 18:12-14 > bmc 18:09-10 incl twin REPORT coupling + js-wrapper whole-bytes; '
    'compute_audit union 231/201->232 CRLF mirror-base; regime_state histories-identical take-theirs) -> push-reject wave-3 (bm-b r337 chain) -> '
    'retry exhausted -> ESCAPE VALVE machine/bm-a-r342 pushed per D-20260925-01iii -> immediate fold-landing stop-2 1-UU compute_audit '
    'union 232/232 shared231->233 (bmb 18:07:01 + mine 18:12:25, latest take-mine, LF face mirror base) -> LAND 9c768ee8 -> valve branch '
    'GC-deleted (content-anchor=union asserts)')
d['current_task'] = ('r342 FULLY LANDED origin/main @9c768ee8 (fold-landing through 3-machine storm: stop-1 bmc-r93 + wave-2 bmc-r94 13-UU '
                     '+ wave-3 bmb-r337 valve->re-land); valve branches both GC; T-91 armed Mon 09-28 09:15; W2-A watch ~21:40')
d['last_round_at'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(now))
json.dump(d, open(ST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# round report: append addendum line
rb = open(RP, 'rb').read()
eol = '\r\n' if rb.count(b'\r\n') > (rb.count(b'\n') - rb.count(b'\r\n')) else '\n'
line = (f"{clock} | R342 bm-a ADDENDUM (dept:工程+舰队) | in-round 3-machine push-storm receipts: wave-2 bmc-r94 chain 13-UU resolved "
        f"(_r342bma_resolve2.py: 12 snapshot/twin/js faces take-new byte-verbatim deep-ts 18:12-14>18:09-10, twin REPORT md coupled same-side; "
        f"compute_audit rolling-ledger union 231/201->232 mirror-base CRLF; regime_state 2-row histories identical -> take-theirs whole) | "
        f"wave-3 bmb-r337 chain push-reject -> retry exhausted -> ESCAPE VALVE machine/bm-a-r342 per D-20260925-01iii -> immediate fold-landing "
        f"stop-2 1-UU compute_audit union 232+232 shared231 -> 233 rows (bmb-only 18:07:01 + mine-only 18:12:25; latest take-mine; LF face "
        f"mirror base) -> rebase continue -> PUSH LANDED c64ab6b2..9c768ee8 origin/main -> valve branch GC-deleted content-anchor | verify: "
        f"resolver2 + stop-2 asserts all-PASS (233==|A u B|, staged marker-scan clean, parse-verify) | next: T-91 Mon 09:15 auto-fire; "
        f"W2-A bmb finalize watch ETA 18:40-21:40; next 5x=R345 HANDOVER")
with open(RP, 'ab') as f:
    sep = eol.encode('utf-8') if rb.endswith(b'\n') else b''
    f.write(sep + line.encode('utf-8') + eol.encode('utf-8'))

# heartbeat: current_task + epoch/clock refresh
h = json.load(open(HB, encoding='utf-8'))
h['last_seen'] = clock
h['current_task'] = ('r342 FULLY LANDED @9c768ee8: fold-landing through 3-machine storm (stop-1 bmc-r93 2-UU; wave-2 bmc-r94 13-UU '
                     'resolver2; wave-3 bmb-r337 -> valve machine/bm-a-r342 -> stop-2 1-UU 233-union re-land); valves GC; W2-A watch ~21:40; '
                     'T-91 Mon 09:15')
h['heartbeat_epoch_utc'] = int(now)
h['clock_read'] = clock
h['round_no'] = 342
json.dump(h, open(HB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

v = json.load(open(HB, encoding='utf-8'))
assert isinstance(v['heartbeat_epoch_utc'], int) and 'T' in v['clock_read'] and '+' in v['clock_read']
assert json.load(open(ST, encoding='utf-8'))['round_no'] == 342
print('addendum ok:', clock, 'epoch', v['heartbeat_epoch_utc'])
