# -*- coding: utf-8 -*-
# r1113 bm-c local convergence: CAS freeze commit e0bc4a0ddd landed via API
# (blobs/trees/commits chain, zero local index) -> verify the 11 untracked twins
# byte-equal to origin blobs (hash-object clean-filter comparison, r1110 converge
# precedent; CAS blobs were hash-object -w default-filter created), delete them,
# ff-pull so HEAD==origin/main, verify all 11 re-materialized. The 2 regenerable
# daemon live-faces (fleet/machine-health.json staged + results/watermark_red.json
# unstaged) are NOT touched by the incoming range -> ff proceeds around them.
import os, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FILES = [
    "research/PERPETUAL_N1_W277_PREREG.md",
    "results/_r1113bmc_build_w277_derive.py",
    "results/_r1113bmc_commit_msg.txt",
    "results/_r1113bmc_content_check.py",
    "results/_r1113bmc_prep.py",
    "results/_r1113bmc_sweep2d.py",
    "results/_r1113bmc_sweep_receipt.json",
    "results/_w277bmc_needle_probe.json",
    "results/_w277bmc_prep_facts.json",
    "results/_w277bmc_prereg_derive.py",
    "results/_w277bmc_w276_frozen_face.txt",
]
EXPECT_ORIGIN = "e0bc4a0dddcac66ecf7af971d7119aeff19febca"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=REPO)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip(), r.stderr.decode("utf-8", "replace").strip()


rc, origin_tip, _ = git(["rev-parse", "origin/main"])
if origin_tip != EXPECT_ORIGIN:
    print("ORIGIN MOVED: %s (expected %s) -- re-verify before delete" % (origin_tip, EXPECT_ORIGIN))
    sys.exit(1)

mismatch = []
for f in FILES:
    rc, origin_blob, _ = git(["rev-parse", "origin/main:%s" % f])
    rc2, local_h, _ = git(["hash-object", f])
    status = "MATCH" if origin_blob == local_h else "DIFF"
    if origin_blob != local_h:
        mismatch.append(f)
    print("%s %s  origin=%s local=%s" % (status, f, origin_blob[:12], local_h[:12]))

if mismatch:
    print("MISMATCH: %r -- NOT deleting, manual adjudication needed" % mismatch)
    sys.exit(1)

for f in FILES:
    os.remove(os.path.join(REPO, f.replace("/", os.sep)))
print("twins deleted: %d" % len(FILES))

rc, out, err = git(["pull", "--ff-only"])
print("pull rc=%d" % rc)
print((out or err)[-600:])
rc, head, _ = git(["rev-parse", "HEAD"])
rc2, origin2, _ = git(["rev-parse", "origin/main"])
print("HEAD now: %s" % head)
print("origin  : %s" % origin2)
present = all(os.path.exists(os.path.join(REPO, f.replace("/", os.sep))) for f in FILES)
print("all 11 files re-materialized: %s" % present)
if not (head == EXPECT_ORIGIN and present):
    print("CONVERGE FAILED")
    sys.exit(1)
print("CONVERGE OK HEAD==origin/main==e0bc4a0ddd, 11/11 twins re-materialized")
