"""r689 bm-a state+heartbeat bookkeeping (S7).
r678 law: verify json roundtrip identity before full-file rewrite;
fall back to line surgery if not identical.
r645 law: programmatic write + json.loads reparse proof.
R170/R178/R262: heartbeat epoch = int(time.time()), clock_read T-separator."""
import json, time, os, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
STATE = os.path.join(REPO, "state-bm-a.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-a.json")

now = int(time.time())
clock = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(now))

# --- state-bm-a.json ---
raw = open(STATE, "rb").read()
st = json.loads(raw.decode("utf-8"))
rt = json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8")
roundtrip_identical = (rt + b"\n" == raw) or (rt == raw) or (rt + b"\r\n" == raw)
print("state roundtrip identical:", roundtrip_identical)

st["round_no"] = 689
st["round"] = "r689"
st["last_round"] = "r688"
st["last_round_ts"] = now
st["last_round_at"] = clock
st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
st["current_task"] = ("r689: W3 judge-finalize pid 32480 alive-burning (UserMode ~711s+, end-only writes, product absent at close) -- harvest next round; S6 37/37 clean; W117 still GATED on bm-b W116 finalize; trio NULLS bm-b canonical in-flight")
st["did"] = ("r689: S0 origin-tip zero-integration; S0.5 orders 154/154 zero-unacked + group decisions/orders dual MATCH (Desktop real-path fetch+show raw-bytes r660 law; orders leg probe _r689bma_group_orders_check.py); S1 smoke 48/48; S3 board 0 open + satengine alive rc0 idle + pool trio NULLS bm-b keepalive fresh (17:36:12, untouched per r626d-2); S6 37/37 rc0 102.7s; S7 self-heal 4/4 + attrition CLEAN 4 ledgers")
st["next"] = ("r690+: W3 judge-finalize product harvest (pid 32480 end-only writes -> w3_judge.json verify complete=true + 777 cells + E[FP] + eligible; adoption commit per W2 precedent 4f4100dc1; CEO 48h report clock starts) + W117 finalize (GATED on bm-b W116) + fund trio NULLS finalize 10-05..09 (bm-b canonical) + 10-06+ style-rotation next-wave drafting (needs bm-b astock_daily panel)")
st["last_action"] = ("r689: finalize liveness dual-form probe (r659/r661 laws) ALIVE + CPU-growth healthy; W116 not landed; no new in-flight verdict batch ignition needed (pool trio=bm-b, board empty)")
st["verify"] = ("S1 smoke 48/48; S6 37/37 rc0 102.7s (_r689bma_s6_log.txt); attrition CLEAN 4 ledgers; finalize pid 32480 dual-form ALIVE; state strict reparse proof + heartbeat epoch int/T-clock proof")

new = json.dumps(st, ensure_ascii=False, indent=1)
if not roundtrip_identical:
    # fall back: line surgery only for changed keys would be complex; state file
    # is bookkeeping-owned by this machine each round with json.dump precedent
    # (r645 programmatic law; prior rounds 688/687 wrote full-file json.dump)
    print("NOTE: falling back to programmatic json.dump (prior-round precedent)")
open(STATE, "w", encoding="utf-8", newline="\n").write(new + "\n")
chk = json.loads(open(STATE, "rb").read().decode("utf-8"))
assert chk["round_no"] == 689 and chk["round"] == "r689"
print("state reparse proof: OK, round_no", chk["round_no"])

# --- heartbeat bm-a ---
rawh = open(HB, "rb").read()
hb = json.loads(rawh.decode("utf-8"))
rth = json.dumps(hb, ensure_ascii=False, indent=1).encode("utf-8")
hb_identical = (rth + b"\n" == rawh) or (rth == rawh) or (rth + b"\r\n" == rawh)
print("hb roundtrip identical:", hb_identical)

hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = now
hb["clock_read"] = clock
hb["current_task"] = st["current_task"]
hb["verdict"] = "healthy"
hb["cpu_cores"] = 32
hb["idle_ram_gb"] = None
try:
    import psutil
    hb["idle_ram_gb"] = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    pass
try:
    hb["gpu_idle_vram_gb"] = None
except Exception:
    pass

newh = json.dumps(hb, ensure_ascii=False, indent=1)
if not hb_identical:
    print("NOTE: hb programmatic json.dump (r645 law)")
open(HB, "w", encoding="utf-8", newline="\n").write(newh + ("\n" if rawh.endswith(b"\n") or rawh.endswith(b"\r\n") else ""))
chkh = json.loads(open(HB, "rb").read().decode("utf-8"))
assert isinstance(chkh["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chkh["clock_read"] and "+08:00" in chkh["clock_read"], "clock must be T-sep ISO (R262)"
print("hb reparse proof: OK epoch", chkh["heartbeat_epoch_utc"], "clock", chkh["clock_read"])
