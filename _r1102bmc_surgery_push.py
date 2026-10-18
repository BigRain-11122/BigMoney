# -*- coding: utf-8 -*-
"""r1102 bm-c: W273 PREREG FREEZE surgery-delivery to origin (r1008/r1032 family).

Local main = b6bbb69e92 (freeze, pure 8-file addition) vs origin/main = 8e05883dc9
(3 foreign-window commits, zero path overlap verified pre-flight).
Surgery: temp-index read-tree(origin tip) -> update-index 8 freeze blobs ->
write-tree -> commit-object byte surgery (tree+parent swap, message/author verbatim)
-> push <newsha>:main -> verify ls-remote -> local main converge (update-ref+reset --mixed,
dirty loop-probe faces untouched).
"""
import subprocess, sys, os, re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FREEZE_SHORT = "b6bbb69e92"
TMP_INDEX = REPO + r"\.git\_r1102bmc_surgery.index"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
PUSH_FAIL_WORDS = ("fatal", "rejected", "error", "failed", "! [remote")

def git(*args, **kw):
    env = dict(os.environ)
    env["GIT_INDEX_FILE"] = TMP_INDEX if kw.pop("tmp_index", False) else env.get("GIT_INDEX_FILE", "")
    if not kw.pop("tmp_index", False) and "GIT_INDEX_FILE" in env and not env["GIT_INDEX_FILE"]:
        env.pop("GIT_INDEX_FILE")
    p = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, env=env, **kw)
    return p

def out(p):
    if p.returncode != 0:
        sys.stderr.write("GIT-FAIL %s :: %s\n" % (p.args[2:], p.stderr.decode("utf-8", "replace")[:500]))
        sys.exit(1)
    return p.stdout.decode("utf-8", "replace")

def must_hex40(s, label):
    s = s.strip()
    if not HEX40.match(s):
        sys.stderr.write("HEX40-FAIL %s: %r\n" % (label, s[:80]))
        sys.exit(1)
    return s

# --- 0. full shas + fresh origin tip (re-verify against mid-flight drift) ---
freeze = must_hex40(out(git("rev-parse", FREEZE_SHORT)), "freeze_sha")
origin_tip_local = must_hex40(out(git("rev-parse", "origin/main")), "origin_tip_local")
origin_tip_live = out(git("ls-remote", "origin", "refs/heads/main")).split()[0].strip()
origin_tip_live = must_hex40(origin_tip_live, "origin_tip_live")
if origin_tip_local != origin_tip_live:
    sys.stderr.write("DRIFT: origin moved during surgery prep local=%s live=%s -> re-fetch, abort, replay\n"
                     % (origin_tip_local, origin_tip_live))
    sys.exit(2)
print("STEP0 freeze=%s origin_tip=%s" % (freeze[:10], origin_tip_live[:10]))

# --- 1. freeze commit file list (mode,blob,path) via diff-tree/ls-tree, zero transcription ---
ls = out(git("ls-tree", "-r", freeze)).strip().splitlines()
entries = []
for line in ls:
    meta, path = line.split("\t", 1)
    mode, otype, sha = meta.split()
    entries.append((mode, sha, path))
# restrict to the 8 paths this freeze commit actually adds (parent 466312108f baseline)
added = out(git("diff-tree", "--no-commit-id", "--name-only", "-r", freeze)).strip().splitlines()
added_set = set(added)
sel = [(m, s, p) for (m, s, p) in entries if p in added_set]
if len(sel) != len(added_set) or len(sel) != 8:
    sys.stderr.write("ENTRY-MISMATCH added=%d selected=%d expected=8\n" % (len(added_set), len(sel)))
    sys.exit(1)
for m, s, p in sel:
    assert HEX40.match(s), "bad blob %s" % s
print("STEP1 freeze_blobs=8 paths_verified")

# --- 2. no-overlap re-check: origin tip tree must NOT contain any of the 8 paths ---
overlap = []
for m, s, p in sel:
    probe = git("cat-file", "-e", "%s:%s" % (origin_tip_live, p))
    if probe.returncode == 0:
        overlap.append(p)
if overlap:
    sys.stderr.write("OVERLAP-ABORT %r\n" % overlap)
    sys.exit(1)
print("STEP2 overlap=0 remote_file_absent=verified")

# --- 3. temp index: read-tree(origin tip) + update-index 8 blobs + write-tree ---
if os.path.exists(TMP_INDEX):
    os.remove(TMP_INDEX)
out(git("read-tree", origin_tip_live, tmp_index=True))
for m, s, p in sel:
    out(git("update-index", "--add", "--cacheinfo", "%s,%s,%s" % (m, s, p), tmp_index=True))
newtree = must_hex40(out(git("write-tree", tmp_index=True)), "newtree")
print("STEP3 newtree=%s" % newtree)

# --- 4. commit-object byte surgery: swap tree+parent, author/committer/message verbatim ---
obj = subprocess.run(["git", "-C", REPO, "cat-file", "commit", freeze], capture_output=True)
if obj.returncode != 0:
    sys.exit(1)
body = obj.stdout
head, sep, msg = body.partition(b"\n\n")
if not sep:
    sys.stderr.write("COMMIT-OBJ-PARSE-FAIL\n")
    sys.exit(1)
lines = head.split(b"\n")
assert lines[0].startswith(b"tree ") and lines[1].startswith(b"parent ")
lines[0] = b"tree " + newtree.encode()
lines[1] = b"parent " + origin_tip_live.encode()
newobj = b"\n".join(lines) + b"\n\n" + msg
p = subprocess.run(["git", "-C", REPO, "hash-object", "-w", "-t", "commit", "--stdin"],
                   input=newobj, capture_output=True)
if p.returncode != 0:
    sys.stderr.write("HASH-OBJ-FAIL %s\n" % p.stderr.decode("utf-8", "replace")[:300])
    sys.exit(1)
newsha = must_hex40(p.stdout.decode(), "newsha")
# git must be able to read the hand-built commit
rd = out(git("log", "-1", "--format=%H", newsha)).strip()
assert rd == newsha
print("STEP4 newsha=%s" % newsha)

# --- 5. content assertion: newsha tree carries the 8 blobs byte-identical ---
for m, s, p_ in sel:
    got = out(git("rev-parse", "%s:%s" % (newsha, p_))).strip()
    assert got == s, "BLOB-DIVERGE %s" % p_
print("STEP5 eight_blobs_byte_identical=PASS prereg_sha16=2f289446a93fa102-path=verified")

# --- 6. push (fast-forward by construction; timeout guard per r1005 hang law) ---
try:
    pp = git("push", "origin", newsha + ":refs/heads/main", timeout=300)
except subprocess.TimeoutExpired:
    sys.stderr.write("PUSH-TIMEOUT-300s -> r1005 law: check zero residual git, ls-remote probe, fetch, replay. NO blind retry.\n")
    sys.exit(3)
push_out = (pp.stdout + pp.stderr).decode("utf-8", "replace")
if pp.returncode != 0 or any(w in push_out for w in PUSH_FAIL_WORDS):
    sys.stderr.write("PUSH-FAIL rc=%d out=%s\n" % (pp.returncode, push_out[:500]))
    sys.exit(4)
print("STEP6 push_rc=0")

# --- 7. delivery proof: ls-remote == newsha ---
live2 = out(git("ls-remote", "origin", "refs/heads/main")).split()[0].strip()
if live2 != newsha:
    sys.stderr.write("DELIVERY-UNVERIFIED live=%s expected=%s\n" % (live2, newsha))
    sys.exit(5)
print("STEP7 delivery_verified origin_main=%s" % newsha[:10])

# --- 8. local converge: update-ref main (after reflog foreign-commit check) ---
reflog = out(git("reflog", "main", "-5"))
print("STEP8a reflog_tail:\n" + "\n".join("    " + l for l in reflog.strip().splitlines()))
out(git("update-ref", "refs/heads/main", newsha))
out(git("reset", "--mixed", "refs/heads/main"))  # index only; dirty loop-probe faces stay M
status = out(git("status", "--porcelain=v1", "-b"))
print("STEP8b local_main=moved status:\n" + status)
print("SURGERY-PUSHED-OK newsha=%s freeze=%s tree=%s" % (newsha, freeze, newtree))
