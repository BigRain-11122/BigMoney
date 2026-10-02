# -*- coding: utf-8 -*-
# _r374bmc_push.py -- r374 surgical push (r532/r523-3/r580bmb-s0-surgery/r373bmc paradigm).
# Diverged base x2 (claw blocked FF pushes twice while origin moved mid-flight);
# local 3 commits ride. Payload = my delta vs fork base 6b8c9fa7c applied onto
# the FRESH origin tip via temp index. Assertions: deletion set == whitelisted
# seat-MSG move only; tree-delta ⊆ payload; CODELY union with concurrent lines.
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = 0x08000000
IDX = os.path.join(ROOT, ".git", "_r374bmc_index")
BASE = "6b8c9fa7c"                      # fork base (my 3 commits sit directly on it)
MOVE_DEL_FROM = "fleet/inbox/MSG-20261002-1625-bmc-w99-seat.md"
MOVE_DEL_TO = "fleet/inbox/processed/MSG-20261002-1625-bmc-w99-seat.md"
MY_PIT_KEY = "r374 bm-c] 带闸 leg0c"


def git(args, env=None, check=True):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CNW, env=e)
    if check and r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (args[:4],
                   r.stderr.decode("utf-8", "replace")[:400]))
    return r


# ---- 0. fresh fetch + origin tip ----
git(["fetch", "origin"])
origin_tip = git(["rev-parse", "origin/main"]).stdout.decode().strip()
print("origin tip: " + origin_tip[:12])

# ---- 1. my delta + their delta (vs fork base) ----
mine = git(["diff", "--name-status", "--no-renames", BASE, "main"]).stdout.decode("utf-8")
theirs = git(["diff", "--name-status", "--no-renames", BASE, origin_tip]).stdout.decode("utf-8")


def parse_status(text):
    out = {}
    for ln in text.splitlines():
        if not ln.strip():
            continue
        parts = ln.split("\t")
        out[parts[-1].strip().strip('"')] = parts[0].strip()
    return out


my_files = parse_status(mine)
their_files = parse_status(theirs)
assert MOVE_DEL_FROM in my_files and my_files[MOVE_DEL_FROM] == "D", my_files.get(MOVE_DEL_FROM)
assert MOVE_DEL_TO in my_files and my_files[MOVE_DEL_TO] == "A"
inter = sorted(set(my_files) & set(their_files))
print("my delta: %d files | their delta: %d files | intersection: %s"
      % (len(my_files), len(their_files), inter))

# ---- 2. CODELY.md union (append-only ledger: origin blob + my line) ----
SRC = os.path.join(ROOT, "CODELY.md")
origin_lf = git(["show", "origin/main:CODELY.md"]).stdout
assert origin_lf.count(b"\r") == 0
local_lf = open(SRC, "rb").read().replace(b"\r\n", b"\n")
o_lines = origin_lf.decode("utf-8").split("\n")
l_lines = local_lf.decode("utf-8").split("\n")
pit_line = next(ln for ln in l_lines if MY_PIT_KEY in ln)
assert pit_line not in o_lines, "my pit line ALREADY on origin (double-union risk)"
assert o_lines.count("### Reference") == 1, "Reference marker not unique on origin"
assert "d19 generic tool bm-b state-file pit" in origin_lf.decode("utf-8") \
    or any("d19" in x and "r582 bm-b" in x for x in o_lines), \
    "bm-b d19 line missing from origin CODELY (union base sanity)"
ref_i = o_lines.index("### Reference")
union = o_lines[:ref_i] + [pit_line] + o_lines[ref_i:]
union_lf = "\n".join(union).encode("utf-8")
assert len(union_lf) == len(origin_lf) + len(pit_line.encode("utf-8")) + 1, (
    "union byte accounting failed", len(union_lf), len(origin_lf))
open(SRC, "wb").write(union_lf.replace(b"\n", b"\r\n"))
print("CODELY union: origin %dB + my pit line %dB == %dB LF (insert before ### Reference)"
      % (len(origin_lf), len(pit_line.encode("utf-8")) + 1, len(union_lf)))

# ---- 3. payload: my delta files (worktree content) ----
payload = sorted(p for p in my_files if p != MOVE_DEL_FROM)
for p in payload:
    assert os.path.exists(os.path.join(ROOT, *p.split("/"))), "payload file missing: " + p

# intersection safety (r580bmb law): CODELY handled by union; machine-local files
# are disjoint by naming; shared derive faces take MY side (re-derived next round)
for p in inter:
    if p == "CODELY.md":
        continue
    assert (".bm-c" in p) or p.endswith("-bm-c.md") or "bmc" in p.lower(), (
        "intersection file is NOT machine-local -- needs manual union: " + p)
    print("intersection machine-local (take mine): " + p)

# ---- 4. temp index: read-tree origin + apply payload + whitelisted move ----
env_idx = {"GIT_INDEX_FILE": IDX}
if os.path.exists(IDX):
    os.remove(IDX)
git(["read-tree", origin_tip], env=env_idx)
git(["add", "--"] + payload, env=env_idx)
git(["update-index", "--force-remove", MOVE_DEL_FROM], env=env_idx)
tree = git(["write-tree"], env=env_idx).stdout.decode().strip()

# assertion A: deletion set == whitelisted seat-MSG move ONLY
delA = git(["diff-tree", "-r", "--diff-filter=D", "--name-only", origin_tip, tree],
           env=env_idx).stdout.decode().strip().splitlines()
assert set(delA) == {MOVE_DEL_FROM}, ("deletion set not whitelisted", delA)
r_has_to = git(["ls-files", "--", MOVE_DEL_TO], env=env_idx).stdout.decode().strip()
assert r_has_to == MOVE_DEL_TO, "move target not present in tree"
print("assertion A PASS: deletion set == seat-MSG move only (inbox->processed whitelist)")

# assertion B: tree-delta ⊆ payload ∪ {move pair}
dset = set(git(["diff-tree", "-r", "--name-only", origin_tip, tree],
               env=env_idx).stdout.decode().strip().splitlines())
pset = set(payload) | {MOVE_DEL_FROM, MOVE_DEL_TO}
assert dset <= pset, ("tree-delta has non-payload files", sorted(dset - pset)[:5])
assert not any(p.startswith("fleet/orders/") for p in dset), "orders dir in payload?!"
for p in sorted(pset - dset):
    r = git(["cat-file", "-e", origin_tip + ":" + p], check=False)
    assert r.returncode == 0, "payload file not in delta AND not on origin: " + p
print("assertion B PASS: tree-delta(%d) subset-of payload(%d) (no-op drops byte-identical to origin)"
      % (len(dset), len(pset)))

# ---- 5. commit-tree + push ----
msg = ("round 374 bm-c: W99 FREEZE five-face (EIGHTY-NINTH wave, bm-c 29th owned; A "
       "241_004..243_003 arithmetic + B 58_551..58_750 D-20261002-05 pinned-skip hops 2; "
       "seat MSG-20261002-1625-bmc pre-pushed r565; banned ADMIT 0; freeze f2191688c) + "
       "engine mtime-reload self-ignition, W99 12/12 burned + S6 37/37 rc0 (dualrun 50/3, "
       "attrition CLEAN) + smoke 47/47 + orders 143/0 + S7 wrap (state 374, heartbeat, "
       "report, seat MSG archived) + CODELY pit line (gate leg0c inbox+processed union) + "
       "surgical push per r523/r580bmb law (diverged-base claw false-positives x2, origin "
       "moved twice mid-flight; CODELY union with concurrent lines preserved) [via bm-c r374]")
new_sha = git(["commit-tree", tree, "-p", origin_tip, "-m", msg]).stdout.decode().strip()
print("commit-tree: %s (parent %s)" % (new_sha[:12], origin_tip[:12]))
r = git(["push", "origin", new_sha + ":main"], check=False)
if r.returncode != 0:
    print("PUSH REJECTED (origin moved during build): "
          + r.stderr.decode("utf-8", "replace")[:300])
    sys.exit(3)
print("PUSH OK: %s -> origin/main" % new_sha[:12])

# ---- 6. realign local main (r578 law: update-ref -> reset --mixed -> D-face restore) ----
old_local = git(["rev-parse", "main"]).stdout.decode().strip()
git(["update-ref", "refs/heads/main", new_sha, old_local])
git(["reset", "--mixed", new_sha])
st2 = git(["status", "--porcelain"]).stdout.decode("utf-8")
restore = []
for ln in st2.splitlines():
    if ln.startswith(" D") or ln.startswith("D "):
        p = ln[3:].strip().strip('"')
        restore.append(p)
if restore:
    git(["checkout", "--"] + restore)
    print("restored %d origin-side files (D face)" % len(restore))

# ---- 7. post-push verification (delivery proof) ----
git(["fetch", "origin"])
tip2 = git(["rev-parse", "origin/main"]).stdout.decode().strip()
behind = git(["rev-list", "--count", "main..origin/main"]).stdout.decode().strip()
ahead = git(["rev-list", "--count", "origin/main..main"]).stdout.decode().strip()
ls = git(["ls-tree", "--name-only", "origin/main", "--",
          "research/PERPETUAL_N1_W99_PREREG.md"]).stdout.decode().strip()
shard_ls = git(["ls-tree", "--name-only", "origin/main", "--",
                "results/p2cal_ext/n1_w99/"]).stdout.decode()
shard_n = len([x for x in shard_ls.splitlines() if x.strip().endswith(".json")])
codely_has = git(["show", "origin/main:CODELY.md"]).stdout.decode("utf-8")
print("delivery proof: origin/main==%s behind=%s ahead=%s" % (tip2[:12], behind, ahead))
print("W99 prereg on origin: %s | W99 shards on origin: %d | my pit line on origin: %s"
      % (bool(ls), shard_n, MY_PIT_KEY in codely_has))
print("PUSH SEQUENCE COMPLETE")
