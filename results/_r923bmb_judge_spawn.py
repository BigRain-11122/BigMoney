import subprocess, sys, os
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
LOG = os.path.join(ROOT, "results", "alphagen_rl_p1", "judge_burn_r923.log")
flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
         | subprocess.CREATE_NO_WINDOW)
with open(LOG, "a", encoding="utf-8") as lf:
    p = subprocess.Popen([sys.executable, os.path.join(ROOT, "scripts", "alphagen_rl_p1.py"), "judge"],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=flags,
                         cwd=ROOT)
print("judge spawned pid", p.pid, "->", LOG)
