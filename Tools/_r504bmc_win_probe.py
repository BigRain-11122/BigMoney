"""r504 bm-c: (a) pool N2-W15 shard statuses; (b) group decisions D-20261004-05
/ D-20261002-02/03 window context (raw-blob read, zero tree touch)."""
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))


def main():
    # (a) pool shard statuses
    with open(os.path.join(ROOT, "results", "runnable_pool.json"),
              encoding="utf-8-sig") as fh:
        pool = json.load(fh)
    n = 0
    for e in pool.get("entries", []):
        eid = e.get("id", "")
        if "N2-W15" in eid or "N2-W15" in e.get("ticket_ref", ""):
            n += 1
            print("SHARD", eid, "| status=%s" % e.get("status"),
                  "| lane=%s" % e.get("lane_owner"),
                  "| since=%s" % e.get("owner_since", e.get("entered_at", "?")))
    print("N2-W15-ENTRIES", n)

    # (b) decisions context
    r = subprocess.run(
        ["git", "show", "origin/main:docs/decisions.md"],
        capture_output=True, cwd=GROUP, creationflags=CREATE_NO_WINDOW)
    text = (r.stdout or b"").decode("utf-8", "replace")
    for key in ("D-20261004-05", "D-20261002-02", "D-20261002-03"):
        idx = text.find(key)
        print("=== %s %s ===" % (key, "FOUND" if idx >= 0 else "MISSING"))
        if idx >= 0:
            print(text[idx:idx + 700])


if __name__ == "__main__":
    main()
