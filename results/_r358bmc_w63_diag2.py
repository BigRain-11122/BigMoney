# r358 bm-c: W63 holes probe part 2 -- queue_next/complete flags/quarantine.
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
d = json.load(open(os.path.join(ROOT, "results", "saturation_engine_state.bm-c.json"), "rb"))

for k in ("queue_next", "wave_complete_flags", "quarantined", "crash_counts",
          "completed", "ignitions", "cycle", "done_count", "append_pending",
          "append_err", "sync", "grammar_consumption", "heartbeat_epoch",
          "last_cycle_ts"):
    v = d.get(k)
    s = json.dumps(v, ensure_ascii=False)
    print("%s = %s" % (k, s[:900]))
    print()
