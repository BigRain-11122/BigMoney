# r976: relaunch S6 chain driver DETACHED (U060 zero-window; survives session
# tool cancels; r947 25min-kill law). Driver writes its own log; this
# launcher only spawns, waits 3s, reports pid, exits.
import subprocess, sys, time
DETACHED = 0x00000008 | 0x08000000  # DETACHED_PROCESS | CREATE_NO_WINDOW
p = subprocess.Popen(
    [sys.executable, r"results\_r976bmb_s6_chain.py"],
    stdout=open(r"results\_r976bmb_s6_wrap.txt", "w", encoding="utf-8"),
    stderr=subprocess.STDOUT,
    creationflags=DETACHED,
    cwd=r".",
)
time.sleep(3)
rc = p.poll()
print("CHAIN_PID=%d early_rc=%s" % (p.pid, rc))
