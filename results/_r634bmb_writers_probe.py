"""r634 bm-b: nulls writers forensics -- who is appending, at what rate."""
import json
import os
import time

import psutil  # type: ignore

now = time.time()
for fam in ("fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"):
    p = rf"results/{fam}/nulls.jsonl"
    st = os.stat(p)
    lines = sum(1 for _ in open(p, encoding="utf-8"))
    print(
        fam,
        "lines=", lines,
        "mtime_age_min=", round((now - st.st_mtime) / 60, 1),
    )

# any python processes touching these files?
for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
    try:
        cmd = " ".join(proc.info["cmdline"] or [])
        if "fund" in cmd and ("nulls" in cmd or "pool" in cmd or "worker" in cmd):
            print(
                "PROC",
                proc.info["pid"],
                "age_min=",
                round((now - proc.info["create_time"]) / 60, 1),
                cmd[:160],
            )
    except Exception:
        pass
