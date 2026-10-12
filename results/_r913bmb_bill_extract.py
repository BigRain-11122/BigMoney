# r913 bm-b: extract group-repo origin blobs to local results faces (raw bytes, zero tree touch)
# Usage: python results/_r913bmb_bill_extract.py
import subprocess

PAIRS = [
    ("cph4/fleet/memory/CODELY-fleet-global.md", "results/_r913bmb_fleet_global.md"),
    ("cph4/fleet/mv-album-001-jay/RESEARCH-星晴-受众洞察-v1.md", "results/_r913bmb_mv_research.md"),
]

for src, dst in PAIRS:
    d = subprocess.run(
        ["git", "-C", "C:/Fluxgroup/FluxGroup", "show", "origin/main:" + src],
        capture_output=True,
    ).stdout
    if not d:
        print("EMPTY/MISSING", src)
        continue
    with open(dst, "wb") as f:
        f.write(d)
    print(dst, len(d))
