import subprocess, os, json, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TMP = os.path.join(REPO, "results", "_r587bma_tmp_index5")

def git(args, env=None, check=True):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=e)
    if check and r.returncode != 0:
        print("GIT FAIL:", args, r.stdout, r.stderr); sys.exit(1)
    return r

git(["fetch", "origin"])
base = git(["rev-parse", "origin/main"]).stdout.strip()
print("base:", base)

MOD = ["scripts/perpetual_faces.py", "scripts/perpetual_faces_n1.py", "research/PERPETUAL_FACES.md"]
NEW = ["research/PERPETUAL_N1_W107_PREREG.md",
       "results/_r587bma_w107_band_gate.py",
       "results/_r587bma_w107_freeze_edits.py",
       "results/_r587bma_w107_prereg_gen.py",
       "results/_r587bma_w101_delivery.py"]
POOL = "results/pool_core_samples.jsonl"

origin_set = set(git(["ls-tree", "-r", "--name-only", "origin/main"]).stdout.strip().splitlines())
for f in NEW:
    assert f not in origin_set, "already on origin: " + f
for f in MOD:
    assert f in origin_set, "missing on origin: " + f

# FIX-C gate: pure insertion check for the 3 edited faces vs origin
for p in MOD:
    out = git(["diff", "origin/main", "--numstat", "--", p]).stdout.strip()
    assert out, "no diff for " + p
    add, dele, path = out.splitlines()[0].split("\t")
    assert int(dele) == 0, f"PURE-INSERTION VIOLATED for {p}: -{dele}"
    print(f"pure-insertion gate: {p} +{add} -0")

# pool union onto CURRENT origin blob (r570/r580 law, dict-gated)
oblob = git(["show", "origin/main:" + POOL]).stdout.replace("\r\n", "\n")
olines = [l for l in oblob.split("\n") if l.strip()]
ltext = open(os.path.join(REPO, POOL), "rb").read().decode("utf-8", errors="replace").replace("\r\n", "\n")
llines = [l for l in ltext.split("\n") if l.strip()]
oset = set(olines)
extra = [l for l in llines if l not in oset]
for l in extra:
    assert isinstance(json.loads(l), dict), "non-dict extra row"
merged = olines + extra
for l in merged:
    assert isinstance(json.loads(l), dict)
open(os.path.join(REPO, POOL), "wb").write(("\n".join(merged) + "\n").encode("utf-8"))
print("pool union: origin", len(olines), "+ extra", len(extra), "=", len(merged))

env = {"GIT_INDEX_FILE": TMP}
if os.path.exists(TMP): os.remove(TMP)
git(["read-tree", "origin/main"], env=env)
for f in MOD + NEW + [POOL]:
    sha = git(["hash-object", "-w", f]).stdout.strip()
    git(["update-index", "--add", "--cacheinfo", "100644", sha, f], env=env)
tree = git(["write-tree"], env=env).stdout.strip()
otree = git(["rev-parse", "origin/main^{tree}"]).stdout.strip()
delta = git(["diff-tree", "-r", "--name-status", otree, tree]).stdout.strip().splitlines()
changed = set(l.split("\t")[-1] for l in delta)
assert changed == set(MOD + NEW + [POOL]), changed ^ set(MOD + NEW + [POOL])
for l in delta:
    st = l.split("\t")[0]
    assert st.startswith(("A", "M")), l
print("tree-delta PASS:", len(delta), "entries")

msg = os.path.join(REPO, "results", "_r587bma_msg5.txt")
with open(msg, "w", encoding="utf-8", newline="\n") as f:
    f.write("round 587 bm-a: W107 FREEZE five-face delivered (seat MSG-20261002-1759-bma pre-published "
            "d548df902 per r565 law; band gate ADMIT rc0 A 257_004..259_003 / B 60_401..60_600 hops 0/0 "
            "arithmetic continuation from the registered W106 tails, results/_r587bma_w107_band_gate.py; "
            "banned gate ADMIT 0; 97th engine wave by machine-derive (engine_owner rows 96 + candidate), "
            "bm-a 30th owned; single state zero seat gap after the REGISTERED W106 row; per-wave prereg "
            "frozen with anchors rolled to W101 finalize landed values (chain head 586,748, K=220,120, "
            "r576 anchor-roll law); n1 selftest PASS with W107 materializer leg live; FIX-A/B/C gates "
            "green, pure insertion +29/+177/+2; pool union rows appended dict-gated). "
            "Engine ignition expected within 2 ticks per r535 law (bm-a tick architecture). [via bm-a r587]")
c = subprocess.run(["git", "commit-tree", tree, "-p", "origin/main", "-F", msg], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
if c.returncode != 0: print("CT FAIL:", c.stderr); sys.exit(1)
sha = c.stdout.strip(); print("commit:", sha)
p = subprocess.run(["git", "push", "origin", sha + ":main"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("push rc:", p.returncode, p.stdout.strip()[:60], p.stderr.strip()[:120])
if p.returncode != 0: sys.exit(1)
git(["fetch", "origin"])
bad = [f for f in MOD + NEW + [POOL] if len(subprocess.run(["git", "ls-tree", "origin/main", "--", f], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.split()) < 3]
print("delivery:", len(MOD + NEW) + 1 - len(bad), "ok,", len(bad), "bad")
os.remove(TMP); os.remove(msg)
print("FREEZE_SHA:", sha)
