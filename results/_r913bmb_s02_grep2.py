# r913 bm-b: grep group origin tree for 安明远 context + extract charter/spec faces (read-only)
# Usage: python results/_r913bmb_s02_grep2.py
import subprocess

PAIRS = [
    ("cph4/fleet/shortvideo-dept/DEPT-CHARTER.md", "results/_r913bmb_sv_charter.md"),
    ("cph4/fleet/meme-daily-v1/SPEC-ACCOUNT.md", "results/_r913bmb_meme_spec.md"),
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
