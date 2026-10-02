# -*- coding: utf-8 -*-
"""r589 bm-b S0-repair: pure-FF integration of the mid-window origin advance
(bm-c r380 + bm-a r589 closing) with the seat commit re-landed on the new base,
plus the shared append-only pool_core_samples.jsonl union (r570/r580 law:
origin bytes verbatim as base + local dict rows appended, line-identity union,
dict-only gate, blob-space LF accounting per r373).

Path = r585 pure-FF precedent (merge-base == own HEAD after the seat-commit
soft undo -> no payload surgery needed):
  1. union pool_core_samples.jsonl -> temp (origin blob + local-only rows)
  2. git reset --mixed <old base> (undo the unpushed seat commit; file stays)
  3. git restore pool_core_samples.jsonl (clean the shared live-writer for FF)
  4. git merge --ff-only origin/main
  5. write the union back to disk (left dirty to ride the freeze commit,
     r587/r588 live-writer precedent)
  6. re-commit the seat on the new base + push (deletion-set claw guards)
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000
POOL = "results/pool_core_samples.jsonl"
UNION_TMP = os.path.join(ROOT, "results", "_r589bmb_pool_union.tmp")


def git(*a, check=True):
    r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True,
                        creationflags=CREAT)
    if check and r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (a[:3], r.stderr.decode("utf-8", "replace")))
    return r


# --- 0. preconditions ---------------------------------------------------------
head = git("rev-parse", "HEAD").stdout.decode().strip()
head_subject = git("log", "-1", "--format=%s").stdout.decode()
assert "W111 seat published=reserved" in head_subject, \
    f"precondition FAIL: HEAD is not my seat commit: {head_subject[:80]}"
old_base = git("rev-parse", "HEAD~1").stdout.decode().strip()
origin = git("rev-parse", "origin/main").stdout.decode().strip()
mb = git("merge-base", "HEAD", "origin/main").stdout.decode().strip()
assert mb == old_base, f"precondition FAIL: merge-base {mb} != seat parent {old_base}"
print(f"precondition OK: HEAD={head[:9]} (seat), parent==merge-base={old_base[:9]}, "
      f"origin={origin[:9]}")

# --- 1. union the shared append-only face (blob-space LF per r373) -------------
r = git("show", f"origin/main:{POOL}")
origin_bytes = r.stdout
origin_lines = [ln for ln in origin_bytes.decode("utf-8").split("\n") if ln.strip()]
local_bytes = open(os.path.join(ROOT, POOL), "rb").read()
local_eol_crlf = local_bytes.count(b"\r\n") * 2 > local_bytes.count(b"\n")
local_txt = local_bytes.decode("utf-8").replace("\r\n", "\n")
local_lines = [ln for ln in local_txt.split("\n") if ln.strip()]

origin_set = set(origin_lines)
assert all(isinstance(json.loads(ln), dict) for ln in origin_lines), \
    "UNION ABORT: origin blob has non-dict rows (r570 corruption face)"
assert all(isinstance(json.loads(ln), dict) for ln in local_lines), \
    "UNION ABORT: local file has non-dict rows (r570 corruption face -- inspect first)"
local_only = [ln for ln in local_lines if ln not in origin_set]
union_lines = origin_lines + local_only
union_blob = ("\n".join(union_lines) + "\n").encode("utf-8")
with open(UNION_TMP, "wb") as f:
    f.write(union_blob)
print(f"union: origin={len(origin_lines)} rows verbatim base + local-only="
      f"{len(local_only)} appended (local total was {len(local_lines)}, "
      f"overlap already-on-origin={len(local_lines) - len(local_only)}) -> "
      f"union={len(union_lines)} rows, blob-space LF, saved {UNION_TMP}")

# --- 2. undo the unpushed seat commit (file survives in worktree) --------------
git("reset", "--mixed", old_base)
st = git("status", "--porcelain").stdout.decode()
assert f"?? {POOL.split('/')[-1]}" not in st, "seat reset sanity"
print(f"step2: seat commit undone (HEAD={old_base[:9]}), seat file now untracked")

# --- 3. clean the shared live-writer face for the FF ---------------------------
git("restore", POOL)
r = git("status", "--porcelain", "--", POOL)
assert r.stdout.decode().strip() == "", "pool_core_samples not clean after restore"
print("step3: pool_core_samples.jsonl restored to HEAD version (union saved aside)")

# --- 4. pure fast-forward -------------------------------------------------------
git("merge", "--ff-only", "origin/main")
new_head = git("rev-parse", "HEAD").stdout.decode().strip()
assert new_head == origin, f"FF failed: HEAD {new_head[:9]} != origin {origin[:9]}"
print(f"step4: pure FF landed, HEAD=origin={new_head[:9]}")

# --- 5. write the union back (left dirty, rides the freeze commit) -------------
disk = union_blob.replace(b"\n", b"\r\n") if local_eol_crlf else union_blob
open(os.path.join(ROOT, POOL), "wb").write(disk)
disk_lines = [ln for ln in open(os.path.join(ROOT, POOL), "rb").read()
              .decode("utf-8").replace("\r\n", "\n").split("\n") if ln.strip()]
assert disk_lines == union_lines, "union write-back verification FAILED"
assert all(isinstance(json.loads(ln), dict) for ln in disk_lines), \
    "post-write dict gate FAILED (r570 law)"
r = git("status", "--porcelain", "--", POOL)
assert r.stdout.decode().strip() == f" M {POOL}", \
    f"pool status after union write unexpected: {r.stdout.decode()!r}"
print(f"step5: union written back to disk ({len(disk_lines)} rows all dict), "
      "left dirty to ride the freeze commit (r587 precedent)")

# --- 6. re-commit the seat on the new base + push ------------------------------
seat = "fleet/inbox/MSG-20261002-1911-bmb-w111-seat.md"
assert os.path.exists(os.path.join(ROOT, seat)), "seat file lost from worktree"
git("add", seat)
msg = ("W111 seat published=reserved (bm-b 38th owned wave, 101st engine wave "
       "by machine-derive; A 265_004..267_003 / B 61_401..61_600 both "
       "arithmetic continuation from the registered W110 tails hops=0, "
       "pre-seat machine ADMIT results/_r589bmb_w111_probe.py rc0; published "
       "BEFORE freeze per r565 early-visibility law; upstream chain W1..W107 "
       "landed (W107 bm-a r589 closing landed mid-window, head derives from "
       "n1_w107_results.json), W108 bm-c next in finalize chain, W108/W109 "
       "products 12/12 delivered finalize pending, W110 bm-a 12/12 delivered "
       "finalize pending; first seat push rejected by origin advance -> "
       "re-landed on new base via r585 pure-FF window + r570 pool union). "
       "[via bm-b r589]")
git("commit", "-m", msg)
r = git("push", "origin", "main", check=False)
out = (r.stdout + r.stderr).decode("utf-8", "replace")
print("push:", out.strip()[-400:] if out.strip() else "(clean)")
if r.returncode != 0:
    sys.exit("PUSH STILL REJECTED -- do not force; fall back to machine branch")
final_head = git("rev-parse", "HEAD").stdout.decode().strip()
r = git("ls-remote", "origin", "refs/heads/main")
remote_main = r.stdout.decode().split()[0] if r.stdout.decode().split() else "?"
assert remote_main == final_head, f"delivery FAIL: remote {remote_main[:9]} != HEAD {final_head[:9]}"
print(f"S0_REPAIR_OK: seat re-landed {final_head[:9]} == origin/main; "
      f"local-not-at-origin commits = 0")
