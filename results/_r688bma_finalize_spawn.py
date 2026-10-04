"""r688 bm-a: detached spawn of judge-finalize --wave 3 (harness 5-min silent kill workaround).

Killed foreground run wrote nothing (log 0B, no out file) -> safe re-run.
Writes happen at end only; single-shot + REFINALIZE guards per cmd_judge_finalize.
"""
import subprocess
import sys

LOG = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r688bma_finalize_log.txt"
CMD = [sys.executable, "-u", "scripts/mass_trial_w1.py", "judge-finalize", "--wave", "3"]
logf = open(LOG, "ab")
p = subprocess.Popen(
    CMD,
    stdout=logf,
    stderr=subprocess.STDOUT,
    cwd=r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney",
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
    close_fds=False,
)
print("spawned detached pid:", p.pid)
