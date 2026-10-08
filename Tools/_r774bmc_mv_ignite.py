"""r774 bm-c A-direction v6 batch ignite: detached spawn of
Tools/_r774bmc_style_gen_v6.py so the SDXL rolling batch survives any
shell-host cap and runs parallel to the S6 chain + QA pack. Poll completion
via results/mv_work/style_gen.log tail 'v6 done' marker + the manifest file
results/mv_work/kf/style_v6_manifest.json. DETACHED_PROCESS + redirected
handles = zero desktop flash (r640 law family). Pattern credit:
Tools/_r773bmc_s6_ignite.py."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r774bmc_mv_v6.out")
ERR = os.path.join(ROOT, "results", "_r774bmc_mv_v6.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(ROOT, "Tools", "_r774bmc_style_gen_v6.py")],
                     cwd=ROOT, stdout=o, stderr=e, creationflags=flags,
                     close_fds=True)
print("MV v6 batch detached pid=%d out=%s" % (p.pid, OUT))
