"""r480 bm-c S7: orders rescan + heartbeat update (roundtrip-gated per r678)."""
import json
import os
import time
import datetime

# --- orders S7 double-scan (same-shape set diff, r477 law) ---
orders = set(f for f in os.listdir("fleet/orders")
             if f.startswith("O-") and f.endswith(".md"))
hb = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
unacked = sorted(orders - ack)
extra = sorted(e for e in (ack - orders) if not e.startswith("README"))
print("ORDERS_RESCAN", len(orders), "unacked", unacked, "extra_non_readme",
      extra)
assert not unacked and not extra, "ORDERS RESCAN FAIL"

# --- heartbeat roundtrip gate (r678: load->dump->bytes compare) ---
p = "fleet/machines/bm-c.json"
raw = open(p, "rb").read()
d0 = json.loads(raw.decode("utf-8"))
rt = json.dumps(d0, ensure_ascii=False, indent=1).encode("utf-8")
roundtrip_ok = (rt == raw)
print("ROUNDTRIP_IDENTICAL", roundtrip_ok)

epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now = "2026-10-04T15:2x"

hb2 = json.loads(raw.decode("utf-8"))
hb2["last_seen"] = clock
hb2["current_task"] = (
    "当前活: MASS_TRIAL_W3 prereg frozen (R99 commit c2141d6c1) + runner "
    "--wave 3 legs + generate detached in-flight (pid 3484, ~80s/fam full "
    "speed, ETA ~16:5x) — O-1440 sec.3 supply pre-position + T-158 "
    "post-judge consumption face | 最近实物: research/MASS_TRIAL_W3_PREREG.md "
    "+ scripts/mass_trial_w1.py w3 legs (selftest 38/38, banned ADMIT) + "
    "results/_r480bmc_w3_generate_log.txt + results/_r480bmc_s6_log.txt "
    "(38/38 rc0) @ " + clock + " | 下个里程碑: W3 generate done -> screen "
    "4-shard pool entries (r481) -> burn -> finalize + sec.9 s3 freeze "
    "<=10-12; fund-trio finalize 10-05 10:30 (bm-b); O-2115/O-2030 "
    "acceptance 10-08")
hb2["heartbeat_epoch_utc"] = epoch
hb2["clock_read"] = clock
hb2["verdict"] = (
    "W3 wave ignited same-round: prereg frozen c2141d6c1 (R99 before any "
    "screen), runner wave-3 legs, banned ADMIT, selftest 38/38, generate "
    "detached full-speed; N2-W15 red card maintained (slice-2 = bm-b seat, "
    "39h unlanded, contact forbidden per anti-dup); S6 38/38 rc0; orders "
    "155/155 dual-scan zero unacked; smoke 48/48")
try:
    import psutil
    cores = psutil.cpu_count(logical=True)
    ram = round(psutil.virtual_memory().available / (1 << 30), 1)
    hb2["cpu_cores"] = cores
    hb2["idle_ram_gb"] = ram
except Exception as ex:
    print("psutil face skip:", ex)

if roundtrip_ok:
    out = json.dumps(hb2, ensure_ascii=False, indent=1).encode("utf-8")
    open(p, "wb").write(out)
else:
    # line-level surgery fallback: only swap the mutable scalar fields
    raise SystemExit("ROUNDTRIP MISMATCH -- line surgery required, ABORT")

# --- POST-WRITE assertions (r479 pattern) ---
v = json.load(open(p, encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock not T-sep"
assert len(v.get("orders_ack", [])) == 155, "ack count drift"
print("HEARTBEAT-OK epoch", v["heartbeat_epoch_utc"],
      "clock", v["clock_read"], "fields", len(v))
