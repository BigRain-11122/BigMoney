# -*- coding: utf-8 -*-
"""r359 bm-a control-plane restoration: CENSUS-FUS-S2-W2B pool entry was
accidentally dropped from results/runnable_pool.json in bm-b r340 commit
50ea26ef (network-dead local-mode commit clobbered the union; every round
report since still says 'W2-B waiting double-dep' -- silent loss). Restore
the entry VERBATIM from its only authoritative version (f5822d92, added by
bm-a R345; git log -S shows exactly add f5822d92 -> remove 50ea26ef, no
intermediate edits). Zero science faces touched; lane_owner stays bm-b;
deps unchanged (D8-receive + W2-A finalize per MSG-1912/2055)."""
import json
import os
import subprocess
import sys
import time

POOL = "results/runnable_pool.json"


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def main():
    blob = subprocess.run(
        ["git", "show", "f5822d92:results/runnable_pool.json"],
        capture_output=True).stdout.decode("utf-8")
    hist = json.loads(blob)
    hist_ents = hist["entries"] if isinstance(hist, dict) else hist
    w2b = [e for e in hist_ents if e.get("id") == "CENSUS-FUS-S2-W2B"]
    assert len(w2b) == 1, f"history W2B count={len(w2b)}"
    entry = w2b[0]

    with open(POOL, encoding="utf-8") as fh:
        pool = json.load(fh)
    ids = [e.get("id") for e in pool["entries"]]
    assert "CENSUS-FUS-S2-W2B" not in ids, "W2B already present -- abort"
    n_before = len(ids)

    pool["entries"].append(entry)
    pool["updated_at"] = now()
    tmp = POOL + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, POOL)

    # reload-verify: entry count +1 and restored object deep-equal to history
    with open(POOL, encoding="utf-8") as fh:
        pool2 = json.load(fh)
    got = [e for e in pool2["entries"] if e.get("id") == "CENSUS-FUS-S2-W2B"]
    assert len(got) == 1 and got[0] == entry, "restore verify FAILED"
    print(f"restore OK: entries {n_before}->{len(pool2['entries'])} "
          f"(+1 CENSUS-FUS-S2-W2B verbatim from f5822d92)")
    print(f"restored face: status={entry['status']} lane_owner="
          f"{entry.get('lane_owner')} entered_at={entry.get('entered_at')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
