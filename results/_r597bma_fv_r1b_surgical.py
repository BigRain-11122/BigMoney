import subprocess, os, sys

FV = r"C:\Users\sjs20\Desktop\FluxGroup\gaming\FluxVerse"
MSG = os.path.join(FV, ".codely-cli-scratch-msg.txt") if os.path.isdir(FV) else None
SCRATCH = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\.codely-cli\scratch\fv_r1b_msg.txt"

PRODUCTS = [
    "City3D-staging/citysim-residents.done",
    "City3D-staging/citysim-residents-report.md",
    "City3D-staging/shots8/B_R1a_residents_overview.jpg",
    "City3D-staging/shots8/B_R1b_idle_group.jpg",
    "City3D-staging/shots8/B_R1c_walk_loop.jpg",
    "City3D-staging/shots8/B_R1d_single.jpg",
    "City3D/Assets/Scenes/CitySim_ResidentsR1.unity",
    "City3D/Assets/Scenes/CitySim_ResidentsR1.unity.meta",
]

def run(cmd, cwd=FV, env=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, env=env)
    out = r.stdout.decode("utf-8", "replace")
    if check and r.returncode != 0:
        print("FAIL:", cmd[:6], r.stderr.decode("utf-8", "replace")[:400])
        sys.exit(1)
    return out

base = run(["git", "rev-parse", "origin/main"]).strip()
head = run(["git", "rev-parse", "HEAD"]).strip()
assert base == head, ("origin moved or not synced", base, head)
print("base = HEAD =", base[:10])

# temporary index (r523 surgical route; shared index with foreign staged set untouched)
idx = os.path.join(FV, ".git", "tmp-r1b-index")
env = dict(os.environ, GIT_INDEX_FILE=idx)
if os.path.exists(idx):
    os.remove(idx)
run(["git", "read-tree", base], env=env)
for p in PRODUCTS:
    sha = run(["git", "hash-object", "-w", "--", p], env=env).strip()
    run(["git", "update-index", "--add", "--cacheinfo", f"100644,{sha},{p}"], env=env)
tree = run(["git", "write-tree"], env=env).strip()
print("tree:", tree[:10])

# payload assertions (r523 three-assert face)
base_tree = run(["git", "rev-parse", base + "^{tree}"]).strip()
diff = run(["git", "diff-tree", "--no-renames", "--name-status", "-r", base_tree, tree])
lines = [l.split("\t") for l in diff.splitlines() if l.strip()]
dels = [p for st, p in lines if st == "D"]
adds = [p for st, p in lines if st == "A"]
mods = [p for st, p in lines if st == "M"]
print("A:", len(adds), "M:", len(mods), "D:", dels)
assert not dels, ("deletion-set must be empty", dels)
assert set(adds + mods) <= set(PRODUCTS), ("payload superset violation", set(adds + mods) - set(PRODUCTS))
assert set(adds + mods) == set(PRODUCTS), ("payload missing files", set(PRODUCTS) - set(adds + mods))

msg = """A leg R1 re-run receipt (O-20261002-2124 ruling B, bm-a executor, base 627e993)

One-command re-run after ruling B (assertions 20->32 + five-piece bake):
RunResidentsAll @ Tuanjie 2022.3.62t15 batchmode, ~50s warm run.

Result: FAIL-loud x1 (honest, no assertion-line touch):
- 7/9 substantive rows PASS: R1 roster 32/32 (id/named/prof complete),
  R2 AD-042 forms 19/19, R3 Hunyuan imports (walk/idle 4.97s clips),
  R5 spawn 32/32 + Animator ctrl+avatar bound 32/32 + ResidentMode 32/32
  + walkers 16, R4 retarget live-measured (walk half-cycle pose diff
  3.535m > 0.02, idle 0.177m), R6 editor-state walk displacement 6.00m
  in 5.0s (> 4), R7 mapping determinism 32/32 double-hash zero mismatch.
- R0 AD-042 Character.fbx Humanoid-ized Avatar NOT obtained: FAIL
  (the ruling's pre-declared residual risk single-point -- Synty base
  model avatar fetch; C-leg code face, bm-c diagnosis pointer).
- R8 frames 4/4 saved (shots8/B_R1a-d, <65KB each; stills show spawned
  residents with materials applied; T-pose in stills = batch still-
  capture artifact outside the R4/R6 editor-state sampling window).

Products: report.md + .done + B_R1a-d x4 + CitySim_ResidentsR1 scene
(+meta). Motions/ FBX excluded per order (git-banned). Shared-index
staged world-lane files untouched (surgical commit-tree route).

Verdict pointer for bm-c: R0 fetch likely needs reimport cycle after
Humanoid meta write or a different Avatar sub-asset fetch path; batch
code is C-leg authored, no local hard-fix per order discipline.
"""
with open(SCRATCH, "w", encoding="utf-8") as f:
    f.write(msg)
commit = run(["git", "commit-tree", tree, "-p", base, "-F", SCRATCH], env=env).strip()
print("commit:", commit[:10])
r = subprocess.run(["git", "push", "origin", commit + ":main"], cwd=FV, capture_output=True)
print("push rc:", r.returncode, r.stdout.decode("utf-8", "replace")[-200:], r.stderr.decode("utf-8", "replace")[-200:])
if r.returncode == 0:
    run(["git", "update-ref", "refs/heads/main", commit, base])
    print("local main moved to", commit[:10])
