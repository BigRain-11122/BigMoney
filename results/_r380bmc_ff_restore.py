# -*- coding: utf-8 -*-
# r380 post-surgical faceted checkout (r578 law; strip-free line parsing per this round's new pit law)
import subprocess

CWD = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = 0x08000000
LIVE = {
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
}

def git(*a):
    return subprocess.run(["git"] + list(a), cwd=CWD, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", creationflags=CNW)

r = git("status", "--porcelain")
lines = [l for l in r.stdout.split("\n") if l.strip()]  # no whole-output strip!
restore, keep = [], []
for l in lines:
    code = l[:2].strip()
    path = l[3:].strip().strip('"')
    if path in LIVE:
        keep.append(path)
    else:
        restore.append(path)
print(f"restore={len(restore)} keep(live)={len(keep)}")
fails = []
for p in restore:
    rr = git("checkout", "--", p)
    if rr.returncode != 0:
        fails.append((p, rr.stderr.strip()[:120]))
print("checkout fails:", fails)
final = [l[3:].strip().strip('"') for l in git("status", "--porcelain").stdout.split("\n") if l.strip()]
print("final face:", final)
assert set(final) == LIVE, f"unexpected: {set(final) ^ LIVE}"
behind = git("rev-list", "--count", "HEAD..origin/main").stdout.strip()
head = git("rev-parse", "HEAD").stdout.strip()
print(f"HEAD={head[:12]} behind-origin={behind}")
assert behind == "0"
print("FACETED CHECKOUT OK")
