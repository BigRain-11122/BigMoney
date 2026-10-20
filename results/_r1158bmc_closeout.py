# -*- coding: utf-8 -*-
# r1158 bm-c closeout: state bump + heartbeat + round report line (single in-process writer).
import datetime, io, json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MID = "bm-c"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(NOW.timestamp())

NOTE = ("r1158: clean continuation product window (state round_no=1157 at open, executed r1158, "
        "advanced 1157->1158 so next=r1159); zero absorb owed (r1157 closeout a2f3e3ce27 landed clean); "
        "zero double-count: S0.5 d19 probe -> decisions sha 715e4134 unchanged (zero action) / orders "
        "1c110b2e unchanged (107 files, 232 acks, unacked=0); S0 origin 0 behind/0 ahead at open; "
        "S1 smoke 49/49; PRODUCT = W288 PREREG FREEZE: research/PERPETUAL_N1_W288_PREREG.md "
        "(24,154B/64 lines) derived from the frozen W287 pre-run face (git show f138546d08, hash-object "
        "identity asserted in-script) via results/_r1158bmc_prereg_derive_w288.py -- 34 count-gated rules "
        "+ single-pass wave/w/r/band token maps + 8 post-shift repairs; bands A 648_901..650_900 (41st "
        "consecutive A-hop, naive 648_701..650_700 refused at start by REGISTERED W287 B 648_701..648_900, "
        "A base==prior-B tail 648_900+1 EXACT) / B 650_901..651_100 (42nd above-own-A, own-A reservation "
        "cascade, base==own-A tail 650_900+1 EXACT); chain K 629,320->631,520 proj / ledger "
        "1,055,741->1,057,941 proj / n_eff 1,053,541->1,055,741 proj / se_mu 0.000309; banned_direction_gate "
        "ADMIT rc0 (matched=[]); receipt results/_w288bmc_prereg_freeze_receipt.json; out sha256_16 "
        "8368bf51dfe9bdd2; six truth repairs disclosed (sec.5 key labels back to the W287 wave the numbers "
        "were measured on, forward-projection ordinals now pointer-to-live-trace, own-wave ordinal captions "
        "42nd/41st, se_mu chain restored verbatim, bmc rows arithmetic healed to 106+candidate=107th, legacy "
        "RAM anchor range W279->W280); commit d6c9ce18ab pushed then rebased onto 1e750d21b7 -> 22ffa74b01 "
        "(0 ahead/0 behind); S3 satengine ALIVE rc0 idle (burns=[] queue=[]); watermark py_low_board_clear "
        "(board closed, pool 0) legal idle; S6 rc0: dualrun ZERO-DRIFT 464 entries streak 18 / compute_audit "
        "FLAG supply_gap+supply_floor (ready 2<floor 3, answered by the W288 splice next window) / update_daily "
        "cutoff 2026-10-19 zero new rows / regime ORANGE_COLD breadth 0.79 / daily_report REPORT-2026-10-20 / "
        "attrition 4 ledger files CLEAN (2 historical shrinks healed) | S7 loop pin=5 no-op (first fire 13:35) / "
        "watchdog re-registered (S4U flip access-denied standing face) / both claws installed LF-normalized / "
        "orphan face=0 (py_faces=4, resident_servers=2, zero kill). current=W288 prereg frozen; "
        "next=r1159 W288 five-face freeze splice (editor derive off _w287bmc_freeze_edits.py) + engine self-burn "
        "+ sixgate/finalize; local-not-on-origin commits=0")

sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 1158
st["round"] = 1158
st["last_round"] = 1158
st["round_no_label"] = "r1158"
st["last_round_label"] = "r1158"
st["r1158_closeout_note"] = NOTE
st["next"] = ("r1159 W288 five-face freeze splice (editor derive off results/_w287bmc_freeze_edits.py) + "
              "engine self-burn 12/12 + sixgate + finalize")
st["next_pointer"] = st["next"]
st["current_task"] = "W288 prereg frozen; next = W288 five-face splice + engine self-burn + finalize"
st["current_task_at"] = TS
st["current_task_ts"] = TS
st["last_action"] = "W288 PREREG FREEZE (24,154B/64 lines, 34 count-gated rules, banned gate ADMIT)"
st["last_action_at"] = TS
st["last_artifact"] = "research/PERPETUAL_N1_W288_PREREG.md"
st["last_artifact_at"] = TS
st["latest_artifact"] = "research/PERPETUAL_N1_W288_PREREG.md"
st["recent_artifact"] = "results/_w288bmc_prereg_freeze_receipt.json"
st["last_round_at"] = TS
st["last_round_summary"] = NOTE
st["last_round_summary_at"] = TS
st["last_round_ts"] = TS
st["last_round_closed"] = True
st["last_round_closed_at"] = TS
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["last_seen"] = TS
st["last_seen_at"] = TS
st["clock_read"] = TS
st["heartbeat_epoch_utc"] = EPOCH
st["heartbeat_epoch_utc_type"] = "int"
st["round_no"] = 1158
st["verdict"] = ("green r1158: W288 PREREG FREEZE -- bands A 648_901..650_900 (41st A-hop) / "
                 "B 650_901..651_100 (42nd above-own-A) on the post-W287 277-owner universe")
st["verify"] = ("smoke 49/49 | banned gate ADMIT rc0 | 34 count-gated rules + 8 truth repairs | "
                "residual empty | dualrun streak 18 | attrition CLEAN | orphan face=0")
st["head_sha"] = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                                capture_output=True).stdout.decode().strip()
io.open(sp, "w", encoding="utf-8").write(json.dumps(st, ensure_ascii=False, indent=1))

hh = os.path.join(REPO, "fleet", "machines", MID + ".json")
h = json.load(io.open(hh, encoding="utf-8"))
h.update({
    "machine_id": MID,
    "last_seen": TS,
    "last_seen_at": TS,
    "ts": TS,
    "clock_read": TS,
    "heartbeat_epoch_utc": EPOCH,
    "current_task": "W288 prereg frozen; next = W288 splice + engine self-burn + finalize",
    "current_task_at": TS,
    "current_task_ts": TS,
    "verdict": "green r1158: W288 PREREG FREEZE (41st A-hop / 42nd above-own-A)",
    "did": "W288 prereg freeze 24,154B + banned gate ADMIT + push 22ffa74b01",
    "last_artifact": "research/PERPETUAL_N1_W288_PREREG.md",
    "last_artifact_at": TS,
    "idle_rounds": 0,
    "agenda_starved": False,
    "orphan_face": 0,
    "cpu_cores": 32,
    "total_ram_gb": 23.9,
})
try:
    import psutil
    h["free_ram_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 2)
except Exception:
    pass
h["free_vram_mb"] = 2039
io.open(hh, "w", encoding="utf-8").write(json.dumps(h, ensure_ascii=False, indent=1))

rp = os.path.join(REPO, "round_reports-bm-c.md")
line = ("| %s | r1158 | W288 PREREG FREEZE: research/PERPETUAL_N1_W288_PREREG.md 24,154B/64 lines, 34 "
        "count-gated rules off frozen W287 face (f138546d08), bands A 648_901..650_900 (41st A-hop) / "
        "B 650_901..651_100 (42nd above-own-A), banned gate ADMIT rc0, 8 truth repairs disclosed; smoke "
        "49/49; dualrun streak 18; attrition CLEAN; push 22ffa74b01 | verify: sha256_16 8368bf51dfe9bdd2, "
        "residual empty, MUST/MUST-NOT green | next: r1159 W288 five-face splice + engine burn + finalize |\n")
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line if os.path.exists(rp) else line)

print(json.dumps({"state_round": st["round_no"], "epoch": EPOCH, "epoch_type": type(EPOCH).__name__,
                  "head": st["head_sha"], "clock_read": TS}, ensure_ascii=False))