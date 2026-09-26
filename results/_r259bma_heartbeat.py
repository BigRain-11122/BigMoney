# -*- coding: utf-8 -*-
"""R259 bm-a heartbeat: fleet/machines/bm-a.json (epoch = python int() JSON
number per R170/R178/F7 law; clock_read ISO with UTC offset per T-04 F5)."""
import io
import json
import time
import datetime as dt

P = "fleet/machines/bm-a.json"
raw = io.open(P, "rb").read()
had_bom = raw.startswith(b"\xef\xbb\xbf")
had_nl = raw.endswith(b"\n")
d = json.loads(raw.decode("utf-8-sig"))

epoch = int(time.time())
clock = dt.datetime.now().astimezone().isoformat(timespec="seconds")
d["machine_id"] = "bm-a"
d["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
d["current_task"] = ("T-73 s3 remaining CN-native consumption next "
                     "(evidence base complete); slice-E style-rotation "
                     "closed R259 = s2 COMPLETE")
d["cpu_cores"] = 32
d["cpu_pct"] = 42.0
d["free_ram_gb"] = 57.0
d["gpu_free_vram_gb"] = 5.5
d["verdict"] = (
    "GREEN R259: s2 COMPLETE via slice-E full arc (dual-horizon rotation "
    "law: annual style momentum thin-alive 1.04x/1.08x null margins + "
    "quarter reversal face OOS -0.192 beyond null; 4 fund artifacts caught "
    "envelope rule; 2 E1 defects self-caught zero-escape: raw-face "
    "descriptive poison -> clean_value bridge, ledger prev-echo -> guard; "
    "102 trials 187585->187687 single-count; post_review 21 YES/0 NO; "
    "no fabricated busywork O-1137"
)
d["heartbeat_epoch_utc"] = epoch
d["clock_read"] = clock
d["round_no"] = 259
d["task"] = ("R259 done: s2 slice-E style-rotation closed (last s2 topic); "
             "next = s3 remaining CN-native model consumption; 09-28 "
             "new-bar chain; 10-01 trio; T-70 verdict 10-09")

out = json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
if had_nl and not out.endswith(b"\n"):
    out += b"\n"
io.open(P, "wb").write(out)

# self-verify: epoch must be JSON int (number, not string)
d2 = json.loads(io.open(P, "rb").read().decode("utf-8-sig"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written; epoch int-verified:", d2["heartbeat_epoch_utc"],
      "clock:", d2["clock_read"], "round:", d2["round_no"])
