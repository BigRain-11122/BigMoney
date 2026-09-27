"""r350 bm-a rebase storm probe: inspect union-family conflict blobs (stage :2: = bmc-r100, :3: = bma-R350)."""
import subprocess
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def blob(stage, path):
    return subprocess.run(["git", "cat-file", "-p", f"{stage}{path}"], capture_output=True).stdout


for path in ["results/compute_audit.json", "results/regime_state.json", "results/autofill_state.json"]:
    for stage, label in [(":2:", "ours=bmc"), (":3:", "theirs=bma")]:
        d = json.loads(blob(stage, path))
        print("==", path, label)
        print(" keys:", list(d.keys())[:14])
        for k in ("history", "launches", "transitions"):
            if k in d and isinstance(d[k], list) and d[k]:
                print(" ", k, "len=", len(d[k]),
                      "first_ts=", d[k][0].get("ts"), "last_ts=", d[k][-1].get("ts"))
    print()

x2a = blob(":2:", "results/x2_watch_log.jsonl").decode("utf-8", errors="replace").splitlines()
x2b = blob(":3:", "results/x2_watch_log.jsonl").decode("utf-8", errors="replace").splitlines()
print("x2 ours lines:", len(x2a), "theirs lines:", len(x2b), "| union:", len(set(x2a) | set(x2b)))
print("ours-only:", len(set(x2a) - set(x2b)), "| theirs-only:", len(set(x2b) - set(x2a)))
