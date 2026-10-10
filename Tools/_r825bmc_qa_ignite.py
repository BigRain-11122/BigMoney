"""r825 bm-c QA pack ignite: detached spawn of scripts/qa_smoke_run.py with
EXPLICIT --round 825 (r758/r640/r644 law family: explicit round label is the
canon). Output pair redirected to results/_r825bmc_qa_runner.{out,err}; runner
survives the wrapper kill (DETACHED_PROCESS, r640 law). Pre-ignition
name-collision pre-check IN-PROCESS (origin qa/ tree must show zero r825-bm-c
files before net-write). Pattern credit: Tools/_r819bmc_qa_ignite.py (clone)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "qa/"],
                   cwd=ROOT, capture_output=True, creationflags=CNW, timeout=60)
hits = [l for l in (r.stdout or b"").decode("utf-8", "replace").splitlines()
        if "r825-bm-c" in l]
if r.returncode != 0 or hits:
    print("QA-PRECHECK FAIL rc=%d hits=%s" % (r.returncode, hits))
    raise SystemExit(3)

OUT = os.path.join(ROOT, "results", "_r825bmc_qa_runner.out")
ERR = os.path.join(ROOT, "results", "_r825bmc_qa_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "scripts", "qa_smoke_run.py"),
                      "--round", "825"],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("QA runner detached pid=%d round=825 out=%s" % (p.pid, OUT))



