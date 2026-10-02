"""r607 bm-a S0 fix: take origin verbatim for ALL other-machine-owned faces
that the blob discriminator left in KEEP_LOCAL (local copies are stale S0
checkout leftovers from earlier integrations, not local daemon writes).
Per r381 (origin verbatim for other machines' faces) + r587 (never commit
stale copies over other machines' live faces)."""
import subprocess, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
OTHER_MACHINE = [
    "fleet/machines/bm-c.json",
    "results/autofill_state.bm-c.json",
    "results/compute_audit.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/futures_update_status.bm-c.json",
    "results/lhb_update_status.bm-c.json",
    "results/pool_dualrun.bm-c.jsonl",
    "results/regime_state.bm-c.json",
    "results/runnable_pool.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/token_usage.bm-c.json",
    "results/update_status.bm-c.json",
    "round_reports-bm-c.md",
    "state-bm-c.json",
]

def git(*args):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True)
    return r.returncode, r.stdout, r.stderr

# only touch files that are still dirty (origin advanced them); if not dirty, skip
rc, out, err = git("status", "--porcelain")
dirty = set()
for ln in out.decode("utf-8", "replace").splitlines():
    if not ln.strip():
        continue
    dirty.add(ln[3:])

to_fix = [p for p in OTHER_MACHINE if p in dirty]
print("taking origin for other-machine faces:", len(to_fix))
if to_fix:
    rc, out, err = git("checkout", "--", *to_fix)
    print("checkout:", "OK" if rc == 0 else f"FAIL {err.decode('utf-8','replace')}")
    if rc != 0:
        sys.exit(1)
    for p in to_fix:
        print("  ", p)

# post-verify: remaining dirty set must contain ONLY bm-a-owned / bm-a-hosted faces
rc, out, err = git("status", "--porcelain")
remain = [ln[3:] for ln in out.decode("utf-8", "replace").splitlines() if ln.strip()]
print(f"\nremaining dirty: {len(remain)}")
bad = [p for p in remain if (".bm-c." in p or ".bm-b." in p or p in ("round_reports-bm-c.md", "state-bm-c.json", "fleet/machines/bm-c.json", "fleet/machines/bm-b.json"))]
print("other-machine faces still dirty:", bad if bad else "NONE")
print("DONE")
