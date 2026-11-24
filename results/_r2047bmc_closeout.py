"""r2047 closeout (bm-c): state round bump + heartbeat fields, merge-only.

    python results/_r2047bmc_closeout.py
"""

import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
FIELDS = os.path.join(ROOT, "results", "_r2047bmc_hb_fields.json")
ROUND = 2047
FACE = "results/cash_shelf_total_return_audit.json"
DOC = "research/CASH_SHELF_TOTAL_RETURN.md"


def main():
    face = json.load(io.open(os.path.join(ROOT, FACE), encoding="utf-8"))
    h = face["headline"]
    st = json.load(io.open(STATE, encoding="utf-8"))
    prev = st.get("round_no")
    st["round_no"] = ROUND
    st["round"] = ROUND
    st["cur_task"] = "r2047 total-return audit of the five cash shelves"
    st["last_round"] = {
        "round_no": ROUND,
        "date": time.strftime("%Y-%m-%d"),
        "kind": "new_file_face_contention_window",
        "artifact_json": FACE,
        "artifact_doc": DOC,
        "script": "scripts/cash_shelf_total_return_audit.py",
        "negative_control": "results/_r2047bmc_totalret_negative.py",
        "selftest": "22/22 PASS",
        "check": "rc0",
        "negative": "10/10 PASS",
        "reading": {
            "price_only_understates": h["price_only_understates"],
            "already_counted": h["already_counted"],
            "no_distributions": h["no_distributions"],
            "threshold_reader_over_repairs": h["threshold_reader_over_repairs"],
        },
        "contention": ("rc3 CONTENTION: interactive host alive in this tree; "
                       "new-file faces only, S6 chain and full smoke still deferred"),
    }
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
        f.write("\n")

    now = time.localtime()
    iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", now)
    fields = {
        "cur_task": st["cur_task"],
        "round": ROUND,
        "round_no": ROUND,
        "last_round_no": ROUND,
        "heartbeat_epoch_utc": int(time.time()),
        "clock_read": iso,
        "ts": iso,
        "agenda_starved": False,
        "idle_rounds": 0,
        "r2047_verdict": ("511010 price-only understates its extra by 2593.71 CNY/yr "
                          "(3241.89 -> 5835.60); 511880 already on the sourced caliber "
                          "(money reader zeroes its 13 ex-dates); 511360/511380/511180 "
                          "pay no distributions so their wait readings stand"),
        "r2047_artifacts": [FACE, DOC, "scripts/cash_shelf_total_return_audit.py"],
        "r2047_contention": "rc3; new-file faces only; S6 chain + full smoke deferred",
    }
    with io.open(FIELDS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(fields, f, ensure_ascii=False, indent=2)
        f.write("\n")

    r = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "heartbeat_write.py"),
                        "apply", "--fields", FIELDS], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip().splitlines()
    print("STATE round %s -> %s" % (prev, st["round_no"]))
    print("HEARTBEAT rc=%d %s" % (r.returncode, out[-1][:400] if out else (r.stderr or "")[:200]))
    hb = json.load(io.open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
    ok_epoch = isinstance(hb.get("heartbeat_epoch_utc"), int)
    print("HEARTBEAT verify: epoch_int=%s acks=%d round_no=%s"
          % (ok_epoch, len(hb.get("orders_ack") or []), hb.get("round_no")))
    return 0 if (r.returncode == 0 and ok_epoch) else 1


if __name__ == "__main__":
    sys.exit(main())
