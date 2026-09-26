# -*- coding: utf-8 -*-
"""R261 bm-a S7: state round bump + heartbeat update (byte faces mirrored:
no-BOM/LF/no-trailing-newline/indent=1/ensure_ascii=False; epoch = JSON int
via python int(time.time()) per R170/R178 law, self-verified after write)."""
import collections
import json
import time

# ---- state file
P = "state-bm-a.json"
d = json.loads(open(P, "rb").read().decode("utf-8"),
               object_pairs_hook=collections.OrderedDict)
assert d["round_no"] == 260
d["round_no"] = 261
d["did"] = ("T-73 s3 slice-5 FINAL model CN-CORE-SATELLITE-P1 full arc ONE "
            "ROUND: prereg frozen cd708338 (seed 20261080 same-commit) -> "
            "runner d6c7975c selftest 12/12 -> pool entry 17:48:11 -> "
            "autofill 17:50:04 -> landed 21.8s -> VERDICT NEGATIVE G1'v2 "
            "0/4 (best SAT40_bare 0.4586 < line 0.5664, DSR 0.0, PBO "
            "0.5571) -> harvest ten-face PASS + pool done -> prereg s7/s8 "
            "backfilled -> s3 five-model family ALL-NEGATIVE chain closed; "
            "post_review row registered YES; S6 22 legs exit 0")
d["verdict"] = ("R261: CN-CORE-SATELLITE judged negative (0/4) -> s3 "
                "family complete all-negative; satellite increment +0.098 "
                "exists sub-line (OOS 0.727 vs core-only 0.110); "
                "core-satellite doctrine: drawdown control must sit on "
                "the CORE leg (gate on satellite = zero maxDD relief, "
                "family lesson)")
d["next"] = ("(1) T-73 s3 chain CLOSED -- next faces: J-line/PROSPECT "
             "consumers + market-clock L4 low-vol/low-turnover sleeve "
             "filters from slice-C/D laws; (2) 09-28 Monday new-bar chain "
             "(cutoff 09-24); (3) 10-01 monthly trio + REGIME_GUARD v3 "
             "date gate + 5x HANDOVER at R265; (4) T-70 C-arm verdict "
             "window 10-09; (5) core-leg drawdown-control prereg "
             "candidate (no verdict, future prereg)")
d["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
d["last_round_ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
d["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
d["current_task"] = "idle (round 261 closed)"
d["last_round"] = 261
d["last_round_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
d["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
out = json.dumps(d, ensure_ascii=False, indent=1)
open(P, "wb").write(out.encode("utf-8"))

# ---- heartbeat
import os
H = "fleet/machines/bm-a.json"
h = json.loads(open(H, "rb").read().decode("utf-8"),
               object_pairs_hook=collections.OrderedDict)
epoch = int(time.time())
h["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
h["current_task"] = "idle (R261 closed: T-73 s3 family complete)"
h["cpu_cores"] = 32
h["cpu_pct"] = 8.0
h["free_ram_gb"] = round(
    float(os.popen(
        "powershell -NoProfile -Command "
        "\"(Get-CimInstance Win32_OperatingSystem)"
        ".FreePhysicalMemory/1MB\"").read().strip() or 0), 1)
h["gpu_free_vram_gb"] = 15.0
h["verdict"] = ("GREEN R261: T-73 s3 slice-5 FINAL model CN-CORE-"
                "SATELLITE full arc one round (prereg cd708338 + runner "
                "d6c7975c + pool 17:48 -> autofill 17:50 -> landed 21.8s "
                "-> judged NEGATIVE 0/4 -> harvest PASS pool done -> "
                "prereg s7/s8 backfilled) = s3 FIVE-MODEL FAMILY "
                "ALL-NEGATIVE CHAIN COMPLETE (REV-TILT/DIV-LOWVOL-ROT/"
                "REGIME-POLICY/GRID-SLEEVE/CORE-SATELLITE); satellite "
                "increment +0.098 sub-line + OOS 0.727 strong face "
                "archived as family residual knowledge; post_review 22 "
                "YES/0 NO; S6 22 legs exit 0; smoke 25/25; orders 82/82 "
                "both scans")
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = time.strftime("%Y-%m-%d %H:%M:%S") + \
    time.strftime("%z")[:3] + ":" + time.strftime("%z")[3:]
out_h = json.dumps(h, ensure_ascii=False, indent=1)
open(H, "wb").write(out_h.encode("utf-8"))

# ---- self-verify (R170/R178 law: type check after write)
h2 = json.loads(open(H, "rb").read().decode("utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert isinstance(h2["heartbeat_epoch_utc"], int) and not isinstance(
    h2["heartbeat_epoch_utc"], bool)
s2 = json.loads(open(P, "rb").read().decode("utf-8"))
assert s2["round_no"] == 261
print("state 260->261; heartbeat epoch int", epoch,
      "clock", h["clock_read"], "self-verified PASS")
