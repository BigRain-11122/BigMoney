# r357 bm-c W63 FREEZE surgical CAS push (five faces + probe provenance).
# Laws: r532 no-rebase route, r530 diff-based payload + deletion-set empty,
# r531 parent rev-parse at push time, r516 delivery self-verify, r511/r518
# seat discipline (origin vacancy re-checked at push time).
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PAYLOAD_ADD = [
    "research/PERPETUAL_N1_W63_PREREG.md",
    "results/_r357bmc_w63_band_gate.py",
    "results/_r357bmc_w63_band_probe.py",
]
PAYLOAD_MOD = [
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py",
    "research/PERPETUAL_FACES.md",
]
ALL = PAYLOAD_ADD + PAYLOAD_MOD

MSG = ("W63 FREEZE (never-dry standing step + de-throttle own-series): "
       "FIFTY-SECOND ENGINE-OWNED WAVE, bm-c's TWENTIETH owned per "
       "machine-derive (engine_owner==bm-c rows 19 + candidate), wave 63 "
       "= first free number after the registered W62 row (chain FULLY "
       "CAUGHT UP W1..W62 at this freeze -- W61+W62 one-pass double "
       "finalize same-window by bm-c r357: 2eb556a8f ledger 498,748 + "
       "c2d4fb7a9 ledger 500,948 K=134,320, ZERO in-flight upstream "
       "seats; origin slot vacancy machine-checked at gate leg3); A "
       "ARITHMETIC CONTINUATION no skip (169_004..171_003 machine-derived "
       "CLEAN == the W62 row W63+ published projection verbatim, bm-a "
       "r565 gate + this gate cross-validated); B FORCED SKIP past "
       "SEED_REGISTRY p4_ext_tilt_q=49_000 and p4_ext_tilt_d20=49_100 "
       "(arithmetic 48_801..49_000 and chained 49_001..49_200 both "
       "REFUSED; first clean window 49_201..49_400 machine-derived, "
       "W26-A/W39-B/W43-B/W47-B/W51-B/W59-B skip family, r307 tail "
       "law); ADMIT receipt results/_r357bmc_w63_band_gate.py (leg0 "
       "61-keys + leg0b W62-row W63+ prose + leg1-A CLEAN + leg1-B "
       "refusal-point 49_000 + leg2 chained-skip first-clean + leg3 "
       "ADMIT + N3-R1 leg + probe-cluster leg + origin slot vacancy); "
       "banned gate ADMIT (zero matched); W64+ projection A "
       "171_004..173_003 CLEAN / B 49_401..49_600 CLEAN (machine-"
       "derived); prereg PERPETUAL_N1_W63_PREREG.md frozen (anchor=W62 "
       "landed K=134,320 head 500,948, ZERO in-flight upstream seats, "
       "cumulative pool projection 136,520, S5 anchors from W62 "
       "actuals: merged mu -0.092547 / W62-only mu -0.100936 / sigma "
       "0.239601 / A-p95 0.3037 / K-lift -0.0006); runner "
       "WAVE_CONFIGS[63] + W63 materializer selftest leg + canon W63 "
       "row; selftest PASS (default-wave call, full chain W2..W63; "
       "indent-corruption in the insert fixed content-anchored + "
       "py_compile verified same window) [via bm-c r357]")


def git(args, env=None):
    r = subprocess.run(["git"] + args, cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


rc, _, err = git(["fetch", "origin"])
assert rc == 0, "fetch failed: " + err
rc, parent, err = git(["rev-parse", "origin/main"])
assert rc == 0, err

# seat discipline: W63 must NOT already be registered on origin
rc, out, err = git(["show", "origin/main:scripts/perpetual_faces.py"])
assert rc == 0, err
assert "63: {\"a\": (169_004" not in out, \
    "W63 row already on origin -- seat taken (r511), abort"
rc, out, err = git(["cat-file", "-e", "origin/main:"
                    "research/PERPETUAL_N1_W63_PREREG.md"])
assert rc != 0, "W63 prereg already on origin -- seat taken (r511), abort"

env = os.environ.copy()
idx = os.path.join(ROOT, ".git", "r357bmc-w63f-index")
if os.path.exists(idx):
    os.remove(idx)
env["GIT_INDEX_FILE"] = idx


def giti(args):
    rc, o, e = git(args, env=env)
    assert rc == 0, " ".join(args) + " -> " + e
    return o


giti(["read-tree", parent])
for p in ALL:
    rc, blob, err = git(["hash-object", "-w", p])
    assert rc == 0, err
    giti(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, p)])
tree = giti(["write-tree"])

# payload + deletion-set assertions (r530/r519 claw)
rc, diffout, err = git(["diff-tree", "-r", "--name-status", parent, tree])
assert rc == 0, err
lines = [l for l in diffout.splitlines() if l.strip()]
adds = [l for l in lines if l.startswith("A")]
mods = [l for l in lines if l.startswith("M")]
dels = [l for l in lines if l.startswith("D")]
assert not dels, "DELETION SET NON-EMPTY -- ABORT (r530 law): " + diffout
assert sorted(l.split("\t", 1)[1] for l in adds) == sorted(PAYLOAD_ADD), \
    "unexpected adds: " + diffout
assert sorted(l.split("\t", 1)[1] for l in mods) == sorted(PAYLOAD_MOD), \
    "unexpected mods: " + diffout

commit = giti(["commit-tree", tree, "-p", parent, "-m", MSG])
rc, out, err = git(["push", "origin", commit + ":main"])
if rc != 0:
    print("PUSH_REJECTED parent=%s err=%s" % (parent, err))
    sys.exit(2)
print("PUSHED commit=%s parent=%s" % (commit, parent))

# delivery self-verify (r516)
rc, _, err = git(["fetch", "origin"])
assert rc == 0, err
rc, head2, err = git(["rev-parse", "origin/main"])
assert rc == 0, err
assert head2 == commit, "origin moved post-push: %s vs %s" % (head2, commit)
rc, out, err = git(["show", "origin/main:scripts/perpetual_faces.py"])
assert rc == 0 and "63: {\"a\": (169_004" in out, \
    "delivery check failed: W63 row not on origin"
print("DELIVERED W63 FREEZE five faces + probe receipt on origin")
