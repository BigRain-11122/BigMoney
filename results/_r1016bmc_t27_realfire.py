"""T27 real-fire: per-machine daemon face deletion now passes the claw.

Reproduces the r1011 live-fire shape (deleting results/*.bm-c.json
faces from bm-c) via plumbing temp-index commits -- zero working-tree
touch, dangling objects only. Also fires the negative leg (deleting a
*.bm-a.json face from bm-c = foreign, still blocked).
"""
import os
import subprocess
import sys

REPO = os.getcwd()
TMP_INDEX = os.path.join(REPO, ".git", "tmp-index-t27")


def g(args, env=None):
    return subprocess.run(["git"] + args, capture_output=True, cwd=REPO,
                          env=env, creationflags=0x08000000)


base_env = dict(os.environ)
base_env["GIT_INDEX_FILE"] = TMP_INDEX


def temp_commit_without(path):
    if os.path.exists(TMP_INDEX):
        os.remove(TMP_INDEX)
    assert g(["read-tree", "HEAD"], base_env).returncode == 0
    r = g(["ls-files", "--", path], base_env)
    tracked = r.stdout.decode().strip().splitlines()
    assert tracked, "fixture path not tracked in HEAD: %s" % path
    assert g(["update-index", "--force-remove", "--", path], base_env).returncode == 0
    tree = g(["write-tree"], base_env).stdout.decode().strip()
    c = g(["commit-tree", tree, "-p", "HEAD", "-m",
           "claw real-fire T27 (dangling)"], base_env)
    assert c.returncode == 0, c.stderr.decode()[:200]
    return c.stdout.decode().strip()


def claw(old, new):
    r = subprocess.run([sys.executable, "Tools/git_claw.py", "check-push",
                        old, new], capture_output=True, cwd=REPO,
                        creationflags=0x08000000)
    return r.returncode, r.stdout.decode(errors="replace")


def blob_has_machine_field(path):
    r = g(["show", "HEAD:%s" % path])
    body = r.stdout.decode(errors="replace")
    return ('"machine"' in body) or ('"machine_id"' in body)


head = g(["rev-parse", "HEAD"]).stdout.decode().strip()
print("HEAD:", head[:12])

# leg 1: self-owned per-machine daemon face (bm-c deletes its own)
self_face = "results/compute_audit.bm-c.json"
print("self_face tracked, machine field inside blob:",
      blob_has_machine_field(self_face))
c1 = temp_commit_without(self_face)
rc1, out1 = claw(head, c1)
print("LEG1 self-owned daemon face -> rc=%d (expect 0)" % rc1)
print(out1.strip()[:200])

# leg 2: foreign per-machine daemon face (bm-c deletes a bm-a face)
r = g(["ls-files", "results/*.bm-a.json"])
foreign = sorted(l for l in r.stdout.decode().splitlines()
                 if l.strip() and not blob_has_machine_field(l.strip()))
assert foreign, "no bm-a daemon face without machine field in HEAD"
foreign_face = foreign[0]
print("foreign_face:", foreign_face)
c2 = temp_commit_without(foreign_face)
rc2, out2 = claw(head, c2)
print("LEG2 foreign daemon face -> rc=%d (expect 1)" % rc2)
print(out2.strip()[:300])

os.remove(TMP_INDEX)
ok = (rc1 == 0 and rc2 == 1 and "(filename, T27)" in out2)
print("REALFIRE VERDICT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
