# r379 pre-claim origin truth check (r239 collision law): W110 seat? W104 finalize? registry tail?
import subprocess

def gitb(args):
    r = subprocess.run(["git"] + args, capture_output=True)
    return r.returncode, r.stdout

gitb(["fetch", "origin"])
rc, out = gitb(["log", "--oneline", "-6", "origin/main"])
print("=== origin last 6 ===")
print(out.decode("utf-8", "replace"))
# registry rows: which waves registered (engine_owner field)
rc, blob = gitb(["show", "origin/main:research/PERPETUAL_FACES.md"])
txt = blob.decode("utf-8", "replace")
rows = [l for l in txt.splitlines() if l.strip().startswith("|") and "W1" in l]
print("=== registry table rows (last 5) ===")
for l in rows[-5:]:
    print(l[:220])
# W110 seat MSG on origin?
rc, tree = gitb(["ls-tree", "--name-only", "origin/main", "fleet/inbox/"])
names = tree.decode("utf-8", "replace").splitlines()
print("=== origin inbox ===")
for n in names:
    print(n)
# W104 finalize landed? (n1_w104_results.json chain face)
rc, f104 = gitb(["ls-tree", "--name-only", "origin/main", "results/n1_w104_results.json"])
print("w104_finalize_face_on_origin:", bool(f104.strip()), f104.decode("utf-8", "replace").strip()[:120])
