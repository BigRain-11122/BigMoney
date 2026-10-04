"""r686 bm-b: quarantine-move this round's reading-scratch files (zero-hit
prescan rc0 receipt above; O-2030 §2 quarantine mode, 7-day observation)."""
import json
import os
import time

QDIR = os.path.join("results", "_quarantine",
                    time.strftime("%Y%m%dT%H%M") + "_r686bmb_scratch")
os.makedirs(QDIR, exist_ok=True)
FILES = [
    "results/_r686bmb_ctx.txt", "results/_r686bmb_ctx2.txt",
    "results/_r686bmb_ctx3.txt", "results/_r686bmb_ctx4.txt",
    "results/_r686bmb_ctx5.txt", "results/_r686bmb_ctx6.txt",
    "results/_r686bmb_bmc_tail.txt", "results/_r686bmb_codely_tail.txt",
    "results/_r686bmb_handover_ctx.txt", "results/_r686bmb_handover_tail.txt",
    "results/_r686bmb_t148.txt", "results/_r686bmb_t148b.txt",
    "results/_r686bmb_t153.txt", "results/_r686bmb_w3_sec4.txt",
    "results/_r686bmb_w3_sec8.txt", "results/_r686bmb_w3_sec9.txt",
    "results/_r686bmb_w3prereg_dump.py", "results/_r686bmb_w3prereg_secs.txt",
    "results/_r686bmb_sched_trio.txt", "results/_r686bmb_scan_-bm.txt",
    "results/_r686bmb_decisions_fresh.md", "results/_r686bmb_orders_fresh.md",
    "results/_r686bmb_extract_reports.py",
]
manifest = {"moved": [], "missing": [], "reason":
            "r686 bm-b reading-scratch cleanup; prescan zero-hit rc0 16:3x; "
            "7-day observation window then sweep"}
for f in FILES:
    if os.path.exists(f):
        dst = os.path.join(QDIR, os.path.basename(f))
        os.replace(f, dst)
        manifest["moved"].append(os.path.basename(f))
    else:
        manifest["missing"].append(f)
json.dump(manifest, open(os.path.join(QDIR, "manifest.json"), "w",
                          encoding="utf-8"), ensure_ascii=True, indent=1)
# post-sweep assert: none of the moved names remain in results/
leftover = [f for f in FILES if os.path.exists(f)]
assert not leftover, "quarantine incomplete: %s" % leftover
print("quarantined:", len(manifest["moved"]), "->", QDIR)
