"""r365 bm-b: x2_watch_log.jsonl incident recovery + conflict-marker purge.

INCIDENT (self-caught, same round): first resolver version opened the file in
"wb" (truncating to 0 bytes) BEFORE encoding its payload -> TypeError left the
file at 0 bytes; a subsequent `git add` staged the truncated file and the
round-365 baseline commit absorbed it (local-only, unpushed).

RECOVERY: the blob staged by the FIRST `git add -A` (full content, 1131 lines
incl. 3 conflict markers) is still a dangling object. Find it by content
signature via git fsck, purge markers per append-log union recipe (keep BOTH
sides' rows), verify all rows JSON-parse, write back in detected newline mode.
"""
import json
import subprocess
import sys

PATH = r"results\x2_watch_log.jsonl"
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


def sh(args):
    return subprocess.run(args, capture_output=True).stdout


# 1) locate dangling blobs
candidates = []
fsck = sh(["git", "fsck", "--unreachable"]).decode("utf-8", "replace")
for ln in fsck.splitlines():
    parts = ln.split()
    if len(parts) >= 2 and parts[0] == "unreachable" and parts[1] == "blob":
        candidates.append(parts[2])

print(f"dangling blobs={len(candidates)}")
found = None
for sha in candidates:
    blob = sh(["git", "cat-file", "-p", sha])
    if (
        b"<<<<<<<" in blob
        and b"06:33:11" in blob
        and b"06:27:58" in blob
        and b"VOLATILITY-CE-01" in blob
    ):
        found = blob
        print(f"recovered blob={sha}")
        break

assert found is not None, "full-content blob not found among dangling objects"

# 2) purge markers, parse-verify every remaining line (r185 law)
text = found.decode("utf-8")
lines = text.splitlines()
kept, dropped = [], 0
batches = {"06:27": 0, "06:33": 0}
for ln in lines:
    if ln.startswith(MARKERS):
        dropped += 1
        continue
    obj = json.loads(ln)
    kept.append(ln)
    for b in batches:
        if b in obj.get("ts", ""):
            batches[b] += 1

# 3) write back in detected newline mode, bytes-safe
nl = "\r\n" if "\r\n" in text else "\n"
with open(PATH, "wb") as f:
    f.write((nl.join(kept) + nl).encode("utf-8"))

print(f"total_in={len(lines)} kept={len(kept)} markers_dropped={dropped}")
print(f"batch_rows={batches}")
assert dropped == 3
assert len(kept) == len(lines) - 3
assert batches["06:27"] == 6 and batches["06:33"] == 6, "both sides must survive (zero-loss union)"
print("RECOVERY OK: full content restored, markers purged, all rows JSON-valid")
