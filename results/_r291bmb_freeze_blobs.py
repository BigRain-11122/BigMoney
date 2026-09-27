# r291 bm-b: freeze UU blob sides for autofill_state.json before any tick blind-add
# (r335 pitfall: tick add/stash legs are not guarded mid-rebase; :2:/:3: die after any git add)
import subprocess, hashlib, os

def blob_bytes(spec):
    return subprocess.run(["git", "show", spec], capture_output=True, check=True).stdout

os.makedirs("results/_r291bmb_blobs", exist_ok=True)
sides = {
    "ours.r291bmb.json": ":2:results/autofill_state.json",     # origin/main side (other machine)
    "theirs.r291bmb.json": ":3:results/autofill_state.json",  # my tick self-commit side
    "base.r291bmb.json": "133454837fa7173d66144c8bf5432e804ab2328d:results/autofill_state.json",  # parent of replayed commit
}
for name, spec in sides.items():
    b = blob_bytes(spec)
    p = os.path.join("results/_r291bmb_blobs", name)
    with open(p, "wb") as f:
        f.write(b)
    print(name, len(b), hashlib.sha256(b).hexdigest()[:16])
