import json, time

# --- state-bm-a.json: round 605
st = json.load(open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 605
st['did'] = ("T-151 N4-B1 DELIVERABLE (5) COMPLETE + FINALIZE FACE SAME-ROUND: "
            "SatEngine FAMILIES adapter (n4 WAVE_CONFIGS/_set_wave/_shard_valid "
            "+ --shard CLI shim; engine N4 row nshards=6 default_wave=B1 "
            "per-family threading) -> wave burned 6/6 via engine ticks 03:35->03:47 "
            "(1200 universe rows, 6/6 receipts k=200/200, ledger 6 rows face=N4) "
            "-> finalize face (prereg sec.4 three products via science_gates "
            "verbatim) landed n4_b1_results.json 3.8s; prereg sec.6 backfilled")
st['verify'] = ("smoke 47/47 (pre+post-edit); n4 selftest 16/16; engine selftest "
                "10 legs incl real-N4 registration; S6 33 legs rc0 (dualrun first "
                "per law); attrition CLEAN; orders 150/150 double-scan 0 unacked")
st['next'] = ("T-151 chain (1)-(5) ALL CLOSED; next faces = fleet-queue demand: "
              "N4-B2 tail-ritual band extension (own-band advance + disjoint "
              "re-scan) / per-member face deepening; FUND-VALUE-P1 pool tail "
              "VALUEPB-X2+NULLS ready unowned (autofill lane drains)")
st['last_round_at'] = "2026-10-03 03:47"
st['current_task'] = ("T-151 N4-B1: DELIVERABLE (5) + FINALIZE FACE COMPLETE r605 "
                      "(wave 6/6 burned same round + sec.4 confidence faces + sec.6 "
                      "backfill); ticket chain (1)-(5) all closed; next = "
                      "fleet-queue-demand faces only")
st['updated'] = "2026-10-03 03:47"
st['last_round'] = 605
st['last_round_ts'] = "2026-10-03 03:22"
json.dump(st, open('state-bm-a.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# --- heartbeat: fleet/machines/bm-a.json
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
hb['last_seen'] = "2026-10-03T03:47:00+08:00"
hb['heartbeat_epoch_utc'] = int(time.time())          # JSON int (smoke F7 law)
hb['clock_read'] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
hb['current_task'] = "T-151 N4-B1 wave 6/6 burned + finalize face (closed r605)"
hb['verdict'] = ("product round: N4-B1 first wave burned end-to-end via SatEngine "
                 "FAMILIES adapter + sec.4 confidence faces delivered; engine "
                 "queue empty (N4 wave complete), pool tail autofill lane")
hb['cpu_cores'] = 32
hb['idle_ram_gb'] = 52
hb['idle_gpu_vram_gb'] = None
json.dump(hb, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
# post-verify: epoch must be JSON int (R170/R178 law)
chk = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('state round 605 + heartbeat ok; epoch int:', chk['heartbeat_epoch_utc'],
      'clock:', chk['clock_read'])
