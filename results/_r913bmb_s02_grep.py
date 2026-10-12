# r913 bm-b: grep group origin tree for Speech-02 context lines (read-only, raw bytes to files)
# Usage: python results/_r913bmb_s02_grep.py
import subprocess

PAIRS = [
    ("cph4/fleet/dispatcher/POOL.json", "results/_r913bmb_pool_face.json"),
    ("cph4/fleet/token-ledger/LEDGER.md", "results/_r913bmb_ledger_face.md"),
]

for src, dst in PAIRS:
    d = subprocess.run(
        ["git", "-C", "C:/Fluxgroup/FluxGroup", "show", "origin/main:" + src],
        capture_output=True,
    ).stdout
    if d:
        with open(dst, "wb") as f:
            f.write(d)
        print(dst, len(d))

# also grep the whole tree for speech-02 with 2 lines of context, dump raw
r = subprocess.run(
    ["git", "-C", "C:/Fluxgroup/FluxGroup", "grep", "-i", "-C", "2", "speech-02", "origin/main"],
    capture_output=True,
)
with open("results/_r913bmb_s02_grep_raw.txt", "wb") as f:
    f.write(r.stdout)
print("grep bytes", len(r.stdout))
