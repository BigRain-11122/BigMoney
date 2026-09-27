# -*- coding: utf-8 -*-
"""r326 bm-a S7 bookkeeping: state-bm-a.json full refresh (round_no 325->326 +
did/verdict/next/ts fields -- full-field refresh fixing the R325 partial gap)
+ heartbeat fleet/machines/bm-a.json (epoch int verified, clock ISO T-sep).
Byte-faithful newline='' io; utf-8 strict re-verify."""
import io
import json
import time

TS = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

STATE = {
    "round_no": 326,
    "did": ("R326: T-86 W2-A runner built + pool entry CENSUS-FUS-S2-W2A ready "
            "lane=bm-b (starvation supply response; audit flags CLEAN again); "
            "seat-3 council opinion C-20260927-01 issued F-20260927-02 (P-32 "
            "catch: R324/R325 not-our-face mis-receipt corrected); frozen-spec "
            "universe reading recorded (panel x mask codes >=5,000; ok_static "
            "3,517 disclosed; MSG-1425 bm-b); glued-tail fixed; S6 32/32 "
            "rc=0; smoke 25/25; w2 selftest 12/12; wave-1 selftest 18/18"),
    "verdict": ("py_low_with_work_cands legal-occupied: sina_mf A1 repull "
                "66.7% live ETA ~15:03; pool 77 done + 1 ready (W2-A lane bm-b) "
                "= starvation structurally lifted; board 0 open tickets; "
                "audit v2.3 CLEAN flags=[]"),
    "next": ("R327+: (1) bm-b W2-A probe->burn -> finalize ledger N=5,920 + "
             "W2-UNC follow-up; W2-B stays GATED sec.9.4; (2) sina_mf repull "
             "terminal window ~15:0x mechanical three-piece then bm-b "
             "sina-construct open-gate MSG; (3) Monday 09-28 09:15 T-91 s3 "
             "auto-fire; (4) 10-01 month trio; (5) R330 5x HANDOVER"),
    "ts": TS,
    "last_round_ts": TS,
    "updated_at": TS,
    "last_seen": TS,
    "current_task": ("R326 done: T-86 W2-A runner+pool entry landed + seat-3 "
                     "council opinion issued; R327: bm-b W2-A burn watch + "
                     "repull terminal three-piece ~15:0x"),
    "task": ("R326 done: T-86 W2-A runner+pool entry landed + seat-3 council "
             "opinion issued; R327: bm-b W2-A burn watch + repull terminal "
             "three-piece ~15:0x"),
}

p = r"state-bm-a.json"
d = json.load(io.open(p, encoding="utf-8"))
d.update(STATE)
d["last_round"] = 325
s = json.dumps(d, indent=1, ensure_ascii=False)
json.loads(s)
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(s)

# ---- heartbeat ----
hp = r"fleet\machines\bm-a.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
h["round_no"] = 326
h["current_task"] = STATE["current_task"]
h["task"] = STATE["task"]
h["verdict"] = STATE["verdict"]
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = TS
try:
    import psutil
    h["cpu_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
    vm = psutil.virtual_memory()
    h["free_ram_gb"] = round(vm.available / 1e9, 1)
    h["idle_ram_gb"] = h["free_ram_gb"]
    h["free_ram_mb"] = int(vm.available / 1e6)
except Exception:
    pass
s2 = json.dumps(h, indent=1, ensure_ascii=False)
json.loads(s2)
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    f.write(s2)

# ---- self-assertions (R170/R178/R262 law family) ----
h2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and not isinstance(
    h2["heartbeat_epoch_utc"], bool), "epoch must be JSON int"
assert "T" in h2["clock_read"] and "+" in h2["clock_read"], "clock ISO T-separated"
st = json.load(io.open(p, encoding="utf-8"))
assert st["round_no"] == 326
print("state round_no 325->326 full-field refresh OK; heartbeat epoch",
      h2["heartbeat_epoch_utc"], "int-verified; clock", h2["clock_read"])
