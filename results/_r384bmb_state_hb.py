# r384 bm-b: state.json + heartbeat update (byte-style preserving per r381 pit-law)
import json, time, datetime

# ---- state.json (CRLF, no trailing newline, indent=1) ----
p = 'state.json'
raw = open(p, 'rb').read()
st = json.loads(raw.decode('utf-8'))
st['round_no'] = 384
st['note'] = ("r384: maintenance+witness round (S6 31 legs rc=0, bm-a hb stale 185-187min -> stale-takeover "
              "derives x7 lawful O-2100 s2.4; census W2B 89% i=4999/5620 final-stretch no-kill; W4-SCREEN ready "
              "flipped by bm-c r164, burn=autofill next tick; judge family W1/W2/W3+MASS x4+V2-P1 all RAM r354 "
              "gated lawful; W5 stays parked funnel full; RAM 3-sample [0.98,2.6,1.64]GB all<4GB)")
out = json.dumps(st, ensure_ascii=False, indent=1).replace('\n', '\r\n')
open(p, 'wb').write(out.encode('utf-8'))

# ---- heartbeat fleet/machines/bm-b.json (LF, no trailing newline, indent=1) ----
p = 'fleet/machines/bm-b.json'
raw = open(p, 'rb').read()
hb = json.loads(raw.decode('utf-8'))
now = datetime.datetime.now().astimezone()
epoch = int(time.time())
hb['last_seen'] = now.isoformat()
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now.isoformat()
hb['current_task'] = ("r384 done: maintenance+witness (S6 31 legs rc=0 incl bm-a-stale takeover derives x7; "
                      "census W2B 89% i=4999/5620 ETA ~13:40-14:00; W4-SCREEN ready, burn=autofill next tick "
                      "bm-c headroom) -> next: census finalize done-flip -> RAM>=4GB 3-sample window -> "
                      "W1/W2/W3+MASS x4 judge flips (bm-b executor) -> burns -> finalize x5 -> W2/W3 intake; "
                      "15:30 new-bar window local dual lanes; CEO 48h report 09-29 22:45")
hb['free_ram_gb'] = 2.27
hb['gpu_free_vram_gb'] = 6.75
hb['cpu_util_pct'] = 31.6
hb['round_no'] = 384
hb['verdict'] = ("healthy: smoke 25/25, orders 99/99 dual-scan clean, S6 31 legs rc=0 (bm-a hb stale 185-187min "
                 "-> stale-takeover derives x7 lawful O-2100 s2.4 zero science drift, bm-a rewrites on revival); "
                 "census W2B 89% (i=4999/5620) final-stretch no-kill; W4-SCREEN ready (bm-c r164 flip, "
                 "burn=autofill next tick); judge family W1/W2/W3+MASS x4+V2-P1 all RAM r354 gated lawful "
                 "serialization; W5 stays parked (judge funnel headroom unchanged); board 0 open; post_review "
                 "0 latest-NO; RAM 3-sample [0.98,2.6,1.64]GB <4GB gate closed")
# derived/mirror fields kept consistent with historical names
hb['cores'] = 16
hb['idle_ram_gb'] = 2.27
hb['idle_ram_mb'] = 2324
hb['free_ram_mb'] = 2324
hb['gpu_free_vram_mb'] = 6912
hb['gpu_idle_vram_mb'] = 6912
hb['gpu_idle_vram_gb'] = 6.75
hb['cpu_pct'] = 31.6
hb['round'] = 384
hb['loop_round'] = 384
out = json.dumps(hb, ensure_ascii=False, indent=1)
open(p, 'wb').write(out.encode('utf-8'))

# post-verify: json round-trip + epoch int + clock T-sep
hb2 = json.loads(open(p, 'rb').read().decode('utf-8'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in hb2['clock_read'] and hb2['clock_read'].endswith('+08:00'), 'clock T-sep'
st2 = json.loads(open('state.json', 'rb').read().decode('utf-8'))
assert st2['round_no'] == 384
b_hb = open(p, 'rb').read(); b_st = open('state.json', 'rb').read()
assert b_hb.count(b'\r\n') == 0 and not b_hb.endswith(b'\n'), 'hb byte style'
assert b_st.count(b'\n') == b_st.count(b'\r\n') and not b_st.endswith(b'\n'), 'state byte style'
print('OK state=384 hb epoch=%d clock=%s styles preserved' % (hb2['heartbeat_epoch_utc'], hb2['clock_read']))
