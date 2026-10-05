# r765 bm-b S6 chain driver: run the 39-leg chain as a child process, capture raw bytes
# (no PS string transcode), write utf-8 log, print tail. Lineage: r749 detached-drv +
# r761-r764 byte-clean log requirement (close script reads window via utf-8 regex).
import subprocess, sys, time
t0 = time.time()
r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                   "-File", r"results\_r765bmb_s6_chain.ps1"],
                   capture_output=True, timeout=1500)
blob = r.stdout + (b"\n== STDERR ==\n" + r.stderr if r.stderr else b"")
open(r"results\_r765bmb_s6_chain.log", "wb").write(blob)
print("rc=%d elapsed=%.0fs bytes=%d" % (r.returncode, time.time() - t0, len(blob)))
tail = blob.decode("utf-8", "replace").splitlines()
print("\n".join(tail[-14:]))
