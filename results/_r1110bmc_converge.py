import subprocess, os, sys

GIT = "C:/Program Files/Git/cmd/git.exe"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FILES = [
    "research/PERPETUAL_N1_W276_PREREG.md",
    "results/_r1110bmc_build_probe.py",
    "results/_r1110bmc_build_w276_derive.py",
    "results/_r1110bmc_commit_msg.txt",
    "results/_r1110bmc_content_check.py",
    "results/_r1110bmc_mkprobe.py",
    "results/_r1110bmc_prep.py",
    "results/_r1110bmc_ram_dump.txt",
    "results/_r1110bmc_src_probe.py",
    "results/_r1110bmc_sweep.py",
    "results/_r1110bmc_sweep.txt",
    "results/_w276bmc_needle_probe.json",
    "results/_w276bmc_prep_facts.json",
    "results/_w276bmc_prereg_derive.py",
    "results/_w276bmc_w275_frozen_face.txt",
]

def git(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip(), r.stderr.decode("utf-8", "replace").strip()

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
print(out[-500:] if out else err[-500:])
rc, head, _ = git(["rev-parse", "HEAD"])
print("HEAD now: %s" % head)
present = all(os.path.exists(os.path.join(REPO, f.replace("/", os.sep))) for f in FILES)
print("all 15 files re-materialized: %s" % present)
