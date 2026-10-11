import json, time

TS = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- state.json (bm-b legacy name per fleet README S5) ----------
sp = "state.json"
s = json.load(open(sp, encoding="utf-8"))
s["round"] = 877
s["round_no"] = 878
s["round_no_label"] = "r877"
s["last_round_at"] = TS
s["last_round_ts"] = TS
s["last_seen"] = TS
s["ts"] = TS
s["updated"] = TS
s["updated_at"] = TS
s["clock_read"] = TS
s["current_task"] = ("r878 E16 leg-2: alphagen RG census prereg draft (PREREG_TEMPLATE: alpha-mechanism "
                     "4-choose-1 + D6>=0.7 reject + exit-axis explicit + consumer_plan=SLOT/core48 "
                     "time-series gate route) -> freeze -> runner (12-shard pool batch, roster facts "
                     "from results/alphagen_rg/e16_roster.json) -> pool entry submit (supply floor 0->1) "
                     "-> autofill claim+burn (O-20261011-0012 sec.4 CPU fill)")
s["task"] = s["current_task"]
s["now_active"] = ("r877 closeout+: E16 leg-1 roster probe landed (panel rebuild unlocked slice-2), "
                   "E16 row registered (T-18 CLEAR + T-19 rc0), E15 queue row flipped done (r876 miss "
                   "backfill); supply floor 0 (entry consumed r876) -> leg-2 next")
s["did"] = ("r877 E16 leg-1 + queue bookkeeping: alphagen slice-2 random-grammar census roster probe "
            "(scripts/alphagen_rg_roster.py selftest 15/15 + results/alphagen_rg/e16_roster.json: "
            "substrate gate 158/9/29/4, panel disk truth 5219 files all cutoff 2026-10-09, universe "
            "join 3517, naive burn est 56.6min singlethread = pool 12-shard scale, d1 space 1160, "
            "K=120+80 depth mix + 200 permutation nulls pinned proposals) + E16 registered in "
            "explore.md (T-18 CLEAR + T-19 seed gate hits=[]) + E15 row flipped done (r876 burn "
            "closeout, retroactive bookkeeping note) + smoke 49/49 + S6 40 rc0 + alloc_paper rc=2 "
            "(T-184 dep, same face as r876) + satengine alive idle (W207 finalized r857; W210=b seat "
            "probe landed, freeze anchor=W209 finalize bm-c pending) + T-184 branch still not on origin "
            "(deadline 2026-10-12 15:30 receiver watch)")
s["last_action"] = s["did"]
s["last_action_at"] = TS
s["latest_artifact"] = ("r877: scripts/alphagen_rg_roster.py + results/alphagen_rg/e16_roster.json "
                        "(E16 leg-1 roster face) + explore.md E16 row + E15 flip")
s["next"] = s["current_task"] + (" -> T-184 transfer receiver leg watch (deadline 2026-10-12 15:30, "
                                 "bm-a push pending) -> W210 freeze anchor watch (W209 finalize, bm-c "
                                 "side) -> E15 s4 intake month-boundary face (2026-11-01) -> 48h CEO "
                                 "report due 2026-10-13 11:2x")
s["next_milestone"] = ("E16 leg-2 prereg+pool entry r878 (supply floor 0->1, >=3 by <=2026-10-13); "
                       "T-184 510880 restore before 2026-10-12 15:30 (bm-a push pending)")
s["orphan_face"] = 0
s["orphan_faces"] = 0
s["orphan_face_note"] = "r877 round probe: py_faces=11 alive, orphans=0"
s["verdict"] = ("GREEN: r877 E16 leg-1 COMPLETE (roster probe 15/15 + E16 registered dual-gate rc0 + "
                "E15 flip backfill); smoke 49/49; S6 40 rc0 + alloc_paper rc=2 T-184 dep honest "
                "(same face r876); WM red face = stale pre-flip series + empty pool (remedy = leg-2 "
                "pool entry next round); T-184 branch not on origin = receiver watch")
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- heartbeat fleet/machines/bm-b.json ----------
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
import psutil
ram = psutil.virtual_memory()
vm = psutil.scanf if False else None
try:
    import shutil
    tot, avail, _pct = shutil.disk_usage("C:\\")
except Exception:
    pass
h["clock_read"] = TS
h["ts"] = TS
h["last_seen"] = TS
h["last_round_at"] = TS
h["heartbeat_epoch_utc"] = EPOCH
h["round"] = 877
h["round_no"] = 878
h["cpu_cores"] = psutil.cpu_count(logical=True)
h["ram_free_gb"] = round(ram.available / (1024 ** 3), 1)
h["free_ram_gb"] = h["ram_free_gb"]
h["ram_free_pct"] = round(ram.available * 100.0 / ram.total, 1)
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["current_task"] = s["current_task"]
h["task"] = s["current_task"]
h["now_active"] = s["now_active"]
h["did"] = s["did"]
h["last_action"] = s["did"]
h["last_action_at"] = TS
h["latest_artifact"] = s["latest_artifact"]
h["next"] = s["next"]
h["next_milestone"] = s["next_milestone"]
h["verdict"] = s["verdict"]
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orphan_face_note"] = s["orphan_face_note"]
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-proof: epoch must be JSON int
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print(json.dumps({"state_round": 877, "round_no": 878, "epoch": chk["heartbeat_epoch_utc"],
                  "epoch_is_int": True, "ram_free_gb": h["ram_free_gb"], "ts": TS}))
