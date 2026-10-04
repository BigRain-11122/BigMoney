"""r681 bm-a state + heartbeat update (programmatic write + strict json.loads self-proof, r645 law)."""
import json, time, datetime

ST = "state-bm-a.json"
HB = r"fleet\machines\bm-a.json"

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

with open(ST, encoding="utf-8") as f:
    st = json.load(f)

st.update({
    "round_no": 681,
    "round": "r681",
    "last_round": "r681",
    "last_round_at": iso,
    "last_round_ts": epoch,
    "last_run": iso,
    "current_task": "r681 done: LHB seat-axis cheap census CLOSE (board-level r680 + seat-level r681 = full-axis closed); next-wave candidate window 10-06+",
    "did": "r681: S0 daemon absorb (4 satengine/autofill bm-a lane faces) + merge origin 7 commits zero-UU + S0.5 orders 153/153 dual-scan zero-unacked + D-19 decisions/orders sha MATCH (4e5be321/82a0cef9, group-tree real-path fetch+show) + S1 smoke 48/48 + S3 seat-axis cheap census (36 sampled windows 2007-2026, 109,372 seat rows, top50-net/freq dual caliber, 4 cells all CLOSE: ret1 edge -3.4/-4.2bp, ret5 edge +18.2/+1.6bp < +20bp no-edge band; gap edge +23bp swallowed post-open = informed leg trapped in gap, E30 re-proof) + TREASURE_REGISTRY seat-level row + digest + S6 37/37 rc0 116.1s (dualrun ZERO-DRIFT streak51; t35 PASS 0 pending; CALL ORANGE_COOL; golden-week no-op family) + S7 self-heal 4/4 + attrition CLEAN 4 ledgers",
    "last_action": "r681: LHB seat-level follow axis closed by cheap census (statistical-seat caliber, alias-registry-free); style-rotation axis naive form hits BAN-01/02/09 (fail-closed, needs new mechanism argument); limit-up relay axis needs astock_daily panel = bm-b local data (MSG or bm-b lane)",
    "next": "r682: fund trio NULLS finalize window 10-05..09 (bm-b canonical in-flight V~10-06/Q~10-07/D~10-08) -> piece-4 excess-CFO prereg (D6 corr measured + mktcap caliber GM P1 pending); 10-06+ next-wave candidate drafting (style-rotation needs new-mechanism argument per BAN-01/02/09; limit-up relay needs bm-b data transfer or bm-b lane); 10-08 market-open window external run-11/run-7 legs",
    "notes": st.get("notes", ""),
    "verify": "S1 smoke 48/48; seat census 4/4 cells CLOSE frozen rules; S6 37/37 rc0 116.1s (_r681bma_s6_log.txt; dualrun streak51); attrition CLEAN 4 ledgers; state strict json.loads proof + heartbeat epoch int/T-sep proof",
})
st["heartbeat_epoch_utc"] = epoch

with open(ST, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
json.loads(open(ST, encoding="utf-8").read())  # self-proof

with open(HB, "rb") as f:
    hb = json.loads(f.read().decode("utf-8"))
hb.update({
    "last_seen": iso,
    "heartbeat_epoch_utc": epoch,
    "current_task": st["current_task"],
})
for k in ("verdict", "cpu_cores", "ram_free_gb", "gpu_vram_free_gb"):
    if k not in hb:
        hb[k] = ""
with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
rt = json.loads(open(HB, encoding="utf-8").read())
assert isinstance(rt["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in rt.get("clock_read", iso), "clock T-sep"
print("STATE_HB_DONE epoch=%d round=681" % epoch)
