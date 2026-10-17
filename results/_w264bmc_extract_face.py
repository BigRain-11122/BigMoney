# -*- coding: utf-8 -*-
# r1076 bm-c: extract the FROZEN W263 prereg template face (PRE-BACKFILL, freeze-commit b32f6bf1c)
# per r1052/r1049 law (never derive from a backfilled twin). Byte-exact via git cat-file subprocess.
import subprocess, hashlib, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
TPL = "research/PERPETUAL_N1_W263_PREREG.md"
FREEZE_SHA = "b32f6bf1c"
OUT = os.path.join(REPO, "results", "_w264bmc_w263_frozen_face.txt")


def git_bytes(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout


blob = git_bytes(["rev-parse", FREEZE_SHA + ":" + TPL]).decode("ascii").strip()
twin = git_bytes(["rev-parse", "HEAD:" + TPL]).decode("ascii").strip()
data = git_bytes(["cat-file", "blob", blob])
with open(OUT, "wb") as f:
    f.write(data)

# byte-identity verification: disk == blob (hash-object) == freeze-commit face
ho = git_bytes(["hash-object", OUT]).decode("ascii").strip()
assert ho == blob, "hash-object mismatch: %s != %s" % (ho, blob)

print("frozen tpl blob @ %s: %s" % (FREEZE_SHA, blob))
print("HEAD twin (post-backfill disclosure face, NOT used): %s" % twin)
print("bytes: %d  lines: %d  sha256_16: %s" % (
    len(data), data.count(b"\n") + 1, hashlib.sha256(data).hexdigest()[:16]))

# W263 finalize actuals (machine-read live, never transcribed)
res_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w263_results.json")
with open(res_path, encoding="utf-8") as f:
    res = json.load(f)
print("=== n1_w263_results.json keys ===")
print(json.dumps({k: v for k, v in res.items() if not isinstance(v, (dict, list))},
                 ensure_ascii=False, indent=1)[:2400])
