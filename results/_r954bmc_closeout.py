# -*- coding: utf-8 -*-
# r954 closeout: state-bm-c.json + heartbeat + round report line
import json, time, datetime, io

NOW = datetime.datetime.now().isoformat(timespec="seconds")
EPOCH = int(time.time())
CLOCK = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# ---------- state ----------
sp = r"state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 955
st["round_no_label"] = "r954"
st["last_round"] = 954
st["clock_read"] = CLOCK
st["ts"] = CLOCK
st["updated"] = CLOCK
st["last_seen"] = CLOCK
st["last_round_at"] = CLOCK
st["last_round_closed"] = CLOCK
st["heartbeat_epoch_utc"] = EPOCH
st["last_ts"] = EPOCH
st["cpu_pct"] = 8.6
st["cpu_util_pct"] = 8.6
st["free_ram_gb"] = 0.2
st["ram_free_gb"] = 0.2
st["idle_ram_gb"] = 0.2
st["orphan_face"] = 4
st["orphan_faces"] = 4
st["did"] = ("r954: (1) S0-1 anchor bm-c + round-zero probe py_faces=12 orphans=4 zero-kill; S0 pull --rebase up-to-date "
             "(transient-state stash bridge); (2) S0.5 dual-delta FALSE both (dec fb5825cb / ord 4aebbfc3, unacked=0); "
             "(3) S1 smoke 49/49; S2 boards clear (jobs 0); "
             "(4) PRODUCT: landing QC patrol 4 clips ALL PASS -> R04_river_dry 8.0 LOCKED / C06_forever_cut_v2 7.5 borderline LOCKED "
             "(hammer-not-in-frame + static debris + uniform chisel disclosed; v1 6.5 early-strike segment = director alternate) / "
             "D02_she_reads 8.0 LOCKED (face-closeup lane first PASS = Seedance-rejected-shot rescue via local INT8 proven) / "
             "D03_two_worlds 8.0 LOCKED (own-reflection gaze-chain compliant; glass-surface anchor note disclosed) -> "
             "QC-r954.json + 3 sheets landed group-tree origin 0bd5cb9e4c66; "
             "(5) TRACK-2 DISPATCH OUT: 3-frame Krea2 regen (C03 BANDS wedge / C04 horizontal-register basalt / C09 two-person oath) "
             "to bm-a night lane -- MSG-20261013-0430-bmc.md (bigmoney origin 0d98741fc) + orders row 10-13 04:3x "
             "(group-tree origin 0bd5cb9e4c66) + poke accepted 04:22:07; bm-c no-Krea2-weights disclosed "
             "(MSG-0215 self-gen fallback declared dead, honest revision); "
             "(6) S6 light: dualrun ZERO-DRIFT streak 47 + audit FLAG pool_starvation/supply_floor = legal RAM-arbitration face "
             "(W227 deferred 0.2G<4G, i2v priority per O-2330-2) + wm py_low_with_work_cands legal (local_batch=i2v GPU 100%); "
             "(7) S7 quad green (loop pin=5 + watchdog + both claws) + attrition 4 CLEAN; counter 954->955")
st["verdict"] = ("green: 4-clip QC patrol ALL PASS (R04 8.0 / C06v2 7.5 borderline / D02 8.0 / D03 8.0 -- face-lane rescue proven) "
                 "+ track-2 3-frame regen dispatched to bm-a (MSG + orders row + poke accepted 04:22:07) + smoke 49/49 "
                 "+ dualrun streak 47 + attrition CLEAN + S7 quad green; W227 RAM-deferred 0.2G<4G legal (O-2330-2 i2v priority); "
                 "burns in flight R05/C07v2/R02v2/B01/E03 ETA ~05:00")
st["current_task"] = ("r954 closeout done; burning: R05_gold_threads + rider C07_stele_sink_v2 + rider R02_she_turns_v2 queued + "
                      "addon B01_weary/E03_gaze_meet (FIFO); track-2 frame return watch on bm-a")
st["current_task_at"] = CLOCK
st["now_active"] = ("2026-10-13 04:2x | r954 | bm-c: 4-clip QC all-PASS locked + track-2 3-frame regen dispatched to bm-a "
                    "(poke accepted); burns R05/C07v2/R02v2/B01/E03 to ~05:00; counter 954->955")
st["activity_now"] = st["now_active"]
st["last_round_summary"] = ("r954: landing QC 4/4 ALL PASS (R04 8.0 / C06v2 7.5 borderline / D02 8.0 / D03 8.0) + "
                            "track-2 dispatch to bm-a (C03/C04/C09 Krea2 regen, dl 05:15)")
st["last_action"] = "r954 closeout (QC-r954 4 verdicts + track-2 dispatch + S6 light + S7 quad)"
st["last_action_at"] = CLOCK
st["last_round_summary_at"] = CLOCK
st["latest_artifact"] = ("bmc/QC-r954.json (4 verdicts all-PASS) + results/_r954bmc_qc_sheet{1,2,3}.png + "
                         "fleet/inbox/MSG-20261013-0430-bmc.md (track-2 dispatch)")
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = ("R05/C07v2/R02v2/B01/E03 QC on landing -> bm-a frame return -> i2v v2 -> 06:30 closeout 21-slot tally "
                        "-> bm-a 07:00 assembly -> 08:30 CEO screen")
st["next"] = ("r955: (1) QC on landing: R05_gold_threads (burning) + C07_stele_sink_v2 (rider ~1000s) + R02_she_turns_v2 (rider behind) "
              "+ B01_weary/E03_gaze_meet (addon, ETA ~05:00 drain) per patrol law <7.5 reshake; "
              "(2) bm-a frame return watch: reply MSG in bmq fleet/inbox/ with CDN URLs -> download to bmc/i2v_frames/ -> "
              "submit i2v v2 self-interleave (INT8 768P) -> QC on landing; "
              "(3) no-return-by-05:15 fallback = disclose C03/C09/C04 FAIL at 06:30 closeout, director seat retime/omit "
              "(H3 t2v object-shot fallback only with director nod); "
              "(4) 06:30 closeout tally 21 slots (locked 13 + C02 best-of disclosed + burns/regen resolution) + "
              "I2V-URL-INDEX final commit+push; bm-a 07:00 assembly; 08:30 CEO screen; "
              "(5) W227 seat first action after RAM relief (probe on disk results/_w227bmc_probe_derive.py); "
              "(6) Tue 15:30 new-bar papers full chain + update family")
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["prod_lanes"] = ("GPU=CEO deathline i2v: 21-slot accounting: locked N01-07+C05+C08+R01+R03+R04+C06v2 (13) + "
                    "D02/D03 addon face-lane PASS + disclosed C02 7.3 best-of + burning R05/C07v2/R02v2/B01/E03 (ETA ~05:00) + "
                    "track-2 regen C03/C09/C04 dispatched bm-a (dl 05:15); CPU=N1 W226 complete, W227 seat RAM-deferred "
                    "(0.2G<4G per O-2330-2)")
st["r954_closeout_note"] = ("r954: (1) S0-1 anchor bm-c + probe py_faces=12 orphans=4 zero-kill + S0 stash-bridge pull up-to-date; "
                            "(2) S0.5 dual-delta FALSE both (dec fb5825cb/ord 4aebbfc3, unacked=0); (3) smoke 49/49; "
                            "(4) QC patrol 4/4 ALL PASS: R04 8.0 / C06_v2 7.5 borderline LOCKED (3 light physics disclosed) / "
                            "D02 8.0 (face lane first PASS) / D03 8.0 (own-reflection compliant); QC-r954.json+3 sheets -> "
                            "group-tree origin 0bd5cb9e4c66 (CAS direct-deposit w/ orders row); "
                            "(5) track-2 3-frame regen dispatched: MSG-0430 (bmq origin 0d98741fc) + orders row 04:3x + "
                            "poke bm-a accepted 04:22:07; no-Krea2-weights honest disclosure (self-gen fallback dead); "
                            "(6) S6 light streak 47 + FLAG=legal RAM arbitration; (7) S7 quad green + attrition CLEAN; counter 954->955")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- heartbeat ----------
hp = r"fleet\machines\bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = CLOCK
hb["ts"] = CLOCK
hb["clock_read"] = CLOCK
hb["heartbeat_epoch_utc"] = EPOCH
hb["cpu_pct"] = 8.6
hb["free_ram_gb"] = 0.2
hb["ram_free_gb"] = 0.2
hb["idle_ram_gb"] = 0.2
hb["gpu_free_vram_mib"] = 779
hb["gpu_free_vram_mb"] = 779
hb["gpu_free_mb"] = 779
hb["verdict"] = ("green: r954 4-clip QC all-PASS (R04/C06v2/D02/D03) + track-2 3-frame regen dispatched to bm-a "
                 "(poke accepted); burns R05/C07v2/R02v2/B01/E03; i2v GPU 100% priority lane; W227 RAM-deferred 0.2G<4G")
hb["current_task"] = ("r954 closeout done; burning R05 + rider C07_v2/R02_v2 + addon B01/E03; track-2 frame-return watch")
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["now_active"] = st["now_active"]
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# heartbeat epoch int self-check (R170/R178 law)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read must be T-separated"

# ---------- round report ----------
rp = r"logs\iteration-loop\round_reports-bm-c.md"
line = ("| %s | r954 | QC patrol 4 clips ALL PASS (R04 8.0 / C06v2 7.5 borderline / D02 8.0 / D03 8.0 -- face-lane rescue proven) "
        "-> QC-r954.json landed origin 0bd5cb9e4c66 + track-2 3-frame regen dispatched to bm-a (MSG-0430 + orders row 04:3x + "
        "poke accepted 04:22:07; no-Krea2 self-gen fallback declared dead honestly) | evidence: QC-r954.json + 3 sheets + "
        "smoke 49/49 + dualrun streak 47 + attrition 4 CLEAN + S7 quad green | next: R05/C07v2/R02v2/B01/E03 QC on landing + "
        "bm-a frame return -> i2v v2 -> 06:30 closeout 21-slot tally; 孤儿面=4 |\n" % CLOCK)
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("CLOSEOUT WRITES OK", CLOCK, "epoch", EPOCH)
