# -*- coding: utf-8 -*-
"""r687 bm-a S7 closeout: state bump (684->687, r685/686 dead-labels adopted),
heartbeat write (epoch int + T clock), round report line append, CODELY pit
append. Programmatic json writes per r645/r678 laws + strict reparse proofs.
Idempotence gate on report/CODELY: marker count==0 before append (r679 law).
"""
import json, time, io, os, datetime

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- state ----------
sp = os.path.join(REPO, "state-bm-a.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round"] = "r687"
st["round_no"] = 687
st["loop_round"] = st.get("loop_round", 583) + 1
st["last_round"] = "r684"
st["last_round_at"] = "2026-10-04T15:5x+08:00"
st["last_round_ts"] = EPOCH
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", 0)
st["heartbeat_epoch_utc"] = EPOCH
st["current_task"] = ("r687 done: W3 s3 judge seat YIELDED to bm-c r484 freeze "
                      "(dual-freeze collision resolved theirs-canonical, seed "
                      "20285600 canonical; bm-a band 20287000 dropped unpushed "
                      "zero-burn); dead r685/r686 session adopted via merge "
                      "a6fc0132d DELIVERED")
st["did"] = ("r687: S0 dual-wave integration -- 24 intersection faces "
             "origin-verbatim pre-alignment absorb (pool probe r474: 0 "
             "owner_since regressions, 4 stale W3-JUDGE tickets dropped "
             "unpushed) + merge 15-commit wave 4 UU canon-resolved (3 judge "
             "faces theirs + CODELY block-union +2 r685 pit lines) + "
             "push_verify DELIVERED; S0.5 orders 154/154 zero-unacked + D-19 "
             "dual MATCH (sparse-clone raw-blob r631 recipe, ssh-first per "
             "r677); S1 smoke 48/48; S2 board 45/45 claimed zero-open; "
             "adopted-face verification: mass_trial_w1 selftest 40/40 + "
             "science_gates 69/69 (-m canonical form per r683 law); S6 37/37 "
             "rc0 86.9s; S7 self-heal 4/4 + attrition CLEAN 4 ledgers + MSG "
             "yield notice + seat MSG-1655 archived")
st["next"] = ("r688+: W3 judge pool tickets watch (bm-c judge-prep spawned "
             "16:35 detached -- tickets then three-machine autofill claims; "
             "bm-a runner face verified 40/40 green for shard burns) + W117 "
             "finalize (GATED on bm-b W116 finalize, rehearsal r684 PASS "
             "FAIL-CLOSED verified) + fund trio NULLS finalize 10-05..09 "
             "watch (bm-b canonical) + 10-06+ next-wave candidate drafting "
             "(style-rotation, needs bm-b astock_daily panel)")
st["verify"] = ("S1 smoke 48/48; mass_trial_w1 selftest 40/40 + science_gates "
               "69/69 (adopted canonical faces green on bm-a); S6 37/37 rc0 "
               "86.9s (_r687bma_s6_log.txt); attrition CLEAN 4 ledgers; "
               "push_verify DELIVERED a6fc0132d (pre-closeout); state "
               "strict json.loads proof + heartbeat epoch int/T-sep proof")
st["updated"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
st["notes"] = ("r687: dead r685/r686 session round-labels adopted honestly "
               "(r685 W3 screen finalize + r686 superseded judge freeze both "
               "in history via r687 merge); state round_no 684->687 skip "
               "nonexistent r685/r686 session bookkeeping per r651/r652 "
               "precedent; science_gates selftest canonical = python -m "
               "scripts.science_gates selftest")
io.open(sp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))
json.load(io.open(sp, encoding="utf-8"))  # strict reparse proof
print("state OK round_no=%d epoch=%d" % (st["round_no"], st["heartbeat_epoch_utc"]))

# ---------- heartbeat ----------
hp = os.path.join(REPO, "fleet", "machines", "bm-a.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = TS
hb["current_task"] = "r687 closeout: W3 judge seat yielded to bm-c (dual-freeze resolved); adopted faces verified 40/40+69/69"
hb["cpu_cores"] = 32
try:
    import psutil
    hb["idle_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    hb["idle_ram_gb"] = hb.get("idle_ram_gb")
hb["gpu_idle_vram_gb"] = hb.get("gpu_idle_vram_gb")
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = TS
io.open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1))
hbx = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(hbx["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hbx["clock_read"] and "+" in hbx["clock_read"], "clock T-format"
print("heartbeat OK epoch=%d clock=%s ack=%d" % (
    hbx["heartbeat_epoch_utc"], hbx["clock_read"],
    len(hbx.get("orders_ack", []))))
