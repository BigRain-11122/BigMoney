# -*- coding: utf-8 -*-
"""r378 V2-P1 defer entry forensics: fields at defer commit vs parent."""
import io
import json
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def entry_at(rev):
    p = subprocess.run(["git", "show", f"{rev}:results/runnable_pool.json"],
                       capture_output=True)
    j = json.loads(p.stdout.decode("utf-8-sig"))
    return [e for e in j["entries"] if e["id"] == "DECISION-CHAIN-V2-P1"][0]


for rev in ("dc3067a0", "4cdc710f", "HEAD"):
    e = entry_at(rev)
    keys = ("status", "entered_at", "updated_at", "defer_note", "defer_ts",
            "lane_note", "lane_owner")
    print(rev, {k: (e.get(k) if k != "defer_note" else str(e.get(k))[:120])
                for k in keys})
