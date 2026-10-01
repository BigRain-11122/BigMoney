import json, io, time

# state-bm-a.json: round 547 -> 553 (r548-r552 crash-salvage sessions skipped
# per r529 law; git self-labels confirm r552 = last used number)
st = json.load(io.open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 553
st['did'] = ("r553: P0 engine revival (r552 crash-session left perpetual_faces_n1.py "
             "WAVE_CONFIGS unclosed -> tick chain dead 03:12-03:23; reverted = W43 zero-burn "
             "yield vs bm-c r346 identical bands r530 law) + W44 FREEZE (34th wave, bm-a "
             "9th-owned, A 131_004..133_003 / B 44_201..44_400 both no-skip machine-derived, "
             "ADMIT+banned+selftest green, pushed 45480dea3) + ignition LIVE 7/12 shards")
st['verify'] = ("band gate ADMIT rc0 + banned ADMIT + selftest PASS incl W44 leg + smoke 47/47 "
                "+ S6 full chain rc0 (dualrun streak 23/3) + attrition CLEAN + push 0/0 "
                "+ engine status alive/ignited")
st['next'] = ("W44 burn complete -> finalize one-pass (r538 law, prev=457,140 derive, K proj "
              "94,720); LOWAMP-P3 NULLS at 710/2000 on bm-c (finalize window opens on "
              "completion, E1 already PASS r552)")
st['last_round_at'] = "2026-10-02T03:37:58+08:00"
st['last_round'] = 553
st['last_round_ts'] = "2026-10-02T03:37:58+08:00"
st['current_task'] = "W44 engine burn in flight (7/12 shards), finalize next round"
st['updated'] = "2026-10-02T03:37:58+08:00"
if 'last_round_at' in st:
    st['last_round_at'] = "2026-10-02T03:37:58+08:00"
with io.open('state-bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=2)

# heartbeat fleet/machines/bm-a.json
hb = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
hb['last_seen'] = "2026-10-02T03:37:58+08:00"
hb['current_task'] = ("W44 frozen+ignited (bm-a 9th owned wave, A 131_004..133_003 / "
                      "B 44_201..44_400), engine burning 7/12 shards; P0 syntax revival "
                      "done (r552 crash salvage)")
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = "2026-10-02T03:37:58+08:00"
hb['verdict'] = ("healthy: P0 engine revival (tick chain dead 03:12-03:23 -> revived), "
                 "W44 freeze pushed 45480dea3, smoke 47/47, S6 rc0, ignition LIVE")
hb['round_no'] = 553
with io.open('fleet/machines/bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)

# self-check: epoch must be JSON int
chk = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), "epoch must be int (F7 law)"
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], "clock_read T-format (R262 law)"
st2 = json.load(io.open('state-bm-a.json', encoding='utf-8'))
assert st2['round_no'] == 553
print("state round 553 + heartbeat epoch", chk['heartbeat_epoch_utc'], "int OK, clock T OK")
