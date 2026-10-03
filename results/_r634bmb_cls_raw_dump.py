"""r634 bm-b: dump raw classifier output to file (bytes-safe) and show keys."""
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
CLS = (
    r"C:\Fluxgroup\FluxGroup\quant\bigmoney\.codely-cli\skills"
    r"\bigmoney-conflict-resolve\scripts\classify_conflicts.py"
)
p = subprocess.run([sys.executable, CLS], cwd=ROOT, capture_output=True)
open(r"results/_r634bmb_cls_raw.txt", "wb").write(p.stdout)
open(r"results/_r634bmb_cls_err.txt", "wb").write(p.stderr)
print("rc=", p.returncode, "stdout_bytes=", len(p.stdout), "stderr_bytes=", len(p.stderr))
print("HEAD:")
print(p.stdout.decode("utf-8", errors="replace")[:1500])
