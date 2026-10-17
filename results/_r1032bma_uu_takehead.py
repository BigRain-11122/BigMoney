# r1032: batch-resolve S6 regen faces -> take HEAD side (bm-c r1066 13:16 regen > dead-window 12:21)
# these are same-day idempotent-regen faces; newer generated ts = truth; zero data loss (deterministic regen)
import re, subprocess, sys, io

BQ = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def git(*args):
    return subprocess.run(["git", "-C", BQ] + list(args), capture_output=True).stdout.decode("utf-8", "replace")

uu = [l[3:].strip() for l in git("status", "--porcelain").splitlines() if l.startswith("UU ")]
print("UU files:", len(uu))

PAT = re.compile(r"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*\r?\n?", re.S)

n_ok = 0
for path in uu:
    full = BQ + "\\" + path.replace("/", "\\")
    with open(full, "r", encoding="utf-8", newline="") as f:
        t = f.read()
    cnt = [0]
    def repl(m):
        cnt[0] += 1
        side = m.group(1)
        return side + ("\n" if not side.endswith("\n") else "")
    out = PAT.sub(repl, t)
    if cnt[0] == 0:
        print("WARN no-hunk:", path)
        continue
    with open(full, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    n_ok += 1
    if "<<<<<<<" in out or ">>>>>>>" in out:
        print("WARN leftover:", path)
print("resolved:", n_ok)
print("BATCH-HEAD-DONE")
